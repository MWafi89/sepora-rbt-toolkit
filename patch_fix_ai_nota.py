#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_fix_ai_nota.py  (2026-09-13, Hermes)

F20 — Ciri AI (imbas gambar jadual / baca RPT) TIDAK aktif tetapi diiklankan.

Penemuan (audit perjalanan guru baharu):
  - analyzeTimetableImageWithAI() dan analyzeRptTextWithAI() guna `const apiKey = ""`.
    Butang "Imbas / Muat Naik Jadual" (kamera) + deskripsi "Muat naik gambar jadual waktu
    sebenar anda" mengiklankan ciri yang MUSTAHIL berfungsi tanpa kunci AI.
  - Bila guru cuba: fetch gagal -> cuba semula 3x (delay) -> console.error + toaster
    "Tidak dapat memproses imej jadual pada masa ini. Sila cuba lagi." (mengelirukan:
    ia bukan masalah sementara, ia ciri yang belum diaktifkan).

Pembetulan:
  1. Satu sumber kunci: SEPORA_AI_KEY (senang diisi pemilik app kemudian).
  2. aiTersedia() + pagar masuk pada kedua-dua fungsi AI: jika tiada kunci, papar mesej
     jujur + alternatif (isi manual / muat naik CSV / .txt) dan JANGAN buat panggilan rangkaian.
  3. Nota status pada tab Jadual ("AI imbas gambar: tidak aktif") supaya janji pada UI jujur.

Guna: python3 patch_fix_ai_nota.py index.html sepora_rbt_toolkit.html
"""
import datetime, os, shutil, sys

KEY_OLD_A = """    async function analyzeTimetableImageWithAI(base64ImageData, mimeType) {
      const apiKey = "";"""
KEY_NEW_A = """    const SEPORA_AI_KEY = "";   // [F20] isi di sini (atau biar kosong) untuk hidupkan ciri AI
    function aiTersedia() { return !!String(SEPORA_AI_KEY || '').trim(); }
    function aiTidakAktifMesej(ciri) {
      const alt = ciri === 'rpt'
        ? 'Muat naik fail teks (.txt) atau isi RPT secara manual (butang Tambah RPT).'
        : 'Isi slot secara manual (Tambah Slot) atau muat naik fail CSV jadual.';
      showToast('Ciri AI (' + (ciri === 'rpt' ? 'baca dokumen RPT' : 'imbas gambar jadual') + ') belum diaktifkan dalam app ini. ' + alt);
    }
    async function analyzeTimetableImageWithAI(base64ImageData, mimeType) {
      if (!aiTersedia()) { aiTidakAktifMesej('jadual'); return; }
      const apiKey = SEPORA_AI_KEY;"""

KEY_OLD_B = """    async function analyzeRptTextWithAI(rawText) {
      const apiKey = "";"""
KEY_NEW_B = """    async function analyzeRptTextWithAI(rawText) {
      if (!aiTersedia()) { aiTidakAktifMesej('rpt'); return; }
      const apiKey = SEPORA_AI_KEY;"""

NOTA_HTML_OLD = """            <div>
              <h1 class="page-title">Jadual Waktu Mengajar</h1>
              <p class="page-desc">Muat naik gambar jadual waktu sebenar anda atau klik mana-mana slot kelas untuk menjana RPH segera.</p>
            </div>"""
NOTA_HTML_NEW = """            <div>
              <h1 class="page-title">Jadual Waktu Mengajar</h1>
              <p class="page-desc">Muat naik jadual anda (CSV) atau klik mana-mana slot kelas untuk menjana RPH segera.</p>
              <p id="notaAiStatus" style="display:none; font-size:0.76rem; color:#b45309; background:rgba(245,158,11,0.10); border:1px solid rgba(245,158,11,0.35); border-radius:8px; padding:6px 10px; margin-top:6px;">
                <i class="fa-solid fa-circle-info"></i> Imbas gambar jadual (AI) belum diaktifkan - guna fail CSV atau isi slot secara manual.
              </p>
            </div>"""

NOTA_JS_ANCHOR = """    function renderTimetable() {"""
NOTA_JS_NEW = """    function renderAiStatusNota() {
      try {
        const n = document.getElementById('notaAiStatus');
        if (n) n.style.display = aiTersedia() ? 'none' : 'block';
      } catch (e) { }
    }

    function renderTimetable() {
      renderAiStatusNota();"""


def patch(src):
    if '[F20]' in src:
        return src, False
    for old, new, nama in (
        (KEY_OLD_A, KEY_NEW_A, 'kunci AI + pagar jadual'),
        (KEY_OLD_B, KEY_NEW_B, 'pagar RPT'),
        (NOTA_HTML_OLD, NOTA_HTML_NEW, 'nota UI jadual'),
        (NOTA_JS_ANCHOR, NOTA_JS_NEW, 'render nota AI'),
    ):
        assert src.count(old) == 1, 'jangkar %s tidak unik (%d)' % (nama, src.count(old))
        src = src.replace(old, new, 1)
    return src, True


def main():
    files = sys.argv[1:] or ['index.html']
    for f in files:
        s = open(f, encoding='utf-8').read()
        os.makedirs('/tmp/sepora_bak', exist_ok=True)
        shutil.copy2(f, '/tmp/sepora_bak/' + os.path.basename(f) + '.bak-f20-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
        out, ch = patch(s)
        open(f, 'w', encoding='utf-8').write(out)
        print('[OK] %s -> %s' % (f, 'ditampal' if ch else 'sudah ditampal'))
    for f in files:
        s = open(f, encoding='utf-8').read()
        for m in ('[F20]', 'function aiTersedia', 'notaAiStatus', 'renderAiStatusNota'):
            assert m in s, 'semakan gagal %s: %s' % (f, m)
    print('[SEMAK] F20 nota AI OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
