#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_fix_arkib_slot.py  (2026-09-12, Hermes)

F5 — "Setiap RPH yang dijana tersimpan sebagai arkib & boleh diedit/guna semula"

MASALAH (ditemui melalui ujian CDP ujian_lengkap_cdp.js):
  Panel "Bina RPH" tiada medan input untuk Hari, Masa, Kelas, Subjek dan Minggu.
  Kesan:
    - loadSlotToRph(hari, masa, kelas, subjek) menulis ke elemen yang tidak wujud
      -> slot daripada modul Jadual TIDAK masuk ke RPH.
    - autoGenerateSmartRph() jatuh ke nilai lalai templat (tmpl.kelas, tarikh lalai,
      currentWeek) untuk SETIAP janaan.
    - arkibSameTarget() membandingkan templateKey+minggu+kelas+hari -> semuanya sama
      bagi setiap janaan, jadi SEMUA janaan bertindih menjadi SATU rekod arkib
      (rekod lama ditimpa). Guru nampak "arkib" tetapi sebenarnya hanya 1 rekod.

PEMBETULAN:
  1. Tambah 5 medan borang sebenar: formRphHari, formRphMasa, formRphKelas,
     formRphSubjek, formRphMinggu (lalai kosong = kekal guna nilai lalai templat,
     jadi tingkah laku lama tidak rosak).
  2. Ikat 'change' pada medan tersebut -> pratonton disegarkan tanpa mencipta rekod
     arkib (arkibWithSuspend), rekod dicipta bila "Jana RPH" / "Simpan ke Arkib".

Guna: python3 patch_fix_arkib_slot.py index.html sepora_rbt_toolkit.html
"""
import shutil, sys, datetime, os, re

FORM_ANCHOR = '            <input type="hidden" id="formRphTahap" value="4_kereta_idamanku">\n'

FORM_NEW = '''            <input type="hidden" id="formRphTahap" value="4_kereta_idamanku">

            <!-- [F5] Medan slot PdPc: diisi oleh modul Jadual (loadSlotToRph) dan dipakai oleh
                 Arkib RPH untuk memisahkan setiap RPH (Hari + Masa + Kelas + Minggu) supaya
                 janaan berbeza TIDAK bertindih dalam satu rekod. Biar kosong = nilai lalai templat. -->
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap:1rem; margin-bottom:0.5rem;">
              <div class="form-group">
                <label class="form-label">Hari / Tarikh</label>
                <input type="text" id="formRphHari" class="form-control" placeholder="cth: Isnin (8 September 2026)">
              </div>
              <div class="form-group">
                <label class="form-label">Masa</label>
                <input type="text" id="formRphMasa" class="form-control" placeholder="cth: 08:00 - 09:30 (90 Minit)">
              </div>
              <div class="form-group">
                <label class="form-label">Kelas</label>
                <input type="text" id="formRphKelas" class="form-control" placeholder="cth: 4 Cekal">
              </div>
              <div class="form-group">
                <label class="form-label">Mata Pelajaran</label>
                <input type="text" id="formRphSubjek" class="form-control" placeholder="cth: RBT Tahun 5">
              </div>
              <div class="form-group">
                <label class="form-label">Minggu</label>
                <input type="number" min="1" max="42" id="formRphMinggu" class="form-control" placeholder="cth: 12">
              </div>
            </div>
'''

BIND_OLD = "      try { pblBindDateEdit(); } catch (e) { /* preview mungkin belum sedia */ }\n"

BIND_NEW = '''      try { pblBindDateEdit(); } catch (e) { /* preview mungkin belum sedia */ }
      // [F5] Segarkan pratonton bila guru ubah medan slot (Hari/Masa/Kelas/Subjek/Minggu).
      //       Tidak mencipta rekod arkib - rekod dicipta hanya bila "Jana RPH" / "Simpan ke Arkib".
      try {
        ['formRphHari', 'formRphMasa', 'formRphKelas', 'formRphSubjek', 'formRphMinggu'].forEach(function (id) {
          const el = document.getElementById(id);
          if (el && !el.dataset.f5bound) {
            el.dataset.f5bound = '1';
            el.addEventListener('change', function () { try { arkibWithSuspend(autoGenerateSmartRph); } catch (e) { } });
          }
        });
      } catch (e) { }
'''


def patch(src):
    # 1) medan borang slot
    if 'id="formRphKelas"' in src:
        pass  # sudah ditampal
    else:
        assert src.count(FORM_ANCHOR) == 1, 'jangkar medan borang tidak unik'
        src = src.replace(FORM_ANCHOR, FORM_NEW, 1)

    # 2) ikatan change pada medan slot
    if 'f5bound' in src:
        pass  # sudah ditampal
    else:
        assert src.count(BIND_OLD) == 1, 'jangkar ikatan tidak unik'
        src = src.replace(BIND_OLD, BIND_NEW, 1)
    return src


def main():
    files = sys.argv[1:] or ['index.html']
    for f in files:
        s = open(f, encoding='utf-8').read()
        ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        bak_dir = '/tmp/sepora_bak'
        os.makedirs(bak_dir, exist_ok=True)
        shutil.copy2(f, os.path.join(bak_dir, os.path.basename(f) + '.bak-' + ts))
        out = patch(s)
        open(f, 'w', encoding='utf-8').write(out)
        print('[OK] %s: %s' % (f, 'dikemas kini' if out != s else 'tiada perubahan (sudah ditampal)'))

    # semakan pantas
    for f in files:
        s = open(f, encoding='utf-8').read()
        for i in ['formRphHari', 'formRphMasa', 'formRphKelas', 'formRphSubjek', 'formRphMinggu']:
            assert s.count('id="%s"' % i) == 1, 'gagal: %s tiada dalam %s' % (i, f)
        assert 'f5bound' in s, 'gagal: ikatan F5 tiada dalam %s' % f
    print('[SEMAK] 5 medan slot + ikatan change OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
