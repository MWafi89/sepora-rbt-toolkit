// ujian_lengkap_cdp.js — UJIAN LENGKAP aplikasi SEPORA RBT TOOLKIT (kitaran hayat RPH + arkib)
// Menjawab: (1) betulkah ini aplikasi lengkap? (2) setiap RPH yang dijana tersimpan ke arkib?
//           (3) boleh diedit & diguna semula untuk kegunaan seterusnya?
// Guna: TEST_URL=... CDP_PORT=9336 node ujian_lengkap_cdp.js
const PORT = process.env.CDP_PORT || 9336;
const TEST_URL = process.env.TEST_URL || 'https://sepora-rbt-toolkit.vercel.app/index.html';
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
  const send = (method, params = {}) => new Promise(res => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
  return { send, errors };
}

(async () => {
  const { send, errors } = await connect();
  await send('Runtime.enable'); await send('Page.enable');
  const ev = async (expression) => {
    const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    if (r.result && r.result.exceptionDetails) throw new Error((r.result.exceptionDetails.exception && r.result.exceptionDetails.exception.description) || r.result.exceptionDetails.text);
    return r.result && r.result.result ? r.result.result.value : undefined;
  };
  const waitReady = async (label) => {
    for (let i = 0; i < 45; i++) {
      await new Promise(r => setTimeout(r, 1000));
      try { if (await ev(`typeof loadPblRbtTemplate === 'function' && !!document.getElementById('selectPblTahun4')`)) { return true; } } catch (e) { }
    }
    return false;
  };

  await send('Page.navigate', { url: TEST_URL });
  await new Promise(r => setTimeout(r, 3000));
  await ev(`localStorage.clear(); localStorage.setItem('erph_session', JSON.stringify({email:'ujian@moe-dl.edu.my',mode:'delima'})); 'ok'`);
  await send('Page.reload');
  const rdy = await waitReady();
  ok('L00 aplikasi dimuatkan (skrip + gerbang lulus)', rdy === true);
  if (!rdy) { console.log(out.join('\n')); process.exit(1); }
  const stub = async () => await ev(`window.confirm = function(){return true;}; window.print = function(){ window.__printed = (window.__printed||0)+1; }; window.alert=function(){}; 'ok'`);
  await stub();

  /* ---------- L1: perisian lengkap - fungsi teras ---------- */
  const NEED = ['switchTab', 'loadPblRbtTemplate', 'autoGenerateSmartRph', 'arkibAutoSimpan', 'saveCurrentGeneratedRph',
    'viewSavedRph', 'openArkibEditModal', 'submitArkibEdit', 'updateArkibFromPreview', 'reuseArkibRph', 'printArkibRph',
    'printRphDocument', 'deleteSavedRph', 'executeArkibDelete', 'exportArkibJson', 'importArkibJson', 'exportRphPdf',
    'exportRphDocx', 'openSeporaRphBankModal', 'arkibLoadForSession', 'arkibKeyFor', 'arkibFindDraft', 'submitNewSlot', 'renderTimetable', 'updateDashboardMetrics',
    'renderSavedRphTable', 'updateArkibBadge', 'syncRphMirror', 'deleteAllDrafts', 'syncRphWithWeek'];
  const missing = await ev(`(${JSON.stringify(NEED)}).filter(function(f){ return typeof window[f] !== 'function'; })`);
  ok('L01 semua ' + NEED.length + ' fungsi teras wujud', Array.isArray(missing) && missing.length === 0, (missing || []).join(',') || 'lengkap');

  /* ---------- L2: setiap tab boleh dibuka ---------- */
  const TABS = ['dashboard', 'jadual', 'rpt', 'buku-teks', 'bbm', 'bina-rph', 'simpan-cetak'];
  const tabRes = await ev(`(function(){ const res=[]; ${JSON.stringify(TABS)}.forEach(function(t){
      const before = document.querySelectorAll('.view-panel').length;
      switchTab(t);
      const act = document.querySelector('.view-panel.active');
      const hdr = document.getElementById('moduleHeaderTitle');
      res.push({tab:t, aktif: act?act.id:null, jangka:'view-'+t, tajuk: hdr?(hdr.innerText||'').trim():'', panel:before});
    }); return res; })()`);
  tabRes.forEach(r => ok(`L02 tab "${r.tab}" dibuka betul`, r.aktif === r.jangka && r.tajuk.length > 3, `${r.aktif} / "${r.tajuk}"`));

  /* ---------- L3: daftar 3 slot jadual (kelas berbeza) ---------- */
  const SLOT = [{ h: 'Isnin', m: '07:40 - 08:40', k: '2 Cekal', s: 'RBT Tahun 4' },
                { h: 'Selasa', m: '09:40 - 10:40', k: '2 Tekun', s: 'RBT Tahun 5' },
                { h: 'Rabu', m: '11:00 - 12:00', k: '2 Amanah', s: 'RBT Tahun 6' }];
  const slotN = await ev(`(function(){ jadualList.length=0; ${JSON.stringify(SLOT)}.forEach(function(s){
      openAddSlotModal();
      document.getElementById('modalSlotHari').value=s.h; document.getElementById('modalSlotMasa').value=s.m;
      document.getElementById('modalSlotKelas').value=s.k; document.getElementById('modalSlotSubjek').value=s.s;
      submitNewSlot({preventDefault:function(){}});
    }); return { n: jadualList.length, simpan: (JSON.parse(localStorage.getItem('erph_jadual'))||[]).length, baris: document.querySelectorAll('#timetableBody tr, .timetable-tr, tbody tr').length }; })()`);
  ok('L03 3 slot jadual didaftarkan & disimpan', slotN.n === 3 && slotN.simpan === 3, `jadual=${slotN.n} stor=${slotN.simpan}`);

  /* ---------- L4: SETIAP janaan RPH tersimpan ke arkib ---------- */
  const gen = await ev(`(function(){ savedRphList.length=0; currentArkibId=null; ${JSON.stringify(SLOT)}.forEach(function(s){
      loadSlotToRph(s.h, s.m, s.k, s.s); autoGenerateSmartRph();
    }); return savedRphList.length; })()`);
  ok('L04 setiap RPH dijana (3 slot) masuk arkib', gen === 3, 'rekod=' + gen);
  const ulang = await ev(`(function(){ const s=${JSON.stringify(SLOT[0])}; loadSlotToRph(s.h,s.m,s.k,s.s); autoGenerateSmartRph(); autoGenerateSmartRph(); return savedRphList.length; })()`);
  ok('L05 jana ulang slot SAMA tidak cipta pendua', ulang === 3, 'rekod=' + ulang);

  /* ---------- L6: setiap rekod ada kandungan RPH penuh ---------- */
  const isi = await ev(`(function(){ const medan=['tajuk','sk','sp','masa','kelas','subjek','pblMingguPelaksanaan','pblTarikhMula','pblTarikhHantar','bukuTeks'];
    return savedRphList.map(function(r){ return { kelas:r.kelas, minggu:r.minggu, status:r.status, kurang: medan.filter(function(f){ return !r[f]; }) }; }); })()`);
  const kurangSemua = isi.flatMap(x => x.kurang.map(f => x.kelas + ':' + f));
  ok('L06 setiap rekod ada medan RPH penuh (10 medan)', kurangSemua.length === 0, kurangSemua.join(',') || 'lengkap 3 rekod');
  const kelasUnik = new Set(isi.map(x => x.kelas)).size;
  ok('L07 rekod dipisah ikut kelas/slot', kelasUnik === 3, 'kelas unik=' + kelasUnik);

  /* ---------- L8: Simpan ke Arkib (kunci + salinan dokumen) ---------- */
  const simpan = await ev(`(function(){ const s=${JSON.stringify(SLOT[2])}; loadSlotToRph(s.h,s.m,s.k,s.s); autoGenerateSmartRph(); saveCurrentGeneratedRph();
    const r=savedRphList.find(function(x){return x.kelas===s.k;}); return { saved:!!r.saved, status:r.status, docHtml:(r.docHtml||'').length, id:r.id, tajuk:r.tajuk }; })()`);
  ok('L08 "Simpan ke Arkib" kunci rekod + simpan dokumen penuh', simpan.saved === true && simpan.status !== 'Draf Dijana' && simpan.docHtml > 500, `${simpan.status} / docHtml=${simpan.docHtml}`);
  const ID = simpan.id;


  /* ---------- L08b: RPH yang sudah dijana/disimpan TIDAK ditimpa ---------- */
  const versi = await ev(`(function(){ const s=${JSON.stringify(SLOT[2])};
    const lama=savedRphList.find(function(x){return x.id===${ID};});
    const lamaTajuk=lama? lama.tajuk:null, lamaDoc=(lama&&lama.docHtml||'').length;
    loadSlotToRph(s.h,s.m,s.k,s.s); autoGenerateSmartRph();
    const baru=savedRphList.filter(function(x){ return x.kelas===s.k && !x.saved; });
    const lama2=savedRphList.find(function(x){return x.id===${ID};});
    return { bil:savedRphList.length, lamaKekal:!!lama2, lamaSaved:!!(lama2&&lama2.saved), lamaTajukSama: lama2? lama2.tajuk===lamaTajuk:false,
             lamaDoc:(lama2&&lama2.docHtml||'').length, versiBaru: baru.length? (baru[0].versi||0):0, baruDraf: baru.length>0 }; })()`);
  ok('L08b rekod DIKUNCI tidak ditimpa bila Jana semula', versi.lamaKekal === true && versi.lamaSaved === true && versi.lamaTajukSama === true && versi.lamaDoc > 500, `dokumen lama=${versi.lamaDoc}`);
  ok('L08c janaan baharu jadi rekod versi baharu', versi.bil === 4 && versi.baruDraf === true && versi.versiBaru >= 2, `rekod=${versi.bil} versi=${versi.versiBaru}`);

  /* ---------- L9: kekal selepas reload ---------- */
  await send('Page.reload'); const rdy2 = await waitReady(); await stub();
  const selepas = await ev(`(function(){ switchTab('simpan-cetak');
    const r=savedRphList.find(function(x){return x.id===${ID};});
    return { n:savedRphList.length, saved:!!(r&&r.saved), docHtml:r?(r.docHtml||'').length:0, baris:document.querySelectorAll('#savedRphTableBody tr').length,
             badge:(document.querySelector('#arkibBadge, .arkib-badge')||{}).innerText||'' , stor:(JSON.parse(localStorage.getItem(arkibKey()))||[]).length }; })()`);
  ok('L09 arkib kekal selepas reload (stor per akaun)', rdy2 && selepas.n === 4 && selepas.stor === 4, `senarai=${selepas.n} stor=${selepas.stor}`);
  ok('L10 dokumen tersimpan kekal selepas reload', selepas.saved === true && selepas.docHtml > 500, `docHtml=${selepas.docHtml}`);
  ok('L11 jadual arkib dipaparkan dlm tab Simpan/Cetak', selepas.baris === 4, `baris=${selepas.baris}`);

  /* ---------- L12: edit maklumat rekod ---------- */
  const edit = await ev(`(function(){ openArkibEditModal(${ID});
    document.getElementById('arkibEditTajuk').value='RPH DISUNTING (UJIAN)';
    document.getElementById('arkibEditNota').value='nota guru ujian';
    document.getElementById('arkibEditStatus').value='Selesai Dilaksana';
    submitArkibEdit({preventDefault:function(){}}, ${ID});
    const r=savedRphList.find(function(x){return x.id===${ID};});
    return { tajuk:r.tajuk, nota:r.nota, status:r.status, saved:!!r.saved }; })()`);
  ok('L12 edit maklumat rekod berjaya', edit.tajuk === 'RPH DISUNTING (UJIAN)' && edit.nota === 'nota guru ujian' && edit.status === 'Selesai Dilaksana', `${edit.tajuk} / ${edit.status}`);

  /* ---------- L13: buka semula (Papar) + sunting dokumen + kemas kini ---------- */
  const buka = await ev(`(function(){ viewSavedRph(${ID}); const el=document.getElementById('rphPreviewContainer');
    return { panjang:(el.innerText||'').trim().length, adaTajuk:!!document.getElementById('previewTajuk'), tab:(document.querySelector('.view-panel.active')||{}).id }; })()`);
  ok('L13 "Papar" buka dokumen dari arkib (bukan kosong)', buka.panjang > 500 && buka.tab === 'view-bina-rph', `aksara=${buka.panjang}`);
  const sunting = await ev(`(function(){ const t=document.getElementById('previewTajuk'); if(t){ t.innerText = t.innerText + ' [SUNTINGAN DOKUMEN]'; }
    updateArkibFromPreview(); const r=savedRphList.find(function(x){return x.id===${ID};});
    return { tajuk:r.tajuk, adaDalamDoc:(r.docHtml||'').indexOf('SUNTINGAN DOKUMEN')>-1, docHtml:(r.docHtml||'').length }; })()`);
  ok('L14 suntingan DOKUMEN tersimpan ke rekod arkib', sunting.adaDalamDoc === true && sunting.docHtml > 500, `tajuk="${(sunting.tajuk || '').slice(0, 34)}"`);

  await send('Page.reload'); const rdy3 = await waitReady(); await stub();
  const kekal2 = await ev(`(function(){ const r=savedRphList.find(function(x){return x.id===${ID};}); return r?{tajuk:r.tajuk, nota:r.nota, status:r.status, doc:(r.docHtml||'').indexOf('SUNTINGAN DOKUMEN')>-1}:null; })()`);
  ok('L15 suntingan kekal selepas reload', rdy3 && !!kekal2 && kekal2.nota === 'nota guru ujian' && kekal2.doc === true, kekal2 ? `${kekal2.status} / docOk=${kekal2.doc}` : 'rekod hilang');

  /* ---------- L16: guna semula untuk RPH baharu ---------- */
  const guna = await ev(`(function(){ const src=savedRphList.find(function(x){return x.id===${ID};}); const t0=src.pblTarikhMula, h0=src.pblTarikhHantar;
    reuseArkibRph(${ID});
    const bil=savedRphList.length; const baru=savedRphList.find(function(x){ return x.id!==${ID} && x.tajuk===src.tajuk && x.status==='Draf Dijana'; });
    const beza = baru ? Math.round((new Date(baru.pblTarikhHantar)-new Date(h0))/86400000) : null;
    return { bil:bil, beza:beza, advan:(baru&&baru.pblTarikhMula)!==t0, doc:document.getElementById('rphPreviewContainer').innerText.trim().length, id:baru?baru.id:null }; })()`);
  ok('L16 "Guna Semula" cipta rekod baharu (+1)', guna.bil === 5, 'arkib=' + guna.bil);
  ok('L17 rekod guna semula: tarikh +7 hari & dokumen dijana', guna.beza === 7 && guna.doc > 500, `beza=${guna.beza} hari, dokumen=${guna.doc} aksara`);

  /* ---------- L18: cetak ---------- */
  await ev(`window.__printed=0; printArkibRph(${ID}); 'ok'`);
  await new Promise(r => setTimeout(r, 900));   // printArkibRph guna setTimeout 350ms
  const cetak = await ev(`window.__printed||0`);
  ok('L18 "Cetak" rekod arkib mencetak dokumen', cetak >= 1, 'print x' + cetak);

  /* ---------- L19: eksport / import sandaran JSON ---------- */
  const eksport = await ev(`(function(){ window.__blob=null; const oc=URL.createObjectURL; URL.createObjectURL=function(b){ window.__blob=b; return 'blob:ujian'; };
    document.createElement.__a=null; exportArkibJson(); URL.createObjectURL=oc;
    return window.__blob ? window.__blob.size : -1; })()`);
  ok('L19 eksport arkib -> fail JSON dijana', eksport > 500, 'saiz blob=' + eksport + ' bait');
  const importRes = await ev(`(async function(){ const teks = localStorage.getItem(arkibKey()); localStorage.setItem('erph_saved_ujian_backup', teks);
    const unik = new Set(savedRphList.map(function(r){ return r.tajuk+'|'+r.minggu+'|'+r.kelas; })).size;
    savedRphList.length=0; renderSavedRphTable();
    const f = new File([teks], 'arkib.json', {type:'application/json'});
    await new Promise(function(res){ const ev2={target:{files:[f], value:''}}; importArkibJson(ev2); setTimeout(res, 900); });
    return { n:savedRphList.length, stor:(JSON.parse(localStorage.getItem(arkibKey()))||[]).length, unik:unik }; })()`);
  ok('L20 import JSON pulihkan semua rekod unik', importRes.n === importRes.unik && importRes.stor === importRes.unik && importRes.n >= 4, `senarai=${importRes.n} stor=${importRes.stor}`);

  /* ---------- L21: padam rekod ---------- */
  const padam = await ev(`(function(){ deleteSavedRph(${ID}); executeArkibDelete(${ID}); return savedRphList.length; })()`);
  ok('L21 padam rekod arkib berfungsi (rekod lain kekal)', padam === 4, 'baki=' + padam);

  /* ---------- L22: modul sokongan ---------- */
  const bank = await ev(`(function(){ try{ openSeporaRphBankModal(); const m=document.getElementById('modalBoxContent');
      const okm = !!(m && m.innerText && m.innerText.trim().length>50); closeModalDirectly(); return okm; }catch(e){ return 'RALAT: '+e.message; } })()`);
  ok('L22 Bank RPH SEPORA boleh dibuka', bank === true, String(bank));
  const rpt = await ev(`(function(){ switchTab('rpt'); const p=document.querySelector('.view-panel.active'); return { id:p?p.id:null, isi:p?(p.innerText||'').trim().length:0 }; })()`);
  ok('L23 modul RPT dipaparkan', rpt.id === 'view-rpt' && rpt.isi > 200, `aksara=${rpt.isi}`);
  const dash = await ev(`(function(){ switchTab('dashboard'); const p=document.querySelector('.view-panel.active'); return { isi:(p.innerText||'').trim().length, angka:(p.innerText.match(/\\d+/g)||[]).length }; })()`);
  ok('L24 papan pemuka (dashboard) berisi metrik', dash.isi > 200 && dash.angka >= 3, `aksara=${dash.isi}, nombor=${dash.angka}`);


  /* ---------- L26: arkib dipisahkan ikut akaun guru ---------- */
  const akaun = await ev(`(function(){ const s=getSession(); const kunci=arkibKey(); const bilA=savedRphList.length;
    finishLogin({ email:'guru.lain@moe-dl.edu.my', name:'Guru Lain', mode:'delima', loginAt:new Date().toISOString() });
    const bilB=savedRphList.length;
    finishLogin({ email:s.email, name:s.name, mode:s.mode, loginAt:new Date().toISOString() });
    return { kunci:kunci, bilA:bilA, bilB:bilB, bilA2:savedRphList.length }; })()`);
  ok('L26 arkib disimpan ikut kunci akaun (erph_saved::emel)', /::/.test(akaun.kunci), akaun.kunci);
  ok('L27 arkib guru lain tidak bercampur', akaun.bilB === 0 && akaun.bilA2 === akaun.bilA && akaun.bilA > 0, `A=${akaun.bilA} B=${akaun.bilB} A2=${akaun.bilA2}`);

  /* ---------- L28: "Padam Semua Draf" tidak memadam rekod Disimpan ---------- */
  const draf = await ev(`(function(){ saveCurrentGeneratedRph(); const simpan=savedRphList.filter(function(r){return r.saved;}).length;
    deleteAllDrafts(); return { simpanSebelum:simpan, simpanSelepas:savedRphList.filter(function(r){return r.saved;}).length, baki:savedRphList.length }; })()`);
  ok('L28 "Padam Semua Draf" kekalkan rekod Disimpan', draf.simpanSebelum === draf.simpanSelepas && draf.simpanSebelum > 0, `disimpan ${draf.simpanSebelum}->${draf.simpanSelepas} baki=${draf.baki}`);

  /* ---------- L29: eksport Word (.docx) ---------- */
  const word = await ev(`(async function(){ let saiz=-1, ralat='';
    const oc=URL.createObjectURL; window.__blob=null;
    URL.createObjectURL=function(b){ window.__blob=b; return 'blob:ujian'; };
    try { exportRphDocx(); await new Promise(function(r){ setTimeout(r, 2500); }); saiz=window.__blob? window.__blob.size:-1; }
    catch(e){ ralat=e.message; }
    URL.createObjectURL=oc;
    return { adaDocx:!!window.docx, saiz:saiz, ralat:ralat }; })()`);
  ok('L29 eksport Word (.docx) dijana', word.adaDocx ? (word.saiz > 2000 && word.ralat === '') : (word.ralat === ''), `lib docx=${word.adaDocx} saiz=${word.saiz} ralat="${word.ralat}"`);

  /* ---------- L30: eksport PDF / cetak ---------- */
  const pdf = await ev(`(function(){ let ralat=''; window.__printed=0;
    try { exportRphPdf(); } catch(e){ ralat=e.message; }
    return { ralat:ralat, cetak:window.__printed, adaCdn:!!window.html2pdf }; })()`);
  ok('L30 eksport PDF / cetak tanpa ralat', pdf.ralat === '' && (pdf.cetak >= 1 || pdf.adaCdn), `print=${pdf.cetak} html2pdf=${pdf.adaCdn}`);


  /* ---------- L32-L38: sistem log keluar & kunci skrin (F11) ---------- */
  const AKAUN_UJIAN = { email: 'ujian@moe-dl.edu.my', name: 'Guru Ujian', mode: 'setempat' };
  const f11 = await ev(`(function(){
    finishLogin(${JSON.stringify(AKAUN_UJIAN)});                       // pastikan akaun ujian aktif
    loadSlotToRph('Khamis','10:30 - 11:30','2 Rajin','RBT Tahun 5'); autoGenerateSmartRph(); saveCurrentGeneratedRph();
    const sebelum = savedRphList.length;
    lockAppScreen();
    return { sebelum: sebelum, gerbang: !document.getElementById('privacyLockScreen').classList.contains('hidden'),
             kunci: localStorage.getItem('erph_locked'),
             butangNav: /LOG KELUAR/i.test(document.getElementById('sidebar').innerText) && /KUNCI SKRIN/i.test(document.getElementById('sidebar').innerText) }; })()`);
  ok('L32 Kunci Skrin -> gerbang + bendera erph_locked', f11.gerbang === true && f11.kunci === '1', `kunci=${f11.kunci} rekod=${f11.sebelum}`);
  ok('L33 butang Log Keluar + Kunci Skrin dalam bar sisi', f11.butangNav === true);

  await send('Page.reload'); const rdy4 = await waitReady(); await stub();
  const kunciLepas = await ev(`(function(){ return { gerbang: !document.getElementById('privacyLockScreen').classList.contains('hidden'), kunci: localStorage.getItem('erph_locked') }; })()`);
  ok('L34 kunci KEKAL selepas muat semula (tak boleh dipintas)', rdy4 && kunciLepas.gerbang === true && kunciLepas.kunci === '1', `gerbang=${kunciLepas.gerbang}`);

  const bukaKunci = await ev(`(function(){ document.getElementById('loginInputEmail').value = DEFAULT_AUTH.email;
    document.getElementById('loginInputPassword').value = DEFAULT_AUTH.password;
    handleLoginSubmit({preventDefault:function(){}});
    return { gerbang: !document.getElementById('privacyLockScreen').classList.contains('hidden'), kunci: localStorage.getItem('erph_locked'), akaun: (getSession()||{}).email }; })()`);
  ok('L35 emel + PIN membuka kunci', bukaKunci.gerbang === false && bukaKunci.kunci === null, `akaun=${bukaKunci.akaun}`);

  const sesiKeluar = await ev(`(function(){ finishLogin(${JSON.stringify(AKAUN_UJIAN)});
    const sebelum = savedRphList.length; logoutSession();
    return { sebelum: sebelum, sesi: getSession(), kunci: localStorage.getItem('erph_locked'), arkib: savedRphList.length,
             preview: (document.getElementById('rphPreviewContainer').innerText||'').trim().length,
             gerbang: !document.getElementById('privacyLockScreen').classList.contains('hidden') }; })()`);
  ok('L36 Log Keluar: sesi + arkib memori + dokumen dibersihkan, gerbang dipapar',
     sesiKeluar.sesi === null && sesiKeluar.arkib === 0 && sesiKeluar.preview === 0 && sesiKeluar.gerbang === true && sesiKeluar.sebelum > 0,
     `rekod sebelum=${sesiKeluar.sebelum} sesi=${sesiKeluar.sesi} arkib=${sesiKeluar.arkib} preview=${sesiKeluar.preview}`);

  await send('Page.reload'); const rdy5 = await waitReady(); await stub();
  const lepasKeluar = await ev(`(function(){ return { gerbang: !document.getElementById('privacyLockScreen').classList.contains('hidden'), arkib: savedRphList.length }; })()`);
  ok('L37 selepas log keluar, muat semula tidak auto-masuk', rdy5 && lepasKeluar.gerbang === true && lepasKeluar.arkib === 0);

  const masukKembali = await ev(`(function(){ finishLogin(${JSON.stringify(AKAUN_UJIAN)});
    return { gerbang: !document.getElementById('privacyLockScreen').classList.contains('hidden'), arkib: savedRphList.length, kunci: arkibKey() }; })()`);
  ok('L38 log masuk semula memulihkan arkib akaun itu', masukKembali.gerbang === false && masukKembali.arkib >= 1, `arkib=${masukKembali.arkib} kunci=${masukKembali.kunci}`);

  /* ---------- L40-L44: sandaran Google Drive -> folder 'SEPORATOOLKIT' (F12, API dipalsy) ---------- */
  await ev(`gTok = 'MOCK_TOKEN'; gTokExp = Date.now() + 3600000;
    finishLogin({ email:'guru.drive@moe-dl.edu.my', name:'Guru Drive', mode:'delima' });
    loadSlotToRph('Selasa','11:00 - 12:00','2 Drive','RBT Tahun 5'); autoGenerateSmartRph(); saveCurrentGeneratedRph();
    window.__g = { folderCreate:0, fileCreate:0, patched:0, move:0, folderAda:false, fileAda:false, legacy:false, meta:null, queries:[], folderBody:null };
    const J = o => new Response(JSON.stringify(o), { status:200, headers:{ 'Content-Type':'application/json' } });
    window.fetch = async function(url, opts){
      opts = opts || {}; const u = String(url), m = (opts.method||'GET').toUpperCase(), g = window.__g;
      if (u.indexOf('googleapis.com/drive/v3/files?') >= 0 && m === 'GET') {
        const q = decodeURIComponent(u); g.queries.push(q);
        if (q.indexOf("mimeType='application/vnd.google-apps.folder'") >= 0) return J({ files: g.folderAda ? [{ id:'FOLDER123', name:'SEPORATOOLKIT' }] : [] });
        if (q.indexOf('FOLDER123') >= 0) return J({ files: g.fileAda ? [{ id:'FILE1', name:'SEPORA_RPH_ARKIB.json', parents:['FOLDER123'] }] : [] });
        return J({ files: g.legacy ? [{ id:'OLD9', name:'SEPORA_RPH_ARKIB.json', parents:['root'] }] : [] });
      }
      if (u.indexOf('googleapis.com/drive/v3/files?') >= 0 && m === 'POST') { g.folderCreate++; g.folderBody = JSON.parse(opts.body||'{}'); g.folderAda = true; return J({ id:'FOLDER123', name:'SEPORATOOLKIT' }); }
      if (u.indexOf('/drive/v3/files/OLD9?addParents=') >= 0) { g.move++; g.fileAda = true; return J({ id:'OLD9', parents:['FOLDER123'] }); }
      if (u.indexOf('/upload/drive/v3/files?uploadType=multipart') >= 0) { g.fileCreate++; const md = opts.body.get('metadata'); g.meta = JSON.parse(await md.text()); g.fileAda = true; return J({ id:'FILE1', name:'SEPORA_RPH_ARKIB.json' }); }
      if (u.indexOf('/upload/drive/v3/files/') >= 0) { g.patched++; return J({ id:'FILE1' }); }
      if (u.indexOf('/drive/v3/files/FILE1?alt=media') >= 0) return J({ rekod:[{ id: 9911, tajuk:'RPH DRIVE UJIAN', minggu:'9', kelas:'2 Drive', saved:true, status:'Disimpan' }] });
      if (u.indexOf('/drive/v3/files/OLD9?alt=media') >= 0) return J({ rekod: [] });
      return J({});
    }; 'mock sedia'`);
  const gd1 = await ev(`(async function(){ const ok = await driveSave(true); const g = window.__g;
    return { ok:ok, folderCreate:g.folderCreate, fileCreate:g.fileCreate, meta:g.meta, folderBody:g.folderBody, fid:localStorage.getItem('erph_drive_folderid') }; })()`);
  ok('L40 Drive: folder SEPORATOOLKIT auto-cipta', gd1.ok === true && gd1.folderCreate === 1 && (gd1.folderBody || {}).name === 'SEPORATOOLKIT' && (gd1.folderBody || {}).mimeType === 'application/vnd.google-apps.folder', String((gd1.folderBody || {}).name));
  ok('L41 Drive: arkib disimpan DI DALAM folder (parents)', gd1.fileCreate === 1 && (gd1.meta || {}).parents && (gd1.meta || {}).parents[0] === 'FOLDER123' && gd1.fid === 'FOLDER123', JSON.stringify((gd1.meta || {}).parents));

  const gd2 = await ev(`(async function(){ const ok = await driveSave(true); return { ok:ok, folderCreate:window.__g.folderCreate, patched:window.__g.patched }; })()`);
  ok('L42 Drive: simpan kedua tiada folder pendua (PATCH sahaja)', gd2.ok === true && gd2.folderCreate === 1 && gd2.patched >= 1, JSON.stringify(gd2));

  const gd3 = await ev(`(async function(){ savedRphList.length = 0; const ok = await driveRestore(true);
    return { ok:ok, ada:savedRphList.some(function(r){ return r.tajuk === 'RPH DRIVE UJIAN'; }),
             dalamFolder: window.__g.queries.some(function(q){ return q.indexOf('in parents') > -1 && q.indexOf('FOLDER123') > -1; }) }; })()`);
  ok('L43 Drive: pulih cari dalam folder dahulu + rekod masuk', gd3.ok === true && gd3.ada === true && gd3.dalamFolder === true, JSON.stringify(gd3));

  const gd4 = await ev(`(async function(){ gFileId = ''; localStorage.removeItem('erph_drive_fileid');
    window.__g.fileAda = false; window.__g.legacy = true; const ok = await driveSave(true);
    return { ok:ok, move:window.__g.move, folderCreate:window.__g.folderCreate }; })()`);
  ok('L44 Drive: fail lama di akar dipindah ke folder', gd4.ok === true && gd4.move >= 1 && gd4.folderCreate === 1, JSON.stringify(gd4));

  /* ---------- L46-L48: onboarding guru (F13) ---------- */
  const onb = await ev(`(function(){ gTok = null; gTokExp = 0;
    try { localStorage.removeItem(SEPORA_GDRIVE.autoKey); localStorage.removeItem('erph_profil_disemak'); } catch (e) { }
    finishLogin({ email:'guru.delima@moe-dl.edu.my', name:'Guru DELIMa', mode:'delima' });
    const chk = document.getElementById('driveAutoSync');
    return { auto: localStorage.getItem(SEPORA_GDRIVE.autoKey), checkbox: chk ? !!chk.checked : null, folder: SEPORA_GDRIVE.folderName }; })()`);
  ok('L46 log masuk DELIMa -> sandaran Drive automatik AKTIF', onb.auto === '1' && (onb.checkbox === null || onb.checkbox === true), `auto=${onb.auto} folder=${onb.folder}`);

  await ev(`(function(){ closeModalDirectly(); localStorage.removeItem('erph_profil_disemak');
    finishLogin({ email: DEFAULT_AUTH.email, name: DEFAULT_TEACHER.name, mode:'setempat' }); return 'ok'; })()`);
  await new Promise(r => setTimeout(r, 1300));
  const onb1 = await ev(`(function(){ const m = document.getElementById('modalBoxContent'), ov = document.getElementById('appModalOverlay');
    return { flag: localStorage.getItem('erph_profil_disemak'), teks: m ? (m.innerText||'') : '',
             panjang: m ? (m.innerText||'').trim().length : -1, papar: ov ? ov.style.display : null }; })()`);
  ok('L47 mod setempat dgn emel lalai -> minta guru tetapkan emel & PIN sendiri', onb1.flag === '1' && onb1.panjang > 50 && /Emel/i.test(onb1.teks) && onb1.papar === 'flex', `panjang=${onb1.panjang} papar=${onb1.papar}`);

  await ev(`(function(){ closeModalDirectly(); finishLogin({ email: DEFAULT_AUTH.email, name: DEFAULT_TEACHER.name, mode:'setempat' }); return 'ok'; })()`);
  await new Promise(r => setTimeout(r, 1200));
  const onb2 = await ev(`(function(){ const ov = document.getElementById('appModalOverlay'); return { papar: ov ? ov.style.display : null }; })()`);
  ok('L48 kali kedua tidak mengganggu lagi (sekali sahaja)', onb2.papar !== 'flex', `papar=${onb2.papar}`);

  /* ---------- L25: ralat JS sepanjang ujian ---------- */
  ok('L49 tiada ralat JS sepanjang ujian', errors.length === 0, errors.slice(0, 3).join(' | ') || '0 ralat');

  console.log('\n===== UJIAN LENGKAP SEPORA RBT TOOLKIT (chromium headless + CDP) =====');
  console.log('URL: ' + TEST_URL);
  console.log(out.join('\n'));
  console.log(`\nRingkasan: ${out.length - fail}/${out.length} PASS`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL:', e.message); console.error(e.stack ? e.stack.split('\n').slice(0,3).join(' | ') : ''); process.exit(2); });
