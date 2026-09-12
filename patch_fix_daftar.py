#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_fix_daftar.py  (2026-09-12, Hermes)

F15 — Skrin DAFTAR / LOG MASUK kali pertama (wajib pilih identiti sendiri)

Tujuan (arahan Wafi: "mereka daftar dulu ... supaya id delima itu betul-betul berfungsi"):
Guru TIDAK lagi boleh terus guna app dengan akaun lalai pemilik (emel + PIN 1234).
Pada penggunaan pertama (belum daftar), app memaparkan skrin WAJIB:

  (A) "Daftar dengan ID DELIMa"  -> pengesahan Google (akaun @moe-dl.edu.my mereka):
      identiti disahkan Google/MOE + sandaran Drive ke folder SEPORATOOLKIT mereka.
      (Ini cara BETUL "ID DELIMa berfungsi" - app tidak pernah menerima kata laluan DELIMa.)
  (B) "Guna tanpa Google"        -> mereka isi Nama + Emel sendiri + PIN sendiri,
      jadi arkib mereka berkunci pada akaun mereka (bukan berkongsi akaun lalai).

Skrin ini TIDAK boleh ditutup sebelum memilih (overlay/klick luar diabaikan) dan akan
muncul semula pada muat semula sehingga selesai.

Guna: python3 patch_fix_daftar.py index.html sepora_rbt_toolkit.html
"""
import datetime, os, shutil, sys

# 1) overlay: hormati mod wajib
OVERLAY_OLD = """      if (e && e.target && e.target.id !== 'appModalOverlay') return;"""
OVERLAY_NEW = """      if (window.__modalWajib) return;   // [F15] skrin wajib (daftar) tidak boleh ditutup dgn klik luar
      if (e && e.target && e.target.id !== 'appModalOverlay') return;"""

# 2) fungsi baru sebelum driveFolderState
FUNC_ANCHOR = "    /* ---------------- [F12] Folder sandaran dalam Google Drive guru ---------------- */\n"
FUNCS = '''    /* ---------------- [F15] Daftar / log masuk kali pertama ---------------- */
    function sudahDaftar() { try { return localStorage.getItem('erph_daftar_selesai') === '1'; } catch (e) { return false; } }
    function perluDaftar() {
      const s = getSession();
      if (s && (s.mode === 'delima' || s.picture)) return false;      // akaun Google/DELIMa = sudah daftar
      if (!s || !s.email) return true;                                 // belum log masuk
      return String(s.email).toLowerCase() === String(DEFAULT_AUTH.email || '').toLowerCase();
    }
    function openDaftarModal() {
      if (sudahDaftar()) return;
      window.__modalWajib = true;
      const html = `
        <div class="card-header">
          <h3><i class="fa-solid fa-user-plus" style="color:var(--primary); margin-right:6px;"></i> Daftar / Log Masuk SEPORA RBT</h3>
        </div>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.9rem;">
          Pilih identiti anda dahulu supaya arkib RPH anda tersimpan bawah akaun anda sendiri
          (bukan berkongsi akaun lalai app).
        </p>
        <div style="background:linear-gradient(135deg, rgba(26,115,232,0.08), rgba(5,150,105,0.06)); border:1px solid var(--surface-border); border-radius:10px; padding:0.9rem; margin-bottom:0.9rem;">
          <div style="font-weight:700; font-size:0.9rem; margin-bottom:0.35rem;"><i class="fa-brands fa-google" style="color:#4285f4;"></i> Pilihan A - Daftar dengan ID DELIMa (disyorkan)</div>
          <div style="font-size:0.78rem; color:var(--text-muted); margin-bottom:0.6rem;">
            Guna akaun Google sekolah anda (@moe-dl.edu.my). Google MOE yang sahkan identiti anda -
            app ini tidak menerima kata laluan DELIMa. Arkib disandarkan automatik ke folder
            <strong>${esc(SEPORA_GDRIVE.folderName)}</strong> dalam Drive anda sendiri.
          </div>
          <button type="button" class="btn btn-primary" onclick="daftarGoogle()"><i class="fa-brands fa-google"></i> Daftar / Log Masuk dengan ID DELIMa</button>
        </div>
        <div style="border:1px dashed var(--surface-border); border-radius:10px; padding:0.9rem;">
          <div style="font-weight:700; font-size:0.9rem; margin-bottom:0.5rem;">Pilihan B - Guna tanpa Google (offline)</div>
          <form onsubmit="submitDaftarLocal(event)">
            <div class="form-group">
              <label class="form-label">Nama Guru</label>
              <input type="text" id="daftarNama" class="form-control" placeholder="cth: Wafi bin Ahmad" required>
            </div>
            <div class="form-group">
              <label class="form-label">Emel anda</label>
              <input type="email" id="daftarEmel" class="form-control" placeholder="cth: nama@moe-dl.edu.my" required>
            </div>
            <div class="form-group">
              <label class="form-label">PIN / Kata Laluan anda (min 4 aksara)</label>
              <input type="text" id="daftarPin" class="form-control" placeholder="PIN sendiri - jangan guna 1234" required>
            </div>
            <button type="submit" class="btn btn-primary" style="width:100%;"><i class="fa-solid fa-user-check"></i> Daftar &amp; Mula Guna</button>
          </form>
          <p style="font-size:0.72rem; color:var(--text-muted); margin-top:0.6rem;">
            Mod ini tidak menyandar ke Drive. Anda boleh daftar guna ID DELIMa bila-bila masa melalui menu Drive.
          </p>
        </div>`;
      openModal(html);
    }
    function daftarGoogle() {
      window.__modalWajib = false;
      closeModalDirectly();
      delimaLoginWithGoogle();
    }
    function submitDaftarLocal(ev) {
      if (ev && ev.preventDefault) ev.preventDefault();
      const nama = String((document.getElementById('daftarNama') || {}).value || '').trim();
      const emel = String((document.getElementById('daftarEmel') || {}).value || '').trim().toLowerCase();
      const pin = String((document.getElementById('daftarPin') || {}).value || '').trim();
      if (nama.length < 3) { showToast('Sila isi nama penuh anda.'); return; }
      if (!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(emel)) { showToast('Emel tidak sah. Contoh: nama@moe-dl.edu.my'); return; }
      if (pin.length < 4) { showToast('PIN terlalu pendek - minimum 4 aksara.'); return; }
      if (emel === String(DEFAULT_AUTH.email || '').toLowerCase()) { showToast('Sila guna emel anda sendiri, bukan emel lalai app.'); return; }
      authCredentials = { email: emel, password: pin };
      try { localStorage.setItem('erph_auth_cred', JSON.stringify(authCredentials)); } catch (e) { }
      teacherProfile.name = nama;
      try { localStorage.setItem('erph_teacher', JSON.stringify(teacherProfile)); } catch (e) { }
      try { localStorage.setItem('erph_daftar_selesai', '1'); } catch (e) { }
      window.__modalWajib = false;
      finishLogin({ email: emel, name: nama, mode: 'setempat' });
      closeModalDirectly();
      showToast('Pendaftaran selesai. Arkib anda kini dikunci pada akaun ' + emel + '.');
    }
    function semakDaftar() {
      try {
        if (sudahDaftar()) return;
        if (!perluDaftar()) return;
        setTimeout(function () { try { openDaftarModal(); } catch (e) { } }, 500);
      } catch (e) { }
    }

'''
# 3) finishLogin: tandakan selesai utk DELIMa; paksa daftar utk akaun lalai
FIN_OLD = """      // [F13b] mod setempat dengan emel lalai -> minta guru tetapkan emel & PIN sendiri (sekali sahaja)
      try {
        const gunakanEmelLalai = sess.mode === 'setempat' &&
          String(sess.email || '').toLowerCase() === String(DEFAULT_AUTH.email || '').toLowerCase();
        if (gunakanEmelLalai && !localStorage.getItem('erph_profil_disemak')) {
          localStorage.setItem('erph_profil_disemak', '1');
          setTimeout(function () {
            try {
              openProfileModal();
              showToast('Sila tukar emel & PIN kepada milik anda supaya arkib anda berasingan.');
            } catch (e) { }
          }, 700);
        }
      } catch (e) { }"""
FIN_NEW = """      // [F15] akaun Google/DELIMa = daftar selesai; akaun lalai = wajib daftar
      try {
        if (sess.mode === 'delima') {
          localStorage.setItem('erph_daftar_selesai', '1');
        } else {
          localStorage.setItem('erph_profil_disemak', '1');   // nota: pernah guna akaun lalai
          if (String(sess.email || '').toLowerCase() === String(DEFAULT_AUTH.email || '').toLowerCase()) {
            semakDaftar();
          }
        }
      } catch (e) { }"""

# 4) boot: semak daftar bila sudah log masuk
BOOT_OLD = """      if (sess && sess.email && !isLocked()) isLoggedIn = true;   // [F11] kunci skrin dihormati"""
BOOT_NEW = """      if (sess && sess.email && !isLocked()) isLoggedIn = true;   // [F11] kunci skrin dihormati
      try { semakDaftar(); } catch (e) { }   // [F15] skrin daftar wajib jika masih akaun lalai"""


