#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_fix_arkib_v3_perakaun.py  (2026-09-12, Hermes)

F6 — Keperluan guru (arahan Wafi):
  (i)  "setiap yang mereka jana boleh simpan dalam arkib"      -> sudah ada (auto-simpan)
  (ii) "RPH yang sudah dijana JANGAN delete"                   -> DIBETULKAN di sini
  (iii)"arkib nyata milik guru itu sendiri"                     -> DIBETULKAN di sini (per akaun)

MASALAH:
  1. arkibAutoSimpan() menimpa rekod sedia ada untuk slot+minggu+kelas+hari yang sama
     (arkibSameTarget). Jika guru sudah menyimpan/mengunci RPH itu lalu menekan "Jana RPH"
     sekali lagi, RPH yang tersimpan tadi DITIMPA -> hilang.
  2. Arkib disimpan dengan kunci localStorage tunggal 'erph_saved' -> jika satu telefon/
     pelayar dikongsi beberapa guru, arkib mereka bercampur.

PEMBETULAN:
  - arkibFindDraft(): auto-simpan hanya mengemas kini rekod DRAF (belum dikunci).
  - Jika slot yang sama sudah DIKUNCI (saved=true), janaan baharu mencipta REKOD VERSI
    BAHARU (versi=2,3,...) dan rekod lama KEKAL (tiada rekod dijana hilang).
  - Kunci stor arkib per akaun: 'erph_saved::<emel>'. Data lama 'erph_saved' dimigrasi
    sekali (disalin, bukan dipadam) bila guru log masuk kali pertama.
  - finishLogin() + permulaan aplikasi memuatkan arkib akaun yang sedang log masuk.
  - "Padam Semua Draf" kekal hanya membuang rekod DRAF (rekod Disimpan tidak disentuh).

Guna: python3 patch_fix_arkib_v3_perakaun.py index.html sepora_rbt_toolkit.html
"""
import shutil, sys, datetime, os

# ---------- 1. helper kunci stor per akaun ----------
ANCHOR_LOAD = "    let savedRphList = JSON.parse(localStorage.getItem('erph_saved')) || [];\n"
NEW_LOAD = """    let savedRphList = JSON.parse(localStorage.getItem('erph_saved')) || [];

    /* [F6] Arkib dipisahkan ikut akaun guru (satu telefon/pelayar boleh dikongsi beberapa guru).
       Kunci: 'erph_saved::<emel>'. Data lama 'erph_saved' dimigrasi (disalin) sekali sahaja. */
    function arkibKeyFor(email) {
      const u = String(email || '').trim().toLowerCase();
      return 'erph_saved' + (u ? '::' + u : '');
    }
    function arkibKey() {
      let s = null;
      try { s = (typeof getSession === 'function') ? getSession() : null; } catch (e) { }
      return arkibKeyFor(s && s.email);
    }
    function arkibLoadForSession() {
      const k = arkibKey();
      let raw = null;
      try { raw = localStorage.getItem(k); } catch (e) { }
      if (!raw) {
        // migrasi sekali: arkib lama (sebelum F6) dipindahkan ke akaun pertama yang log masuk
        try { raw = localStorage.getItem('erph_saved'); } catch (e) { }
      }
      let list = [];
      try { list = JSON.parse(raw || '[]') || []; } catch (e) { list = []; }
      savedRphList = arkibNormalize(list);
      try { localStorage.setItem(k, JSON.stringify(savedRphList)); } catch (e) { }
      return savedRphList.length;
    }
