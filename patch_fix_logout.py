#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_fix_logout.py  (2026-09-12, Hermes)

F11 — SISTEM LOG KELUAR (dan Kunci Skrin yang benar-benar berkunci)

MASALAH:
  1. Tiada butang "Log Keluar" yang kelihatan — logoutSession() hanya ada di dalam
     panel Google Drive (tersembunyi).
  2. "Kunci Skrin" (lockAppScreen) TIDAK berkunci sebenarnya: ia cuma menyembunyikan
     gerbang, tetapi sesi (erph_session) kekal, dan checkAuthStatus() menetapkan
     isLoggedIn=true hanya kerana sesi wujud -> muat semula halaman (F5) terus masuk.
  3. Log keluar tidak membersihkan arkib dalam memori/dokumen semasa -> guru seterusnya
     pada telefon yang sama masih nampak RPH guru sebelumnya.

PEMBETULAN:
  - Bendera kunci 'erph_locked' disimpan; checkAuthStatus menghormatinya walaupun sesi ada.
  - finishLogin() membuka kunci.
  - logoutSession(): sahkan -> kosongkan sesi + bendera + arkib dalam memori + dokumen
    pratonton + kembali ke dashboard + gerbang log masuk dipaparkan (data kekal dalam
    peranti & Drive; masuk semula = arkib kembali).
  - Butang kelihatan: "Kunci Skrin" + "Log Keluar" dalam bar sisi DAN dalam modal Profil.

