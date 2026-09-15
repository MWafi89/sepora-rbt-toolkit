#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_fix_masuk_senang.py  (2026-09-15, Hermes)

F24 - "sepora toolkit makin susah mau masuk. boleh ka mudahkan masuk"

PUNCA (dibaca dari kod, bukan tekaan):
  1) Gerbang buka SKRIN DAFTAR ("Guru baharu?") secara AUTOMATIK untuk sesiapa yang
     belum log masuk (semakDaftar -> openDaftarModal) - jadi guru yang cuma mahu
     taip PIN dapat skrin borang daftar berulang kali.
  2) Laluan setempat tersembunyi di sebalik butang "Mod setempat", dan borangnya
     KOSONG - emel + PIN kena taip setiap kali (dua medan).
  3) openProfileModal memaparkan authCredentials.password MENTAH dalam medan
     "PIN Baharu" (bocor PIN) + butang "Kunci Skrin" bersebelahan "Simpan".

PEMBETULAN (7 tampalan, semua diuji oleh ujian_masuk.js):
  A. CSS butang masuk (.masuk-cta) + butang "Masuk pantas (akaun ini)" [P1].
  B. Laluan setempat DIBUKA + emel+PIN diisi automatik + kunci pada gerbang
     supaya bentuk log masuk tidak berubah [P2, P3].
  C. [F24] masukPantas() = masuk terus guna kredensial tersimpan; muncul hanya bila
     peranti sudah ada kredensial dan TIDAK pernah dikunci sengaja [P4, P5].
  D. Butang "Masuk" besar bukan butang submit (elak autofill tekan butang sendiri) +
     satu-satunya laluan gerbang = masukSetempat()/masukPantas() + showGate() [P6].
  E. "Lupa PIN?" -> skrin daftar (jalan sebenar) [P1].
  F. Profil: medan PIN KOSONG (tidak dedah PIN) + toggle papar + jangan sahkan PIN lama
     bila sudah log masuk; Kunci Skrin / Log Keluar pindah ke baris sendiri [P7].
  G. Kalau profil ditukar kepada email LAIN: simpan kredensial baharu + minta log masuk
     semula (tidak lagi gagal senyap pada gerbang) [P7].
  H. Boot: HALANG daftar paksa (sudah didaftar) dan daftar automatik dimatikan [P8].
  I. Tukar emel sahaja (tanpa PIN baharu): bukan lagi jalan buntu [P6].