def patch(src):
    if 'F15' in src and 'openDaftarModal' in src:
        return src, False
    for old, new, nama in ((OVERLAY_OLD, OVERLAY_NEW, 'overlay wajib'),
                           (FUNC_ANCHOR, FUNCS + FUNC_ANCHOR, 'fungsi daftar'),
                           (FIN_OLD, FIN_NEW, 'finishLogin'),
                           (BOOT_OLD, BOOT_NEW, 'boot checkAuthStatus')):
        assert src.count(old) == 1, 'jangkar %s tidak unik' % nama
        src = src.replace(old, new, 1)
    return src, True


def main():
    files = sys.argv[1:] or ['index.html']
    for f in files:
        s = open(f, encoding='utf-8').read()
        os.makedirs('/tmp/sepora_bak', exist_ok=True)
        shutil.copy2(f, '/tmp/sepora_bak/' + os.path.basename(f) + '.bak-f15-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
        out, ch = patch(s)
        open(f, 'w', encoding='utf-8').write(out)
        print('[OK] %s -> %s' % (f, 'ditampal' if ch else 'sudah ditampal'))
    for f in files:
        s = open(f, encoding='utf-8').read()
        for m in ('openDaftarModal', 'submitDaftarLocal', 'semakDaftar', 'daftarGoogle', 'erph_daftar_selesai', '__modalWajib'):
            assert m in s, 'semakan gagal %s: %s' % (f, m)
    print('[SEMAK] F15 skrin daftar wajib OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
