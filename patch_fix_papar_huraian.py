#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_fix_papar_huraian.py  (2026-09-12, Hermes)

Membetulkan 4 kecacatan SEPORA RBT TOOLKIT:
  F1  "X boleh papar RPH"  — bahagian sidebar Simpan/Cetak tiada pratonton RPH:
      tambah panel "Pratonton RPH Semasa" (cermin dokumen) + butang Cetak RPH /
      Edit / Simpan, dan butang Cetak pada setiap baris arkib.
  F2  "Huraian PBL tak berubah" — (a) tempoh/tarikh pelaksanaan PBL tidak ikut
      templat; (b) PAK21 + Pentaksiran identik utk 20 templat. Kedua-dua kini
      dijana ikut projek; suntingan guru pada dokumen tetap dihormati.
  F3  Arkib dipenuhi 'Draf Dijana' setiap kali guru menekan butang/dropdown PBL
      (20 rekod sampah) — melayari templat tidak lagi auto-simpan; auto-simpan
      hanya pada "Jana RPH" / simpan manual.
  F4  Tambah butang "Padam Semua Draf" untuk bersihkan draf sedia ada.

Guna: python3 patch_fix_papar_huraian.py <fail.html> [...]
"""
import re
import sys
import shutil
import datetime

PAK21_PENTAKSIRAN = {
    "4_kereta_idamanku": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Sumbang Saran Reka Bentuk, Amali Binaan Bengkel, Pameran & Ujian Larian Kereta",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Ujian larian kereta (kestabilan & ketahanan), Semakan lakaran rakan sebaya, Jurnal/Refleksi projek",
    ),
    "4_pen3d": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Demonstrasi Pen 3D, Latihan Stensil & Lakaran, Galeri Keychain Murid",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Penilaian produk keychain (kekemasan & ketahanan), Semakan rakan sebaya, Jurnal/Refleksi projek",
    ),
    "4_jahitan": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Demonstrasi Jahitan Asas, Amali Menjahit, Persembahan Artikel Jahitan",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Penilaian kekemasan mata jahitan, Semakan rakan sebaya, Jurnal/Refleksi projek",
    ),
    "4_pembungkusan": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Analisis Bentangan 3D, Amali Bina Prototaip, Pameran Produk Berbungkus",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Penilaian prototaip pembungkusan (kekuatan & estetika), Semakan rakan sebaya, Jurnal/Refleksi projek",
    ),
    "4_makanan": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Demonstrasi Penyediaan Bento, Amali Dapur Selamat, Pameran Bento Sihat",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Penilaian bento (kebersihan, keseimbangan nutrisi & kreativiti), Semakan rakan sebaya, Jurnal/Refleksi projek",
    ),
    "4_pengaturcaraan": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Unplugged Coding, Pair Programming, Demo Projek Scratch",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Semakan atur cara projek Scratch, Ujian fungsi sprite, Jurnal/Refleksi projek",
    ),
    "4_kerongsang": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Demonstrasi Pen 3D, Latihan Bentuk & Hiasan, Galeri Kerongsang",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Penilaian kerongsang (kekemasan & kreativiti), Semakan rakan sebaya, Jurnal/Refleksi projek",
    ),
    "5_rumah_tangga": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Demonstrasi Jahitan Mesin, Amali Kerja Tangan, Pameran Artikel Rumah Tangga",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Penilaian artikel jahitan (kekemasan & fungsi), Semakan rakan sebaya, Jurnal/Refleksi projek",
    ),
    "5_kipas_solar": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Inkuiri Tenaga Solar, Amali Siri Litar, Ujian Prestasi Kipas",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Ujian prestasi kipas solar (putaran & kestabilan), Semakan sambungan litar, Jurnal/Refleksi projek",
    ),
    "5_atmega": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Demontrasi Litar Mikropengawal, Amali Kod Arduino, Demo Projek LED",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Ujian muat naik kod & fungsi litar, Semakan skematik, Jurnal/Refleksi projek",
    ),
    "5_tanaman": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Inkuiri Pertanian Bandar, Amali Takungan & Pemindahan Anak Benih, Galeri Hijau Kelas",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Pemerhatian pertumbuhan tanaman mingguan, Penilaian sistem takungan, Jurnal/Refleksi projek",
    ),
    "5_pagar_keselamatan": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Inkuiri Sensor Ultrasonik, Amali Litar & Kod, Ujian Palang Automatik",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Ujian fungsi palang automatik (jarak sensor), Semakan atur cara, Jurnal/Refleksi projek",
    ),
    "5_alas_keledar": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Demonstrasi Ukuran & Pola, Amali Menjahit Alas, Ujian Keselesaan",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Ujian keselesaan & ketepatan ukuran alas keledar, Semakan rakan sebaya, Jurnal/Refleksi projek",
    ),
    "6_kereta_kawalan": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Demonstrasi Elektromekanikal, Amali Pemasangan Motor & Bateri, Ujian Kawalan Jauh",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Ujian kawalan jauh (gerakan, laju & stereng), Semakan sambungan litar, Jurnal/Refleksi projek",
    ),
    "6_auto_plant": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Inkuiri Sensor Kelembapan, Amali Litar & Kod Pam, Ujian Sistem Automatik",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Ujian sistem automatik (sensor vs tindak balas pam), Semakan kod, Jurnal/Refleksi projek",
    ),
    "6_penghasilan": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Pemikiran Reka Bentuk (Design Thinking), Amali Prototaip, Pitching Produk",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Penilaian prototaip produk gabungan bahan, Pembentangan reka bentuk, Jurnal/Refleksi projek",
    ),
    "6_pintu_pagar": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Inkuiri Sistem Elektromekanikal, Amali Litar Motor Pagar, Ujian Keselamatan",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Ujian fungsi pintu pagar (sensor & had gerakan), Semakan aspek keselamatan, Jurnal/Refleksi projek",
    ),
    "6_robot_halangan": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Inkuiri Sistem Robotik, Amali Kod & Sensor Ultrasonik, Cabaran Robot Elak Halangan",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Ujian robot mengelak halangan, Semakan kod robot, Jurnal/Refleksi projek",
    ),
    "6_robot_penjaga_air": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Inkuiri Sistem Robotik, Amali Pam & Sensor Kelembapan, Demo Robot Penjaga Air",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Ujian robot memberi air mengikut kelembapan tanah, Semakan kod, Jurnal/Refleksi projek",
    ),
    "6_bot_motor": (
        "Pembelajaran Koperatif (kumpulan 4-5 orang), Inkuiri Daya Apungan, Amali Bina Bot & Motor, Ujian Bot di Air",
        "Pemerhatian amali (senarai semak), Soal jawab lisan, Ujian bot bergerak di atas air (kestabilan & arah), Semakan binaan, Jurnal/Refleksi projek",
    ),
}

MIRROR_CARD = '''          <!-- [F1] Pratonton RPH dlm bahagian Simpan/Cetak supaya RPH boleh dilihat & dicetak terus dari sini -->
          <div class="card rph-paper-card" style="margin-top:1rem;">
            <div class="card-header no-print" style="display:flex; flex-wrap:wrap; gap:0.5rem; align-items:center; justify-content:space-between;">
              <h3 style="font-size:1.05rem; margin:0;"><i class="fa-solid fa-eye" style="color:#0369a1; margin-right:6px;"></i> Pratonton RPH Semasa</h3>
              <div style="display:flex; gap:0.4rem; flex-wrap:wrap;">
                <button class="btn btn-sm btn-secondary" onclick="printRphDocument()"><i class="fa-solid fa-print"></i> Cetak / Simpan PDF</button>
                <button class="btn btn-sm btn-outline" onclick="switchTab('bina-rph')"><i class="fa-solid fa-pen-to-square"></i> Edit RPH</button>
                <button class="btn btn-sm btn-outline" onclick="saveCurrentGeneratedRph()"><i class="fa-solid fa-floppy-disk"></i> Simpan ke Arkib</button>
              </div>
            </div>
            <div id="rphMirrorWrap" style="overflow-x:auto;">
              <p id="rphMirrorEmpty" style="font-size:0.85rem; color:var(--text-muted); margin:0.5rem 0;">
                Belum ada RPH dijana. Buka <strong>Bina RPH Auto</strong>, pilih projek PBL dan tekan <strong>Jana RPH</strong>.
              </p>
            </div>
          </div>

'''

HELPERS = '''    /* ===== [F1/F3] Pratonton cermin + cetak rekod + bersih draf (2026-09-12) ===== */
    function syncRphMirror() {
      const wrap = document.getElementById('rphMirrorWrap');
      const src = document.getElementById('rphPreviewContainer');
      if (!wrap || !src) return;
      const empty = document.getElementById('rphMirrorEmpty');
      const adaKandungan = (src.innerText || '').replace(/\\s+/g, ' ').trim().length > 40;
      if (!adaKandungan) { if (empty) empty.style.display = ''; return; }
      if (empty) empty.style.display = 'none';
      Array.from(wrap.children).forEach(function (c) { if (c.id !== 'rphMirrorEmpty') wrap.removeChild(c); });
      const clone = src.cloneNode(true);
      clone.removeAttribute('id');
      clone.querySelectorAll('[id]').forEach(function (n) { n.removeAttribute('id'); });
      clone.querySelectorAll('[contenteditable]').forEach(function (n) { n.setAttribute('contenteditable', 'false'); });
      clone.style.boxShadow = 'none';
      wrap.appendChild(clone);
    }

    function printArkibRph(id) {
      const r = savedRphList.find(function (x) { return x.id === id; });
      if (!r) return;
      viewSavedRph(id);
      setTimeout(function () { try { printRphDocument(); } catch (e) { } }, 350);
    }

    function deleteAllDrafts() {
      const draf = savedRphList.filter(function (r) { return !r.saved; });
      if (!draf.length) { showToast('Tiada draf untuk dipadam.'); return; }
      if (!confirm('Padam ' + draf.length + ' rekod Draf Dijana? Rekod yang telah Disimpan kekal.')) return;
      savedRphList = savedRphList.filter(function (r) { return !!r.saved; });
      currentArkibId = null;
      arkibPersist(); renderSavedRphTable(); updateArkibBadge();
      try { updateArkibSelectedInfo(); } catch (e) { }
      try { updateDashboardMetrics(); } catch (e) { }
      showToast(draf.length + ' draf dipadam. Rekod Disimpan tidak disentuh.');
    }

'''


def patch(src: str) -> str:
    orig = src
    changes = []

    # ---------- F1a: panel pratonton dalam tab Simpan/Cetak ----------
    anchor_card = '          <div class="card" style="border-left:4px solid #059669;">\n            <div class="card-header">\n              <h3 style="font-size:1.05rem;"><i class="fa-solid fa-box-archive" style="color:#059669; margin-right:6px;"></i> Simpan, Edit &amp; Guna Semula RPH</h3>'
    assert src.count(anchor_card) == 1, 'anchor kad arkib tak unik: %d' % src.count(anchor_card)
    src = src.replace(anchor_card, MIRROR_CARD + anchor_card, 1)
    changes.append('F1a panel pratonton cermin')

    # ---------- F1b: fungsi pembantu ----------
    anchor_fn = '    function openSeporaRphBankModal() {'
    assert src.count(anchor_fn) == 1, 'anchor openSeporaRphBankModal tak unik'
    src = src.replace(anchor_fn, HELPERS + anchor_fn, 1)
    changes.append('F1b syncRphMirror/printArkibRph/deleteAllDrafts')

    # ---------- F1c: panggil syncRphMirror bila buka tab & lepas janaan ----------
    old_switch = """        const targetPanel = document.getElementById(`view-${tabId}`);
        if (targetPanel) {
          targetPanel.classList.add('active');
        }"""
    new_switch = """        const targetPanel = document.getElementById(`view-${tabId}`);
        if (targetPanel) {
          targetPanel.classList.add('active');
        }
        if (tabId === 'simpan-cetak') { try { syncRphMirror(); } catch (e) { } }"""
    assert src.count(old_switch) == 1, 'anchor switchTab tak unik'
    src = src.replace(old_switch, new_switch, 1)

    old_tail = """      updateSidebarJanaan();
      updateArkibBadge();"""
    new_tail = """      updateSidebarJanaan();
      try { syncRphMirror(); } catch (e) { }
      updateArkibBadge();"""
    assert src.count(old_tail) == 1, 'anchor tail autoGenerate tak unik'
    src = src.replace(old_tail, new_tail, 1)
    changes.append('F1c hook syncRphMirror')

    # ---------- F1d: butang Cetak pada setiap baris arkib ----------
    old_btn = '<button class="btn btn-sm btn-outline" style="color:var(--danger);" onclick="deleteSavedRph(${r.id})" title="Padam rekod"><i class="fa-solid fa-trash"></i></button>'
    new_btn = '<button class="btn btn-sm btn-outline" style="color:#059669; border-color:#6ee7b7;" onclick="printArkibRph(${r.id})" title="Cetak rekod ini"><i class="fa-solid fa-print"></i></button>\n            ' + old_btn
    assert src.count(old_btn) == 1, 'anchor butang padam rekod tak unik'
    src = src.replace(old_btn, new_btn, 1)
    changes.append('F1d butang Cetak per baris')

    # ---------- F4: butang padam semua draf ----------
    old_imp = """<input type="file" id="arkibImportInput" accept="application/json,.json" style="display:none" onchange="importArkibJson(event)">"""
    new_imp = old_imp + """
              <button class="btn btn-outline" style="border-color:#fca5a5; color:#b91c1c;" onclick="deleteAllDrafts()"><i class="fa-solid fa-broom"></i> Padam Semua Draf</button>"""
    assert src.count(old_imp) == 1, 'anchor import arkib tak unik'
    src = src.replace(old_imp, new_imp, 1)
    changes.append('F4 butang padam semua draf')

    # ---------- F2a: PBL tempoh/tarikh ikut templat ----------
    old_pbl = """      const tplTempohMinggu = tmpl.tempoh || "4 Minggu";
      const _wkNow = (typeof currentWeek !== 'undefined' && currentWeek) ? parseInt(currentWeek) : 12;
      const pblTempoh = document.getElementById('formPblMingguPelaksanaan')?.value || `Minggu ${_wkNow} hingga Minggu ${_wkNow + (tplTempohMinggu.indexOf('3') === 0 ? 2 : 3)} (${tplTempohMinggu})`;
      const pblMula = document.getElementById('formPblTarikhMula')?.value || "2026-09-08";
      const pblHantar = document.getElementById('formPblTarikhHantar')?.value || "2026-09-29";"""
    new_pbl = """      const tplTempohMinggu = tmpl.tempoh || "4 Minggu";
      const _wkNow = (typeof currentWeek !== 'undefined' && currentWeek) ? parseInt(currentWeek) : 12;
      // [F2a] tempoh pelaksanaan PBL IKUT templat projek (bukan tetap 4 minggu)
      const _nWk = (function () { const m = String(tplTempohMinggu).match(/(\\d+)/); return m ? Math.max(1, parseInt(m[1], 10)) : 4; })();
      const _pblEdited = window.__pblEdited || (window.__pblEdited = { tempoh: false, mula: false, hantar: false });
      const _pblFormVal = function (id) { const el = document.getElementById(id); return el && el.value ? String(el.value).trim() : ''; };
      const _pvT = document.getElementById('previewPblMingguTempoh');
      const _pvM = document.getElementById('previewPblTarikhMula');
      const _pvH = document.getElementById('previewPblTarikhHantar');
      const _pblDMY = function (d) { const x = new Date(d); return String(x.getDate()).padStart(2, '0') + '/' + String(x.getMonth() + 1).padStart(2, '0') + '/' + x.getFullYear(); };
      const _pblToDate = function (t) {
        const s = String(t || '').trim();
        let m = s.match(/^(\\d{1,2})\\/(\\d{1,2})\\/(\\d{4})$/);
        if (m) return new Date(Number(m[3]), Number(m[2]) - 1, Number(m[1]));
        m = s.match(/^(\\d{4})-(\\d{2})-(\\d{2})$/);
        if (m) return new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
        return null;
      };
      const pblTempoh = _pblFormVal('formPblMingguPelaksanaan') || (_pblEdited.tempoh && _pvT && _pvT.innerText.trim() ? _pvT.innerText.trim() : `Minggu ${_wkNow} hingga Minggu ${_wkNow + _nWk - 1} (${tplTempohMinggu})`);
      const pblMula = _pblFormVal('formPblTarikhMula') || (_pblEdited.mula && _pvM && _pvM.innerText.trim() ? _pvM.innerText.trim() : "2026-09-08");
      const _pblHantarAuto = (function () {
        if (_pblEdited.hantar && _pvH && _pvH.innerText.trim()) return _pvH.innerText.trim();
        const d = _pblToDate(pblMula);
        if (!d) return "2026-09-29";
        return _pblDMY(new Date(d.getTime() + (_nWk * 7 - 1) * 86400000));
      })();
      const pblHantar = _pblFormVal('formPblTarikhHantar') || _pblHantarAuto;"""
    assert src.count(old_pbl) == 1, 'anchor blok tempoh PBL tak unik'
    src = src.replace(old_pbl, new_pbl, 1)
    changes.append('F2a tempoh/tarikh PBL ikut templat')

    # ---------- F2b: suntingan guru dihormati (tanda __pblEdited) ----------
    old_bind = """      try { pblBindDateEdit(); } catch (e) { /* preview mungkin belum sedia */ }"""
    new_bind = """      try { pblBindDateEdit(); } catch (e) { /* preview mungkin belum sedia */ }
      // [F2b] tanda suntingan guru pada medan PBL supaya janaan templat tak menimpa suntingan
      try {
        window.__pblEdited = window.__pblEdited || { tempoh: false, mula: false, hantar: false };
        [['previewPblMingguTempoh', 'tempoh'], ['previewPblTarikhMula', 'mula'], ['previewPblTarikhHantar', 'hantar']].forEach(function (pair) {
          const el = document.getElementById(pair[0]);
          if (el) el.addEventListener('input', function () { window.__pblEdited[pair[1]] = true; });
        });
      } catch (e) { }"""
    assert src.count(old_bind) == 1, 'anchor pblBindDateEdit tak unik'
    src = src.replace(old_bind, new_bind, 1)
    changes.append('F2b tanda suntingan guru')

    # ---------- F3: melayari templat PBL tak lagi auto-simpan ke arkib ----------
    old_gen = """      if (typeof arkibWithSuspend === 'function') { arkibWithSuspend(autoGenerateSmartRph); } else { autoGenerateSmartRph(); }"""
    legacy_gen = """      autoGenerateSmartRph();
      const labelTajuk"""
    new_gen = """      // [F3] muat templat sahaja (bukan "Jana RPH") -> jangan cemar arkib dgn Draf Dijana
      if (typeof arkibWithSuspend === 'function') { arkibWithSuspend(autoGenerateSmartRph); } else { autoGenerateSmartRph(); }
      const labelTajuk"""
    if src.count(old_gen) == 1:
        pass  # sudah ditampal
    else:
        assert src.count(legacy_gen) == 1, 'anchor autoGenerate dlm loadPblRbtTemplate tak unik'
        src = src.replace(legacy_gen, new_gen, 1)
    changes.append('F3 arkib tidak dicemar semasa melayari templat')

    # ---------- F2c: PAK21 & Pentaksiran ikut projek (20 templat) ----------
    lines = src.split('\n')
    start = next(i for i, l in enumerate(lines) if 'const PBL_TEMPLATES' in l)
    end = next(i for i in range(start + 1, len(lines)) if re.match(r'^    \};', lines[i]))
    block = '\n'.join(lines[start:end + 1])
    n_ok = 0
    for key, (pak, pent) in PAK21_PENTAKSIRAN.items():
        m = re.search(r'(\n    "%s": \{)(.*?)(\n    \},|\n    \})' % re.escape(key), block, re.S)
        if not m:
            print('  [!] templat tak jumpai:', key)
            continue
        body = m.group(2)
        b2 = re.sub(r'("pak21":\s*)"(?:[^"\\]|\\.)*"', lambda mm: mm.group(1) + '"' + pak.replace('"', '\\"') + '"', body, count=1)
        b2 = re.sub(r'("pentaksiran":\s*)"(?:[^"\\]|\\.)*"', lambda mm: mm.group(1) + '"' + pent.replace('"', '\\"') + '"', b2, count=1)
        if b2 == body:
            print('  [!] pak21/pentaksiran tak jumpai dlm', key)
            continue
        block = block.replace(m.group(0), m.group(1) + b2 + m.group(3), 1)
        n_ok += 1
    assert n_ok == len(PAK21_PENTAKSIRAN), 'hanya %d/%d templat dikemas kini' % (n_ok, len(PAK21_PENTAKSIRAN))
    src = src[:len('\n'.join(lines[:start])) + 1] + block + src[len('\n'.join(lines[:end + 1])):]
    changes.append('F2c PAK21+Pentaksiran ikut projek (%d templat)' % n_ok)

    assert src != orig
    return src


def main():
    files = sys.argv[1:] or ['index.html', 'sepora_rbt_toolkit.html']
    for f in files:
        s = open(f, encoding='utf-8').read()
        ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        bak_dir = '/tmp/sepora_bak'
        import os
        os.makedirs(bak_dir, exist_ok=True)
        bak = os.path.join(bak_dir, os.path.basename(f) + '.bak-' + ts)
        shutil.copy2(f, bak)
        out = patch(s)
        open(f, 'w', encoding='utf-8').write(out)
        print('[OK] %s ditampal (%d -> %d bait) | backup: %s' % (f, len(s), len(out), bak))


if __name__ == '__main__':
    main()
