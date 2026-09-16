// ujian_sandaran_manual.js — sahkan sandaran MANUAL (Eksport/Import JSON) berfungsi
// sebagai ganti sandaran Drive ketika Client ID belum dipasang.
const PORT = process.env.CDP_PORT || 9410;
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
  const nav = async (ms = 3000) => { await send('Page.navigate', { url: TEST_URL }); await tidur(ms); };

  await nav(); await ev("try{localStorage.clear();sessionStorage.clear()}catch(e){}; 'ok'"); await nav();
  await ev("window.confirm=function(){return true}; window.print=function(){}; 'ok'");

  // 1) butang Drive TERSEMBUNYI (Client ID kosong) + nota ganti TAMPIL
  const ui = await ev(`(function(){ var a=document.getElementById('driveActions'), n=document.getElementById('driveGantiNota');
    return { aksi:a?a.style.display:'tiada', nota:n?n.style.display:'tiada',
             clientId:(function(){ try{ return gdriveClientId()||'(kosong)'; }catch(e){ return 'ralat'; } })() }; })()`);
  ok('1. Butang Drive tersembunyi bila Client ID kosong (tiada butang mati)',
    ui.aksi === 'none' && ui.clientId === '(kosong)', `aksi=${ui.aksi} clientId=${ui.clientId}`);
  ok('2. Nota ganti (Eksport Arkib JSON) ditunjuk kepada guru', ui.nota === '', `nota=${ui.nota}`);

  // 3) guru guna app: jana + simpan RPH
  await ev("openDaftarModal(true,true); 'ok'");
  await ev(`(function(){ document.getElementById('daftarNama').value='Cikgu Sandaran';
    document.getElementById('daftarEmel').value='g-31415926'; document.getElementById('daftarPin').value='556677'; return 'ok'; })()`);
  await ev("submitDaftarLocal({preventDefault:function(){}}); 'dihantar'");
  await tidur(2600);
  await ev("loadSlotToRph('Selasa','11:00 - 12:00','2 Cekal','RBT Tahun 5'); autoGenerateSmartRph(); saveCurrentGeneratedRph(); 'ok'");
  const bil = await ev("(savedRphList||[]).length");
  ok('3. Guru daftar + jana + simpan RPH', bil >= 1, `rekod=${bil}`);

  // 4) EKSPORT ARKIB JSON - tangkap blob sebenar
  const eksport = await ev(`(async function(){ const asalUrl=URL.createObjectURL, asalKlik=HTMLAnchorElement.prototype.click;
    let blob=null, nama='', ralat='';
    URL.createObjectURL=function(b){ blob=b; return asalUrl.call(URL,b); };
    HTMLAnchorElement.prototype.click=function(){ nama=this.download||nama; };
    try { exportArkibJson(); } catch(e){ ralat=String(e.message); }
    for (let i=0;i<30 && !blob;i++) await new Promise(r=>setTimeout(r,200));
    URL.createObjectURL=asalUrl; HTMLAnchorElement.prototype.click=asalKlik;
    if(!blob) return { adaBlob:false, nama:nama, ralat:ralat };
    const teks = await blob.text();
    let data=null; try{ data=JSON.parse(teks); }catch(e){}
    return { adaBlob:true, saiz:blob.size, nama:nama, sah:!!data,
             bil:(data&&(data.rekod||data.arkib||[]).length)||0,
             jenisBlob:blob.type||'(tiada)' }; })()`);
  ok('4. Eksport Arkib (JSON) menghasilkan fail sah (boleh dibuka guru)',
    eksport.adaBlob === true && eksport.sah === true && eksport.saiz > 200,
    `saiz=${eksport.saiz} nama=${eksport.nama} rekod=${eksport.bil}`);

  // 5) IMPORT semula (simulasi guru tukar telefon): padam arkib, import, pastikan pulih
  const sebelumPadam = await ev("(savedRphList||[]).length");
  await ev(`(function(){ const arkibAsal = JSON.stringify({ app:'SEPORA RBT TOOLKIT', jenis:'arkib-rph', versi:2, rekod: savedRphList });
    window.__arkibUji = arkibAsal;
    try { localStorage.removeItem(arkibKey()); } catch(e){}
    savedRphList = []; renderSavedRphTable(); updateArkibBadge();
    return 'ok'; })()`);
  const kosong = await ev("(savedRphList||[]).length");
  // guna laluan import app sebenar (FileReader async -> tunggu sampai arkib terisi)
  await ev(`(function(){ const f = new File([window.__arkibUji], 'uji.json', { type:'application/json' });
    importArkibJson({ target: { files: [f], value: '' } });
    return 'dihantar'; })()`);
  let dipulihkan = 0;
  for (let i = 0; i < 30 && dipulihkan === 0; i++) {
    await tidur(300);
    dipulihkan = await ev("(savedRphList||[]).length");
  }
  const kekal = await ev("(function(){ try{ const k=arkibKey(); return JSON.parse(localStorage.getItem(k)||'[]').length; }catch(e){ return -1; } })()");
  ok('5. Import Arkib (JSON) memulihkan RPH selepas arkib dipadam (kes tukar telefon)',
    kosong === 0 && dipulihkan === sebelumPadam && kekal === sebelumPadam,
    `sebelum=${sebelumPadam} kosong=${kosong} dipulihkan=${dipulihkan} dlmStoran=${kekal}`);

  // 6) bila Client ID DISET, butang Drive mesti muncul semula
  const aktif = await ev(`(function(){ try { localStorage.setItem('erph_gdrive_clientid','1234567890-uji.apps.googleusercontent.com'); } catch(e){}
    kemasKiniDriveUI(); kemasKiniButangGoogle();
    var a=document.getElementById('driveActions'), n=document.getElementById('driveGantiNota'), g=document.getElementById('delimaGoogleBtn');
    return { aksi:a.style.display, nota:n.style.display, googleNampak: g ? !g.classList.contains('hidden') : false }; })()`);
  ok('6. Bila Client ID diset: butang Drive + butang Google muncul semula (auto)',
    aktif.aksi === '' && aktif.nota === 'none' && aktif.googleNampak === true, JSON.stringify(aktif));

  ok('7. Tiada ralat JS sepanjang ujian sandaran manual', errors.length === 0, errors.slice(0, 2).join(' | ') || '0 ralat');

  console.log('\n===== UJIAN SANDARAN MANUAL (ganti Drive) =====');
  console.log('URL: ' + TEST_URL);
  console.log(out.join('\n'));
  console.log(`\nRingkasan: ${out.length - fail}/${out.length} PASS`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(2); });
