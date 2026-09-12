#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_fix_drive_folder.py  (2026-09-12, Hermes)

F12 — Sandaran Google Drive dalam FOLDER sendiri (auto-cipta)

Arahan: "kalau guru log in guna delima, boleh ka link terus simpanan dalam delima,
autocreate folder dalam delima gdrive atas nama seporatoolkit"

Sebelum ini arkib disandarkan sebagai fail SEPORA_RPH_ARKIB.json di akar My Drive guru.
Kini app:
  1. Cari folder 'SEPORATOOLKIT' (mimeType application/vnd.google-apps.folder) dalam
     Drive guru -> cipta kalau belum ada (auto-create).
  2. Simpan/kemas kini fail arkib DI DALAM folder itu (parents=[folderId]).
  3. Fail arkib lama yang berada di akar Drive dipindahkan ke folder (addParents/removeParents).
  4. Pemulihan: cari dalam folder dahulu, jika tiada barulah cari global (kes lama).
Skop kekal 'drive.file' — app hanya nampak fail/folder yang DIA sendiri cipta (privasi guru).

Guna: python3 patch_fix_drive_folder.py index.html sepora_rbt_toolkit.html
"""
import datetime, os, shutil, sys

CONF_OLD = """      fileName: 'SEPORA_RPH_ARKIB.json',
"""
CONF_NEW = """      fileName: 'SEPORA_RPH_ARKIB.json',
      folderName: 'SEPORATOOLKIT',            // [F12] folder sandaran auto-cipta dalam Drive guru
