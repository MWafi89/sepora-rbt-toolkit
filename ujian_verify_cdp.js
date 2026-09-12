// ujian_verify_cdp.js — ad-hoc verification (assertions, exit != 0 on fail)
// Guna: TEST_URL=... CDP_PORT=9334 node /tmp/ujian_verify_cdp.js
const PORT = process.env.CDP_PORT || 9334;
const TEST_URL = process.env.TEST_URL || 'http://127.0.0.1:8899/index.html';
const out = []; let fail = 0;
const ok = (name, cond, info) => { out.push(`${cond ? 'PASS' : 'FAIL'}  ${name}${info !== undefined ? '  [' + info + ']' : ''}`); if (!cond) fail++; };

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
    if (m.method === 'Runtime.exceptionThrown') errors.push((m.params.exceptionDetails.exception && m.params.exceptionDetails.exception.description) || m.params.exceptionDetails.text);
  };
  const send = (method, params = {}) => new Promise(res => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
  return { send, errors };
}
const ev = async (send, expression) => {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (r.result && r.result.exceptionDetails) throw new Error((r.result.exceptionDetails.exception && r.result.exceptionDetails.exception.description) || r.result.exceptionDetails.text);
  return r.result?.result?.value;
};
const pick = (k) => `(function(){ const b=Array.from(document.querySelectorAll('[onclick*="loadPblRbtTemplate"]')).find(x=>String(x.getAttribute('onclick')).includes('${k}')); if(b) b.click(); else loadPblRbtTemplate('${k}');
  const g=function(id){const el=document.getElementById(id);return el?(el.innerText||'').replace(/\\s+/g,' ').trim():'';};
  return {tempoh:g('previewPblMingguTempoh'),hantar:g('previewPblTarikhHantar'),pak21:g('previewPak21'),pent:g('previewPentaksiran'),arkib:savedRphList.length}; })()`;

(async () => {
  const { send, errors } = await connect();
  await send('Runtime.enable'); await send('Page.enable');
  await send('Page.navigate', { url: TEST_URL });
  await new Promise(r => setTimeout(r, 4000));
  await ev(send, `localStorage.clear(); localStorage.setItem('erph_session', JSON.stringify({email:'v@moe-dl.edu.my',mode:'delima'})); 'ok'`);
  await send('Page.reload'); await new Promise(r => setTimeout(r, 5000));
  await ev(send, `window.confirm=function(){return true;}; window.print=function(){window.__printed=(window.__printed||0)+1;}; 'stub'`);

  // A1: melayari templat tak cipta rekod
  await ev(send, pick('4_jahitan')); await ev(send, pick('5_tanaman')); await ev(send, pick('6_bot_motor'));
  const afterBrowse = await ev(send, `savedRphList.length`);
  ok('A1 melayari templat PBL tidak cipta rekod arkib', afterBrowse === 0, 'arkib=' + afterBrowse);

  // A2: Jana RPH cipta 1
  await ev(send, `(function(){const b=Array.from(document.querySelectorAll('button')).find(x=>/Jana RPH/i.test(x.innerText||'')); if(b) b.click(); return 1;})()`);
  const afterJana = await ev(send, `savedRphList.length`);
  ok('A2 Jana RPH auto-simpan 1 rekod', afterJana === 1, 'arkib=' + afterJana);

  // A3: tempoh ikut templat
  const t3 = (await ev(send, pick('4_kereta_idamanku'))).tempoh;
  const t4 = (await ev(send, pick('4_pembungkusan'))).tempoh;
  ok('A3 tempoh PBL ikut projek (3 vs 4 Minggu)', /3 Minggu/.test(t3) && /4 Minggu/.test(t4) && t3 !== t4, `${t3} | ${t4}`);

  // A4: PAK21 & Pentaksiran unik ikut projek
  const jah = await ev(send, pick('4_jahitan')), bot = await ev(send, pick('6_bot_motor'));
  ok('A4a PAK21 berbeza ikut projek', jah.pak21 !== bot.pak21 && jah.pak21.length > 30, jah.pak21.slice(0, 42));
  ok('A4b Pentaksiran berbeza ikut projek', jah.pent !== bot.pent && jah.pent.length > 30, jah.pent.slice(0, 42));

  // A5: pratonton cermin dalam tab Simpan/Cetak
  const mirror = await ev(send, `(function(){ switchTab('simpan-cetak'); const w=document.getElementById('rphMirrorWrap'); const c=w?w.querySelector('.rph-paper'):null;
    return { len: w?(w.innerText||'').trim().length:-1, idDup: c?c.querySelectorAll('[id]').length:-1, btnPanel: w?w.parentElement.querySelectorAll('[onclick*="printRphDocument"]').length:-1 }; })()`);
  ok('A5a pratonton RPH ada dalam tab Simpan/Cetak', mirror.len > 1000, 'aksara=' + mirror.len);
  ok('A5b klon pratonton tiada id bertindih', mirror.idDup === 0, 'id=' + mirror.idDup);
  ok('A5c butang Cetak dalam panel pratonton', mirror.btnPanel >= 1, 'btn=' + mirror.btnPanel);

  // A6: cetak per baris arkib
  const cetak = await ev(send, `(function(){ const b=document.querySelector('#savedRphTableBody button[onclick^="printArkibRph"]'); if(!b) return {ada:false};
    window.__printed=0; b.click(); return {ada:true}; })()`);
  await new Promise(r => setTimeout(r, 1200));
  ok('A6 cetak rekod arkib (print dipanggil)', cetak.ada === true && (await ev(send, `window.__printed||0`)) >= 1);

  // A7: padam draf — rekod Disimpan kekal
  const draf = await ev(send, `(function(){ saveCurrentGeneratedRph(); const simpanAlt=savedRphList.filter(r=>r.saved).length; loadPblRbtTemplate('5_atmega'); const before=savedRphList.length; deleteAllDrafts(); return {simpanAlt, before, after:savedRphList.length, savedAfter:savedRphList.filter(r=>r.saved).length}; })()`);
  ok('A7 tambah draf baris PBL tak cipta rekod', draf.before === draf.simpanAlt, `sebelum=${draf.before} disimpan=${draf.simpanAlt}`);
  ok('A7b Padam Semua Draf kekalkan rekod Disimpan', draf.savedAfter === draf.simpanAlt && draf.after === draf.simpanAlt, `selepas=${draf.after} disimpan=${draf.savedAfter}`);

  ok('A8 tiada ralat JS semasa ujian', errors.length === 0, errors.slice(0, 2).join(' | ') || '0');

  console.log('\n===== AD-HOC VERIFICATION (chromium headless CDP) — ' + TEST_URL + ' =====');
  console.log(out.join('\n'));
  console.log(`\nRingkasan: ${out.length - fail}/${out.length} PASS`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(2); });
