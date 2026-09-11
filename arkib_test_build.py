# -*- coding: utf-8 -*-
"""Extract big script block from index.html -> run under a DOM stub in node, exercise Arkib v2."""
import io, re, os, subprocess, shutil, json

SRC = r"D:\SEPORA TOOLKIT\index.html"
OUTDIR = r"D:\SEPORA TOOLKIT\.arkib_test"
os.makedirs(OUTDIR, exist_ok=True)

s = io.open(SRC, encoding="utf-8").read()
blocks = re.findall(r'<script[^>]*>(.*?)</script>', s, re.DOTALL)
blocks = [b for b in blocks if len(b) > 5000]
assert len(blocks) == 1, "jangka 1 blok skrip besar, jumpa %d" % len(blocks)
app = blocks[0]
io.open(os.path.join(OUTDIR, "app.js"), "w", encoding="utf-8", newline="").write(app)

r = subprocess.run("node --check app.js", shell=True, cwd=OUTDIR, capture_output=True, text=True)
print("node --check:", r.returncode, r.stdout.strip(), r.stderr.strip()[:400])

STUB = r"""
// ---------------- DOM stub ----------------
class El {
  constructor(id) {
    this.id = id || ''; this._t = ''; this._h = ''; this.value = ''; this.dataset = {};
    this.style = {}; this.options = []; this.tagName = 'DIV'; this.selectedIndex = 0;
    this.children = []; this.files = null; this.rows = [];
  }
  get innerText() { return this._t; }
  set innerText(v) { this._t = String(v); }
  get innerHTML() { return this._h; }
  set innerHTML(v) { this._h = String(v); }
  appendChild(c) { this.children.push(c); if (String(c.tagName) === 'OPTION') this.options.push(c); return c; }
  removeChild(c) { return c; }
  addEventListener() { }
  remove() { }
  removeEventListener() { }
  setAttribute() { }
  getAttribute() { return null; }
  querySelectorAll() { return []; }
  querySelector() { return null; }
  click() { }
  focus() { }
}
Object.defineProperty(El.prototype, 'classList', {
  get() {
    const self = this;
    if (!self._cls) {
      const set = new Set();
      self._cls = { add: c => set.add(c), remove: c => set.delete(c), toggle: c => set.has(c) ? set.delete(c) : set.add(c), contains: c => set.has(c), _set: set };
    }
    return self._cls;
  }
});

const _els = {};
function el(id) { if (!_els[id]) _els[id] = new El(id); return _els[id]; }
function mkSelect(id, vals) { const e = el(id); e.tagName = 'SELECT'; vals.forEach(v => { const o = new El(''); o.tagName = 'OPTION'; o.value = String(v); o.text = String(v); e.options.push(o); }); return e; }

global.document = {
  body: new El('body'),
  getElementById: (id) => _els[id] === undefined ? null : _els[id],
  createElement: (t) => { const e = new El(''); e.tagName = String(t).toUpperCase(); return e; },
  querySelectorAll: () => [], querySelector: () => null, addEventListener() { }
};
global.window = { addEventListener() { }, print() { }, __rphTemplKey: '', navigator: global.navigator, matchMedia: null, open() { } };
global.localStorage = {
  _d: {}, getItem(k) { return Object.prototype.hasOwnProperty.call(this._d, k) ? this._d[k] : null; },
  setItem(k, v) { this._d[k] = String(v); }, removeItem(k) { delete this._d[k]; }
};
global.sessionStorage = {
  _d: {}, getItem(k) { return Object.prototype.hasOwnProperty.call(this._d, k) ? this._d[k] : null; },
  setItem(k, v) { this._d[k] = String(v); }, removeItem(k) { delete this._d[k]; }
};
global.location = { protocol: 'https:', hostname: 'sepora-rbt-toolkit.vercel.app', origin: 'https://sepora-rbt-toolkit.vercel.app', search: '', href: 'https://sepora-rbt-toolkit.vercel.app/' };
global.navigator = { onLine: true, userAgent: 'Mozilla/5.0 (Linux; Android 14) Chrome/120' };
global.alert = (m) => { global.__alerts = (global.__alerts || []).concat([m]); };
global.Blob = class { constructor(p) { this.parts = p; } };
global.URL = { createObjectURL: () => 'blob:stub', revokeObjectURL() { } };
global.FileReader = class {
  readAsText(f) { this.result = f._content || '{}'; if (this.onload) this.onload(); }
};
global.HTMLElement = El;

// pre-register the app's real elements we care about
el('rphPreviewContainer').innerHTML = '<div class="rph-header-doc">RPH stub (kandungan dokumen sebenar)</div>';
mkSelect('formRphHari', ['Isnin', 'Selasa', 'Rabu', 'Khamis', 'Jumaat']);
mkSelect('formRphMasa', ['08:00 - 09:30', '10:30 - 11:30']);
mkSelect('formRphMinggu', Array.from({ length: 42 }, (_, i) => i + 1));
el('formRphKelas').value = '4 Dinamik';
el('formRphSubjek').value = 'RBT Tahun 4';
el('formRphTajuk').value = 'PBL 1: Reka Bentuk Kereta Idamanku';
el('formRphSk').value = '2.2 Reka Bentuk Produk Bertema';
el('formRphSp').value = '2.2.1 ...';
el('formRphBukuTeks').value = 'Buku Teks RBT Tahun 4 (Unit 2, ms 20-30)';
el('formPblMingguPelaksanaan').value = 'Minggu 12 hingga Minggu 15 (4 Minggu)';
el('formPblTarikhMula').value = '2026-09-08';
el('formPblTarikhHantar').value = '2026-09-29';
el('formRphTahap').value = '4_kereta_idamanku';
['previewTajuk', 'previewKelas', 'previewPblMingguTempoh', 'previewMinggu', 'previewHariTarikh',
  'previewMasa', 'previewSubjek', 'previewSK', 'previewSP', 'previewBukuTeksRef', 'previewPblTarikhMula',
  'previewPblTarikhHantar', 'previewRefleksi', 'previewRptRef', 'previewBbmRef', 'previewPak21',
  'previewPembezaan', 'previewPentaksiran', 'previewTmk', 'previewKeselamatan', 'previewEmk',
  'previewTimelineContainer', 'previewRujukanIntegrasi', 'previewRujukanIntegrasiBlock', 'rphPreviewContainer',
  'savedRphTableBody', 'recentRphList', 'sidebarArkibBadge', 'sidebarRecentContent', 'arkibSelectedInfo',
  'modalBoxContent', 'appModalOverlay', 'toastContainer', 'cardTotalRph',
  'privacyLockScreen', 'delimaStatus', 'delimaGoogleBtn', 'loginInputEmail', 'loginInputPassword',
  'rememberSessionCheck', 'driveStatusChip', 'installAppBtn', 'driveAutoSync', 'gdriveClientIdInput'].forEach(i => el(i));

// ---------------- tests ----------------
const R = [];
function chk(name, cond, extra) { R.push((cond ? 'PASS ' : 'FAIL ') + name + (extra ? ' :: ' + extra : '')); }

localStorage.setItem('erph_saved', JSON.stringify([]));
arkibWithSuspend(function () { loadPblRbtTemplate(5); });
chk('buka app TIDAK cipta rekod arkib', savedRphList.length === 0, 'count=' + savedRphList.length);
loadPblRbtTemplate('5_rumah_tangga');
chk('autoGenerate jalan (previewTajuk terisi)', el('previewTajuk').innerText.length > 0, el('previewTajuk').innerText);
chk('auto-simpan: 1 rekod arkib', savedRphList.length === 1, JSON.stringify(savedRphList.map(r => [r.templateKey, r.kelas, r.minggu, r.status])));
chk('rekod guna templat betul (bukan 4_kereta)', savedRphList[0] && savedRphList[0].templateKey === '5_rumah_tangga', savedRphList[0] && savedRphList[0].templateKey);
chk('kelas ikut templat', savedRphList[0] && savedRphList[0].kelas === PBL_TEMPLATES['5_rumah_tangga'].kelas, savedRphList[0] && savedRphList[0].kelas);
chk('tarikh mula/hantar direkod', savedRphList[0] && savedRphList[0].pblTarikhMula === '2026-09-08' && savedRphList[0].pblTarikhHantar === '2026-09-29');
chk('status draf', savedRphList[0] && savedRphList[0].status === 'Draf Dijana', savedRphList[0] && savedRphList[0].status);
chk('badge arkib = 1', el('sidebarArkibBadge').innerText === '1', el('sidebarArkibBadge').innerText);

autoGenerateSmartRph(); autoGenerateSmartRph();
chk('jana semula TIDAK gandakan rekod', savedRphList.length === 1, 'count=' + savedRphList.length);

let navTajuk = el('previewTajuk').innerText;
saveCurrentGeneratedRph();
chk('simpan manual: masih 1 rekod (upsert)', savedRphList.length === 1, 'count=' + savedRphList.length);
chk('status jadi Disimpan', savedRphList[0].status === 'Disimpan', savedRphList[0].status);
chk('saved=true', savedRphList[0].saved === true);
chk('docHtml tersimpan', String(savedRphList[0].docHtml || '').length > 0, 'len=' + String(savedRphList[0].docHtml || '').length);

const firstId = savedRphList[0].id;
const html = el('savedRphTableBody').innerHTML;
chk('jadual render ada baris', html.indexOf('viewSavedRph(' + firstId + ')') > 0);
chk('jadual ada butang Edit', html.indexOf('openArkibEditModal(' + firstId + ')') > 0);
chk('jadual ada butang Guna Semula', html.indexOf('reuseArkibRph(' + firstId + ')') > 0);
chk('jadual 8 lajur', (html.match(/<td/g) || []).length === 8, 'td=' + (html.match(/<td/g) || []).length);
chk('tiada colspan=7', html.indexOf('colspan="7"') < 0);
chk('arkibSelectedInfo diisi', el('arkibSelectedInfo').innerHTML.indexOf('Rekod dipilih') >= 0, el('arkibSelectedInfo').innerHTML.slice(0, 90));

// edit modal + submit
openArkibEditModal(firstId);
chk('modal edit dibuka', el('modalBoxContent').innerHTML.indexOf('Edit Rekod Arkib RPH') > 0);
chk('modal ada butang Guna utk RPH Baharu', el('modalBoxContent').innerHTML.indexOf('Guna untuk RPH Baharu') > 0);
el('arkibEditTajuk').value = 'PBL 1: Teknologi Rumah Tangga (Dikemas Kini)';
el('arkibEditNota').value = 'Perlu tambah aktiviti pemulihan minggu 2';
el('arkibEditTarikhHantar').value = '2026-10-06';
el('arkibEditStatus').value = 'Sedang Dilaksana';
submitArkibEdit({ preventDefault() { } }, firstId);
chk('edit tersimpan (tajuk)', savedRphList[0].tajuk.indexOf('Dikemas Kini') > 0, savedRphList[0].tajuk);
chk('nota tersimpan', savedRphList[0].nota.indexOf('pemulihan') > 0);
chk('status edit tersimpan', savedRphList[0].status === 'Sedang Dilaksana', savedRphList[0].status);
chk('tempoh auto-kira ikut tarikh baru', /Minggu 12 hingga Minggu 15 \(4 Minggu\)/.test(savedRphList[0].pblMingguPelaksanaan || ''), savedRphList[0].pblMingguPelaksanaan);

// kemas kini dari dokumen (contenteditable)
el('previewTajuk').innerText = 'PBL 1: Teknologi Rumah Tangga Artikel Jahitan (Suntingan Dokumen)';
el('previewPblMingguTempoh').innerText = 'Minggu 13 hingga Minggu 15 (3 Minggu)';
updateArkibFromPreview();
chk('kemas kini rekod dari dokumen', savedRphList[0].tajuk.indexOf('Suntingan Dokumen') > 0, savedRphList[0].tajuk);
chk('tempoh dari dokumen', savedRphList[0].pblMingguPelaksanaan === 'Minggu 13 hingga Minggu 15 (3 Minggu)', savedRphList[0].pblMingguPelaksanaan);

// guna semula
const before = savedRphList.length;
reuseArkibRph(firstId);
chk('guna semula: rekod baharu ditambah', savedRphList.length === before + 1, 'count=' + savedRphList.length);
const copy = savedRphList[0];
chk('salinan tarikh +7 minggu', copy.pblTarikhMula === '2026-09-15' && copy.pblTarikhHantar === '2026-10-06', copy.pblTarikhMula + ' / ' + copy.pblTarikhHantar);
chk('salinan tempoh dikira semula (3 Minggu)', /Minggu 12 hingga Minggu 14 \(3 Minggu\)/.test(copy.pblMingguPelaksanaan || ''), copy.pblMingguPelaksanaan);
chk('rekod asal TIDAK diubah oleh guna semula', savedRphList.find(r => r.id === firstId).pblTarikhMula === '2026-09-08', JSON.stringify(savedRphList.find(r => r.id === firstId).pblTarikhMula));
chk('salinan status Draf Dijana', copy.status === 'Draf Dijana', copy.status);
chk('salinan docHtml kosong', !copy.docHtml);
chk('salinan id berbeza', copy.id !== firstId);
chk('form diisi dgn salinan (kelas)', el('formRphKelas').value === copy.kelas, el('formRphKelas').value);

// padam
const delId = savedRphList[0].id;
deleteSavedRph(delId);
chk('modal padam dibuka', el('modalBoxContent').innerHTML.indexOf('Padam Rekod Arkib') > 0);
executeArkibDelete(delId);
chk('padam berjaya', savedRphList.filter(r => r.id === delId).length === 0, 'count=' + savedRphList.length);

// export / import
exportArkibJson();
let exported = null;
chk('eksport json ada rekod', savedRphList.length === 1);
importArkibJson({ target: { files: [{ _content: JSON.stringify({ jenis: 'arkib-rph', rekod: [Object.assign({}, savedRphList[0], { id: 999999, tajuk: 'RPH IMPORT UJIAN', kelas: 'X' })] }) }], value: 'x' } });
chk('import tambah rekod', savedRphList.some(r => r.tajuk === 'RPH IMPORT UJIAN'), 'count=' + savedRphList.length);
importArkibJson({ target: { files: [{ _content: JSON.stringify({ rekod: [Object.assign({}, savedRphList[0], { id: 999999, tajuk: 'RPH IMPORT UJIAN', kelas: 'X' })] }) }], value: 'x' } });
chk('import tidak gandakan rekod sama', savedRphList.filter(r => r.tajuk === 'RPH IMPORT UJIAN').length === 1, 'count=' + savedRphList.length);

// data lama (tiada medan v2) - normalize
const legacy = arkibNormalize([{ id: 5, hari: 'Isnin', kelas: '5 Inovatif', minggu: 12, tajuk: 'LAMA', status: 'Selesai Dijana' }]);
chk('normalize rekod lama', legacy.length === 1 && legacy[0].pblTarikhMula === '' && legacy[0].id === 5 && legacy[0].tajuk === 'LAMA');

// empty state
savedRphList = []; renderSavedRphTable();
chk('empty state colspan=8', el('savedRphTableBody').innerHTML.indexOf('colspan="8"') > 0);
chk('empty state ada butang Bina RPH', el('savedRphTableBody').innerHTML.indexOf("switchTab('bina-rph')") > 0);


// ---------------- ujian DELIMa / Google Drive / PWA ----------------
global.google = { accounts: { oauth2: { initTokenClient: function (cfg) { global.__gisCfg = cfg; return { requestAccessToken: function () { cfg.callback({ access_token: 'TOK-UJIAN', expires_in: 3600 }); } }; } } } };
window.google = global.google;
global.FormData = class { constructor() { this._p = []; } append(k, v) { this._p.push([k, v]); } };

const FETCH_LOG = [];
function mockFetch(handler) { global.fetch = async function (url, opts) { FETCH_LOG.push(String(url)); return handler(String(url), opts || {}); }; }
function J(obj) { const body = JSON.stringify(obj); return { ok: true, status: 200, headers: { get: () => 'application/json' }, json: async () => JSON.parse(body), text: async () => body }; }
function ERR(msg) { return { ok: false, status: 403, headers: { get: () => 'application/json' }, json: async () => ({ error: { message: msg } }), text: async () => '' }; }

chk('isDelimEmail: moe-dl diterima', isDelimEmail('cikgu@moe-dl.edu.my') === true);
chk('isDelimEmail: gmail ditolak', isDelimEmail('someone@gmail.com') === false);
chk('client id belum diset -> belum konfigur', gdriveConfigured() === false);

localStorage.setItem('erph_gdrive_clientid', '1234567890-abcdefg.apps.googleusercontent.com');
chk('client id sah -> dikonfigur', gdriveConfigured() === true);

// gerbang log masuk: belum log masuk -> dipapar
localStorage.removeItem('erph_session'); sessionStorage._d = {}; localStorage.removeItem('erph_remember_login');
checkAuthStatus();
chk('gerbang dipapar bila belum log masuk', el('privacyLockScreen').classList.contains('hidden') === false);
chk('status gerbang ada mesej', el('delimaStatus').innerHTML.length > 10, el('delimaStatus').innerHTML.slice(0, 60));

// log masuk Google dgn akaun BUKAN DELIMa
mockFetch((u) => J({ email: 'someone@gmail.com', name: 'Bukan Delim' }));
(async () => {
  await delimaLoginWithGoogle();
  chk('akaun bukan DELIMa ditolak (tiada sesi)', getSession() === null, JSON.stringify(getSession()));
  chk('mesej ralat domain dipaparkan', el('delimaStatus').innerHTML.indexOf('bukan ID DELIMa') > 0, el('delimaStatus').innerHTML.slice(0, 80));

  // log masuk Google dgn akaun DELIMa
  mockFetch((u) => {
    if (u.indexOf('userinfo') > 0) return J({ email: 'Cikgu.Wafi@moe-dl.edu.my', name: 'Cikgu Wafi', picture: 'https://x/y.png' });
    if (u.indexOf('/upload/drive/v3/files') > 0) return J({ id: 'FILE-ABC', name: 'SEPORA_RPH_ARKIB.json', modifiedTime: '2026-09-11T10:00:00Z' });
    if (u.indexOf('/drive/v3/files?') > 0) return J({ files: [] });
    return J({});
  });
  savedRphList = []; renderSavedRphTable();
  await delimaLoginWithGoogle();
  const sess = getSession();
  chk('log masuk DELIMa berjaya (sesi disimpan)', sess && sess.email === 'cikgu.wafi@moe-dl.edu.my', JSON.stringify(sess && sess.email));
  chk('sesi mod delima', sess && sess.mode === 'delima');
  chk('nama guru diambil dari Google', teacherProfile.name === 'Cikgu Wafi', teacherProfile.name);
  chk('gerbang ditutup selepas log masuk', el('privacyLockScreen').classList.contains('hidden') === true);
  refreshDriveChip();
  chk('chip Drive papar emel DELIMa', el('driveStatusChip').innerHTML.indexOf('cikgu.wafi@moe-dl.edu.my') > 0, el('driveStatusChip').innerHTML);
  chk('chip Drive berwarna hijau bila sesi DELIMa aktif', el('driveStatusChip').style.color === '#059669', el('driveStatusChip').style.color);

  // sandaran ke Drive
  loadPblRbtTemplate('6_kereta_kawalan');
  const okSave = await driveSave(true);
  chk('driveSave berjaya', okSave === true);
  chk('fail Drive id disimpan', (gFileId === 'FILE-ABC') || (localStorage.getItem('erph_drive_fileid') === 'FILE-ABC'), gFileId + ' / ' + localStorage.getItem('erph_drive_fileid'));
  chk('masa sandaran direkod', !!localStorage.getItem('erph_drive_lastsync'));
  chk('payload Drive ada rekod RPH', FETCH_LOG.some(u => u.indexOf('upload/drive/v3/files') > 0));

  // pulih dari Drive (merge)
  FETCH_LOG.length = 0;
  mockFetch((u) => {
    if (u.indexOf('/drive/v3/files?') > 0) return J({ files: [{ id: 'FILE-ABC', name: 'SEPORA_RPH_ARKIB.json', modifiedTime: '2026-09-11T10:00:00Z' }] });
    if (u.indexOf('alt=media') > 0) return J({ jenis: 'arkib-rph', rekod: [{ id: 777001, tajuk: 'RPH DARI DRIVE', kelas: '6 Cemerlang', minggu: '20', hari: 'Isnin', pblTarikhHantar: '2026-11-03', status: 'Disimpan', dikemas: '2026-09-11T09:00:00Z' }] });
    return J({});
  });
  const n0 = savedRphList.length;
  const okRes = await driveRestore(true);
  chk('driveRestore berjaya', okRes === true);
  chk('rekod Drive digabungkan', savedRphList.some(r => r.tajuk === 'RPH DARI DRIVE'), 'count=' + savedRphList.length);
  chk('rekod tempatan tidak hilang', savedRphList.length >= n0 + 1, n0 + ' -> ' + savedRphList.length);

  // auto-sandaran
  toggleDriveAutoSync(true);
  chk('auto-sandaran disimpan', localStorage.getItem(SEPORA_GDRIVE.autoKey) === '1');
  driveMaybeAuto();
  chk('auto-sandaran dijadual (timer)', gAutoTimer !== null);

  // log keluar
  logoutSession();
  chk('log keluar: sesi dikosongkan', getSession() === null);
  chk('log keluar: gerbang dipapar semula', el('privacyLockScreen').classList.contains('hidden') === false);

  // mod setempat
  authCredentials = { email: 'guru@moe-dl.edu.my', password: '9999' };
  el('loginInputEmail').value = 'guru@moe-dl.edu.my';
  el('loginInputPassword').value = '9999';
  el('rememberSessionCheck').checked = true;
  localStorage.removeItem('erph_session');
  handleLoginSubmit({ preventDefault() { } });
  const s2 = getSession();
  chk('mod setempat: sesi dicipta', !!s2 && s2.mode === 'setempat', JSON.stringify(s2 && s2.mode));
  chk('mod setempat: gerbang ditutup', el('privacyLockScreen').classList.contains('hidden') === true);
  chk('mod setempat: chip amaran', el('driveStatusChip').innerHTML.indexOf('setempat') >= 0, el('driveStatusChip').innerHTML);

  // PWA
  chk('PWA: boolean standalone dikira', typeof isStandalone() === 'boolean');
  chk('PWA: modal cara pasang ada kandungan', (openInstallHelpModal(), el('modalBoxContent').innerHTML.indexOf('Add to Home Screen') > 0));
  chk('PWA: panel Drive boleh dibuka', (openDrivePanel(), el('modalBoxContent').innerHTML.indexOf('Sandaran Google Drive') > 0));
  chk('PWA: setelan client id boleh dibuka', (openGdriveSetupModal(), el('modalBoxContent').innerHTML.indexOf('OAuth Client ID') > 0));
  chk('PWA: deep link tab berfungsi', (function () { location = { search: '' }; return true; })());

  console.log(R.join('\n'));
  console.log('\nRINGKASAN: ' + R.filter(x => x.startsWith('PASS')).length + ' pass / ' + R.filter(x => x.startsWith('FAIL')).length + ' fail');
  if (R.some(x => x.startsWith('FAIL'))) process.exitCode = 1;
})();
"""

MARK = "// ---------------- tests ----------------"
assert MARK in STUB
prelude, tests = STUB.split(MARK, 1)
io.open(os.path.join(OUTDIR, "prelude.js"), "w", encoding="utf-8", newline="").write(prelude)
io.open(os.path.join(OUTDIR, "tests.js"), "w", encoding="utf-8", newline="").write(MARK + tests)
# run.js = stub + app sebenar + ujian
io.open(os.path.join(OUTDIR, "run.js"), "w", encoding="utf-8", newline="").write(prelude + "\n" + app + "\n" + MARK + tests)
r = subprocess.run("node run.js", shell=True, cwd=OUTDIR, capture_output=True, text=True)
print(r.stdout)
print("STDERR:", r.stderr.strip()[:2000])
print("exit:", r.returncode)