Guna: python3 patch_fix_logout.py index.html sepora_rbt_toolkit.html
"""
import datetime, os, shutil, sys

HELPERS = '''    /* [F11] Kunci skrin sebenar: bendera 'erph_locked' mesti dibuka dengan emel+PIN.
       (Sebelum ini muat semula halaman terus memintas kunci kerana sesi masih ada.) */
    const SEPORA_LOCK_KEY = 'erph_locked';
    function setLocked(on) {
      try { on ? localStorage.setItem(SEPORA_LOCK_KEY, '1') : localStorage.removeItem(SEPORA_LOCK_KEY); } catch (e) { }
    }
    function isLocked() {
      try { return localStorage.getItem(SEPORA_LOCK_KEY) === '1'; } catch (e) { return false; }
    }

'''

LOCK_OLD_START = '    function lockAppScreen() {'
LOCK_OLD_END = "      showToast('Sistem dikunci untuk privasi.');\n    }"
LOCK_NEW = '''    function lockAppScreen() {
      setLocked(true);                       // [F11] mesti buka kunci dgn emel + PIN
      closeModalDirectly();
      // Sembunyikan arkib & dokumen semasa (privasi) - data KEKAL dalam peranti
      try {
        savedRphList = arkibNormalize(JSON.parse(localStorage.getItem(arkibKey()) || '[]'));
      } catch (e) { }
      const el = document.getElementById('rphPreviewContainer');
      if (el) el.innerHTML = '';
      try { syncRphMirror(); } catch (e) { }

      const lockScreen = document.getElementById('privacyLockScreen');
      if (lockScreen) {
        lockScreen.classList.remove('hidden');
        const emField = document.getElementById('loginInputEmail');
        if (emField && !emField.value) emField.value = authCredentials.email || DEFAULT_AUTH.email;
        const pwField = document.getElementById('loginInputPassword');
        if (pwField) { pwField.value = ''; pwField.focus(); }
      }
      setGateStatus('Sistem dikunci. Masukkan emel & PIN anda untuk membuka semula.');
      showToast('Sistem dikunci untuk privasi.');
    }'''

AUTH_OLD = "      if (sess && sess.email) isLoggedIn = true;"
AUTH_NEW = "      if (sess && sess.email && !isLocked()) isLoggedIn = true;   // [F11] kunci skrin dihormati"

FINISH_OLD = """    function finishLogin(sess) {
      sess.loginAt = new Date().toISOString();
      setSession(sess);"""
FINISH_NEW = """    function finishLogin(sess) {
      sess.loginAt = new Date().toISOString();
      setSession(sess);
      setLocked(false);   // [F11] kunci dibuka selepas pengesahan"""

LOGOUT_OLD_START = '    function logoutSession() {'
LOGOUT_OLD_END = "      showToast('Log keluar. Data RPH kekal dalam peranti.');\n    }"
LOGOUT_NEW = '''    function logoutSession() {
      if (!confirm('Log keluar dari akaun ini?\\n\\nArkib tetap tersimpan dalam peranti & Google Drive, dan hanya boleh dilihat selepas log masuk semula.')) return;
      setSession(null);
      setLocked(false);
      gTok = null; gTokExp = 0;
      try {
        sessionStorage.removeItem('erph_logged_in');
        localStorage.removeItem('erph_remember_login');
      } catch (e) { }
      // [F11] kosongkan arkib & dokumen dalam memori supaya guru seterusnya tidak nampak
      // RPH guru sebelumnya pada telefon/peranti yang sama (data kekal dalam storan).
      try {
        savedRphList = []; currentArkibId = null;
        renderSavedRphTable(); updateArkibBadge(); updateArkibSelectedInfo(); updateDashboardMetrics();
      } catch (e) { }
      const pv = document.getElementById('rphPreviewContainer');
      if (pv) pv.innerHTML = '';
      try { syncRphMirror(); } catch (e) { }
      closeModalDirectly();
      try { switchTab('dashboard'); } catch (e) { }
      const lock = document.getElementById('privacyLockScreen');
      if (lock) lock.classList.remove('hidden');
      const emField = document.getElementById('loginInputEmail');
      if (emField) emField.value = authCredentials.email || DEFAULT_AUTH.email;
      const pwField = document.getElementById('loginInputPassword');
      if (pwField) { pwField.value = ''; pwField.focus(); }
      setGateStatus('Anda telah log keluar. Masukkan emel & PIN untuk log masuk semula (data kekal dalam peranti).');
      refreshDriveChip();
      showToast('Log keluar. Data RPH kekal dalam peranti.');
    }'''

SIDEBAR_OLD = '''          <i class="fa-solid fa-arrow-up-right-from-square" style="color:#059669;"></i> Portal RBT SEPORA
        </a>
      </nav>'''
SIDEBAR_NEW = '''          <i class="fa-solid fa-arrow-up-right-from-square" style="color:#059669;"></i> Portal RBT SEPORA
        </a>
        <a class="nav-item" style="color:var(--danger);" onclick="lockAppScreen()">
          <i class="fa-solid fa-lock"></i> Kunci Skrin
        </a>
        <a class="nav-item" style="color:var(--danger); font-weight:700;" onclick="logoutSession()">
          <i class="fa-solid fa-right-from-bracket"></i> Log Keluar
        </a>
      </nav>'''

PROFILE_OLD = '''            <button type="button" class="btn btn-outline" style="color:var(--danger); border-color:var(--danger);" onclick="lockAppScreen()">
              <i class="fa-solid fa-lock"></i> Kunci Skrin Sekarang
            </button>'''
PROFILE_NEW = '''            <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
              <button type="button" class="btn btn-outline" style="color:var(--danger); border-color:var(--danger);" onclick="lockAppScreen()">
                <i class="fa-solid fa-lock"></i> Kunci Skrin
              </button>
              <button type="button" class="btn btn-danger" onclick="logoutSession()">
                <i class="fa-solid fa-right-from-bracket"></i> Log Keluar
              </button>
            </div>'''


def between(src, start, end, new, label):
    i = src.find(start)
    assert i >= 0, 'jangkar mula tiada: ' + label
    j = src.find(end, i)
    assert j >= 0, 'jangkar tamat tiada: ' + label
    return src[:i] + new + src[j + len(end):]


def patch(src):
    if 'SEPORA_LOCK_KEY' in src:
        return src, False
    assert src.count(LOCK_OLD_START) == 1 and 'function lockAppScreen()' in src
    src = src.replace(LOCK_OLD_START, HELPERS + LOCK_OLD_START, 1)          # helper dahulu
    src = between(src, LOCK_OLD_START, LOCK_OLD_END, LOCK_NEW, 'lockAppScreen')
    assert src.count(AUTH_OLD) == 1, 'jangkar checkAuthStatus tidak unik'
    src = src.replace(AUTH_OLD, AUTH_NEW, 1)
    assert src.count(FINISH_OLD) == 1, 'jangkar finishLogin tidak unik'
    src = src.replace(FINISH_OLD, FINISH_NEW, 1)
    src = between(src, LOGOUT_OLD_START, LOGOUT_OLD_END, LOGOUT_NEW, 'logoutSession')
    assert src.count(SIDEBAR_OLD) == 1, 'jangkar bar sisi tidak unik'
    src = src.replace(SIDEBAR_OLD, SIDEBAR_NEW, 1)
    assert src.count(PROFILE_OLD) == 1, 'jangkar modal profil tidak unik'
    src = src.replace(PROFILE_OLD, PROFILE_NEW, 1)
    return src, True


def main():
    files = sys.argv[1:] or ['index.html']
    for f in files:
        s = open(f, encoding='utf-8').read()
        os.makedirs('/tmp/sepora_bak', exist_ok=True)
        shutil.copy2(f, '/tmp/sepora_bak/' + os.path.basename(f) + '.bak-f11-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
        out, changed = patch(s)
        open(f, 'w', encoding='utf-8').write(out)
        print('[OK] %s -> %s' % (f, 'ditampal' if changed else 'sudah ditampal'))
    for f in files:
        s = open(f, encoding='utf-8').read()
        for m in ('SEPORA_LOCK_KEY', 'isLocked()', 'Log Keluar', 'Kunci Skrin', 'updateArkibSelectedInfo(); updateDashboardMetrics();'):
            assert m in s, 'semakan gagal %s: %s' % (f, m)
    print('[SEMAK] bendera kunci + butang Log Keluar/Kunci Skrin OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
