/* ujian_masuk.js — bukti "jalan masuk SENANG" (F24) melalui chromium headless + CDP
   Guna: TEST_URL=http://127.0.0.1:8899/index.html CDP_PORT=9338 node ujian_masuk.js
   Fokus: guru yang DAH ada akaun -> berapa banyak langkah untuk masuk semula. */
const http = require('http');
const TEST_URL = process.env.TEST_URL || 'https://sepora-rbt-toolkit.vercel.app/index.html';
const PORT = Number(process.env.CDP_PORT || 9338);
const out = []; let fail = 0;
const ok = (nama, lulus, info) => { out.push((lulus ? '  PASS ' : '  FAIL ') + nama + (info ? '  [' + info + ']' : '')); if (!lulus) fail++; };
const tidur = ms => new Promise(r => setTimeout(r, ms));
const get = url => new Promise((res, rej) => http.get(url, r => { let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d))); }).on('error', rej));
const FMT = p => encodeURIComponent(JSON.stringify({ metod: 'Runtime.callFunctionOn', params: p }));

(async () => {
  const tapak = m => console.log('[jejak] ' + m);
  tapak('mula');
  let page = null;
  for (let i = 0; i < 40 && !page; i++) {
    try { const l = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json(); page = l.find(t => t.type === 'page'); } catch (e) { }
    if (!page) await tidur(500);
  }
  if (!page) throw new Error('tiada target CDP pada ' + PORT);
  tapak('target dijumpai');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let id = 0; const tunggu = new Map(); const errors = [];
  ws.onmessage = e => {
    const d = JSON.parse(e.data);
    if (d.id && tunggu.has(d.id)) { const w = tunggu.get(d.id); tunggu.delete(d.id); w(d); }
    if (d.method === 'Runtime.exceptionThrown') errors.push(((d.params.exceptionDetails.exception || {}).description) || d.params.exceptionDetails.text || 'exception');
    if (d.method === 'Runtime.consoleAPICalled' && d.params.type === 'error') errors.push(d.params.args.map(a => a.value || a.description || '').join(' '));
  };
  const send = (method, params = {}) => new Promise(res => { const i = ++id; tunggu.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
  tapak('ws terbuka');
  await send('Runtime.enable'); await send('Page.enable');
  tapak('runtime hidup');
  const ev = async (expr, await_ = true) => {
    const r = await Promise.race([
      send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: await_ }),
      tidur(15000).then(() => ({ __timeout: true }))
    ]);
    if (r.__timeout) throw new Error('ev() TIMEOUT (15s): ' + expr.slice(0, 100));
    if (r && r.result && r.result.exceptionDetails) {
      const d = r.result.exceptionDetails;
      throw new Error(d.text + ' :: ' + ((d.exception || {}).description || '') + ' :: ' + expr.slice(0, 120));
    }
    return r.result.result.value;
  };
  const nav = async (ms = 2800) => {
    await send('Page.navigate', { url: TEST_URL });
    await tidur(ms);
    try { await send('Runtime.evaluate', { expression: "window.confirm=function(){return true}; window.print=function(){}; 'ok'", returnByValue: true }); } catch (e) { }
  };

  await nav();
  tapak('muat pertama');
  await ev("try{localStorage.clear();sessionStorage.clear()}catch(e){}; window.confirm=function(){return true}; window.print=function(){}; 'ok'");
  await nav();

  /* ---- K00: diagnosa halaman (kalau elemen hilang -> tahu sebabnya) ---- */
  // keadaan "peranti BAHARU": SAPU semua storan + muat semula (tiada kredensial tersimpan)
  await ev("try{localStorage.clear();sessionStorage.clear()}catch(e){}; 'ok'");
  await nav();
  const diag = await ev(`(function(){ return { url: location.href, sedia: document.readyState,
      gerbangAda: !!document.getElementById('privacyLockScreen'),
      pantasAda: !!document.getElementById('btnMasukPantas'),
      masukAda: !!document.getElementById('btnMasukSetempat'),
      pendaftarAda: !!document.getElementById('btnDaftarGuruBaharu'),
      tajuk: document.title, panjangBody: (document.body ? document.body.innerHTML.length : -1) }; })()`);
  ok('K00 halaman dimuat sepenuhnya (gerbang + butang baharu wujud)',
    diag.gerbangAda === true && diag.pantasAda === true && diag.masukAda === true, JSON.stringify(diag));

  /* ---- K01: gerbang TIDAK lagi membuka skrin daftar sendiri ---- */
  const gerbang = await ev(`(function(){ var b=document.getElementById('btnMasukPantas'), o=document.getElementById('appModalOverlay');
      return { modal: o ? o.style.display : '(tiada)',
      daftarBtn: !!document.getElementById('btnMasukSetempat'),
      pantas: !!b,
      pantasTunjuk: b ? !b.classList.contains('hidden') : false }; })()`);
  ok('K01 gerbang bersih: skrin daftar TIDAK dibuka automatik + butang masuk besar ada',
    gerbang.modal !== 'flex' && gerbang.daftarBtn === true, `modal=${gerbang.modal || '(tutup)'}`);

  /* ---- K02: guru baharu (tiada kredensial) TIDAK nampak "masuk pantas" ---- */
  ok('K02 peranti baharu: butang "Masuk pantas" TIDAK muncul (tiada kredensial tersimpan)',
    gerbang.pantasTunjuk === false, `tunjuk=${gerbang.pantasTunjuk}`);

  /* ---- K03: daftar guru baharu (laluan normal) ---- */
  const daftar = await ev(`(async function(){ openDaftarModal(true, true);
    document.getElementById('daftarNama').value = 'Cikgu Ujian';
    document.getElementById('daftarEmel').value = 'g-43210000';
    document.getElementById('daftarPin').value = '778899';
    await submitDaftarLocal({ preventDefault: function(){} });
    return { masuk: document.getElementById('privacyLockScreen').classList.contains('hidden'),
             emel: (getSession()||{}).email }; })()`);
  ok('K03 daftar guru baharu terus masuk (ID DELIMa sahaja pun boleh)',
    daftar.masuk === true && daftar.emel === 'g-43210000@moe-dl.edu.my', `emel=${daftar.emel}`);

  /* ---- K04: log keluar -> bentuk log masuk TERBUKA + medan TERISI + butang pantas MUNCUL ---- */
  await ev("logoutSession(); 'ok'");
  const keluar = await ev(`(function(){ return { gerbang: !document.getElementById('privacyLockScreen').classList.contains('hidden'),
      formTerbuka: !document.getElementById('delimaLocalForm').classList.contains('hidden'),
      emel: document.getElementById('loginInputEmail').value,
      pantasTunjuk: !document.getElementById('btnMasukPantas').classList.contains('hidden') }; })()`);
  ok('K04 selepas log keluar: borang log masuk terus TERBUKA + emel terisi (tak perlu tekan apa-apa)',
    keluar.gerbang === true && keluar.formTerbuka === true && keluar.emel === 'g-43210000@moe-dl.edu.my', `emel=${keluar.emel} form=${keluar.formTerbuka}`);
  ok('K04b butang "Masuk pantas (akaun ini)" muncul untuk akaun sendiri', keluar.pantasTunjuk === true);

  /* ---- K05: SATU TEKANAN = masuk semula (butang pantas) ---- */
  await ev("masukPantas(); 'dipanggil'");
  await tidur(1500);
  const pantas = await ev(`(function(){ return { masuk: document.getElementById('privacyLockScreen').classList.contains('hidden'),
             toser: (document.getElementById('toastContainer')||{innerText:''}).innerText.slice(0,80) }; })()`);
  ok('K05 MASUK SEMULA dengan SATU tekanan butang (tanpa taip emel/PIN sekali pun)',
    pantas.masuk === true, `toast=${pantas.toser.replace(/\s+/g,' ')}`);

  /* ---- K06: butang "Masuk" besar pada borang benar-benar berfungsi ---- */
  await ev("logoutSession(); 'ok'");
  await ev(`(function(){ authCredentials = JSON.parse(localStorage.getItem('erph_auth_cred'));
    document.getElementById('loginInputEmail').value = authCredentials.email;
    document.getElementById('loginInputPassword').value = '778899';  // guru taip PIN, tekan "Masuk"
    return 'ok'; })()`);
  await ev("masukSetempat(); 'dipanggil'");
  await tidur(1500);
  const besar = await ev("document.getElementById('privacyLockScreen').classList.contains('hidden')");
  ok('K06 butang besar "Masuk" berfungsi (bukan butang mati)', besar === true);

  /* ---- K07: "Lupa PIN?" -> skrin daftar (jalan sebenar) ---- */
  await ev("logoutSession(); 'ok'");
  const lupa = await ev(`(function(){ bukaBantuanPin({preventDefault:function(){}});
    return { modal: document.getElementById('appModalOverlay').style.display,
             daftar: ((document.getElementById('modalBoxContent')||{innerText:''}).innerText||'').indexOf('Pilihan B') > -1 }; })()`);
  ok('K07 "Lupa PIN?" membuka skrin daftar (laluan pulih, bukan hanya mesej)', lupa.modal === 'flex' && lupa.daftar === true);
  await ev("closeModalDirectly(); 'ok'");

  /* ---- K08: bentuk log masuk kekal TERBUKA pada setiap kunjungan (satu tekaan kurang) ---- */
  await nav();
  const lepasMuat = await ev(`(function(){ return { formTerbuka: !document.getElementById('delimaLocalForm').classList.contains('hidden'),
      emel: document.getElementById('loginInputEmail').value, pantas: !document.getElementById('btnMasukPantas').classList.contains('hidden') }; })()`);
  ok('K08 buka semula app: borang terus terbuka + emel terisi + butang pantas ada',
    lepasMuat.formTerbuka === true && lepasMuat.emel === 'g-43210000@moe-dl.edu.my' && lepasMuat.pantas === true,
    `form=${lepasMuat.formTerbuka} emel=${lepasMuat.emel}`);

  /* ---- K09: kunci skrin sengaja = laluan pantas DIMATIKAN (privasi kekal) ---- */
  await ev("masukPantas(); 'ok'"); await tidur(900);
  await ev("lockAppScreen(); 'ok'"); await tidur(400);
  const kunci = await ev(`(function(){ return { pantasTunjuk: !document.getElementById('btnMasukPantas').classList.contains('hidden'),
      gerbang: !document.getElementById('privacyLockScreen').classList.contains('hidden'),
      kerja: !!document.getElementById('loginInputEmail') }; })()`);
  ok('K09 skrin dikunci sengaja: tiada butang pantas (mesti taip PIN) - privasi tidak dikorbankan',
    kunci.pantasTunjuk === false && kunci.gerbang === true);

  /* ---- K10: akaun LALAI (kongsi) TIDAK mendapat butang pantas ---- */
  await ev(`(function(){ localStorage.removeItem('erph_daftar_selesai');
    var k = { email: DEFAULT_AUTH.email, password: DEFAULT_AUTH.password };
    localStorage.setItem('erph_auth_cred', JSON.stringify(k));
    authCredentials = k; return 'ok'; })()`);
  await nav();
  const lalai = await ev(`(async function(){ document.getElementById('loginInputEmail').value = 'muhammad.wafi@moe-dl.edu.my';
    document.getElementById('loginInputPassword').value = '1234';
    await handleLoginSubmit({preventDefault:function(){}});
    return { masuk: document.getElementById('privacyLockScreen').classList.contains('hidden'),
             pantas: !document.getElementById('btnMasukPantas').classList.contains('hidden') }; })()`);
  ok('K10a PIN lalai 4 aksara masih diterima (log masuk sedia ada tidak dipecahkan)', lalai.masuk === true);
  ok('K10b akaun LALAI (kongsi) TIDAK memaparkan butang "Masuk pantas" (OPSEC)', lalai.pantas === false);

  /* ---- K11: profil tidak lagi mendedahkan PIN ---- */
  const prof = await ev(`(function(){ openProfileModal();
    const f = document.getElementById('modalAuthPassword');
    const r = { jenis: f.type, nilai: f.value, adaPapar: !!document.getElementById('modalPaparPin') }; closeModalDirectly(); return r; })()`);
  ok('K11 modal profil: medan PIN KOSONG + jenis password (PIN tidak lagi dipaparkan)',
    prof.nilai === '' && prof.jenis === 'password' && prof.adaPapar === true, `jenis=${prof.jenis} nilai='${prof.nilai}'`);

  /* ---- K12: profil (nama/sekolah sahaja) TIDAK lagi jadi kebuntuan ---- */
  const simpanProf = await ev(`(async function(){ openProfileModal();
    document.getElementById('modalTeacherSchool').value = 'SK Poring';
    document.getElementById('modalAuthPassword').value = '';
    await submitTeacherProfile({preventDefault:function(){}});
    return { modal: document.getElementById('appModalOverlay').style.display,
             toser: (document.getElementById('toastContainer')||{innerText:''}).innerText.replace(/\\s+/g,' ').slice(0,90) }; })()`);
  ok('K12 simpan profil tanpa mengisi PIN: berjaya (tiada ralat "Isi KEDUA-DUA")',
    simpanProf.modal !== 'flex' && simpanProf.toser.indexOf('KEDUA-DUA') === -1, `toast=${simpanProf.toser}`);

  /* ---- K13: tiada ralat JS / CSP sepanjang ujian masuk ---- */
  ok('K13 tiada ralat JS sepanjang ujian jalan masuk', errors.length === 0, errors.slice(0, 3).join(' | ') || '0 ralat');

  console.log('\n===== UJIAN JALAN MASUK SENANG (F24) =====');
  console.log('URL: ' + TEST_URL);
  console.log(out.join('\n'));
  console.log(`\nRingkasan: ${out.length - fail}/${out.length} PASS`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(2); });
