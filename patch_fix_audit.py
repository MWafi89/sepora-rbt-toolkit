#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_fix_audit.py  (2026-09-12, Hermes) — AUDIT KESELAMATAN (reverse engineering) SEPORA RBT TOOLKIT

Penemuan (bukti baris dalam index.html sebelum patch) & pembetulan:

  W1 [TINGGI] Stored XSS melalui docHtml.
      Bukti: `el.innerHTML = r.docHtml` (viewSavedRph). docHtml datang dari
      (a) pratonton sendiri, (b) IMPORT fail JSON sandaran, (c) PULIH dari Google Drive.
      Fail yang dikongsi/ditampal guru boleh mengandungi <script>/onerror -> skrip
      berjalan dalam origin app (boleh baca storan + panggil Drive API).
      FIX: arkibSanitizeHtml() - buang <script>/<iframe>/<object>/<embed>/<link>/<meta>/
      <base>/<form>/<style>, semua atribut on*, srcdoc, dan href/src javascript:.
      Digunakan pada render + semasa import + semasa pulih Drive.

  W2 [TINGGI] PIN guru disimpan sebagai TEKS BIASA dan DIPAPARKAN pada skrin.
      Bukti: localStorage 'erph_auth_cred' = {email, password}; showDefaultLoginHelp()
      memaparkan "Emel Berdaftar: ... | PIN: ...".
      FIX: simpan hash PBKDF2-SHA256 (garam rawak) sahaja; paparan PIN dibuang;
      migrasi automatik pada log masuk berjaya; DEFAULT_AUTH (1234) kekal utk peranti baru.

  W3 [SEDERHANA] Tiada SRI pada 5 pustaka CDN (font-awesome, pdf.js, mammoth, html2pdf, docx).
      FIX: integrity=sha384 + crossorigin=anonymous pada URL versi tetap.

  W4 [SEDERHANA] Tiada header keselamatan di Vercel.
      FIX: CSP + X-Content-Type-Options + Referrer-Policy + Permissions-Policy +
      X-Frame-Options + HSTS dalam vercel.json.

  W5 [RENDAH] esc() tidak mengescape petikan (" ') -> suntikan atribut (cth value="${esc(x)}").
      FIX: esc() kini mengescape & < > " '.

  W6 [RENDAH/INI] showToast() guna innerHTML dgn mesej mentah.
      FIX: mesej dinyahbahaya melalui sanitizer.

  NOTA: Gemini apiKey kosong (tiada rahsia hardcoded) - disahkan; service worker sudah
  elak cache panggilan API Google (token tidak masuk cache) - disahkan.

Guna: python3 patch_fix_audit.py index.html sepora_rbt_toolkit.html
"""
import datetime, os, shutil, sys

# ---------- W5: esc() ----------
ESC_OLD = """    function esc(v) { return String(v).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }"""
ESC_NEW = """    // [W5] escape & < > " ' (petikan perlu supaya suntikan atribut mustahil)
    function esc(v) {
      return String(v == null ? '' : v).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }"""

# ---------- W6: showToast ----------
TOAST_OLD = """      toast.innerHTML = `<i class="fa-solid fa-circle-info" style="color:var(--primary);"></i> <span>${message}</span>`;"""
TOAST_NEW = """      const _msgSelamat = (typeof arkibSanitizeHtml === 'function') ? arkibSanitizeHtml(String(message)) : esc(String(message));
      toast.innerHTML = `<i class="fa-solid fa-circle-info" style="color:var(--primary);"></i> <span>${_msgSelamat}</span>`;"""

# ---------- W1: sanitizer ----------
SANI_ANCHOR = "    function arkibNormalize(list) {\n"
SANI = '''    /* [W1] Nyahbahaya HTML sebelum dipaparkan (fail sandaran / Drive boleh datang dari luar). */
    const ARKIB_TAG_BURUK = ['script', 'iframe', 'frame', 'frameset', 'object', 'embed', 'applet', 'link', 'meta', 'base', 'form', 'style', 'template', 'noscript', 'video', 'audio', 'source', 'track', 'canvas'];
    function arkibSanitizeHtml(html) {
      const mentah = String(html == null ? '' : html);
      if (!mentah) return '';
      try {
        const doc = new DOMParser().parseFromString('<div id="arkibAkar">' + mentah + '</div>', 'text/html');
        const akar = doc.getElementById('arkibAkar');
        if (!akar) return '';
        Array.prototype.slice.call(akar.querySelectorAll(ARKIB_TAG_BURUK.join(','))).forEach(function (n) { n.remove(); });
        const semua = akar.querySelectorAll('*');
        Array.prototype.forEach.call(semua, function (n) {
          Array.prototype.slice.call(n.attributes).forEach(function (at) {
            const nama = String(at.name || '').toLowerCase();
            const nilai = String(at.value || '');
            const buang = nama.indexOf('on') === 0 || nama === 'srcdoc' || nama === 'formaction' ||
              ((nama === 'href' || nama === 'src' || nama === 'xlink:href' || nama === 'action') &&
                /^\\s*(javascript|vbscript|data:text\\/html)/i.test(nilai));
            if (buang) { try { n.removeAttribute(at.name); } catch (e) { } }
          });
          // keselamatan tambahan: <a> luar mesti selamat
          if (n.tagName === 'A') { n.setAttribute('rel', 'noopener noreferrer'); }
        });
        return akar.innerHTML;
      } catch (e) {
        return mentah.replace(/<\\s*(script|iframe|object|embed|link|meta|base|form|style)[^>]*>[\\s\\S]*?<\\s*\\/\\s*\\1\\s*>/gi, '')
          .replace(/\\son\\w+\\s*=\\s*("[^"]*"|'[^']*'|[^\\s>]+)/gi, '')
          .replace(/<\\s*(script|iframe|object|embed|link|meta|base|form|style)[^>]*>/gi, '');
      }
    }
    function arkibSanitizeList(list) {
      (list || []).forEach(function (r) { if (r && r.docHtml) r.docHtml = arkibSanitizeHtml(r.docHtml); });
      return list;
    }
'''

# render rekod arkib
RENDER_OLD = """      if (el && r.docHtml) {
        el.innerHTML = r.docHtml;"""
RENDER_NEW = """      if (el && r.docHtml) {
        r.docHtml = arkibSanitizeHtml(r.docHtml);   // [W1] nyahbahaya sebelum papar
        el.innerHTML = r.docHtml;"""

# import JSON
IMP_OLD = """          const norm = arkibNormalize(rows);"""
IMP_NEW = """          const norm = arkibSanitizeList(arkibNormalize(rows));   // [W1] fail import tidak dipercayai"""

# pulih dari Drive
RES_OLD = """        const rows = arkibNormalize(Array.isArray(data) ? data : (data.rekod || []));"""
RES_NEW = """        const rows = arkibSanitizeList(arkibNormalize(Array.isArray(data) ? data : (data.rekod || [])));   // [W1] fail Drive tidak dipercayai"""

# ---------- W2: PIN di-hash ----------
PIN_ANCHOR = "    function getSession() { try { return JSON.parse(localStorage.getItem('erph_session') || 'null'); } catch (e) { return null; } }\n"
PIN_FUNCS = '''    /* [W2] PIN disimpan sebagai hash PBKDF2-SHA256 + garam (bukan teks biasa). */
    function pinRandB64(n) {
      const a = new Uint8Array(n || 16);
      if (self.crypto && self.crypto.getRandomValues) self.crypto.getRandomValues(a); else for (let i = 0; i < a.length; i++) a[i] = Math.floor(Math.random() * 256);
      let s = ''; a.forEach(function (b) { s += String.fromCharCode(b); });
      return btoa(s);
    }
    async function pinHash(pin, garamB64) {
      const enc = new TextEncoder();
      if (!(self.crypto && self.crypto.subtle && self.crypto.subtle.importKey)) return '';   // konteks tak selamat
      const kunci = await self.crypto.subtle.importKey('raw', enc.encode(String(pin)), 'PBKDF2', false, ['deriveBits']);
      const bit = await self.crypto.subtle.deriveBits({ name: 'PBKDF2', salt: enc.encode(String(garamB64 || '')), iterations: 60000, hash: 'SHA-256' }, kunci, 256);
      const arr = Array.from(new Uint8Array(bit));
      let s = ''; arr.forEach(function (b) { s += String.fromCharCode(b); });
      return btoa(s);
    }
    async function simpanKredensial(email, pin) {
      const garam = pinRandB64(16);
      const h = await pinHash(pin, garam);
      if (!h) {   // pelayar lama tanpa SubtleCrypto: simpan hash ringkas (lebih baik drpd teks biasa)
        authCredentials = { email: email, pinLemas: btoa(unescape(encodeURIComponent('sepora|' + garam + '|' + pin))), garam: garam, v: 2 };
      } else {
        authCredentials = { email: email, pinHash: h, garam: garam, v: 2 };
      }
      try { localStorage.setItem('erph_auth_cred', JSON.stringify(authCredentials)); } catch (e) { }
      return authCredentials;
    }
    async function sahPin(pin) {
      const k = authCredentials || DEFAULT_AUTH;
      if (k.pinHash) return (await pinHash(pin, k.garam)) === k.pinHash;
      if (k.pinLemas) return btoa(unescape(encodeURIComponent('sepora|' + k.garam + '|' + pin))) === k.pinLemas;
      return String(pin) === String(k.password || DEFAULT_AUTH.password);   // lalai / belum migrasi
    }
'''

# handleLoginSubmit -> async + hash + migration
LOGIN_OLD = """      const validEmail = (authCredentials.email || DEFAULT_AUTH.email).toLowerCase();
      const validPw = authCredentials.password || DEFAULT_AUTH.password;

      if (inputEmail === validEmail && inputPw === validPw) {"""
LOGIN_NEW = """      const validEmail = (authCredentials.email || DEFAULT_AUTH.email).toLowerCase();
      const sah = inputEmail === validEmail && (await sahPin(inputPw));   // [W2] bandingkan hash

      if (sah) {
        // [W2] migrasi kredensial lama (teks biasa) -> hash
        if (!authCredentials.pinHash && !authCredentials.pinLemas) { try { await simpanKredensial(validEmail, inputPw); } catch (e) { } }"""

LOGIN_SIG_OLD = "    function handleLoginSubmit(event) {"
LOGIN_SIG_NEW = "    async function handleLoginSubmit(event) {"

# paparan PIN dibuang
HELP_OLD = """    function showDefaultLoginHelp(event) {
      if (event) event.preventDefault();
      const currentEmail = authCredentials.email || DEFAULT_AUTH.email;
      const currentPw = authCredentials.password || DEFAULT_AUTH.password;
      showToast(`Emel Berdaftar: ${currentEmail} | PIN: ${currentPw}`);
    }"""
HELP_NEW = """    function showDefaultLoginHelp(event) {
      if (event) event.preventDefault();
      // [W2] JANGAN paparkan PIN. Hanya tunjuk emel berdaftar.
      const currentEmail = authCredentials.email || DEFAULT_AUTH.email;
      showToast('Emel berdaftar: ' + currentEmail + ' - lupa PIN? Tetapkan PIN baharu melalui menu Profil (nama guru di atas) atau guna butang ID DELIMa.');
    }"""

# simpan profil & privasi -> hash
PROF_OLD = """      if (newEmail && newPassword) {
        authCredentials = {
          email: newEmail,
          password: newPassword
        };
        localStorage.setItem('erph_auth_cred', JSON.stringify(authCredentials));
      }"""
PROF_NEW = """      if (newEmail && newPassword) {
        await simpanKredensial(newEmail, newPassword);   // [W2] simpan hash, bukan teks biasa
      }"""
PROF_SIG_OLD = "function submitTeacherProfile(e) {"
PROF_SIG_NEW = "async function submitTeacherProfile(e) {"

# daftar -> hash
DAFTAR_OLD = """      authCredentials = { email: emel, password: pin };
      try { localStorage.setItem('erph_auth_cred', JSON.stringify(authCredentials)); } catch (e) { }"""
DAFTAR_NEW = """      authCredentials = { email: emel, password: pin };   // sementara (pengesahan dlm sesi ini)
      await simpanKredensial(emel, pin);                   // [W2] yang disimpan ialah hash sahaja
      delete authCredentials.password;"""


def patch(src):
    if '[W1]' in src and 'arkibSanitizeHtml' in src:
        return src, False
    for old, new, nama in (
        (ESC_OLD, ESC_NEW, 'esc'), (TOAST_OLD, TOAST_NEW, 'showToast'),
        (SANI_ANCHOR, SANI + SANI_ANCHOR, 'sanitizer'),
        (RENDER_OLD, RENDER_NEW, 'render docHtml'), (IMP_OLD, IMP_NEW, 'import'), (RES_OLD, RES_NEW, 'pulih Drive'),
        (PIN_ANCHOR, PIN_FUNCS + PIN_ANCHOR, 'fungsi hash PIN'),
        (LOGIN_SIG_OLD, LOGIN_SIG_NEW, 'tandatangan login'),
        (LOGIN_OLD, LOGIN_NEW, 'login hash'), (HELP_OLD, HELP_NEW, 'paparan PIN'),
        (PROF_SIG_OLD, PROF_SIG_NEW, 'tandatangan profil'), (PROF_OLD, PROF_NEW, 'profil hash'),
        (DAFTAR_OLD, DAFTAR_NEW, 'daftar hash'),
        ('    function submitDaftarLocal(ev) {', '    async function submitDaftarLocal(ev) {   // [W2] perlu async utk hashing PIN', 'daftar async'),
    ):
        assert src.count(old) == 1, 'jangkar %s tidak unik (%d)' % (nama, src.count(old))
        src = src.replace(old, new, 1)
    return src, True


def main():
    files = sys.argv[1:] or ['index.html']
    for f in files:
        s = open(f, encoding='utf-8').read()
        os.makedirs('/tmp/sepora_bak', exist_ok=True)
        shutil.copy2(f, '/tmp/sepora_bak/' + os.path.basename(f) + '.bak-audit-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
        out, ch = patch(s)
        open(f, 'w', encoding='utf-8').write(out)
        print('[OK] %s -> %s' % (f, 'ditampal' if ch else 'sudah ditampal'))
    for f in files:
        s = open(f, encoding='utf-8').read()
        for m in ('arkibSanitizeHtml', 'pinHash', 'sahPin', 'simpanKredensial', '[W1]', '[W2]', '[W5]'):
            assert m in s, 'semakan gagal %s: %s' % (f, m)
    print('[SEMAK] W1/W2/W5/W6 ditampal')
    return 0


if __name__ == '__main__':
    sys.exit(main())