"""

GID_OLD = "    let gFileId = '';\n"
GID_NEW = "    let gFileId = '';\n    let gFolderId = '';   // [F12] id folder sandaran google drive\n"

HELPERS_ANCHOR = "    async function driveSave(silent) {\n"
HELPERS = '''    /* ---------------- [F12] Folder sandaran dalam Google Drive guru ---------------- */
    function driveFolderState() { try { return localStorage.getItem('erph_drive_folderid') || ''; } catch (e) { return ''; } }
    async function driveFindArchiveFile(tok, folderId, dalamFolder) {
      let q = "name='" + SEPORA_GDRIVE.fileName + "' and trashed=false";
      if (dalamFolder && folderId) q = "name='" + SEPORA_GDRIVE.fileName + "' and '" + folderId + "' in parents and trashed=false";
      const l = await driveApi('/drive/v3/files?q=' + encodeURIComponent(q) + '&spaces=drive&fields=files(id,name,modifiedTime,parents)', {}, tok);
      return (l && l.files && l.files.length) ? l.files[0] : null;
    }
    async function driveMoveToFolder(fileId, folderId, tok) {
      await driveApi('/drive/v3/files/' + fileId + '?addParents=' + folderId + '&removeParents=root&fields=id,parents',
        { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: '{}' }, tok);
    }
    async function ensureDriveFolder(tok) {
      if (!gFolderId) gFolderId = driveFolderState();
      if (gFolderId) return gFolderId;
      const q = "name='" + SEPORA_GDRIVE.folderName + "' and mimeType='application/vnd.google-apps.folder' and trashed=false";
      const l = await driveApi('/drive/v3/files?q=' + encodeURIComponent(q) + '&spaces=drive&fields=files(id,name)', {}, tok);
      if (l && l.files && l.files.length) {
        gFolderId = l.files[0].id;
      } else {
        const created = await driveApi('/drive/v3/files?fields=id,name', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: SEPORA_GDRIVE.folderName,
            mimeType: 'application/vnd.google-apps.folder',
            description: 'Arkib RPH SEPORA RBT TOOLKIT'
          })
        }, tok);
        gFolderId = created.id;
      }
      try { localStorage.setItem('erph_drive_folderid', gFolderId); } catch (e) { }
      return gFolderId;
    }

'''

SAVE_OLD = """        const tok = await gToken(true);
        const body = JSON.stringify(drivePayload());
        if (!gFileId) {
          const q = encodeURIComponent("name='" + SEPORA_GDRIVE.fileName + "' and trashed=false");
          const list = await driveApi('/drive/v3/files?q=' + q + '&spaces=drive&fields=files(id,name,modifiedTime)', {}, tok);
          if (list.files && list.files.length) gFileId = list.files[0].id;
        }
        if (gFileId) {
          await driveApi('/upload/drive/v3/files/' + gFileId + '?uploadType=media', {
            method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: body
          }, tok);
        } else {
          const meta = { name: SEPORA_GDRIVE.fileName, mimeType: 'application/json', description: 'Arkib RPH SEPORA RBT TOOLKIT (' + sess.email + ')' };"""
SAVE_NEW = """        const tok = await gToken(true);
        const body = JSON.stringify(drivePayload());
        // [F12] pastikan folder sandaran wujud, kemudian simpan fail DI DALAM folder itu
        const folderId = await ensureDriveFolder(tok);
        if (!gFileId) {
          const dalamFolder = await driveFindArchiveFile(tok, folderId, true);
          if (dalamFolder) {
            gFileId = dalamFolder.id;
          } else {
            const lama = await driveFindArchiveFile(tok, '', false);   // fail versi lama di akar Drive
            if (lama) { await driveMoveToFolder(lama.id, folderId, tok); gFileId = lama.id; }
          }
        }
        if (gFileId) {
          await driveApi('/upload/drive/v3/files/' + gFileId + '?uploadType=media', {
            method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: body
          }, tok);
        } else {
          const meta = { name: SEPORA_GDRIVE.fileName, mimeType: 'application/json', parents: [folderId], description: 'Arkib RPH SEPORA RBT TOOLKIT (' + sess.email + ')' };"""
SAVE_TOAST_OLD = "        if (!silent) showToast('Arkib (' + savedRphList.length + ' rekod) disandarkan ke Google Drive ' + sess.email + '.');"
SAVE_TOAST_NEW = "        if (!silent) showToast('Arkib (' + savedRphList.length + ' rekod) disandarkan ke folder \"' + SEPORA_GDRIVE.folderName + '\" dalam Google Drive ' + sess.email + '.');"

REST_OLD = """        const tok = await gToken(true);
        const q = encodeURIComponent("name='" + SEPORA_GDRIVE.fileName + "' and trashed=false");
        const list = await driveApi('/drive/v3/files?q=' + q + '&spaces=drive&fields=files(id,name,modifiedTime)', {}, tok);
        if (!list.files || !list.files.length) {"""
REST_NEW = """        const tok = await gToken(true);
        // [F12] cari dalam folder sandaran dahulu; jika tiada, cari global (sandaran versi lama)
        const fid = driveFolderState();
        let f = fid ? await driveFindArchiveFile(tok, fid, true) : null;
        if (!f) f = await driveFindArchiveFile(tok, '', false);
        if (!f) {"""
REST_F_OLD = """        const f = list.files[0];
        gFileId = f.id;"""
REST_F_NEW = """        gFileId = f.id;"""

PANEL_OLD = """          Fail sandaran: <strong>${SEPORA_GDRIVE.fileName}</strong> dalam Google Drive akaun DELIMa anda."""
PANEL_NEW = """          Fail sandaran: <strong>${SEPORA_GDRIVE.fileName}</strong> dalam folder <strong>${SEPORA_GDRIVE.folderName}</strong> (Google Drive akaun DELIMa anda)."""


def patch(src):
    if 'folderName' in src and 'ensureDriveFolder' in src:
        return src, False
    assert src.count(CONF_OLD) == 1, 'konfigurasi GDRIVE tidak unik'
    src = src.replace(CONF_OLD, CONF_NEW, 1)
    assert src.count(GID_OLD) == 1, 'gFileId tidak unik'
    src = src.replace(GID_OLD, GID_NEW, 1)
    assert src.count(HELPERS_ANCHOR) == 1, 'jangkar driveSave tidak unik'
    src = src.replace(HELPERS_ANCHOR, HELPERS + HELPERS_ANCHOR, 1)
    assert src.count(SAVE_OLD) == 1, 'blok driveSave tidak unik'
    src = src.replace(SAVE_OLD, SAVE_NEW, 1)
    assert src.count(SAVE_TOAST_OLD) == 1, 'toast driveSave tidak unik'
    src = src.replace(SAVE_TOAST_OLD, SAVE_TOAST_NEW, 1)
    assert src.count(REST_OLD) == 1, 'blok driveRestore tidak unik'
    src = src.replace(REST_OLD, REST_NEW, 1)
    assert src.count(REST_F_OLD) == 1, 'baris fail pulih tidak unik'
    src = src.replace(REST_F_OLD, REST_F_NEW, 1)
    assert src.count(PANEL_OLD) == 1, 'teks panel Drive tidak unik'
    src = src.replace(PANEL_OLD, PANEL_NEW, 1)
    return src, True


def main():
    files = sys.argv[1:] or ['index.html']
    for f in files:
        s = open(f, encoding='utf-8').read()
        os.makedirs('/tmp/sepora_bak', exist_ok=True)
        shutil.copy2(f, '/tmp/sepora_bak/' + os.path.basename(f) + '.bak-f12-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
        out, ch = patch(s)
        open(f, 'w', encoding='utf-8').write(out)
        print('[OK] %s -> %s' % (f, 'ditampal' if ch else 'sudah ditampal'))
    for f in files:
        s = open(f, encoding='utf-8').read()
        for m in ("folderName: 'SEPORATOOLKIT'", 'ensureDriveFolder', 'driveMoveToFolder', "parents: [folderId]", 'driveFolderState'):
            assert m in s, 'semakan gagal %s: %s' % (f, m)
        assert 'list.files[0]' not in s.split('function driveRestore')[1].split('function toggleDriveAutoSync')[0], 'sisa kod lama dalam driveRestore'
    print('[SEMAK] folder auto-cipta + simpan dalam folder OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
