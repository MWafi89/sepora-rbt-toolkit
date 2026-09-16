// ujian_pbl_organizer_cdp.js — UJIAN LARIAN SEBENAR modul Organizer PBL
// Guna: CDP_PORT=9337 node ujian_pbl_organizer_cdp.js
const PORT = process.env.CDP_PORT || 9337;
const TEST_URL = process.env.TEST_URL || 'file:///root/sepora-rbt-toolkit/index.html';
const out = []; let fail = 0;
const ok = (n, c, i) => { const line = `${c ? 'PASS' : 'FAIL'}  ${n}${i !== undefined ? '  [' + i + ']' : ''}`; out.push(line); console.log(line); if (!c) fail++; };

async function connect() {
  let page = null;
  for (let i = 0; i < 40 && !page; i++) {
    try { const l = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json(); page = l.find(t => t.type === 'page'); } catch (e) { }
    if (!page) await new Promise(r => setTimeout(r, 500));
  }
  if (!page) throw new Error('tiada target CDP pada ' + PORT);
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let id = 0; const pending = new Map(); const errors = [];
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
    if (m.method === 'Runtime.exceptionThrown') {
      const d = m.params.exceptionDetails;
      errors.push((d.exception && d.exception.description) || d.text);
    }
  };
  const send = (method, params) => new Promise(res => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params: params || {} })); });
  await send('Runtime.enable'); await send('Page.enable');
  const ev = async (expr) => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.result && r.result.exceptionDetails) return { err: r.result.exceptionDetails.text };
    return r.result && r.result.result ? r.result.result.value : undefined;
  };
  return { send, ev, errors, ws };
}

