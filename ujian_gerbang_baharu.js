// ujian_gerbang_baharu.js — SAHKAN guru baharu boleh masuk dalam SATU langkah jelas.
// Fokus: adakah butang "Saya guru BAHARU - Daftar sekarang" kelihatan, boleh ditekan,
// dan membuka borang yang boleh terus diisi + daftar BERJAYA.
const PORT = process.env.CDP_PORT || 9390;
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
  if (!page) throw new Error('tiada target CDP pada ' + PORT);
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
    return { ada:true, x:x, yy:y, y:Math.round(r.y), h:Math.round(r.height), vh:window.innerHeight,
      nampak:(r.top>=0 && r.bottom<=window.innerHeight) && r.height>5,
      penghalang: t?(t===b||b.contains(t)?null:(t.tagName+'.'+(t.className||'').slice(0,20))):'TIADA',
      bolehTekan: !!(t&&(t===b||b.contains(t))) }; })()`;
  const klik = async (g) => {
    await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: g.x, y: g.yy });
    await tidur(120);
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: g.x, y: g.yy, button: 'left', clickCount: 1, buttons: 1 });
    await tidur(100);
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: g.x, y: g.yy, button: 'left', clickCount: 1, buttons: 0 });
    await tidur(800);
  };

  for (const [w, h, nama] of [[360, 640, 'kecil 360x640'], [390, 844, 'biasa 390x844'], [360, 780, 'pendek 360x780']]) {
    await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 2, mobile: true });
    await send('Page.navigate', { url: TEST_URL }); await tidur(2400);
    await ev("try{localStorage.clear();sessionStorage.clear()}catch(e){}; 'ok'");
    await send('Page.navigate', { url: TEST_URL }); await tidur(3200);
    await ev("window.confirm=function(){return true}; window.print=function(){}; 'ok'");

    // 1) guru BAHARU: butang daftar mesti nampak + boleh tekan
    const bd = await ev(GEO('btnDaftarUtama'));
    ok(`${nama}: butang "Saya guru BAHARU - Daftar sekarang" nampak + boleh ditekan`,
      bd.ada === true && bd.nampak === true && bd.bolehTekan === true,
      `y=${bd.y} h=${bd.h} vh=${bd.vh} penghalang=${bd.penghalang || 'tiada'}`);

    // 2) butang lama tidak lagi mengelirukan
    const blama = await ev("(function(){var b=document.getElementById('btnDaftarGuruBaharu');return b?b.classList.contains('hidden'):true})()");
    ok(`${nama}: butang lama "Guru baharu?" tidak lagi ditunjuk (tiada butang bertindih)`, blama === true);

    // 3) klik sebenar -> skrin daftar terbuka + Pilihan B tersedia
    if (bd.ada && bd.bolehTekan) {
      await klik(bd);
      const d = await ev(`(function(){ var o=document.getElementById('appModalOverlay'); var pa=document.getElementById('daftarPilihanA');
        return { papar:o?o.style.display:'(tiada)', medan:!!document.getElementById('daftarEmel'),
                 pilihanA: pa ? pa.style.display : 'tiada' }; })()`);
      ok(`${nama}: KLIK butang daftar -> skrin daftar terbuka (medan Pilihan B sedia)`,
        d.papar === 'flex' && d.medan === true, `papar=${d.papar} pilihanA=${d.pilihanA}`);
      ok(`${nama}: Pilihan A (Google belum aktif) TIDAK ditunjuk (elak guru keliru)`, d.pilihanA === 'none');

      // 4) isi + daftar -> mesti BERJAYA masuk
      await ev(`(function(){ document.getElementById('daftarNama').value='Guru Baharu Ujian';
        document.getElementById('daftarEmel').value='g-88001100';
        document.getElementById('daftarPin').value='445566'; return 'ok'; })()`);
      await ev("submitDaftarLocal({ preventDefault: function(){} }); 'dihantar'");
      await tidur(2600);
      const hasil = await ev(`(function(){ var k=JSON.parse(localStorage.getItem('erph_auth_cred')||'null');
        return { ada:!!k, emel:k?k.email:null, gerbangTutup:document.getElementById('privacyLockScreen').classList.contains('hidden') }; })()`);
      ok(`${nama}: guru baharu DAFTAR -> terus MASUK (kredensial tersimpan + gerbang buka)`,
        hasil.ada === true && hasil.emel === 'g-88001100@moe-dl.edu.my' && hasil.gerbangTutup === true, JSON.stringify(hasil));
    }
  }
  await send('Emulation.clearDeviceMetricsOverride');
  ok('tiada ralat JS sepanjang ujian guru baharu', errors.length === 0, errors.slice(0, 2).join(' | ') || '0 ralat');

  console.log('\n===== UJIAN GERBANG GURU BAHARU (F28) =====');
  console.log('URL: ' + TEST_URL);
  console.log(out.join('\n'));
  console.log(`\nRingkasan: ${out.length - fail}/${out.length} PASS`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(2); });
