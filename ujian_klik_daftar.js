// ujian_klik_daftar.js — klik SEBENAR pada butang "Guru baharu?" (Input.dispatchMouseEvent),
// termasuk pada skrin rendah, untuk sahkan guru benar-benar boleh masuk ke skrin daftar.
const PORT = process.env.CDP_PORT || 9350;
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
  let id = 0; const tunggu = new Map();
  ws.onmessage = e => { const d = JSON.parse(e.data); if (d.id && tunggu.has(d.id)) { const w = tunggu.get(d.id); tunggu.delete(d.id); w(d); } };
  const send = (m, p = {}) => new Promise(res => { const i = ++id; tunggu.set(i, res); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  await send('Runtime.enable'); await send('Page.enable');
  const ev = async (x, aw = true) => {
    const r = await Promise.race([send('Runtime.evaluate', { expression: x, returnByValue: true, awaitPromise: aw }), tidur(15000).then(() => ({ __to: 1 }))]);
    if (r.__to) throw new Error('TIMEOUT ev: ' + x.slice(0, 80));
    if (r.result && r.result.exceptionDetails) throw new Error(((r.result.exceptionDetails.exception || {}).description || r.result.exceptionDetails.text) + ' :: ' + x.slice(0, 80));
    return r.result.result.value;
  };
  const nav = async (ms = 3000) => { await send('Page.navigate', { url: TEST_URL }); await tidur(ms); };

  // setiap saiz skrin: guru baharu pada telefon kecil, sederhana, besar
  for (const [lebar, tinggi, nama] of [[360, 640, 'telefon kecil 360x640'], [390, 844, 'telefon biasa 390x844'], [980, 344, 'skrin sangat rendah 980x344']]) {
    await send('Emulation.setDeviceMetricsOverride', { width: lebar, height: tinggi, deviceScaleFactor: 2, mobile: lebar < 900 });
    await nav(2200);
    await ev("try{localStorage.clear();sessionStorage.clear()}catch(e){}; 'ok'");
    await nav(2600);
    await ev("window.confirm=function(){return true}; window.print=function(){}; 'ok'");

    // kedudukan butang + apa yang ada di titik tengahnya (adakah boleh ditekan?)
    const geo = await ev(`(function(){ var b = document.getElementById('btnDaftarGuruBaharu'); if(!b) return {ada:false};
      var r = b.getBoundingClientRect();
      var x = Math.round(r.x + r.width/2), y = Math.round(r.y + r.height/2);
      var el = document.elementFromPoint(x, y);
      return { ada:true, x:x, y:y, lebar:Math.round(r.width), tinggi:Math.round(r.height),
        dlmPandangan:(r.top>=0 && r.bottom<=window.innerHeight), vh:window.innerHeight,
        penghalang: el ? (el===b || b.contains(el) ? null : (el.tagName + '.' + (el.className||''))) : 'TIADA',
        bolehTekan: !!(el && (el===b || b.contains(el))) }; })()`);
    ok(`KLIK ${nama}: butang "Guru baharu?" nampak & boleh ditekan`, geo.ada === true && geo.bolehTekan === true,
      `x=${geo.x} y=${geo.y} vh=${geo.vh} penghalang=${geo.penghalang || 'tiada'}`);

    if (geo.ada && geo.bolehTekan) {
      // KLIK SEBENAR dengan jari (mouse event pada koordinat skrin)
      await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: geo.x, y: geo.y, button: 'left', clickCount: 1 });
      await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: geo.x, y: geo.y, button: 'left', clickCount: 1 });
      await tidur(700);
      const hasil = await ev(`(function(){ var ov = document.getElementById('appModalOverlay'), m = document.getElementById('modalBoxContent');
        var t = m ? (m.innerText||'') : '';
        return { papar: ov ? ov.style.display : '(tiada)', pilihanB: t.indexOf('Guna tanpa Google') > -1,
                 adaMedan: !!document.getElementById('daftarEmel'), adaBtn: !!document.getElementById('btnDaftarGuruBaharu') }; })()`);
      ok(`KLIK ${nama}: SKRIN DAFTAR terbuka + medan sedia diisi`,
        hasil.papar === 'flex' && hasil.pilihanB === true && hasil.adaMedan === true,
        `papar=${hasil.papar} pilihanB=${hasil.pilihanB} medan=${hasil.adaMedan}`);
    }
  }
  await send('Emulation.clearDeviceMetricsOverride');
  console.log('\n===== KLIK SEBENAR BUTANG "GURU BAHARU?" =====');
  console.log('URL: ' + TEST_URL);
  console.log(out.join('\n'));
  console.log(`\nRingkasan: ${out.length - fail}/${out.length} PASS`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(2); });