(async () => {
  const { send, ev, errors, ws } = await connect();
  await send('Page.navigate', { url: TEST_URL });
  await new Promise(r => setTimeout(r, 2500));

  // --- Gerbang: buka (login sebagai guru ujian kalau perlu) ---
  await ev(`(function(){
     try{ localStorage.clear(); }catch(e){}
     try{ localStorage.setItem('erph_auth_cred', JSON.stringify({emel:'uji.pbl@moe-dl.edu.my',pinHash:'x'})); }catch(e){}
  })()`);
  await send('Page.navigate', { url: TEST_URL });
  await new Promise(r => setTimeout(r, 2500));

  // Paksa buka panel (elak gerbang)
  await ev(`(function(){ try{ document.querySelectorAll('.gate,#gateScreen,#view-gate').forEach(function(g){g.style.display='none';}); }catch(e){} return 1; })()`);

  // --- U1: switchTab ke pbl-organizer ---
  const u1 = await ev(`(function(){ switchTab('pbl-organizer');
      var p = document.getElementById('view-pbl-organizer');
      return p ? (p.classList.contains('active') ? 'aktif' : 'ada-tak-aktif') : 'tiada'; })()`);
  ok('U1 switchTab("pbl-organizer") buka panel', u1 === 'aktif', String(u1));

  // --- U2: dropdown projek terisi ---
  const u2 = await ev(`(function(){ var s=document.getElementById('pblOrgProjek');
      return s ? s.options.length : -1; })()`);
  ok('U2 dropdown projek terisi dari PBL_TEMPLATES', Number(u2) >= 20, 'pilihan=' + u2);

  // --- U3: timeline ADDIE render 5 baris ---
  await ev(`(function(){ var s=document.getElementById('pblOrgProjek'); s.value='4_kereta_idamanku'; pblOrgTukarProjek(); return 1; })()`);
  const u3 = await ev(`document.querySelectorAll('#pblAddieTrack .addie-row').length`);
  ok('U3 timeline ADDIE render 5 fasa', Number(u3) === 5, 'baris=' + u3);

  // --- U4: kelas/subjek terpapar ---
  const u4 = await ev(`(document.getElementById('pblOrgKelas')||{}).textContent + '|' + (document.getElementById('pblOrgSubjek')||{}).textContent`);
  ok('U4 info kelas & subjek terisi', String(u4).includes('4 Dinamik'), String(u4));

  // --- U5: set fasa -> status berubah + progres dikira ---
  await ev(`(function(){ pblOrgSetFasa('analysis','siap'); pblOrgSetFasa('design','siap'); pblOrgSetFasa('develop','sedang'); return 1; })()`);
  const u5 = await ev(`(function(){
      var rows=document.querySelectorAll('#pblAddieTrack .addie-row');
      var st=[]; rows.forEach(function(r){st.push(r.getAttribute('data-status'));});
      return st.join(',') + ' || ' + (document.getElementById('pblOrgProgres')||{}).textContent; })()`);
  ok('U5 status fasa tersimpan & progres dikira', String(u5).includes('siap,siap,sedang,belum,belum') && String(u5).includes('2/5'), String(u5));

  // --- U6: data impak -> analisis auto ---
  await ev(`(function(){
      document.getElementById('pblMurid').value='30';
      document.getElementById('pblTP1').value='1';
      document.getElementById('pblTP2').value='2';
      document.getElementById('pblTP3').value='3';
      document.getElementById('pblTP4').value='10';
      document.getElementById('pblTP5').value='8';
      document.getElementById('pblTP6').value='6';
      document.getElementById('pblSkor').value='78';
      document.getElementById('pblRefleksi').value='Murid lebih yakin bekerja dalam kumpulan.';
      document.getElementById('pblMasalah').value='Bahan kitar semula kurang, perlu stok awal.';
      pblOrgKira(); return 1; })()`);
  const u6 = await ev(`(function(){ var a=pblOrgAnalisis();
      return JSON.stringify({murid:a.murid,total:a.jumlahTP,capai:a.capai,pct:Math.round(a.peratusCapai*10)/10,gred:a.gred}); })()`);
  const a6 = JSON.parse(u6);
  ok('U6 analisis: jumlah TP = 30', a6.total === 30, JSON.stringify(a6));
  ok('U7 analisis: TP4+ = 24 murid', a6.capai === 24, 'capai=' + a6.capai);
  ok('U8 analisis: peratus = 80%', a6.pct === 80, 'pct=' + a6.pct);
  ok('U9 analisis: gred "Sangat Tinggi"', a6.gred === 'Sangat Tinggi', a6.gred);

  // --- U10: kotak statistik terpapar ---
  const u10 = await ev(`document.querySelectorAll('#pblStatBox .impak-box').length`);
  ok('U10 kotak statistik impak render', Number(u10) === 5, 'kotak=' + u10);

  // --- U11: kesimpulan mengandungi angka betul ---
  const u11 = await ev(`(document.getElementById('pblKesimpulan')||{}).innerText`);
  ok('U11 kesimpulan sebut 24 murid & 80%', String(u11).includes('24') && String(u11).includes('80.0%'), String(u11).slice(0, 90));

  // --- U12: OPR auto dijana ---
  const u12 = await ev(`(document.getElementById('pblOprDoc')||{}).innerText`);
  const hasO = String(u12).includes('OBJECTIVES');
  const hasP = String(u12).includes('PROCESS');
  const hasR = String(u12).includes('RESULTS');
  ok('U12 OPR jana: O+P+R lengkap', hasO && hasP && hasR, `O=${hasO} P=${hasP} R=${hasR}`);
  ok('U13 OPR Results ada angka impak', String(u12).includes('24') && String(u12).includes('80.0%'));
  ok('U14 OPR sebut impak POSITIF', String(u12).includes('POSITIF'));

  // --- U15: PERSISTEN — reload & semak data kekal ---
  await send('Page.navigate', { url: TEST_URL });
  await new Promise(r => setTimeout(r, 2500));
  await ev(`(function(){ document.querySelectorAll('.gate,#gateScreen,#view-gate').forEach(function(g){g.style.display='none';}); return 1; })()`);
  await ev(`(function(){ switchTab('pbl-organizer'); var s=document.getElementById('pblOrgProjek'); s.value='4_kereta_idamanku'; pblOrgTukarProjek(); return 1; })()`);
  const u15 = await ev(`(function(){
      var rows=document.querySelectorAll('#pblAddieTrack .addie-row');
      var st=[]; rows.forEach(function(r){st.push(r.getAttribute('data-status'));});
      return JSON.stringify({fasa:st.join(','), murid:document.getElementById('pblMurid').value,
        tp4:document.getElementById('pblTP4').value, skor:document.getElementById('pblSkor').value,
        ref:(document.getElementById('pblRefleksi').value||'').slice(0,20)}); })()`);
  const p15 = JSON.parse(u15);
  ok('U15 PERSISTEN: status fasa kekal selepas reload', p15.fasa === 'siap,siap,sedang,belum,belum', p15.fasa);
  ok('U16 PERSISTEN: data murid kekal', p15.murid === '30', p15.murid);
  ok('U17 PERSISTEN: data TP4 kekal', p15.tp4 === '10', p15.tp4);
  ok('U18 PERSISTEN: skor kekal', p15.skor === '78', p15.skor);
  ok('U19 PERSISTEN: refleksi kekal', p15.ref.indexOf('Murid lebih yakin') === 0, p15.ref);

  // --- U20: projek lain ada data sendiri (tidak bercampur) ---
  const u20 = await ev(`(function(){ var s=document.getElementById('pblOrgProjek'); s.value='4_pen3d'; pblOrgTukarProjek();
      return JSON.stringify({murid:document.getElementById('pblMurid').value, fasa:document.querySelectorAll('#pblAddieTrack .addie-row[data-status="siap"]').length}); })()`);
  const p20 = JSON.parse(u20);
  ok('U20 projek lain: data TIDAK bercampur (kosong)', p20.murid === '' && p20.fasa === 0, u20);

  // --- U21: kes TAB (aplikasi guru sebenar) ---
  const u21 = await ev(`(function(){
      switchTab('dashboard'); var d=document.getElementById('view-dashboard').classList.contains('active');
      switchTab('pbl-organizer'); var o=document.getElementById('view-pbl-organizer').classList.contains('active');
      switchTab('dashboard'); var d2=document.getElementById('view-dashboard').classList.contains('active');
      return JSON.stringify({d:d,o:o,d2:d2}); })()`);
  const p21 = JSON.parse(u21);
  ok('U21 navigasi tab berfungsi dua hala', p21.d && p21.o && p21.d2, u21);

  // --- U22: tiada ralat JS ---
  ok('U22 tiada ralat JS sepanjang ujian', errors.length === 0, errors.slice(0, 2).join(' | '));

  console.log('\nRingkasan: ' + (out.filter(l => l.startsWith('PASS')).length) + '/' + out.length + ' PASS');
  try { ws.close(); } catch (e) { }
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('RALAT:', e.message); process.exit(1); });
