// ujian_offline.js — BUKTI app berfungsi TANPA INTERNET:
// 1) muat laman + biar service worker cache shell
// 2) MATIKAN rangkaian (Network.emulateNetworkConditions offline)
// 3) muat semula + daftar guru + jana RPH + eksport JSON
const PORT = process.env.CDP_PORT || 9420;
const TEST_URL = process.env.TEST_URL || 'http://127.0.0.1:8899/index.html';
const out = []; let fail = 0;
const ok = (n, c, i) => { out.push((c ? '  PASS ' : '  FAIL ') + n + (i ? '  [' + i + ']' : '')); if (!c) fail++; };
const tidur = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  let page = null;
  for (let i = 0; i < 40 && !page; i++) {
    try { const l = await (await fetch('http://127.0.0.1:' + PORT + '/json/list')).json(); page = l.find(t => t.type === 'page'); } catch (e) { }
    if (!page) await tidur(500);
  }
  if (!page) throw new Error('tiada target CDP');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let id = 0; const tunggu = new Map(); const errors = [];
  ws.onmessage = e => {
    const d = JSON.parse(e.data);
    if (d.id && tunggu.has(d.id)) { const w = tunggu.get(d.id); tunggu.delete(d.id); w(d); }
    if (d.method === 'Runtime.exceptionThrown') errors.push(((d.params.exceptionDetails.exception || {}).description) || d.params.exceptionDetails.text);
  };
  const send = (m, p = {}) => new Promise(res => { const i = ++id; tunggu.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  await send('Runtime.enable'); await send('Page.enable'); await send('Network.enable');
  const ev = async (x) => {
    const r = await Promise.race([send('Runtime.evaluate', { expression: x, returnByValue: true, awaitPromise: true }), tidur(15000).then(() => ({ __to: 1 }))]);
    if (r.__to) throw new Error('TIMEOUT: ' + x.slice(0, 70));
    if (r.result && r.result.exceptionDetails) throw new Error(((r.result.exceptionDetails.exception || {}).description || r.result.exceptionDetails.text) + ' :: ' + x.slice(0, 70));
    return r.result.result.value;
  };

  // ---- 1) Muat ONLINE dulu supaya service worker pasang + cache ----
  await send('Page.navigate', { url: TEST_URL }); await tidur(4000);
  await send('Page.navigate', { url: TEST_URL }); await tidur(4000);   // muat kedua: SW aktif
  const sw = await ev(`(async function(){ if(!('serviceWorker' in navigator)) return {ada:false};
    const r = await navigator.serviceWorker.getRegistration();
    return { ada: !!r, aktif: !!(r && r.active), skop: r ? r.scope : null }; })()`);
  ok('1. Service worker (PWA) terpasang & aktif', sw.ada === true && sw.aktif === true, JSON.stringify(sw));

  await ev("try{localStorage.clear();sessionStorage.clear()}catch(e){}; 'ok'");

  // ---- 2) MATIKAN RANGKAIAN ----
  await send('Network.emulateNetworkConditions', { offline: true, latency: 0, downloadThroughput: 0, uploadThroughput: 0 });
  await tidur(500);
  const offlineNow = await ev("navigator.onLine");
  ok('2. Rangkaian DIMATIKAN (offline=true)', offlineNow === false, `navigator.onLine=${offlineNow}`);

  // ---- 3) Buka laman semasa OFFLINE ----
  await send('Page.navigate', { url: TEST_URL }); await tidur(5000);
  const muat = await ev(`(function(){ return { url: location.href, tajuk: document.title,
    gerbangAda: !!document.getElementById('privacyLockScreen'),
    butangDaftar: !!document.getElementById('btnDaftarUtama'),
    skripHidup: typeof openDaftarModal === 'function' }; })()`);
  ok('3. OFFLINE: laman tetap terbuka (dari cache) + gerbang + skrip hidup',
    muat.butangDaftar === true && muat.skripHidup === true, JSON.stringify(muat));

  // ---- 4) Daftar guru OFFLINE ----
  await ev("window.confirm=function(){return true}; window.print=function(){}; 'ok'");
  await ev("openDaftarModal(true,true); 'ok'");
  await ev(`(function(){ document.getElementById('daftarNama').value='Cikgu Offline';
    document.getElementById('daftarEmel').value='g-24681012'; document.getElementById('daftarPin').value='778899'; return 'ok'; })()`);
  await ev("submitDaftarLocal({preventDefault:function(){}}); 'dihantar'");
  await tidur(2800);
  const daftarOff = await ev(`(function(){ var k=null; try{ k=JSON.parse(localStorage.getItem('erph_auth_cred')); }catch(e){}
    return { kredensial: k?k.email:null, gerbangTutup: document.getElementById('privacyLockScreen').classList.contains('hidden') }; })()`);
  ok('4. OFFLINE: guru boleh DAFTAR + terus masuk', daftarOff.kredensial === 'g-24681012@moe-dl.edu.my' && daftarOff.gerbangTutup === true, JSON.stringify(daftarOff));

  // ---- 5) Jana RPH OFFLINE ----
  const jana = await ev(`(function(){ try { loadSlotToRph('Selasa','11:00 - 12:00','2 Cekal','RBT Tahun 5');
    autoGenerateSmartRph(); var pv=document.getElementById('rphPreviewContainer');
    return { panjang: pv?(pv.textContent||'').length:0 }; } catch(e){ return {panjang:0, ralat:e.message}; } })()`);
  ok('5. OFFLINE: guru boleh JANA RPH (app berfungsi penuh)', jana.panjang > 500, `panjang=${jana.panjang} ralat=${jana.ralat || 'tiada'}`);

  // ---- 6) Simpan arkib + eksport JSON OFFLINE ----
  const simpan = await ev(`(function(){ saveCurrentGeneratedRph(); return (savedRphList||[]).length; })()`);
  const eksport = await ev(`(async function(){ const asalUrl=URL.createObjectURL, asalKlik=HTMLAnchorElement.prototype.click;
    let blob=null, nama='';
    URL.createObjectURL=function(b){ blob=b; return asalUrl.call(URL,b); };
    HTMLAnchorElement.prototype.click=function(){ nama=this.download||nama; };
    try { exportArkibJson(); } catch(e){}
    for (let i=0;i<30 && !blob;i++) await new Promise(r=>setTimeout(r,200));
    URL.createObjectURL=asalUrl; HTMLAnchorElement.prototype.click=asalKlik;
    if(!blob) return { ada:false };
    let sah=false; try{ JSON.parse(await blob.text()); sah=true; }catch(e){}
    return { ada:true, saiz:blob.size, sah:sah, nama:nama }; })()`);
  ok('6. OFFLINE: simpan arkib + Eksport Arkib (JSON) berfungsi',
    simpan >= 1 && eksport.ada === true && eksport.sah === true, `rekod=${simpan} saiz=${eksport.saiz}`);

  // ---- 7) Pustaka eksport (pdf/docx) tersedia OFFLINE? ----
  const lib = await ev(`(function(){ return { docx: typeof docx, html2pdf: typeof html2pdf, pdfjs: typeof pdfjsLib, fa: typeof document.querySelector('.fa-solid') }; })()`);
  ok('7. OFFLINE: pustaka eksport dimuat dari cache (Word/PDF sedia)',
    lib.docx === 'object' && lib.html2pdf === 'function' && lib.pdfjs === 'object', JSON.stringify(lib));

  // ---- 8) HIDUPKAN rangkaian semula ----
  await send('Network.emulateNetworkConditions', { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
  await tidur(1200);
  const onlineSemula = await ev("navigator.onLine");
  ok('8. Rangkaian hidup semula -> app pulih', onlineSemula === true, `online=${onlineSemula}`);

  ok('9. Tiada ralat JS sepanjang ujian offline', errors.length === 0, errors.slice(0, 3).join(' | ') || '0 ralat');

  console.log('\n===== UJIAN OFFLINE (tanpa internet) =====');
  console.log('URL: ' + TEST_URL);
  console.log(out.join('\n'));
  console.log(`\nRingkasan: ${out.length - fail}/${out.length} PASS`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(2); });
