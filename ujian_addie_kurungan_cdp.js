// ujian_addie_kurungan_cdp.js — sahkan label asal KEKAL + kurungan ADDIE terpapar
const PORT = process.env.CDP_PORT || 9338;
const TEST_URL = process.env.TEST_URL || 'file:///root/sepora-rbt-toolkit/index.html';
const out = []; let fail = 0;
const ok = (n, c, i) => { const l = `${c ? 'PASS' : 'FAIL'}  ${n}${i !== undefined ? '  [' + i + ']' : ''}`; out.push(l); console.log(l); if (!c) fail++; };

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
    if (m.method === 'Runtime.exceptionThrown') { const d = m.params.exceptionDetails; errors.push((d.exception && d.exception.description) || d.text); }
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
  await ev(`(function(){ document.querySelectorAll('.gate,#gateScreen,#view-gate').forEach(function(g){g.style.display='none';}); return 1; })()`);

  // K1: data label asal PLAN/DO/CHECK/ACT masih ada
  const k1 = await ev(`(function(){
      var k=Object.keys(PBL_TEMPLATES);
      var count={PLAN:0,DO:0,CHECK:0,ACT:0};
      k.forEach(function(key){ (PBL_TEMPLATES[key].fasaProjek||[]).forEach(function(f){ if(count[f.fasa]!==undefined) count[f.fasa]++; }); });
      return JSON.stringify(count); })()`);
  const c1 = JSON.parse(k1);
  ok('K1 label asal PLAN kekal (20)', c1.PLAN === 20, 'PLAN=' + c1.PLAN);
  ok('K2 label asal DO kekal (20)', c1.DO === 20, 'DO=' + c1.DO);
  ok('K3 label asal CHECK kekal (20)', c1.CHECK === 20, 'CHECK=' + c1.CHECK);
  ok('K4 label asal ACT kekal (20)', c1.ACT === 20, 'ACT=' + c1.ACT);

  // K5: tajuk masih ada (PLAN) dsb — label asal tak diubah
  const k5 = await ev(`(function(){
      var t=PBL_TEMPLATES['4_kereta_idamanku'].fasaProjek.map(function(f){return f.tajuk;});
      return JSON.stringify(t); })()`);
  const t5 = JSON.parse(k5);
  ok('K5 tajuk asal "(PLAN)" kekal', t5[0].includes('(PLAN)'), t5[0]);
  ok('K6 tajuk asal "(DO)" kekal', t5[1].includes('(DO)'), t5[1]);
  ok('K7 tajuk asal "(CHECK)" kekal', t5[2].includes('(CHECK)'), t5[2]);
  ok('K8 tajuk asal "(ACT)" kekal', t5[3].includes('(ACT)'), t5[3]);

  // K9: medan kurunganAddie wujud & betul
  const k9 = await ev(`(function(){
      var f=PBL_TEMPLATES['4_kereta_idamanku'].fasaProjek.map(function(x){return x.kurunganAddie;});
      return JSON.stringify(f); })()`);
  const k9v = JSON.parse(k9);
  ok('K9 kurungan ADDIE ada pada semua 4 fasa', k9v.every(x => x && x.indexOf('(ADDIE:') === 0), JSON.stringify(k9v));
  ok('K10 PLAN -> ADDIE: Analysis & Design', String(k9v[0]).includes('Analysis'), k9v[0]);
  ok('K11 DO -> ADDIE: Develop', String(k9v[1]).includes('Develop'), k9v[1]);
  ok('K12 CHECK -> ADDIE: Implementation', String(k9v[2]).includes('Implementation'), k9v[2]);
  ok('K13 ACT -> ADDIE: Evaluation', String(k9v[3]).includes('Evaluation'), k9v[3]);

  // K14: RENDER sebenar — jana RPH dan semak DOM
  const k14 = await ev(`(function(){
      try{
        switchTab('bina-rph');
        var s=document.getElementById('formTahap');
        if(s){ s.value='4_kereta_idamanku'; if(typeof onTahapChange==='function') onTahapChange(); }
        var btn=document.querySelector('[onclick*="autoGenerateSmartRph"], [onclick*="Jana"]');
        if(btn) btn.click();
      }catch(e){ return 'RALAT: '+e.message; }
      return 'ok'; })()`);
  await new Promise(r => setTimeout(r, 1500));

  const k15 = await ev(`(function(){
      var tl=document.getElementById('previewTimelineContainer');
      if(!tl) return JSON.stringify({err:'tiada container'});
      var boxes=tl.querySelectorAll('.phase-box');
      var titles=[]; boxes.forEach(function(b){ titles.push((b.querySelector('.phase-title')||{}).innerText||''); });
      return JSON.stringify({n:boxes.length, titles:titles}); })()`);
  const v15 = JSON.parse(k15);
  ok('K14 RENDER: timeline 4 kotak fasa', v15.n === 4, 'kotak=' + v15.n);
  const allTitles = (v15.titles || []).join(' || ');
  ok('K15 RENDER: tajuk papar label asal (PLAN)', allTitles.includes('(PLAN)'), allTitles.slice(0, 120));
  ok('K16 RENDER: tajuk papar label asal (ACT)', allTitles.includes('(ACT)'));
  ok('K17 RENDER: kurungan ADDIE terpapar', allTitles.includes('ADDIE: Analysis') && allTitles.includes('ADDIE: Develop'), allTitles.slice(0, 200));
  ok('K18 RENDER: ADDIE Evaluation terpapar', allTitles.includes('ADDIE: Evaluation'));

  // K19: tab Organizer PBL masih berfungsi
  const k19 = await ev(`(function(){
      switchTab('pbl-organizer');
      var p=document.getElementById('view-pbl-organizer');
      var aktif = p && p.classList.contains('active');
      var rows=document.querySelectorAll('#pblAddieTrack .addie-row').length;
      return JSON.stringify({aktif:aktif, rows:rows}); })()`);
  const v19 = JSON.parse(k19);
  ok('K19 tab Organizer PBL masih berfungsi', v19.aktif === true, k19);
  ok('K20 tracker ADDIE 5 fasa masih render', v19.rows === 5, 'baris=' + v19.rows);

  // K21: tiada ralat JS
  ok('K21 tiada ralat JS', errors.length === 0, errors.slice(0, 2).join(' | '));

  console.log('\nRingkasan: ' + out.filter(l => l.startsWith('PASS')).length + '/' + out.length + ' PASS');
  try { ws.close(); } catch (e) { }
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('RALAT:', e.message); process.exit(1); });
