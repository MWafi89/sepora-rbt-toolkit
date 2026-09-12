#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_fix_drive_diagnostik.py  (2026-09-12, Hermes)

F14 — "macam mana ia masuk gdrive? saya test belum masuk"

Punca biasa sandaran TIDAK masuk Drive (ketiga-tiganya perlu betul):
  1. Client ID OAuth belum diset  -> butang Google tak boleh buka pengesahan.
  2. Guru log masuk cara MOD SETEMPAT (emel + PIN) -> Drive memang TIDAK aktif
     (driveSave/driveRestore menolak mode 'setempat').
  3. Auto-sandaran mati, atau token Google sudah tamat -> dulu driveMaybeAuto
     DIAM-DIAM tidak menyandar (hanya tukar chip kecil).

PEMBETULAN:
  F14a driveMaybeAuto: cuba perbaharui token Google secara senyap dahulu, kemudian
       sandar; kalau gagal, beritahu dgn jelas (bukan diam).
  F14b Panel Drive: baris diagnostik - Client ID OAuth, Cara log masuk, Token Google,
       Folder Drive (nama + id) - supaya guru/app tahu pautan mana yang belum siap.
  F14c Amaran jelas dalam panel bila log masuk mod setempat (Drive tidak aktif).
  F14d Chip Drive: sebut "tidak aktif - log masuk guna ID DELIMa" utk mod setempat.

Guna: python3 patch_fix_drive_diagnostik.py index.html sepora_rbt_toolkit.html
"""
import datetime, os, shutil, sys

CHIP_OLD = "      if (s.mode !== 'delima') { setDriveChip('<i class=\"fa-solid fa-cloud-slash\"></i> Mod setempat: ' + esc(s.email || ''), '#b45309'); return; }\n"
CHIP_NEW = "      if (s.mode !== 'delima') { setDriveChip('<i class=\"fa-solid fa-cloud-slash\"></i> Drive: tidak aktif (mod setempat) - log masuk guna ID DELIMa', '#b45309'); return; }\n"

AUTO_OLD = """        gAutoTimer = setTimeout(function () {
          if (gTok && Date.now() < gTokExp - 60000) driveSave(true);
          else setDriveChip('<i class="fa-solid fa-cloud-arrow-up"></i> Drive: tekan untuk sandaran (sesi tamat)', '#f59e0b');
        }, 6000);"""
AUTO_NEW = """        gAutoTimer = setTimeout(async function () {
          // [F14a] jangan diam-diam: cuba perbaharui token Google, kemudian sandar
          try {
            if (!(gTok && Date.now() < gTokExp - 60000)) {
              if (!gdriveConfigured()) {
                setDriveChip('<i class="fa-solid fa-cloud-slash"></i> Drive: Client ID belum diset', '#b45309');
                return;
              }
              await gToken(true);          // perbaharui token secara senyap
            }
            await driveSave(true);
          } catch (e) {
            setDriveChip('<i class="fa-solid fa-cloud-arrow-up"></i> Drive: tekan untuk sandaran (sesi Google tamat)', '#f59e0b');
          }
        }, 6000);"""

PANEL_OLD = """        ['Fail Drive', gFileId || localStorage.getItem('erph_drive_fileid') || '<em>Belum dicipta</em>'],
        ['Rekod dalam arkib', String(savedRphList.length)],
        ['Auto-sandaran', auto ? 'Aktif' : 'Mati'],"""
PANEL_NEW = """        ['Client ID OAuth', gdriveConfigured()
          ? '<span style="color:#059669;">Sedia (' + esc(gdriveClientId().slice(0, 12)) + '...)</span>'
          : '<span style="color:#b45309;">Belum diset - tekan "Setelan Client ID"</span>'],
        ['Cara log masuk', sess && sess.mode === 'delima'
          ? '<span style="color:#059669;">ID DELIMa (Google) - Drive aktif</span>'
          : '<span style="color:#b45309;">Mod setempat (emel + PIN) - Drive TIDAK aktif</span>'],
        ['Token Google', (gTok && Date.now() < gTokExp - 60000) ? 'Sah' : '<em>Tiada / tamat (diperbaharui automatik bila perlu)</em>'],
        ['Folder Drive', esc(SEPORA_GDRIVE.folderName) + (driveFolderState() ? ' <span style="color:#059669;">(id: ' + esc(String(driveFolderState()).slice(0, 10)) + ')</span>' : ' <em>(akan dicipta pada sandaran pertama)</em>')],
        ['Fail Drive', gFileId || localStorage.getItem('erph_drive_fileid') || '<em>Belum dicipta</em>'],
        ['Rekod dalam arkib', String(savedRphList.length)],
        ['Auto-sandaran', auto ? 'Aktif' : 'Mati'],"""

WARN_OLD = """        <table style="width:100%; font-size:0.82rem; border-collapse:collapse; margin-bottom:1rem;">${rows}</table>"""
WARN_NEW = """        ${(sess && sess.mode === 'setempat') ? '<div style="background:#fef3c7; border:1px solid #fcd34d; border-radius:8px; padding:0.7rem 0.9rem; margin-bottom:0.85rem; font-size:0.8rem; color:#92400e;"><strong>Drive belum aktif.</strong> Log masuk sekarang guna <strong>mod setempat</strong> (emel + PIN), jadi sandaran Drive tidak berjalan. Tekan <strong>Log masuk DELIMa</strong> (butang Google) untuk sandaran automatik ke folder ' + esc(SEPORA_GDRIVE.folderName) + '.</div>' : ''}
        <table style="width:100%; font-size:0.82rem; border-collapse:collapse; margin-bottom:1rem;">${rows}</table>"""


def patch(src):
    if 'F14a' in src:
        return src, False
    for old, new, nama in ((CHIP_OLD, CHIP_NEW, 'chip'), (AUTO_OLD, AUTO_NEW, 'driveMaybeAuto'),
                           (PANEL_OLD, PANEL_NEW, 'panel diagnostik'), (WARN_OLD, WARN_NEW, 'amaran mod setempat')):
        assert src.count(old) == 1, 'jangkar %s tidak unik' % nama
        src = src.replace(old, new, 1)
    return src, True


def main():
    files = sys.argv[1:] or ['index.html']
    for f in files:
        s = open(f, encoding='utf-8').read()
        os.makedirs('/tmp/sepora_bak', exist_ok=True)
        shutil.copy2(f, '/tmp/sepora_bak/' + os.path.basename(f) + '.bak-f14-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
        out, ch = patch(s)
        open(f, 'w', encoding='utf-8').write(out)
        print('[OK] %s -> %s' % (f, 'ditampal' if ch else 'sudah ditampal'))
    for f in files:
        s = open(f, encoding='utf-8').read()
        for m in ('[F14a]', 'Client ID OAuth', 'Cara log masuk', 'Folder Drive', 'Drive belum aktif'):
            assert m in s, 'semakan gagal %s: %s' % (f, m)
    print('[SEMAK] F14 diagnostik Drive + auto-refresh token OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