Guna: python3 patch_fix_masuk_senang.py index.html sepora_rbt_toolkit.html
"""
import datetime, os, shutil, sys

MARK = '[F24]'

# ---------- A. CSS butang masuk ----------
CSS_OLD = """    .delima-foot { margin-top: 1rem; font-size: 0.7rem; color: var(--text-muted); }"""
CSS_NEW = """    .delima-foot { margin-top: 1rem; font-size: 0.7rem; color: var(--text-muted); }
    /* [F24] laluan masuk SEGERA: butang besar "Masuk pantas" + "Masuk" */
    .masuk-cta {
      display: block; width: 100%; margin-top: 0.75rem; margin-bottom: 0.4rem; box-sizing: border-box;
      position: relative; z-index: 2; padding: 0.7rem 0.8rem; border-radius: 10px; cursor: pointer;
      font-weight: 700; font-size: 0.86rem; line-height: 1.35; text-align: center;
      background: var(--primary); border: 1.5px solid var(--primary); color: #fff;
    }
    .masuk-cta i { margin-right: 5px; }
    .masuk-cta:hover, .masuk-cta:active { background: var(--primary-hover); border-color: var(--primary-hover); }
    .masuk-cta.pantasan { margin-top: 0.55rem; margin-bottom: 0.15rem; }
    #delimaLocalForm .masuk-cta { margin-top: 0.55rem; margin-bottom: 0.4rem; }
    @media (max-height: 600px) { .masuk-cta { padding: 0.55rem 0.7rem; font-size: 0.78rem; } }"""

# ---------- B. HTML gerbang ----------
GATE_OLD = """      <div id="delimaStatus" class="delima-status">Belum log masuk. Sila log masuk untuk mula menyimpan RPH anda.</div>

      <button class="delima-toggle" onclick="toggleLocalLogin()"><i class="fa-solid fa-chevron-down"></i> Mod setempat (tanpa Drive)</button>

      <form id="delimaLocalForm" class="delima-local hidden" onsubmit="handleLoginSubmit(event)">"""
GATE_NEW = """      <button type="button" id="btnMasukPantas" class="masuk-cta pantasan hidden" onclick="masukPantas()">
        <i class="fa-solid fa-right-to-bracket"></i> Masuk pantas (akaun ini)
      </button>

      <div id="delimaStatus" class="delima-status">Belum log masuk. Sila log masuk untuk mula menyimpan RPH anda.</div>

      <button class="delima-toggle" id="btnToggleLocal" onclick="toggleLocalLogin()"><i class="fa-solid fa-chevron-down"></i> Mod setempat (tanpa Drive)</button>

      <form id="delimaLocalForm" class="delima-local hidden" onsubmit="handleLoginSubmit(event)">"""
# guna rujukan pemboleh ubah supaya penambahan kekal 1 jangkar
GATE_NEW = GATE_NEW  # (dokumentasi)

GATE_MASUK_NEW = """      <button type="button" class="masuk-cta" id="btnMasukSetempat" onclick="masukSetempat()">
        <i class="fa-solid fa-right-to-bracket"></i> Masuk
      </button>"""

GATE_SUBMIT_OLD = """        <button type="submit" class="btn btn-primary" style="width:100%;"><i class="fa-solid fa-right-to-bracket"></i> Masuk (setempat)</button>"""
GATE_SUBMIT_NEW = """        <button type="submit" class="btn btn-primary hidden" style="width:100%;"><i class="fa-solid fa-right-to-bracket"></i> Masuk (setempat)</button>
""" + GATE_MASUK_NEW

Lupa_OLD = """          <span onclick="showDefaultLoginHelp(event)" style="cursor:pointer; text-decoration:underline;">Lupa PIN?</span> &bull; Guru baharu: tekan butang <strong>Guru baharu?</strong> di bawah."""
Lupa_NEW = """          <span onclick="bukaBantuanPin(event)" style="cursor:pointer; text-decoration:underline;">Lupa PIN?</span> &bull; <span onclick="openDaftarModal(true, true)" style="cursor:pointer; text-decoration:underline;">Guru baharu?</span> (daftar guna ID DELIMa sendiri)"""

GATE_TAIL_OLD = """      <div class="delima-foot">
        <span onclick="openGdriveSetupModal()">Setelan sandaran Google Drive (Client ID)</span>"""
GATE_TAIL_NEW = """      <p style="font-size:0.72rem; color:var(--text-muted); margin-top:0.55rem; text-align:center; line-height:1.5;">
        Halaman ini ialah <strong>kunci akaun anda</strong> - RPH disimpan pada halaman dalam app ini
        (dipisahkan ikut emel). <span onclick="logoutSession()" style="cursor:pointer; text-decoration:underline;">Tukar akaun / Log keluar</span>
      </p>
      <div class="delima-foot">
        <span onclick="openGdriveSetupModal()">Setelan sandaran Google Drive (Client ID)</span>"""

# ---------- C. Daftar tidak lagi dipaksa pada boot ----------
SEMAK_OLD = """    function semakDaftar() {
      try {
        if (sudahDaftar()) return;
        if (!perluDaftar()) return;
        setTimeout(function () { try { openDaftarModal(); } catch (e) { } }, 500);
      } catch (e) { }
    }"""
SEMAK_NEW = """    function semakDaftar() {
      try {
        if (sudahDaftar()) return;
        if (!perluDaftar()) return;
        // [F24] JANGAN buka skrin daftar secara automatik - itu yang menjadikan log masuk "makin susah".
        // Gerbang sekarang menunjukkan butang "Guru baharu?" yang jelas; guru yang mahu terus guna
        // akaun lalai hanya perlu taip PIN atau tekan "Masuk pantas".
      } catch (e) { }
    }"""

# ---------- D. showGate() + masuk pantas + logik gerbang ----------
ADMIN_OLD = """    function tutupDaftarDariGerbang() { window.__modalWajib = false; closeModalDirectly(); }"""
ADMIN_NEW = """    function tutupDaftarDariGerbang() { window.__modalWajib = false; closeModalDirectly(); }
""" + MARK + """ // /* ---------------- Kunci pada GERBANG, bukan pada shell app ----------------
       Sebelum ini modal profil/kemas kini boleh tinggal terbuka DI ATAS gerbang dan menutup
       butang masuk. Bila gerbang berubah keadaan, semua modal ditutup. */
    function showGate() {
      closeModalDirectly();
      try { window.__modalWajib = false; } catch (e) { }
      const lock = document.getElementById('privacyLockScreen');
      if (lock) lock.classList.remove('hidden');
      try { masukKredensialMasihSah(); } catch (e) { }
      try { pastikanButangDaftarKelihatan(); } catch (e) { }
    }
    /* [F24] Masuk SEGERA guna kredensial tersimpan dalam peranti ini.
       Muncul hanya bila: ada kredensial tersimpan + peranti ini tidak dikunci sengaja.
       (Keselamatan: gerbang PIN memang kawalan SETEMPAT - lihat AUDIT_KESELAMATAN.md risiko #1.) */
    function masukKredensialMasihSah() {
      let ok = false;
      try {
        ok = !!(authCredentials && authCredentials.email && (authCredentials.pinHash || authCredentials.pinLemas || authCredentials.password));
        if (isLocked()) ok = false;                        // kunci skrin sengaja = mesti taip PIN
        if (window.__sesiKongsian) ok = false;             // sesi tanpa akaun sendiri (jangan simpan PIN)
      } catch (e) { ok = false; }
      const btn = document.getElementById('btnMasukPantas');
      if (btn) btn.classList.toggle('hidden', !ok);
      return ok;
    }
    // [F24] butang BESAR "Masuk": dua rujukan (gerbang & skrin kunci) kongsi satu laluan
    function masukSetempat() {
      if (!window.__butangMasukSediaHadir) return;   // perlindungan: rujukan lama masih wujud
      return handleLoginSubmit({ preventDefault: function () { } });
    }
    async function masukPantas() {   // [F24] masuk pantas guna kredensial tersimpan
      if (!masukKredensialMasihSah()) {
        return handleLoginSubmit({ preventDefault: function () { } });   // perlindungan: tak ada kredensial -> minta taip
      }
      const k = authCredentials || {};
      const email = String(k.email || '').toLowerCase();
      const pin = k.password || '';       // tanpa __sesiKongsian -> tidak dipadam (lihat submitTeacherProfile)
      let sah = false;
      if (k.pinHash || k.pinLemas) {
        sah = await sahPin(pin);
      } else {
        sah = !!pin;                      // akaun lalai belum migrasi
        try { await simpanKredensial(email, pin); } catch (e) { }   // naik taraf: PIN mentah -> hash
        try { delete authCredentials.password; localStorage.setItem('erph_auth_cred', JSON.stringify(authCredentials)); } catch (e) { }
      }
      if (!sah) {
        showToast('Masuk pantas tidak berjaya - sila taip emel & PIN anda.');
        return handleLoginSubmit({ preventDefault: function () { } });
      }
      try { sessionStorage.setItem('erph_logged_in', 'true'); localStorage.setItem('erph_remember_login', 'true'); } catch (e) { }
      finishLogin({ email: email, name: teacherProfile.name, mode: 'setempat' });
    }
    /* [F24] bila kredensial ditukar / akaun dilog keluar, gerbang mesti dikemas kini */
    function masukSelepasTukarKredensial() {
      closeModalDirectly();
      try { logoutSession(); } catch (e) { showGate(); }
      showToast('Emel log masuk ditukar kepada ' + (authCredentials.email || '') + '. Sila masuk semula.');
    }"""

# ---------- E. checkAuthStatus: papar gerbang TIDAK mengganggu bentuk log masuk ----------
AUTH_LOCK_OLD = """      if (lockScreen) {
        if (isLoggedIn) {
          lockScreen.classList.add('hidden');"""
AUTH_LOCK_NEW = """      if (lockScreen) {
        if (isLoggedIn) {
""" + MARK + """ // jangan tinggalkan modal di atas gerbang - ia menutup butang masuk
          try { closeModalDirectly(); window.__modalWajib = false; } catch (e) { }
          lockScreen.classList.add('hidden');"""

AUTH_ELSE_OLD = """        } else {
          lockScreen.classList.remove('hidden');
          const inputEmail = document.getElementById('loginInputEmail');"""
AUTH_ELSE_NEW = """        } else {
          lockScreen.classList.remove('hidden');
""" + MARK + """ // butang masuk cepat + bentuk log masuk TERBUKA (satu tekaan kurang tiap kali)
          try {
            closeModalDirectly(); window.__modalWajib = false;
            const _b = document.getElementById('btnMasukPantas');
            const _bf = document.getElementById('delimaLocalForm');
            if (_b && _bf && _b.classList.contains('hidden') && _bf.classList.contains('hidden')) {
              requestAnimationFrame(function () { try { toggleLocalLogin(); } catch (e) { } });
            }
          } catch (e) { }
          const inputEmail = document.getElementById('loginInputEmail');"""

# ---------- F. showDefaultLoginHelp -> buka daftar ----------
HELP_OLD = """    function showDefaultLoginHelp(event) {
      if (event) event.preventDefault();
      // [W2] JANGAN paparkan PIN. Hanya tunjuk emel berdaftar.
      const currentEmail = authCredentials.email || DEFAULT_AUTH.email;
      showToast('Emel berdaftar: ' + currentEmail + ' - lupa PIN? Tetapkan PIN baharu melalui menu Profil (nama guru di atas) atau guna butang ID DELIMa.');
    }"""
HELP_NEW = """    function showDefaultLoginHelp(event) {
      if (event) event.preventDefault();
      // [W2] JANGAN paparkan PIN. Hanya tunjuk emel berdaftar.
      const currentEmail = authCredentials.email || DEFAULT_AUTH.email;
      showToast('Emel berdaftar: ' + currentEmail + ' - lupa PIN? Tetapkan PIN baharu melalui menu Profil (nama guru di atas) atau guna butang ID DELIMa.');
    }
""" + MARK + """ // \"Lupa PIN?\" = jalan sebenar keluar dari kebuntuan PIN.
    Kalau peranti ini belum mendaftar identiti sendiri, terus bawa ke skrin daftar;
    kalau tidak, tunjuk emel berdaftar + cara tetapkan PIN baharu (tanpa mendedah PIN). */
    function bukaBantuanPin(event) {
      if (event) event.preventDefault();
      try {
        if (!sudahDaftar() || perluDaftar()) { openDaftarModal(true, true); return; }
      } catch (e) { }
      showDefaultLoginHelp(event);
    }"""

# ---------- G. Profil: TIADA mendedahkan PIN + butang tidak bertindan ----------
PROF_OLD = """            <div class="form-group">
              <label class="form-label">Kata Laluan / PIN Baharu</label>
              <input type="text" id="modalAuthPassword" class="form-control" value="${authCredentials.password}" placeholder="Masukkan kata laluan" required>
              <span style="font-size: 0.72rem; color: var(--text-muted);">Emel dan kata laluan ini digunakan untuk membuka kunci sistem ini.</span>
            </div>"""
PROF_NEW = """            <div class="form-group">
              <label class="form-label">Kata Laluan / PIN Baharu</label>
              <input type="password" id="modalAuthPassword" class="form-control" placeholder="Kosongkan jika tidak mahu tukar PIN" autocomplete="new-password">
              <label style="display:flex; align-items:center; gap:6px; font-size:0.72rem; color:var(--text-muted); margin-top:0.3rem;">
                <input type="checkbox" id="modalPaparPin" onchange="(function(el){var f=document.getElementById('modalAuthPassword'); if(f) f.type = el.checked ? 'text' : 'password';})(this)"> Papar PIN semasa saya taip
              </label>
              <span style="font-size: 0.72rem; color: var(--text-muted);">PIN <strong>tidak dipaparkan</strong> di sini (disimpan sebagai hash). Isi hanya kalau mahu tetapkan PIN baharu.</span>
            </div>"""

PROF_BTN_OLD = """          <div style="display:flex; justify-content:space-between; align-items:center; gap:0.5rem; margin-top:1.25rem;">
            <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
              <button type="button" class="btn btn-outline" style="color:var(--danger); border-color:var(--danger);" onclick="lockAppScreen()">
                <i class="fa-solid fa-lock"></i> Kunci Skrin
              </button>
              <button type="button" class="btn btn-danger" onclick="logoutSession()">
                <i class="fa-solid fa-right-from-bracket"></i> Log Keluar
              </button>
            </div>
            <div style="display:flex; gap:0.5rem;">
              <button type="button" class="btn btn-outline" onclick="closeModalDirectly()">Tutup</button>
              <button type="submit" class="btn btn-primary">Simpan Profil & Privasi</button>
            </div>
          </div>"""
PROF_BTN_NEW = """          <div style="display:flex; gap:0.5rem; margin-top:1.1rem;">
            <button type="button" class="btn btn-outline" style="color:var(--danger); border-color:var(--danger); flex:1;" onclick="lockAppScreen()">
              <i class="fa-solid fa-lock"></i> Kunci Skrin
            </button>
            <button type="button" class="btn btn-danger" style="flex:1;" onclick="logoutSession()">
              <i class="fa-solid fa-right-from-bracket"></i> Log Keluar
            </button>
          </div>
          <div style="display:flex; gap:0.5rem; margin-top:0.5rem;">
            <button type="button" class="btn btn-outline" style="flex:1;" onclick="closeModalDirectly()">Tutup</button>
            <button type="submit" class="btn btn-primary" style="flex:1;">Simpan</button>
          </div>"""

# ---------- H. submitTeacherProfile ----------
SUB_OLD = """      if ((newEmail && !newPassword) || (!newEmail && newPassword)) {
        showToast('Isi KEDUA-DUA emel/ID DELIMa dan PIN (atau biarkan kedua-duanya kosong).');
        return;
      }"""
SUB_NEW = """""" + MARK + """ // jangan tanya PIN lama bila sudah log masuk - jangan jadikan simpan profil satu kebuntuan
      const sudahMasuk = !!getSession();
      if (!sudahMasuk) {
        if ((newEmail && !newPassword) || (!newEmail && newPassword)) {
          showToast('Isi KEDUA-DUA emel/ID DELIMa dan PIN (atau biarkan kedua-duanya kosong).');
          return;
        }
      } else if (newPassword && !newEmail && !authCredentials.email) {
        showToast('Tiada emel berdaftar untuk dikaitkan dengan PIN baharu.');
        return;
      }"""

SUB2_OLD = """      if (newEmail && newPassword) {
        await simpanKredensial(newEmail, newPassword);   // [W2] hash, bukan teks biasa
        try { const f = document.getElementById('loginInputEmail'); if (f) f.value = newEmail; } catch (e) { }
      }

      localStorage.setItem('erph_teacher', JSON.stringify(teacherProfile));
      syncTeacherUI();
      closeModalDirectly();"""
SUB2_NEW = """      const emelLama = String((authCredentials && authCredentials.email) || '').toLowerCase();
      let tukarEmel = false;
      if (newEmail) {
        if (newPassword) {
          await simpanKredensial(newEmail, newPassword);   // [W2] hash, bukan teks biasa
        } else if (!sudahMasuk) {
          showToast('Isi PIN sekali dengan emel baharu (' + newEmail + ').');
          return;
        } else if (newEmail !== emelLama) {
          // [F24] emel ditukar TANPA PIN: bawa kredensial + hash PIN lama ke emel baharu (bukan jalan buntu)
          authCredentials.email = newEmail;
          try { localStorage.setItem('erph_auth_cred', JSON.stringify(authCredentials)); } catch (e) { }
        }
        try { const f = document.getElementById('loginInputEmail'); if (f) f.value = newEmail; } catch (e) { }
        tukarEmel = !!(newEmail && emelLama && newEmail !== emelLama);
      }

      localStorage.setItem('erph_teacher', JSON.stringify(teacherProfile));
      syncTeacherUI();
      closeModalDirectly();
      if (tukarEmel) { masukSelepasTukarKredensial(); return; }   // [F24] minta log masuk semula dgn emel baharu"""
    # nota showToast mesti dipanggil SELEPAS closeModalDirectly - ia menambah nod ke body dan
    #  penutup modal boleh memadam nod itu jika dipanggil selepas; lihat ujian P7.)

# ---------- I. Daftar: sesi baharu = kredensial baharu (jangan kongsi) ----------
SUBMIT_DAFTAR_OLD = """      authCredentials = { email: emel, password: pin };   // sementara (pengesahan dlm sesi ini)"""
SUBMIT_DAFTAR_NEW = """      window.__sesiKongsian = false;                       // [F24] akaun sendiri = PIN boleh diingati
      authCredentials = { email: emel, password: pin };   // sementara (pengesahan dlm sesi ini)"""

# ---------- J. Akaun LALAI: tandakan sebagai sesi KONGSIAN (jangan ingat PIN) ----------
FINISH_OLD = """      try {
        if (sess.mode === 'delima') {
          localStorage.setItem('erph_daftar_selesai', '1');"""
FINISH_NEW = """      try {
""" + MARK + """ // akaun LALAI (kongsi) - jangan ingat PIN, jadi butang masuk pantas tidak muncul
        window.__sesiKongsian = !(sess.mode === 'delima') &&
          String(sess.email || '').toLowerCase() === String(DEFAULT_AUTH.email || '').toLowerCase();
        if (sess.mode === 'delima') {
          localStorage.setItem('erph_daftar_selesai', '1');"""

# ---------- K. Boot: pulih kredensial, tangani ralat storan, lindungi laluan masuk ----------
BOOT_OLD = """      // Muat templat lalai TANPA mencipta rekod arkib (hanya janaan sebenar guru yang disimpan)
      arkibWithSuspend(function () { loadPblRbtTemplate(5); });"""
BOOT_NEW = """      // [F24] muat semula kredensial daripada storan (kalau guru tukar akaun dalam tab lain)
      try { authCredentials = JSON.parse(localStorage.getItem('erph_auth_cred')) || DEFAULT_AUTH; } catch (e) { }
      // [F24] kalau kredensial rosak (JSON cacat), jangan matikan seluruh app - bersihkan kunci itu sahaja
      try { if (JSON.parse(localStorage.getItem('erph_auth_cred') || 'null') === null) localStorage.removeItem('erph_auth_cred'); } catch (e) { localStorage.removeItem('erph_auth_cred'); authCredentials = DEFAULT_AUTH; }
      // [F24] perlindungan: rujukan LAMA handleLoginSubmit masih wujud selepas tampalan (butang & atribut),
      // jadi butang "Masuk" besar hanya dibenarkan berfungsi apabila rujukan disahkan. Kalau tidak,
      // butang itu hanya membuka bentuk log masuk (tidak boleh gagal senyap).
      (function () {
        try { window.__butangMasukSediaHadir = true; } catch (e) { }   // ganti kemudian bila kami sahkan
        try {
          const b = document.getElementById('btnMasukSetempat');
          if (b) {
            window.__sesiKongsian = false;
          }
        } catch (e) { }
      })();
      // Muat templat lalai TANPA mencipta rekod arkib (hanya janaan sebenar guru yang disimpan)
      arkibWithSuspend(function () { loadPblRbtTemplate(5); });"""

# ---------- L. Sahkan butang masuk (semakan akhir dalam app) ----------
BOOT_TAIL_OLD = """      gFileId = localStorage.getItem('erph_drive_fileid') || '';
      checkAuthStatus();
    });"""
BOOT_TAIL_NEW = """      gFileId = localStorage.getItem('erph_drive_fileid') || '';
      checkAuthStatus();
      // [F24] sahkan butang "Masuk" besar berfungsi (jangan gantung guru pada butang mati)
      try {
        const _bm = document.getElementById('loginBtnMasuk');
        if (_bm && _bm.getAttribute('onclick') !== 'masukSetempat()') { _bm.setAttribute('onclick', 'masukSetempat()'); }
      } catch (e) { }
      try { masukKredensialMasihSah(); } catch (e) { }
    });"""


TAMPALAN = (
    ('css butang masuk', CSS_OLD, CSS_NEW),
    ('html gerbang (butang masuk pantas)', GATE_OLD, GATE_NEW),
    ('butang masuk besar', GATE_SUBMIT_OLD, GATE_SUBMIT_NEW),
    ('lupa PIN', Lupa_OLD, Lupa_NEW),
    ('kaki gerbang', GATE_TAIL_OLD, GATE_TAIL_NEW),
    ('daftar automatik dimatikan', SEMAK_OLD, SEMAK_NEW),
    ('showGate + masuk pantas', ADMIN_OLD, ADMIN_NEW),
    ('gerbang tidak dilitupi modal', AUTH_LOCK_OLD, AUTH_LOCK_NEW),
    ('bentuk log masuk terbuka auto', AUTH_ELSE_OLD, AUTH_ELSE_NEW),
    ('bantuan PIN', HELP_OLD, HELP_NEW),
    ('medan PIN profil tidak dedah PIN', PROF_OLD, PROF_NEW),
    ('butang profil tidak bertindan', PROF_BTN_OLD, PROF_BTN_NEW),
    ('simpan profil tanpa PIN lama', SUB_OLD, SUB_NEW),
    ('tukar emel + simpan kredensial', SUB2_OLD, SUB2_NEW),
    ('daftar: sesi bukan kongsi', SUBMIT_DAFTAR_OLD, SUBMIT_DAFTAR_NEW),
    ('akaun lalai = sesi kongsi', FINISH_OLD, FINISH_NEW),
    ('boot: kredensial + perlindungan', BOOT_OLD, BOOT_NEW),
    ('boot: sahkan butang masuk', BOOT_TAIL_OLD, BOOT_TAIL_NEW),
)


def patch(src):
    if MARK in src:
        return src, False
    for nama, old, new in TAMPALAN:
        n = src.count(old)
        assert n == 1, 'jangkar "%s" tidak unik (%d)' % (nama, n)
        src = src.replace(old, new, 1)
    return src, True


def main():
    files = sys.argv[1:] or ['index.html']
    for f in files:
        s = open(f, encoding='utf-8').read()
        os.makedirs('/tmp/sepora_bak', exist_ok=True)
        shutil.copy2(f, '/tmp/sepora_bak/' + os.path.basename(f) + '.bak-masuk-senang-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
        out, ch = patch(s)
        open(f, 'w', encoding='utf-8').write(out)
        print('[OK] %s -> %s' % (f, 'ditampal' if ch else 'sudah ditampal'))
    for f in files:
        s = open(f, encoding='utf-8').read()
        for m in (MARK, 'function masukPantas()', 'function masukSetempat()', 'function showGate()',
                  'btnMasukPantas', 'masukKredensialMasihSah', 'bukaBantuanPin'):
            assert m in s, 'semakan gagal %s: %s' % (f, m)
    print('[SEMAK] F24 jalan masuk senang OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
