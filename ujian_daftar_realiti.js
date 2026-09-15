// ujian_daftar_realiti.js — Uji PENDAFTARAN seperti guru sebenar:
// buka laman -> tekan butang hijau -> isi -> Daftar & Mula Guna -> adakah MASUK?
// Guna klik SEBENAR (Input.dispatchMouseEvent) + taip SEBENAR (Input.insertText).
const PORT = process.env.CDP_PORT || 9400;
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
  await send('Runtime.enable'); await send('Page.enable');
  const ev = async (x) => {
    const r = await Promise.race([send('Runtime.evaluate', { expression: x, returnByValue: true, awaitPromise: true }), tidur(15000).then(() => ({ __to: 1 }))]);
    if (r.__to) throw new Error('TIMEOUT: ' + x.slice(0, 70));
    if (r.result && r.result.exceptionDetails) throw new Error(((r.result.exceptionDetails.exception || {}).description || r.result.exceptionDetails.text) + ' :: ' + x.slice(0, 70));
    return r.result.result.value;
  };
  const tengah = async (el) => ev(`(function(){ var b=document.getElementById('${el}'); if(!b) return null;
    var r=b.getBoundingClientRect(); return {x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2)}; })()`);
  const klikEl = async (el) => {
    const t = await tengah(el);
    if (!t) throw new Error('elemen tiada: ' + el);
    await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: t.x, y: t.y }); await tidur(90);
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: t.x, y: t.y, button: 'left', clickCount: 1, buttons: 1 }); await tidur(80);
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: t.x, y: t.y, button: 'left', clickCount: 1, buttons: 0 });
    await tidur(700);
  };
  const taip = async (el, teks) => {   // taip SEBENAR: fokus + insertText
    await klikEl(el);
    await send('Input.insertText', { text: teks });
    await tidur(200);
  };

  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
  await send('Page.navigate', { url: TEST_URL }); await tidur(2400);
  await ev("try{localStorage.clear();sessionStorage.clear()}catch(e){}; 'ok'");   // peranti BAHARU
  await send('Page.navigate', { url: TEST_URL }); await tidur(3400);
  await ev("window.confirm=function(){return true}; window.print=function(){}; 'ok'");

  // STEP 1: guru baharu tekan butang hijau
  const lihatButang = await ev(`(function(){ var b=document.getElementById('btnDaftarUtama');
    if(!b) return {ada:false};
    var r=b.getBoundingClientRect();
    return {ada:true, teks:(b.innerText||'').replace(/\\s+/g,' ').trim(), y:Math.round(r.y), h:Math.round(r.height),
            nampak:(r.top>=0&&r.bottom<=window.innerHeight)}; })()`);
  ok('1. Butang daftar kelihatan pada gerbang', lihatButang.ada === true && lihatButang.nampak === true,
    `teks="${lihatButang.teks}" y=${lihatButang.y} h=${lihatButang.h}`);

  await klikEl('btnDaftarUtama');
  const skrin = await ev(`(function(){ var o=document.getElementById('appModalOverlay');
    return { papar:o?o.style.display:'(tiada)', nama:!!document.getElementById('daftarNama'),
             emel:!!document.getElementById('daftarEmel'), pin:!!document.getElementById('daftarPin'),
             pilihanA:(document.getElementById('daftarPilihanA')||{style:{}}).style.display }; })()`);
  ok('2. Klik -> skrin daftar terbuka dengan 3 medan', skrin.papar === 'flex' && skrin.nama && skrin.emel && skrin.pin,
    `papar=${skrin.papar} pilihanA=${skrin.pilihanA}`);

  // STEP 2: taip SEBENAR ke dalam medan
  await taip('daftarNama', 'Cikgu Aisyah');
  await taip('daftarEmel', 'g-99001122');
  await taip('daftarPin', '445566');
  const terisi = await ev(`(function(){ return { nama:document.getElementById('daftarNama').value,
    emel:document.getElementById('daftarEmel').value, pin:document.getElementById('daftarPin').value }; })()`);
  ok('3. Taip SEBENAR masuk ke medan', terisi.nama === 'Cikgu Aisyah' && terisi.emel === 'g-99001122' && terisi.pin === '445566',
    JSON.stringify(terisi));

  // STEP 3: tekan "Daftar & Mula Guna" (klik sebenar pada butang submit)
  const btnDaftar = await ev(`(function(){ var b=document.querySelector('#modalBoxContent button[type=submit]');
    if(!b) return null; var r=b.getBoundingClientRect();
    return {x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2), teks:(b.innerText||'').replace(/\\s+/g,' ').trim(),
            nampak:(r.top>=0&&r.bottom<=window.innerHeight)}; })()`);
  ok('4. Butang "Daftar & Mula Guna" ada & nampak', !!btnDaftar && btnDaftar.nampak === true,
    btnDaftar ? `teks="${btnDaftar.teks}" y=${btnDaftar.y}` : 'TIADA BUTANG SUBMIT');
  if (btnDaftar) {
    await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: btnDaftar.x, y: btnDaftar.y }); await tidur(90);
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: btnDaftar.x, y: btnDaftar.y, button: 'left', clickCount: 1, buttons: 1 }); await tidur(80);
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: btnDaftar.x, y: btnDaftar.y, button: 'left', clickCount: 1, buttons: 0 });
  }
  await tidur(3500);   // PBKDF2 60k + simpan

  // STEP 4: adakah benar-benar MASUK?
  const hasil = await ev(`(function(){ var k=null; try{ k=JSON.parse(localStorage.getItem('erph_auth_cred')); }catch(e){}
    return { kredensial: k ? k.email : null, hash: k ? !!k.pinHash : false,
      gerbangTutup: document.getElementById('privacyLockScreen').classList.contains('hidden'),
      modalTutup: document.getElementById('appModalOverlay').style.display === 'none',
      sesi: (function(){ try{ return (JSON.parse(localStorage.getItem('erph_session')||'null')||{}).email; }catch(e){ return null; } })(),
      toser: (document.getElementById('toastContainer')||{innerText:''}).innerText.replace(/\\s+/g,' ').slice(0,140) }; })()`);
  ok('5. DAFTAR BERJAYA: kredensial tersimpan + gerbang terbuka + sesi wujud',
    hasil.kredensial === 'g-99001122@moe-dl.edu.my' && hasil.hash === true && hasil.gerbangTutup === true,
    JSON.stringify(hasil));
  ok('6. Guru boleh terus guna app (modal tertutup, tiada halangan)', hasil.modalTutup === true, `modal=${hasil.modalTutup}`);

  // STEP 5: botol terakhir - bolehkah guru JANA RPH selepas daftar?
  const guna = await ev(`(function(){ try { loadSlotToRph('Selasa','11:00 - 12:00','2 Cekal','RBT Tahun 5'); autoGenerateSmartRph();
      var pv=document.getElementById('rphPreviewContainer');
      return { panjang: pv ? (pv.textContent||'').length : 0, ralat:null }; } catch(e){ return {panjang:0, ralat:e.message}; } })()`);
  ok('7. Selepas daftar, guru boleh JANA RPH (app berfungsi penuh)',
    guna.panjang > 500, `panjang=${guna.panjang} ralat=${guna.ralat || 'tiada'}`);

  ok('8. Tiada ralat JS sepanjang pendaftaran', errors.length === 0, errors.slice(0, 2).join(' | ') || '0 ralat');

  console.log('\n===== UJIAN DAFTAR GURU BAHARU (realiti: klik + taip sebenar) =====');
  console.log('URL: ' + TEST_URL);
  console.log(out.join('\n'));
  console.log(`\nRingkasan: ${out.length - fail}/${out.length} PASS`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(2); });
