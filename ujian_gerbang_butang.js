// ujian_gerbang_semua_butang.js — SAHKAN keempat-empat butang gerbang kelihatan & boleh ditekan
// pada 4 saiz skrin telefon. Ini yang menangkap "tekan2 tidak boleh masuk".
const PORT = process.env.CDP_PORT || 9354;
const TEST_URL = process.env.TEST_URL || 'https://sepora-rbt-toolkit.vercel.app/index.html';
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
  await send('Runtime.enable'); await send('Page.enable');
  const ev = async (x) => {
    const r = await Promise.race([send('Runtime.evaluate', { expression: x, returnByValue: true, awaitPromise: true }), tidur(15000).then(() => ({ __to: 1 }))]);
    if (r.__to) throw new Error('TIMEOUT: ' + x.slice(0, 70));
    if (r.result && r.result.exceptionDetails) throw new Error(((r.result.exceptionDetails.exception || {}).description || r.result.exceptionDetails.text) + ' :: ' + x.slice(0, 70));
    return r.result.result.value;
  };
  const GEO = (el) => `(function(){ var b=document.getElementById('${el}'); if(!b) return {ada:false};
    var r=b.getBoundingClientRect(); var x=Math.round(r.x+r.width/2), y=Math.round(r.y+r.height/2);
    var t=document.elementFromPoint(x,y);
    return { ada:true, x:x, y:Math.round(r.y), yy:y, h:Math.round(r.height), vh:window.innerHeight,
      dlm:(r.top>=0 && r.bottom<=window.innerHeight),
      penghalang: t?(t===b||b.contains(t)?null:(t.tagName+'.'+(t.className||''))):'TIADA',
      bolehTekan: !!(t&&(t===b||b.contains(t))) }; })()`;

  // nama butang yang guru betul-betul perlu
  const BUTANG = [
    ['delimaGoogleBtn', 'Log Masuk dengan ID DELIMa (Google)'],
    ['btnMasukSetempat', 'Masuk (setempat)'],
    ['btnDaftarGuruBaharu', 'Guru baharu? Daftar'],
  ];

  for (const [w, h, nama] of [[360, 640, 'telefon kecil 360x640'], [390, 844, 'telefon biasa 390x844'], [412, 915, 'telefon besar 412x915'], [360, 780, 'telefon pendek 360x780']]) {
    await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 2, mobile: true });
    await send('Page.navigate', { url: TEST_URL }); await tidur(2400);
    await ev("try{localStorage.clear();sessionStorage.clear()}catch(e){}; 'ok'");
    await send('Page.navigate', { url: TEST_URL }); await tidur(3000);
    await ev("window.confirm=function(){return true}; window.print=function(){}; 'ok'");
    for (const [el, label] of BUTANG) {
      const g = await ev(GEO(el));
      ok(`${nama}: "${label}" kelihatan + boleh ditekan`,
        g.ada === true && g.dlm === true && g.bolehTekan === true,
        `y=${g.y} h=${g.h} vh=${g.vh} penghalang=${g.penghalang || 'tiada'}`);
    }
    // tombak: klik SEBENAR pada "Guru baharu?" mesti buka skrin daftar
    await tidur(600);                                  // beri gerbang masa stabil
    const g2 = await ev(GEO('btnDaftarGuruBaharu'));
    if (g2.ada && g2.bolehTekan) {
      await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: g2.x, y: g2.y });   // seperti jari mendarat
      await tidur(150);
      await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: g2.x, y: g2.y, button: 'left', clickCount: 1, buttons: 1 });
      await tidur(120);
      await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: g2.x, y: g2.y, button: 'left', clickCount: 1, buttons: 0 });
      await tidur(900);
      const d = await ev("(function(){var o=document.getElementById('appModalOverlay');return {papar:o?o.style.display:'(tiada)', medan:!!document.getElementById('daftarEmel')};})()");
      ok(`${nama}: KLIK "Guru baharu?" -> skrin daftar terbuka`, d.papar === 'flex' && d.medan === true, `papar=${d.papar}`);
    }
  }
  await send('Emulation.clearDeviceMetricsOverride');
  ok('tiada ralat JS sepanjang ujian gerbang', errors.length === 0, errors.slice(0, 2).join(' | ') || '0 ralat');

  console.log('\n===== SEMUA BUTANG GERBANG (klik sebenar) =====');
  console.log('URL: ' + TEST_URL);
  console.log(out.join('\n'));
  console.log(`\nRingkasan: ${out.length - fail}/${out.length} PASS`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(2); });