"""

# ---------- 2. arkibPersist guna kunci per akaun ----------
P_OLD_1 = "        localStorage.setItem('erph_saved', JSON.stringify(savedRphList));\n        driveMaybeAuto();\n"
P_NEW_1 = "        localStorage.setItem(arkibKey(), JSON.stringify(savedRphList));\n        driveMaybeAuto();\n"
P_OLD_2 = "          localStorage.setItem('erph_saved', JSON.stringify(savedRphList));\n          if (drop)"
P_NEW_2 = "          localStorage.setItem(arkibKey(), JSON.stringify(savedRphList));\n          if (drop)"
P_OLD_3 = "      localStorage.setItem('erph_saved', JSON.stringify(savedRphList));\n\n      // Update current RPH form if it matches"
P_NEW_3 = "      localStorage.setItem(arkibKey(), JSON.stringify(savedRphList));\n\n      // Update current RPH form if it matches"

# ---------- 3. arkibAutoSimpan: jangan timpa rekod yang dikunci ----------
A_OLD_START = "    function arkibAutoSimpan() {"
A_OLD_END = "      } catch (e) { /* jangan sesekali ganggu penjanaan RPH */ }\n    }"
A_NEW = """    /* [F6] Cari rekod DRAF sahaja (rekod yang sudah dikunci/disimpan tidak ditimpa). */
    function arkibFindDraft(snap) {
      return savedRphList.find(function (r) { return !r.saved && arkibSameTarget(r, snap); });
    }
    function arkibAutoSimpan() {
      if (window.__arkibSuspend) return;
      try {
        const snap = arkibSnapshot();
        if (!snap.tajuk) return;
        let rec = arkibFindDraft(snap);
        if (rec) {
          Object.assign(rec, snap, { dikemas: arkibNow() });
          if (!rec.saved) rec.status = 'Draf Dijana';
        } else {
          // Slot sama tetapi rekod lama sudah DIKUNCI -> cipta rekod versi baharu, rekod lama kekal
          const sama = savedRphList.filter(function (r) { return arkibSameTarget(r, snap); });
          const versiBaru = sama.length
            ? Math.max.apply(null, sama.map(function (x) { return Number(x.versi) || 1; })) + 1
            : 1;
          rec = Object.assign({ id: Date.now(), created: arkibNow(), auto: true, saved: false, status: 'Draf Dijana', nota: '', docHtml: '', versi: versiBaru }, snap);
          savedRphList.unshift(rec);
        }
        currentArkibId = rec.id;
        arkibPersist();
        renderSavedRphTable();
        updateArkibBadge();
        updateDashboardMetrics();
        updateArkibSelectedInfo();
      } catch (e) { /* jangan sesekali ganggu penjanaan RPH */ }
    }"""

# ---------- 4. saveCurrentGeneratedRph: pastikan medan versi ada ----------
S_OLD_START = "    function saveCurrentGeneratedRph(forceNew) {"
S_OLD_END = "      showToast('RPH \"' + rec.tajuk + '\" ' + (forceNew ? 'disimpan sebagai rekod baharu' : 'disimpan ke Arkib') + ' (' + (rec.pblMingguPelaksanaan || 'M' + rec.minggu) + ').');\n    }"
S_NEW = """    function saveCurrentGeneratedRph(forceNew) {
      const snap = arkibSnapshot();
      if (!snap.tajuk) { showToast('Tiada RPH untuk disimpan. Tekan \"Jana RPH\" dahulu.'); return; }
      const now = arkibNow();
      let rec = forceNew ? null : arkibFindRecord(snap);
      if (rec) {
        Object.assign(rec, snap, { dikemas: now });
        rec.saved = true;
        if (!rec.status || rec.status === 'Draf Dijana') rec.status = 'Disimpan';
      } else {
        const sama = savedRphList.filter(function (r) { return arkibSameTarget(r, snap); });
        const versiBaru = sama.length
          ? Math.max.apply(null, sama.map(function (x) { return Number(x.versi) || 1; })) + 1
          : 1;
        rec = Object.assign({ id: Date.now(), created: now, auto: false, saved: true, status: 'Disimpan', nota: '', docHtml: '', versi: versiBaru }, snap);
        savedRphList.unshift(rec);
      }
      if (!rec.versi) rec.versi = 1;
      rec.docHtml = arkibDocHtml();
      currentArkibId = rec.id;
      arkibPersist();
      renderSavedRphTable();
      updateArkibBadge();
      updateDashboardMetrics();
      updateArkibSelectedInfo();
      showToast('RPH \"' + rec.tajuk + '\" ' + (forceNew ? 'disimpan sebagai rekod baharu' : 'disimpan ke Arkib') + ' (versi ' + (rec.versi || 1) + ', ' + (rec.pblMingguPelaksanaan || 'M' + rec.minggu) + ').');
    }"""

# ---------- 5. muat arkib ikut akaun selepas log masuk ----------
L_OLD = "    function finishLogin(sess) {\n      sess.loginAt = new Date().toISOString();\n      setSession(sess);\n"
L_NEW = """    function finishLogin(sess) {
      sess.loginAt = new Date().toISOString();
      setSession(sess);
      // [F6] muatkan arkib milik akaun ini (arkib guru lain dalam telefon sama tidak bercampur)
      try { arkibLoadForSession(); renderSavedRphTable(); updateArkibBadge(); updateArkibSelectedInfo(); updateDashboardMetrics(); } catch (e) { }
"""

# ---------- 6. permulaan aplikasi: muat arkib akaun ----------
B_OLD = "        if (!sess) setSession({ email: (authCredentials.email || DEFAULT_AUTH.email), name: teacherProfile.name, mode: 'setempat', loginAt: new Date().toISOString() });\n"
B_NEW = B_OLD + "        // [F6] muatkan arkib milik akaun yang sedang log masuk\n        try { arkibLoadForSession(); renderSavedRphTable(); updateArkibBadge(); } catch (e) { }\n"


def replace_between(src, start, end, new, label):
    i = src.find(start)
    assert i >= 0, 'jangkar mula tidak dijumpai: ' + label
    j = src.find(end, i)
    assert j >= 0, 'jangkar tamat tidak dijumpai: ' + label
    return src[:i] + new + src[j + len(end):]


def patch(src):
    changes = []

    if 'arkibKeyFor' in src:
        return src, changes

    assert src.count(ANCHOR_LOAD) == 1, 'jangkar senarai arkib tidak unik'
    src = src.replace(ANCHOR_LOAD, NEW_LOAD, 1); changes.append('F6a kunci stor per akaun')

    assert src.count(P_OLD_1) == 1, 'arkibPersist#1 tidak unik'
    src = src.replace(P_OLD_1, P_NEW_1, 1); changes.append('F6b persist per akaun (1)')
    assert src.count(P_OLD_2) == 1, 'arkibPersist#2 tidak unik'
    src = src.replace(P_OLD_2, P_NEW_2, 1); changes.append('F6b persist per akaun (2)')
    assert src.count(P_OLD_3) == 1, 'penulis arkib urus kelas tidak unik'
    src = src.replace(P_OLD_3, P_NEW_3, 1); changes.append('F6b persist per akaun (3)')

    src = replace_between(src, A_OLD_START, A_OLD_END, A_NEW, 'arkibAutoSimpan'); changes.append('F6c jangan timpa rekod dikunci (versi baharu)')
    src = replace_between(src, S_OLD_START, S_OLD_END, S_NEW, 'saveCurrentGeneratedRph'); changes.append('F6d versi pada simpan manual')
    assert src.count(L_OLD) == 1, 'finishLogin tidak unik'
    src = src.replace(L_OLD, L_NEW, 1); changes.append('F6e muat arkib akaun selepas log masuk')
    assert src.count(B_OLD) == 1, 'permulaan aplikasi tidak unik'
    src = src.replace(B_OLD, B_NEW, 1); changes.append('F6f muat arkib akaun semasa boot')
    return src, changes


def main():
    files = sys.argv[1:] or ['index.html']
    for f in files:
        s = open(f, encoding='utf-8').read()
        ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        os.makedirs('/tmp/sepora_bak', exist_ok=True)
        shutil.copy2(f, '/tmp/sepora_bak/' + os.path.basename(f) + '.bak-' + ts)
        out, ch = patch(s)
        open(f, 'w', encoding='utf-8').write(out)
        print('[OK] %s -> %s' % (f, '; '.join(ch) if ch else 'sudah ditampal'))

    for f in files:
        s = open(f, encoding='utf-8').read()
        assert 'arkibFindDraft' in s and 'arkibKeyFor' in s and 'versiBaru' in s, 'semakan gagal: ' + f
        assert s.count("localStorage.setItem('erph_saved'") == 0, 'semakan gagal: penulis arkib lama masih ada (%s)' % f
    print('[SEMAK] kunci per akaun + versi + draft-only OK (tiada penulis arkib lama kekal, baca lama utk migrasi sahaja)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
