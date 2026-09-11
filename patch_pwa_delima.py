# -*- coding: utf-8 -*-
"""SEPORA RBT TOOLKIT - Patch #3: PWA (install) + gerbang log masuk DELIMa + sandaran Google Drive"""
import io, shutil, json

P = r"D:\SEPORA TOOLKIT\index.html"
s = io.open(P, encoding="utf-8").read()
orig_len = len(s)

def rep(old, new, label, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, "ANCHOR %s: jumpa %d (jangka %d)\n---\n%s" % (label, n, cnt, old[:200])
    s = s.replace(old, new, cnt)
    print("OK ", label)

# ============================================================ A. HEAD: manifest + meta PWA
rep("""    <script src="https://cdn.jsdelivr.net/npm/docx@8.5.0/build/index.umd.js"></script>
""",
"""    <script src="https://cdn.jsdelivr.net/npm/docx@8.5.0/build/index.umd.js"></script>

  <!-- ===== PWA: boleh dipasang pada telefon & laptop (ikon + offline) ===== -->
  <link rel="manifest" href="/manifest.webmanifest">
  <meta name="theme-color" content="#1a73e8">
  <meta name="application-name" content="SEPORA RBT TOOLKIT">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="SEPORA RBT">
  <meta name="description" content="Sistem Pembina RPH & Inovasi PBL RBT - arkib RPH, cetak PDF/Word, sandaran Google Drive DELIMa.">
  <link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png">
  <link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
""", "A. head PWA")

# ============================================================ B. CSS gate + chip
rep("\n\n</style>",
"""\n\n
    /* ===== PWA & gerbang log masuk DELIMa ===== */
    .hidden { display: none !important; }
    #driveStatusChip {
      display: inline-flex; align-items: center; gap: 6px; cursor: pointer;
      font-size: 0.72rem; font-weight: 600; padding: 5px 10px; border-radius: 20px;
      border: 1px solid var(--surface-border); color: var(--text-muted); background: var(--surface);
      max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }
    #driveStatusChip:hover { border-color: var(--primary); color: var(--primary); }
    #installAppBtn { display: none; }
    .delima-gate {
      position: fixed; inset: 0; z-index: 5000; display: flex; align-items: center; justify-content: center;
      padding: 1rem; background: linear-gradient(135deg, #0b57d0 0%, #1a73e8 45%, #34a853 100%);
      overflow-y: auto;
    }
    .delima-card {
      width: 100%; max-width: 430px; background: var(--surface); border-radius: 18px; padding: 1.6rem 1.4rem;
      box-shadow: 0 24px 60px rgba(0,0,0,0.35); text-align: center; margin: auto;
    }
    .delima-card h1 { font-size: 1.25rem; font-weight: 800; margin: 0.75rem 0 0.15rem; letter-spacing: 0.4px; }
    .delima-card .delima-sub { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1.1rem; }
    .delima-google {
      width: 100%; display: flex; align-items: center; justify-content: center; gap: 10px;
      background: #fff; color: #3c4043; border: 1.5px solid #dadce0; border-radius: 10px;
      padding: 0.8rem 1rem; font-weight: 700; font-size: 0.95rem; cursor: pointer; transition: all .15s;
    }
    .delima-google:hover { border-color: #1a73e8; box-shadow: 0 2px 10px rgba(26,115,232,0.25); }
    .delima-google i { color: #4285f4; font-size: 1.1rem; }
    .delima-note { font-size: 0.75rem; color: var(--text-muted); margin: 0.7rem 0 0.9rem; line-height: 1.45; text-align: left; }
    .delima-status {
      font-size: 0.78rem; padding: 0.55rem 0.7rem; border-radius: 8px; background: var(--primary-light);
      color: var(--primary); margin-bottom: 0.85rem; text-align: left; line-height: 1.4;
    }
    .delima-toggle {
      background: none; border: none; color: var(--text-muted); font-size: 0.78rem; cursor: pointer;
      text-decoration: underline; padding: 4px;
    }
    .delima-foot { margin-top: 1rem; font-size: 0.7rem; color: var(--text-muted); }
    .delima-foot span:hover { color: var(--primary); }
    .delima-local { text-align: left; margin-top: 0.9rem; border-top: 1px dashed var(--surface-border); padding-top: 0.9rem; }
\n</style>""", "B. CSS gate")

# ============================================================ C. Topbar: chip Drive + butang install
rep("""        <div class="header-right">
          <button class="btn-icon" id="themeToggleBtn" onclick="toggleDarkMode()" title="Tukar Tema Gelap/Cerah">
            <i class="fa-solid fa-moon"></i>
          </button>""",
"""        <div class="header-right">
          <span id="driveStatusChip" onclick="openDrivePanel()" title="Status sandaran Google Drive (ID DELIMa)">
            <i class="fa-solid fa-cloud"></i> Drive: belum log masuk
          </span>
          <button class="btn btn-outline btn-sm" id="installAppBtn" onclick="installApp()" title="Pasang aplikasi pada peranti ini" style="border-color:#10b981; color:#047857; white-space:nowrap;">
            <i class="fa-solid fa-download"></i> Pasang
          </button>
          <button class="btn-icon" id="themeToggleBtn" onclick="toggleDarkMode()" title="Tukar Tema Gelap/Cerah">
            <i class="fa-solid fa-moon"></i>
          </button>""", "C. topbar chip+install")

# ============================================================ D. Gerbang log masuk DELIMa
rep("""  <div id="appModalOverlay" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.5); z-index:100; align-items:center; justify-content:center; padding:1rem;" onclick="closeAllModals(event)">""",
"""  <!-- ================= GERBANG LOG MASUK (WAJIB) - ID DELIMa / Mod Setempat ================= -->
  <div id="privacyLockScreen" class="delima-gate">
    <div class="delima-card">
      <img src="/icons/icon-192.png" alt="SEPORA RBT TOOLKIT" style="width:66px;height:66px;border-radius:16px;">
      <h1>SEPORA RBT TOOLKIT</h1>
      <p class="delima-sub">Sistem Pembina RPH &amp; Inovasi PBL &bull; e-RPH RBT</p>

      <button class="delima-google" id="delimaGoogleBtn" onclick="delimaLoginWithGoogle()">
        <i class="fa-brands fa-google"></i> Log Masuk dengan ID DELIMa
      </button>

      <p class="delima-note">
        Gunakan akaun <strong>@moe-dl.edu.my</strong> (DELIMa). Arkib RPH anda akan disandarkan ke
        <strong>Google Drive akaun DELIMa anda sendiri</strong> supaya rekod kekal walaupun tukar telefon atau laptop.
        Data juga disimpan dalam peranti ini untuk kegunaan offline.
      </p>

      <div id="delimaStatus" class="delima-status">Belum log masuk. Sila log masuk untuk mula menyimpan RPH anda.</div>

      <button class="delima-toggle" onclick="toggleLocalLogin()"><i class="fa-solid fa-chevron-down"></i> Mod setempat (tanpa Drive)</button>

      <form id="delimaLocalForm" class="delima-local hidden" onsubmit="handleLoginSubmit(event)">
        <div class="form-group">
          <label class="form-label">Emel / ID DELIMa</label>
          <input type="text" id="loginInputEmail" class="form-control" value="cikgu.rahmah@moe-dl.edu.my" autocomplete="username">
        </div>
        <div class="form-group">
          <label class="form-label">Kata Laluan / PIN</label>
          <input type="password" id="loginInputPassword" class="form-control" placeholder="PIN anda" autocomplete="current-password">
        </div>
        <label style="display:flex; align-items:center; gap:8px; font-size:0.78rem; color:var(--text-muted); margin-bottom:0.7rem;">
          <input type="checkbox" id="rememberSessionCheck" checked> Ingat log masuk pada peranti ini
        </label>
        <button type="submit" class="btn btn-primary" style="width:100%;"><i class="fa-solid fa-right-to-bracket"></i> Masuk (setempat)</button>
        <p style="font-size:0.72rem; color:var(--text-muted); margin-top:0.5rem; text-align:center;">
          <span onclick="showDefaultLoginHelp(event)" style="cursor:pointer; text-decoration:underline;">Lupa PIN? Tunjuk log masuk asal</span>
        </p>
      </form>

      <div class="delima-foot">
        <span onclick="openGdriveSetupModal()">Setelan sandaran Google Drive (Client ID)</span>
        &nbsp;•&nbsp;
        <span onclick="openInstallHelpModal()">Cara pasang pada telefon/laptop</span>
      </div>
    </div>
  </div>

  <div id="appModalOverlay" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.5); z-index:100; align-items:center; justify-content:center; padding:1rem;" onclick="closeAllModals(event)">""", "D. gerbang DELIMa")

# ============================================================ E. Toolbar Arkib: butang Drive
rep("""              <input type="file" id="arkibImportInput" accept="application/json,.json" style="display:none" onchange="importArkibJson(event)">
            </div>""",
"""              <input type="file" id="arkibImportInput" accept="application/json,.json" style="display:none" onchange="importArkibJson(event)">
              <span style="width:1px; height:22px; background:var(--surface-border);"></span>
              <button class="btn btn-outline" style="border-color:#93c5fd; color:#1d4ed8;" onclick="driveSave(false)"><i class="fa-solid fa-cloud-arrow-up"></i> Sandaran ke Drive</button>
              <button class="btn btn-outline" style="border-color:#93c5fd; color:#1d4ed8;" onclick="driveRestore(false)"><i class="fa-solid fa-cloud-arrow-down"></i> Pulih dari Drive</button>
              <label style="display:flex; align-items:center; gap:7px; font-size:0.8rem; color:var(--text-muted); font-weight:600;">
                <input type="checkbox" id="driveAutoSync" onchange="toggleDriveAutoSync(this.checked)">
                Auto-sandaran Drive
              </label>
            </div>""", "E. butang Drive")

# ============================================================ F. JS: modul PWA + DELIMa + Drive
MODUL = r"""
    /* =========================================================================
       PWA (boleh dipasang) + GERBANG LOG MASUK DELIMa + SANDARAN GOOGLE DRIVE
       Aliran: log masuk DELIMa (Google) -> arkib kekal dalam localStorage peranti
       -> setiap perubahan disandarkan ke fail JSON dalam Google Drive pengguna.
       ========================================================================= */
    const PWA_INFO = { nama: 'SEPORA RBT TOOLKIT', versi: '1.0' };
    const SEPORA_GDRIVE = {
      // Isi Client ID OAuth Google anda di sini (atau melalui "Setelan sandaran Google Drive"):
      clientId: '',
      scope: 'openid email profile https://www.googleapis.com/auth/drive.file',
      fileName: 'SEPORA_RPH_ARKIB.json',
      delimDomains: ['moe-dl.edu.my', 'moe.edu.my', 'moe-dl.edu.my.gov.my'],
      autoKey: 'erph_drive_autosync'
    };
    let gTok = null, gTokExp = 0, gSyncing = false, gAutoTimer = null, gInstallEvt = null;
    let gFileId = '';

    function gdriveClientId() { try { return (localStorage.getItem('erph_gdrive_clientid') || SEPORA_GDRIVE.clientId || '').trim(); } catch (e) { return SEPORA_GDRIVE.clientId || ''; } }
    function gdriveConfigured() { return /\.apps\.googleusercontent\.com$/i.test(gdriveClientId()); }
    function getSession() { try { return JSON.parse(localStorage.getItem('erph_session') || 'null'); } catch (e) { return null; } }
    function setSession(v) { try { if (v) localStorage.setItem('erph_session', JSON.stringify(v)); else localStorage.removeItem('erph_session'); } catch (e) { } }
    function isDelimEmail(e) {
      const v = String(e || '').toLowerCase();
      return SEPORA_GDRIVE.delimDomains.some(function (d) { return v.slice(-1 * (d.length + 1)) === '@' + d; });
    }
    function loginTime(d) {
      const x = d ? new Date(d) : new Date();
      return ('0' + x.getDate()).slice(-2) + '/' + ('0' + (x.getMonth() + 1)).slice(-2) + ' ' + ('0' + x.getHours()).slice(-2) + ':' + ('0' + x.getMinutes()).slice(-2);
    }
    function setDriveChip(html, warna) {
      const el = document.getElementById('driveStatusChip');
      if (!el) return;
      el.innerHTML = html;
      el.style.borderColor = warna || '';
      el.style.color = warna || '';
    }
    function refreshDriveChip() {
      const s = getSession();
      const last = localStorage.getItem('erph_drive_lastsync');
      if (!s) { setDriveChip('<i class="fa-solid fa-cloud"></i> Drive: belum log masuk', ''); return; }
      if (s.mode !== 'delima') { setDriveChip('<i class="fa-solid fa-cloud-slash"></i> Mod setempat: ' + esc(s.email || ''), '#b45309'); return; }
      setDriveChip('<i class="fa-solid fa-cloud-circle-check"></i> Drive: ' + esc(s.email) + (last ? ' &bull; ' + loginTime(last) : ''), '#059669');
    }
    function toggleLocalLogin() {
      const f = document.getElementById('delimaLocalForm');
      if (f) f.classList.toggle('hidden');
    }
    function setGateStatus(html) { const el = document.getElementById('delimaStatus'); if (el) el.innerHTML = html; }

    /* ---------------- PWA: daftar service worker & butang pasang ---------------- */
    function registerPwaWorker() {
      if (!('serviceWorker' in navigator)) return;
      if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') return;
      navigator.serviceWorker.register('/sw.js', { scope: '/' }).then(function (reg) {
        window.__swReg = reg;
        if (reg.waiting) showToast('Versi baharu sedia. Tutup & buka semula aplikasi untuk kemas kini.');
        reg.addEventListener('updatefound', function () {
          const nw = reg.installing; if (!nw) return;
          nw.addEventListener('statechange', function () {
            if (nw.state === 'installed' && navigator.serviceWorker.controller) showToast('Kemas kini aplikasi dimuat di latar belakang.');
          });
        });
      }).catch(function () { });
    }
    function isStandalone() {
      return (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) || window.navigator.standalone === true;
    }
    function installApp() {
      if (gInstallEvt) {
        gInstallEvt.prompt();
        gInstallEvt.userChoice.then(function (c) {
          if (c && c.outcome === 'accepted') showToast('Aplikasi sedang dipasang...');
          gInstallEvt = null;
          const b = document.getElementById('installAppBtn'); if (b) b.style.display = 'none';
        }).catch(function () { });
        return;
      }
      openInstallHelpModal();
    }
    function bindInstallPrompt() {
      window.addEventListener('beforeinstallprompt', function (e) {
        e.preventDefault(); gInstallEvt = e;
        const b = document.getElementById('installAppBtn'); if (b) b.style.display = 'inline-flex';
      });
      window.addEventListener('appinstalled', function () {
        gInstallEvt = null;
        const b = document.getElementById('installAppBtn'); if (b) b.style.display = 'none';
        showToast('SEPORA RBT TOOLKIT telah dipasang pada peranti ini.');
      });
      const ios = /iphone|ipad|ipod/i.test(navigator.userAgent || '');
      if (ios && !isStandalone()) { const b = document.getElementById('installAppBtn'); if (b) b.style.display = 'inline-flex'; }
    }
    function openInstallHelpModal() {
      const ios = /iphone|ipad|ipod/i.test(navigator.userAgent || '');
      const html = `
        <div class="card-header">
          <h3><i class="fa-solid fa-mobile-screen-button" style="color:#059669; margin-right:6px;"></i> Pasang Aplikasi (PWA)</h3>
          <button class="btn-icon" onclick="closeModalDirectly()"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.75rem;">
          Bila dipasang, SEPORA RBT TOOLKIT muncul sebagai ikon aplikasi (ada arkib RPH tersendiri),
          boleh dibuka tanpa internet, dan arkib disandarkan ke Google Drive DELIMa anda.
        </p>
        <div style="font-size:0.85rem; line-height:1.6;">
          <p style="font-weight:700; margin-bottom:4px;">Android (Chrome)</p>
          <p style="color:var(--text-muted); margin-bottom:0.6rem;">Ketik butang <strong>Pasang</strong> di bar atas, atau menu (⋮) &rarr; <em>Add to Home screen</em> / <em>Install app</em>.</p>
          <p style="font-weight:700; margin-bottom:4px;">iPhone / iPad (Safari)</p>
          <p style="color:var(--text-muted); margin-bottom:0.6rem;">Ketik butang <strong>Share</strong> &rarr; <em>Add to Home Screen</em> &rarr; <em>Add</em>.</p>
          <p style="font-weight:700; margin-bottom:4px;">Laptop / Komputer (Chrome / Edge)</p>
          <p style="color:var(--text-muted);">Klik ikon <strong>pasang</strong> (⊞/monitor) di hujung kanan bar alamat, atau menu &rarr; <em>Install SEPORA RBT TOOLKIT</em>.</p>
        </div>
        ${ios ? '<p style="font-size:0.78rem; color:#b45309; margin-top:0.7rem;">Peranti iOS: ciri pasang hanya melalui Safari (bukan Chrome iOS).</p>' : ''}
        <div style="display:flex; justify-content:flex-end; margin-top:1rem;">
          <button class="btn btn-primary" onclick="closeModalDirectly()">Faham</button>
        </div>`;
      openModal(html);
    }

    /* ---------------- Google Identity Services ---------------- */
    function loadGis() {
      if (window.google && window.google.accounts && window.google.accounts.oauth2) return Promise.resolve(true);
      return new Promise(function (resolve) {
        const sc = document.createElement('script');
        sc.src = 'https://accounts.google.com/gsi/client'; sc.async = true; sc.defer = true;
        sc.onload = function () { resolve(!!(window.google && window.google.accounts)); };
        sc.onerror = function () { resolve(false); };
        document.head.appendChild(sc);
      });
    }
    function gToken(silent) {
      return new Promise(function (resolve, reject) {
        if (gTok && Date.now() < gTokExp - 60000) return resolve(gTok);
        loadGis().then(function (ok) {
          if (!ok) return reject(new Error('Gagal muat skrip Google. Perlu sambungan internet sekali untuk log masuk.'));
          const sess = getSession();
          try {
            const tc = google.accounts.oauth2.initTokenClient({
              client_id: gdriveClientId(),
              scope: SEPORA_GDRIVE.scope,
              hint: sess && isDelimEmail(sess.email) ? sess.email : '',
              prompt: silent ? '' : 'consent',
              callback: function (resp) {
                if (resp && resp.access_token) {
                  gTok = resp.access_token;
                  gTokExp = Date.now() + (Number(resp.expires_in || 3600) * 1000);
                  resolve(gTok);
                } else { reject(new Error('Kebenaran Google tidak diberikan.')); }
              },
              error_callback: function (err) { reject(new Error('Ralat pengesahan Google: ' + ((err && err.message) || 'tidak diketahui'))); }
            });
            tc.requestAccessToken({ prompt: silent ? '' : 'consent' });
          } catch (e) { reject(e); }
        });
      });
    }
    async function gFetch(url, opts, tok) {
      opts = opts || {};
      const mk = function (t) {
        const h = Object.assign({ Authorization: 'Bearer ' + t }, opts.headers || {});
        return Object.assign({}, opts, { headers: h });
      };
      let res = await fetch(url, mk(tok));
      if (res.status === 401) { const t2 = await gToken(true); res = await fetch(url, mk(t2)); }
      if (!res.ok) {
        let msg = res.status + ' ' + res.statusText;
        try { const j = await res.json(); msg = (j.error && j.error.message) || msg; } catch (e) { }
        throw new Error(msg);
      }
      const ct = (res.headers.get('content-type') || '');
      return ct.indexOf('application/json') >= 0 ? res.json() : res.text();
    }
    function driveApi(path, opts, tok) { return gFetch('https://www.googleapis.com' + path, opts, tok); }
    function drivePayload() {
      const sess = getSession() || {};
      return {
        app: PWA_INFO.nama, jenis: 'arkib-rph', versi: 2, tarikh: new Date().toISOString(),
        pemilik: sess.email || '', sekolah: sess.school || '', bilangan: savedRphList.length, rekod: savedRphList
      };
    }

    /* ---------------- Log masuk DELIMa ---------------- */
    async function delimaLoginWithGoogle() {
      const btn = document.getElementById('delimaGoogleBtn');
      if (!gdriveConfigured()) { openGdriveSetupModal(); return; }
      if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Membuka pengesahan Google...'; }
      setGateStatus('Membuka tetingkap pengesahan Google (pilih akaun DELIMa anda)...');
      try {
        const tok = await gToken(false);
        const info = await fetch('https://openidconnect.googleapis.com/v1/userinfo', { headers: { Authorization: 'Bearer ' + tok } }).then(function (r) { return r.json(); });
        const email = String(info.email || '').toLowerCase();
        if (!isDelimEmail(email)) {
          setGateStatus('<span style="color:#b45309;">Akaun <strong>' + esc(email) + '</strong> bukan ID DELIMa (@moe-dl.edu.my). Sila pilih akaun DELIMa sekolah anda.</span>');
          showToast('Sila gunakan ID DELIMa untuk sandaran Drive.');
          return;
        }
        finishLogin({ email: email, name: info.name || email, picture: info.picture || '', mode: 'delima' });
        await restoreAfterLogin();
      } catch (e) {
        setGateStatus('<span style="color:#dc2626;">' + esc(e.message || 'Gagal log masuk.') + ' Cuba lagi atau guna mod setempat.</span>');
      } finally {
        if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fa-brands fa-google"></i> Log Masuk dengan ID DELIMa'; }
      }
    }
    function finishLogin(sess) {
      sess.loginAt = new Date().toISOString();
      setSession(sess);
      try {
        sessionStorage.setItem('erph_logged_in', 'true');
        localStorage.setItem('erph_remember_login', 'true');
      } catch (e) { }
      if (sess.name) { teacherProfile.name = sess.name; try { localStorage.setItem('erph_teacher', JSON.stringify(teacherProfile)); } catch (e) { } }
      const lock = document.getElementById('privacyLockScreen');
      if (lock) lock.classList.add('hidden');
      if (typeof syncTeacherUI === 'function') syncTeacherUI();
      refreshDriveChip();
      const au = document.getElementById('driveAutoSync');
      if (au) au.checked = localStorage.getItem(SEPORA_GDRIVE.autoKey) === '1';
      showToast('Selamat datang ' + (sess.name || sess.email) + (sess.mode === 'delima' ? ' (ID DELIMa)' : ' (mod setempat)') + '!');
    }
    async function restoreAfterLogin() {
      if (typeof driveRestore !== 'function') return;
      if (savedRphList.length === 0) {
        const ok = await driveRestore(true);
        if (!ok) showToast('Belum ada sandaran dalam Drive. RPH yang dijana akan disandarkan secara automatik.');
      } else if (!localStorage.getItem('erph_drive_lastsync')) {
        if (confirm('Arkib dalam peranti ini ada ' + savedRphList.length + ' rekod. Mahu muat turun & gabungkan arkib dari Google Drive?')) await driveRestore(true);
      }
    }

    /* ---------------- Sandaran Drive ---------------- */
    async function driveSave(silent) {
      const sess = getSession();
      if (!sess || sess.mode !== 'delima') {
        if (!silent) { showToast('Log masuk dengan ID DELIMa dahulu untuk sandaran Drive.'); openDrivePanel(); }
        return false;
      }
      if (gSyncing) return false;
      gSyncing = true;
      setDriveChip('<i class="fa-solid fa-arrows-rotate fa-spin"></i> Drive: menyimpan...', '#2563eb');
      try {
        const tok = await gToken(true);
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
          const meta = { name: SEPORA_GDRIVE.fileName, mimeType: 'application/json', description: 'Arkib RPH SEPORA RBT TOOLKIT (' + sess.email + ')' };
          const form = new FormData();
          form.append('metadata', new Blob([JSON.stringify(meta)], { type: 'application/json' }));
          form.append('file', new Blob([body], { type: 'application/json' }));
          const up = await driveApi('/upload/drive/v3/files?uploadType=multipart&fields=id,name,modifiedTime', { method: 'POST', body: form }, tok);
          gFileId = up.id;
        }
        try {
          localStorage.setItem('erph_drive_fileid', gFileId || '');
          localStorage.setItem('erph_drive_lastsync', new Date().toISOString());
        } catch (e) { }
        refreshDriveChip();
        if (!silent) showToast('Arkib (' + savedRphList.length + ' rekod) disandarkan ke Google Drive ' + sess.email + '.');
        return true;
      } catch (e) {
        setDriveChip('<i class="fa-solid fa-triangle-exclamation"></i> Drive: gagal - ' + esc(String(e.message || 'ralat').slice(0, 60)), '#dc2626');
        if (!silent) showToast('Sandaran Drive gagal: ' + (e.message || 'ralat rangkaian'));
        return false;
      } finally { gSyncing = false; }
    }
    async function driveRestore(silent) {
      const sess = getSession();
      if (!sess || sess.mode !== 'delima') {
        if (!silent) { showToast('Log masuk dengan ID DELIMa dahulu untuk memulihkan arkib dari Drive.'); openDrivePanel(); }
        return false;
      }
      setDriveChip('<i class="fa-solid fa-arrows-rotate fa-spin"></i> Drive: memuat turun...', '#2563eb');
      try {
        const tok = await gToken(true);
        const q = encodeURIComponent("name='" + SEPORA_GDRIVE.fileName + "' and trashed=false");
        const list = await driveApi('/drive/v3/files?q=' + q + '&spaces=drive&fields=files(id,name,modifiedTime)', {}, tok);
        if (!list.files || !list.files.length) {
          setDriveChip('<i class="fa-solid fa-cloud-question"></i> Drive: tiada fail sandaran', '#b45309');
          if (!silent) showToast('Tiada fail sandaran dalam Drive anda lagi.');
          return false;
        }
        const f = list.files[0];
        gFileId = f.id;
        try { localStorage.setItem('erph_drive_fileid', gFileId); } catch (e) { }
        const raw = await driveApi('/drive/v3/files/' + f.id + '?alt=media', {}, tok);
        const data = typeof raw === 'string' ? JSON.parse(raw) : raw;
        const rows = arkibNormalize(Array.isArray(data) ? data : (data.rekod || []));
        let added = 0, updated = 0;
        rows.forEach(function (n) {
          const ex = savedRphList.find(function (x) { return x.id === n.id; });
          if (ex) { if (String(n.dikemas || '') > String(ex.dikemas || '')) { Object.assign(ex, n); updated++; } }
          else { savedRphList.push(n); added++; }
        });
        savedRphList.sort(function (a, b) { return (Number(b.id) || 0) - (Number(a.id) || 0); });
        arkibPersist(); renderSavedRphTable(); updateArkibBadge(); updateDashboardMetrics(); updateArkibSelectedInfo();
        try { localStorage.setItem('erph_drive_lastsync', new Date().toISOString()); } catch (e) { }
        refreshDriveChip();
        if (!silent || added || updated) showToast('Pulih dari Drive: ' + added + ' rekod baharu, ' + updated + ' dikemas kini (fail: ' + f.name + ').');
        return true;
      } catch (e) {
        setDriveChip('<i class="fa-solid fa-triangle-exclamation"></i> Drive: gagal - ' + esc(String(e.message || 'ralat').slice(0, 60)), '#dc2626');
        if (!silent) showToast('Pulih dari Drive gagal: ' + (e.message || 'ralat rangkaian'));
        return false;
      }
    }
    function toggleDriveAutoSync(on) {
      try { localStorage.setItem(SEPORA_GDRIVE.autoKey, on ? '1' : '0'); } catch (e) { }
      if (on && !getSession()) { showToast('Auto-sandaran aktif, tetapi anda belum log masuk DELIMa.'); return; }
      showToast(on ? 'Auto-sandaran Drive diaktifkan (setiap perubahan arkib).' : 'Auto-sandaran Drive dimatikan.');
      if (on) driveSave(true);
    }
    function driveMaybeAuto() {
      try {
        if (localStorage.getItem(SEPORA_GDRIVE.autoKey) !== '1') return;
        const sess = getSession();
        if (!sess || sess.mode !== 'delima') return;
        clearTimeout(gAutoTimer);
        gAutoTimer = setTimeout(function () {
          if (gTok && Date.now() < gTokExp - 60000) driveSave(true);
          else setDriveChip('<i class="fa-solid fa-cloud-arrow-up"></i> Drive: tekan untuk sandaran (sesi tamat)', '#f59e0b');
        }, 6000);
      } catch (e) { }
    }

    /* ---------------- Panel Drive & setelan ---------------- */
    function openDrivePanel() {
      const sess = getSession();
      const last = localStorage.getItem('erph_drive_lastsync');
      const auto = localStorage.getItem(SEPORA_GDRIVE.autoKey) === '1';
      const rows = [
        ['Akaun DELIMa', sess ? esc(sess.email) + (sess.mode === 'delima' ? ' <span style="color:#059669;">(disahkan)</span>' : ' <span style="color:#b45309;">(mod setempat)</span>') : '<em>Belum log masuk</em>'],
        ['Sandaran terakhir', last ? loginTime(last) : '<em>Belum ada</em>'],
        ['Fail Drive', gFileId || localStorage.getItem('erph_drive_fileid') || '<em>Belum dicipta</em>'],
        ['Rekod dalam arkib', String(savedRphList.length)],
        ['Auto-sandaran', auto ? 'Aktif' : 'Mati'],
        ['Status internet', navigator.onLine ? 'Dalam talian' : 'Luar talian'],
        ['Dipasang pada peranti', isStandalone() ? 'Ya (PWA)' : 'Tidak (dibuka dalam pelayar)']
      ].map(function (r) { return '<tr><td style="padding:6px 8px; font-weight:600;">' + r[0] + '</td><td style="padding:6px 8px; color:var(--text-muted);">' + r[1] + '</td></tr>'; }).join('');
      const html = `
        <div class="card-header">
          <h3><i class="fa-solid fa-cloud" style="color:#1a73e8; margin-right:6px;"></i> Sandaran Google Drive (DELIMa)</h3>
          <button class="btn-icon" onclick="closeModalDirectly()"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <table style="width:100%; font-size:0.82rem; border-collapse:collapse; margin-bottom:1rem;">${rows}</table>
        <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
          ${sess ? '' : '<button class="btn btn-primary" onclick="closeModalDirectly(); delimaLoginWithGoogle()"><i class="fa-brands fa-google"></i> Log masuk DELIMa</button>'}
          <button class="btn btn-outline" onclick="driveSave(false)"><i class="fa-solid fa-cloud-arrow-up"></i> Sandaran sekarang</button>
          <button class="btn btn-outline" onclick="driveRestore(false)"><i class="fa-solid fa-cloud-arrow-down"></i> Pulih dari Drive</button>
          <button class="btn btn-outline" onclick="openGdriveSetupModal()"><i class="fa-solid fa-gear"></i> Setelan Client ID</button>
          ${sess ? '<button class="btn btn-outline" style="color:var(--danger); border-color:#fca5a5;" onclick="logoutSession()"><i class="fa-solid fa-right-from-bracket"></i> Log keluar</button>' : ''}
        </div>
        <p style="font-size:0.75rem; color:var(--text-muted); margin-top:0.85rem;">
          Fail sandaran: <strong>${SEPORA_GDRIVE.fileName}</strong> dalam Google Drive akaun DELIMa anda.
          Data juga kekal dalam peranti ini (localStorage) untuk kegunaan offline.
        </p>`;
      openModal(html);
    }
    function logoutSession() {
      setSession(null);
      gTok = null; gTokExp = 0;
      try {
        sessionStorage.removeItem('erph_logged_in');
        localStorage.removeItem('erph_remember_login');
      } catch (e) { }
      closeModalDirectly();
      const lock = document.getElementById('privacyLockScreen');
      if (lock) lock.classList.remove('hidden');
      setGateStatus('Anda telah log keluar. Data arkib kekal dalam peranti ini.');
      refreshDriveChip();
      showToast('Log keluar. Data RPH kekal dalam peranti.');
    }
    function openGdriveSetupModal() {
      const cur = gdriveClientId();
      const origin = (location.protocol === 'https:' || location.hostname === 'localhost') ? location.origin : 'https://sepora-rbt-toolkit.vercel.app';
      const html = `
        <div class="card-header">
          <h3><i class="fa-solid fa-gear" style="color:#1a73e8; margin-right:6px;"></i> Setelan Sandaran Google Drive</h3>
          <button class="btn-icon" onclick="closeModalDirectly()"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.75rem;">
          Untuk menyimpan arkib terus ke Google Drive guru, sistem perlu <strong>OAuth Client ID</strong> daripada Google Cloud
          (percuma, sekali sahaja, ~5 minit). Rujuk fail <strong>PANDUAN_GDRIVE.md</strong> dalam folder projek untuk langkah bergambar.
        </p>
        <ol style="font-size:0.82rem; line-height:1.6; padding-left:1.2rem; color:var(--text);">
          <li>Buka <a href="https://console.cloud.google.com/apis/credentials" target="_blank" rel="noopener">console.cloud.google.com/apis/credentials</a> &rarr; Create Credentials &rarr; <em>OAuth client ID</em> &rarr; Web application.</li>
          <li>Authorised JavaScript origins: <code style="background:var(--primary-light); padding:1px 5px; border-radius:4px;">${origin}</code></li>
          <li>Aktifkan <strong>Google Drive API</strong> (APIs &amp; Services &rarr; Library).</li>
          <li>Salin Client ID (<code>...apps.googleusercontent.com</code>) dan tampal di bawah.</li>
        </ol>
        <div class="form-group" style="margin-top:0.8rem;">
          <label class="form-label">OAuth Client ID</label>
          <input type="text" id="gdriveClientIdInput" class="form-control" placeholder="1234567890-xxxxxxxx.apps.googleusercontent.com" value="${escAttr(cur)}">
        </div>
        <div style="display:flex; justify-content:flex-end; gap:0.5rem;">
          <button class="btn btn-outline" onclick="closeModalDirectly()">Tutup</button>
          <button class="btn btn-primary" onclick="saveGdriveClientId()"><i class="fa-solid fa-floppy-disk"></i> Simpan &amp; cuba log masuk</button>
        </div>`;
      openModal(html);
    }
    function saveGdriveClientId() {
      const el = document.getElementById('gdriveClientIdInput');
      const v = (el ? el.value : '').trim();
      if (v && !/\.apps\.googleusercontent\.com$/i.test(v)) { showToast('Client ID tidak sah - mesti berakhir dengan .apps.googleusercontent.com'); return; }
      try { v ? localStorage.setItem('erph_gdrive_clientid', v) : localStorage.removeItem('erph_gdrive_clientid'); } catch (e) { }
      closeModalDirectly();
      showToast(v ? 'Client ID disimpan. Tekan "Log Masuk dengan ID DELIMa".' : 'Client ID dikosongkan.');
      const btn = document.getElementById('delimaGoogleBtn');
      if (btn && v) btn.click();
    }
    function applyDeepLinkTab() {
      try {
        const t = new URLSearchParams(location.search).get('tab');
        if (t && document.getElementById('view-' + t)) switchTab(t);
      } catch (e) { }
    }
    window.addEventListener('online', function () { refreshDriveChip(); driveMaybeAuto(); });
    window.addEventListener('offline', function () { setDriveChip('<i class="fa-solid fa-wifi"></i> Luar talian - data kekal dalam peranti', '#b45309'); });

"""

rep("""    window.addEventListener('DOMContentLoaded', () => {""",
MODUL + """    window.addEventListener('DOMContentLoaded', () => {""", "F. modul PWA+DELIMa+Drive")

# ============================================================ G. checkAuthStatus: sokong sesi DELIMa
rep("""    function checkAuthStatus() {
      const lockScreen = document.getElementById('privacyLockScreen');
      const isLoggedIn = sessionStorage.getItem('erph_logged_in') === 'true' || localStorage.getItem('erph_remember_login') === 'true';

      if (lockScreen) {
        if (isLoggedIn) {
          lockScreen.classList.add('hidden');
        } else {
          lockScreen.classList.remove('hidden');
          const inputEmail = document.getElementById('loginInputEmail');
          if (inputEmail) {
            inputEmail.value = authCredentials.email || DEFAULT_AUTH.email;
            setTimeout(() => {
              const pwField = document.getElementById('loginInputPassword');
              if (pwField) pwField.focus();
            }, 200);
          }
        }
      }
    }""",
"""    function checkAuthStatus() {
      const lockScreen = document.getElementById('privacyLockScreen');
      const sess = getSession();
      let isLoggedIn = false;
      try {
        isLoggedIn = sessionStorage.getItem('erph_logged_in') === 'true' || localStorage.getItem('erph_remember_login') === 'true';
      } catch (e) { }
      if (sess && sess.email) isLoggedIn = true;

      if (lockScreen) {
        if (isLoggedIn) {
          lockScreen.classList.add('hidden');
          if (!sess) setSession({ email: (authCredentials.email || DEFAULT_AUTH.email), name: teacherProfile.name, mode: 'setempat', loginAt: new Date().toISOString() });
        } else {
          lockScreen.classList.remove('hidden');
          const inputEmail = document.getElementById('loginInputEmail');
          if (inputEmail) inputEmail.value = authCredentials.email || DEFAULT_AUTH.email;
          setGateStatus(gdriveConfigured()
            ? 'Belum log masuk. Log masuk dengan ID DELIMa untuk sandaran Drive automatik.'
            : 'Belum log masuk. Sandaran Drive belum diset (tekan "Setelan sandaran Google Drive" di bawah) - anda boleh guna mod setempat dahulu.');
        }
      }
      const au = document.getElementById('driveAutoSync');
      if (au) au.checked = localStorage.getItem(SEPORA_GDRIVE.autoKey) === '1';
      refreshDriveChip();
    }""", "G. checkAuthStatus DELIMa")

# ============================================================ H. handleLoginSubmit -> finishLogin
rep("""      if (inputEmail === validEmail && inputPw === validPw) {
        sessionStorage.setItem('erph_logged_in', 'true');
        if (remember) {
          localStorage.setItem('erph_remember_login', 'true');
        } else {
          localStorage.removeItem('erph_remember_login');
        }

        const lockScreen = document.getElementById('privacyLockScreen');
        if (lockScreen) lockScreen.classList.add('hidden');
        document.getElementById('loginInputPassword').value = '';
        showToast(`Selamat datang, ${teacherProfile.name}! Sesi emel disahkan.`);""",
"""      if (inputEmail === validEmail && inputPw === validPw) {
        if (remember) {
          localStorage.setItem('erph_remember_login', 'true');
        } else {
          localStorage.removeItem('erph_remember_login');
        }
        sessionStorage.setItem('erph_logged_in', 'true');
        finishLogin({
          email: inputEmail,
          name: teacherProfile.name,
          picture: '',
          mode: isDelimEmail(inputEmail) ? 'setempat' : 'setempat'
        });
        const pw = document.getElementById('loginInputPassword');
        if (pw) pw.value = '';""", "H. handleLoginSubmit")

# ============================================================ I. init: SW + install + deep link
rep("""      arkibWithSuspend(function () { loadPblRbtTemplate(5); });
      checkAuthStatus();""",
"""      arkibWithSuspend(function () { loadPblRbtTemplate(5); });
      bindInstallPrompt();
      registerPwaWorker();
      applyDeepLinkTab();
      gFileId = localStorage.getItem('erph_drive_fileid') || '';
      checkAuthStatus();""", "I. init")

s = s.replace("""      localStorage.setItem('erph_saved', JSON.stringify(savedRphList));
        return true;""", """      localStorage.setItem('erph_saved', JSON.stringify(savedRphList));
        driveMaybeAuto();
        return true;""")

io.open(P, "w", encoding="utf-8", newline="").write(s)
shutil.copyfile(P, r"D:\SEPORA TOOLKIT\sepora_rbt_toolkit.html")
print("\nindex.html: %d -> %d aksara (twin disalin)" % (orig_len, len(s)))

# ============================================================ vercel.json: header sw + manifest
V = r"D:\SEPORA TOOLKIT\vercel.json"
vj = {
  "version": 2,
  "builds": [{"src": "**", "use": "@vercel/static"}],
  "routes": [
    {"src": "/sw.js", "headers": {"Cache-Control": "public, max-age=0, must-revalidate", "Service-Worker-Allowed": "/"}},
    {"src": "/manifest.webmanifest", "headers": {"Content-Type": "application/manifest+json", "Cache-Control": "public, max-age=3600"}},
    {"src": "/(.*)", "headers": {"Cache-Control": "public, max-age=0, must-revalidate"}}
  ],
  "cleanUrls": True,
  "trailingSlash": False
}
io.open(V, "w", encoding="utf-8", newline="\n").write(json.dumps(vj, indent=2))
print("vercel.json dikemas kini (header sw.js + manifest)")
