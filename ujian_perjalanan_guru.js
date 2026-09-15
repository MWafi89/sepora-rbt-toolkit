// ujian_perjalanan_guru.js — PERJALANAN PENGGUNA BAHARU (guru) hujung-ke-hujung
// Menjawab: "sebagai pengguna baharu, boleh ke guna app ini sampai habis - jana RPH,
//            simpan, arkib, eksport, keluar/masuk semula?"
// Guna: TEST_URL=... CDP_PORT=9337 node ujian_perjalanan_guru.js
const PORT = process.env.CDP_PORT || 9337;
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
    if (m.method === 'Runtime.exceptionThrown') { const d = m.params.exceptionDetails; errors.push((d.exception && d.exception.description) || d.text); }
    // dialog (confirm/prompt) tidak boleh menyekat ujian headless
    if (m.method === 'Page.javascriptDialogOpening') ws.send(JSON.stringify({ id: ++id, method: 'Page.handleJavaScriptDialog', params: { accept: true } }));
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
  const waitReady = async () => {
    for (let i = 0; i < 45; i++) {
      await new Promise(r => setTimeout(r, 1000));
      try { if (await ev(`typeof openDaftarModal === 'function' && !!window.switchTab && !!document.getElementById('btnDaftarUtama')`)) return true; } catch (e) { }
    }
    return false;
  };

  await send('Page.navigate', { url: TEST_URL });
  await new Promise(r => setTimeout(r, 2500));
  await ev(`localStorage.clear(); sessionStorage.clear(); location.reload(); 1`);
  const rdy = await waitReady();
  ok('P00 aplikasi dimuatkan (peranti baharu kosong)', rdy === true);
  if (!rdy) { console.log(out.join('\n')); process.exit(1); }
  // confirm/alert/print tidak boleh menyekat ujian headless (sama seperti ujian_lengkap_cdp.js)
  await ev(`window.confirm = function(){ return true; }; window.print = function(){ window.__printed = (window.__printed||0)+1; }; window.alert = function(){}; 'ok'`);

  /* ---------- P1: gerbang -> daftar guru baharu (ID DELIMa sendiri) ---------- */
  // [F28] Gerbang baharu: butang daftar = #btnDaftarUtama ("Saya guru BAHARU - Daftar").
  // Pilihan A (Google) sengaja tersembunyi bila Client ID kosong -> yang diuji: Pilihan B + jalan kembali.
  await new Promise(r => setTimeout(r, 700));
  const gerbang = await ev(`(function(){ const b = document.getElementById('btnDaftarUtama');
    if (b) b.click();
    const t = (document.getElementById('modalBoxContent') || { innerText: '' }).innerText || '';
    return { butang: !!b, papar: document.getElementById('appModalOverlay').style.display,
             pilihanB: t.indexOf('Pilihan B') > -1 || t.indexOf('Guna tanpa Google') > -1,
             kembali: t.indexOf('Kembali ke log masuk') > -1 }; })()`);
  ok('P01 gerbang: butang "Saya guru BAHARU" -> skrin daftar (Pilihan B + jalan kembali)', gerbang.butang && gerbang.papar === 'flex' && gerbang.pilihanB && gerbang.kembali, JSON.stringify(gerbang));
  await ev("closeModalDirectly(); window.__modalWajib = false; 'ok'");   // bersihkan sebelum P02

  const daftar = await ev(`(async function(){ openDaftarModal(true, true);
    document.getElementById('daftarNama').value = 'Cikgu Aisyah';
    document.getElementById('daftarEmel').value = 'g-99001122';
    document.getElementById('daftarPin').value = '246813';
    await submitDaftarLocal({ preventDefault: function(){} });
    const s = getSession() || {};
    return { gerbangTutup: document.getElementById('privacyLockScreen').classList.contains('hidden'),
             emel: s.email, id: s.delimaId, nama: teacherProfile.name, daftar: localStorage.getItem('erph_daftar_selesai'), sesi: s.mode || '' }; })()`);
  ok('P02 daftar guru baharu: identiti ID DELIMa sendiri + gerbang terbuka',
    daftar.gerbangTutup === true && daftar.emel === 'g-99001122@moe-dl.edu.my' && daftar.id === 'g-99001122' && daftar.daftar === '1', `emel=${daftar.emel}`);

  /* ---------- P3: setiap tab ada kandungan ---------- */
  const TAB = ['dashboard', 'jadual', 'rpt', 'buku-teks', 'bina-rph', 'bbm', 'simpan-cetak'];
  const tab = await ev(`(function(){ const r = {}; ${JSON.stringify(TAB)}.forEach(function(t){
      switchTab(t); const p = document.getElementById('view-' + t);
      r[t] = p ? (p.innerText || '').replace(/\\s+/g, ' ').trim().length : -1; }); return r; })()`);
  ok('P03 kesemua 7 tab mempunyai kandungan (tiada tab kosong)', TAB.every(t => (tab[t] || 0) > 40), JSON.stringify(tab));

  /* ---------- P4: jadual + jana RPH ---------- */
  const jadual = await ev(`(function(){ return { slot: (jadualList || []).length, import: !!document.getElementById('timetableFileInput'),
      tambah: !!document.querySelector('[onclick*="openAddSlotModal"]'), ai: aiTersedia() }; })()`);
  ok('P04 jadual ada data permulaan + cara import/tambah slot (+ status AI jujur)', jadual.slot > 0 && jadual.import && jadual.tambah && jadual.ai === false, `slot=${jadual.slot}`);

  const jana = await ev(`(function(){ loadSlotToRph('Selasa','11:00 - 12:00','2 Cekal','RBT Tahun 5'); autoGenerateSmartRph();
    const g = (i) => { const e = document.getElementById(i); return e ? (e.innerText || e.value || '').trim() : ''; };
    return { tajuk: g('previewTajuk'), sk: g('previewSK'), sp: g('previewSP'), objektif: g('previewObjektif').length,
             pak21: g('previewPak21'), pentaksiran: g('previewPentaksiran'), hari: g('formRphHari'), kelas: g('formRphKelas') }; })()`);
  ok('P05 jana RPH: tajuk + SK + SP + objektif + PAK21 + pentaksiran terisi',
    !!jana.tajuk && jana.sk.length > 2 && jana.sp.length > 5 && jana.objektif > 50 && !!jana.pak21 && !!jana.pentaksiran, `SK=${jana.sk.slice(0, 24)}`);

  /* ---------- P6: simpan + arkib + guna semula ---------- */
  const simpan = await ev(`(function(){ saveCurrentGeneratedRph(); const r = (savedRphList || [])[0] || {};
    return { bil: (savedRphList || []).length, adaDoc: !!(r.docHtml && r.docHtml.length > 500), id: r.id }; })()`);
  ok('P06 simpan ke arkib: rekod + dokumen tersimpan', simpan.bil >= 1 && simpan.adaDoc === true, `bil=${simpan.bil}`);

  const arkib = await ev(`(async function(){ const r = (savedRphList || [])[0] || {}; let pv = 0, modal = 0, guna = '';
    viewSavedRph(r.id); pv = ((document.getElementById('rphPreviewContainer') || { innerText: '' }).innerText || '').length;
    openArkibEditModal(r.id); modal = ((document.getElementById('modalBoxContent') || { innerText: '' }).innerText || '').length; closeModalDirectly();
    reuseArkibRph(r.id); guna = (document.getElementById('toastContainer') || { innerText: '' }).innerText || '';
    return { pv: pv, modal: modal, guna: guna.indexOf('RPH baharu dari rekod') > -1 }; })()`);
  ok('P07 arkib: lihat + edit + guna semula (cadang tarikh +1 minggu)', arkib.pv > 1000 && arkib.modal > 40 && arkib.guna === true, `pv=${arkib.pv}`);

  /* ---------- P8: eksport Word / PDF / cetak ---------- */
  const eksport = await ev(`(async function(){ const lib = { docx: typeof docx, html2pdf: typeof html2pdf, pdfjs: typeof pdfjsLib };
    const r = { lib: lib };
    try { await exportRphDocx(); r.docx = true; } catch (e) { r.docx = String(e.message); }
    try { await exportRphPdf(); r.pdf = true; } catch (e) { r.pdf = String(e.message); }
    try { printRphDocument(); r.cetak = true; } catch (e) { r.cetak = String(e.message); }
    return r; })()`);
  ok('P08 eksport Word/PDF/cetak tanpa ralat + pustaka CDN dimuat',
    eksport.lib.docx === 'object' && eksport.lib.html2pdf === 'function' && eksport.lib.pdfjs === 'object'
    && eksport.docx === true && eksport.pdf === true && eksport.cetak === true, JSON.stringify(eksport.lib));

  /* ---------- P9: RPT / Buku Teks / BBM / Bank RPH ---------- */
  const lain = await ev(`(async function(){ const r = {};
    try { loadDefaultSampleRpt(); r.rpt = (rptList || []).length; } catch (e) { r.rpt = String(e.message); }
    ['openAddTextbookModal', 'openAddBbmModal', 'openSeporaRphBankModal', 'openAddSlotModal'].forEach(function(fn){
      try { window[fn](); r[fn] = ((document.getElementById('modalBoxContent') || { innerText: '' }).innerText || '').length > 30; closeModalDirectly(); }
      catch (e) { r[fn] = String(e.message); } });
    return r; })()`);
  ok('P09 RPT + Buku Teks + BBM + Bank RPH + tambah slot boleh dibuka',
    lain.rpt > 10 && lain.openAddTextbookModal === true && lain.openAddBbmModal === true && lain.openSeporaRphBankModal === true && lain.openAddSlotModal === true, `rpt=${lain.rpt}`);

  /* ---------- P10: ciri AI jujur (kunci AI kosong) + Drive jelas ---------- */
  const aiDrive = await ev(`(async function(){ const r = { ai: aiTersedia() };
    const asal = window.fetch; let n = 0; window.fetch = function(){ n++; return asal.apply(this, arguments); };
    try { await analyzeTimetableImageWithAI('AAAA', 'image/jpeg'); } catch (e) { }
    window.fetch = asal; r.rangkaian = n;
    openDrivePanel(); r.panel = ((document.getElementById('modalBoxContent') || { innerText: '' }).innerText || '').replace(/\\s+/g, ' '); closeModalDirectly();
    return r; })()`);
  ok('P10a AI belum aktif: tiada panggilan rangkaian + mesej jujur', aiDrive.ai === false && aiDrive.rangkaian === 0 && aiDrive.panel !== undefined);
  ok('P10b panel Drive beri penjelasan jelas untuk mod setempat', aiDrive.panel.indexOf('Drive belum aktif') > -1 && aiDrive.panel.indexOf('SEPORATOOLKIT') > -1);

  /* ---------- P11: profil + keluar/masuk semula (kunci akaun guru) ---------- */
  const profil = await ev(`(async function(){ openProfileModal();
    document.getElementById('modalTeacherSchool').value = 'SK Ujian Baharu';
    document.getElementById('modalAuthEmail').value = 'g-99001122';      // ID tanpa domain
    document.getElementById('modalAuthPassword').value = '778899';
    await submitTeacherProfile({ preventDefault: function(){} });
    const k = JSON.parse(localStorage.getItem('erph_auth_cred') || '{}');
    return { emel: k.email, hash: !!k.pinHash, sekolah: teacherProfile.school, gerbang: document.getElementById('loginInputEmail').value }; })()`);
  ok('P11 profil: ID DELIMa dinormalkan + PIN disimpan sebagai hash',
    profil.emel === 'g-99001122@moe-dl.edu.my' && profil.hash === true && profil.sekolah === 'SK Ujian Baharu' && profil.gerbang === 'g-99001122@moe-dl.edu.my', `emel=${profil.emel}`);

  const keluar = await ev(`(function(){ const bil = (savedRphList || []).length; logoutSession();
    return { sebelum: bil, gerbang: !document.getElementById('privacyLockScreen').classList.contains('hidden'), dalam: (savedRphList || []).length }; })()`);
  const masuk = await ev(`(async function(){ document.getElementById('loginInputEmail').value = 'g-99001122';   // ID sahaja
    document.getElementById('loginInputPassword').value = '778899';
    await handleLoginSubmit({ preventDefault: function(){} });
    return { gerbangTutup: document.getElementById('privacyLockScreen').classList.contains('hidden'), arkib: (savedRphList || []).length }; })()`);
  ok('P12 keluar bersihkan arkib dalam memori, masuk semula (ID sahaja) pulihkan arkib',
    keluar.gerbang === true && keluar.dalam === 0 && masuk.gerbangTutup === true && masuk.arkib >= 1, `pulih=${masuk.arkib}`);

  /* ---------- P14: EDIT RPH yang sudah disimpan (kitaran penuh simpan->edit->simpan) ---------- */
  const edit = await ev(`(function(){ const r = (savedRphList || [])[0] || {};
    openArkibEditModal(r.id);
    document.getElementById('arkibEditTajuk').value = 'RPH DIEDIT OLEH GURU';
    document.getElementById('arkibEditNota').value = 'nota ujian edit';
    document.getElementById('arkibEditKelas').value = '3 Bestari';
    submitArkibEdit({ preventDefault: function(){} }, r.id);
    const selepas = savedRphList.find(function (x) { return x.id === r.id; }) || {};
    const emel = ((getSession() || {}).email) || '';
    const kunci = (typeof arkibKeyFor === 'function') ? arkibKeyFor(emel) : ('erph_saved::' + emel);
    const storan = localStorage.getItem(kunci) || '';
    return { tajuk: selepas.tajuk, kelas: selepas.kelas, nota: selepas.nota, dalamStoran: storan.indexOf('RPH DIEDIT OLEH GURU') > -1 }; })()`);
  ok('P14 edit RPH tersimpan: tajuk/kelas/nota dikemas kini + kekal dalam storan',
    edit.tajuk === 'RPH DIEDIT OLEH GURU' && edit.kelas === '3 Bestari' && edit.nota === 'nota ujian edit' && edit.dalamStoran === true,
    `tajuk=${String(edit.tajuk).slice(0, 24)}`);

  /* ---------- P15: JANA WORD (.docx) - struktur fail sebenar (bukan sekadar tiada ralat) ---------- */
  await ev(`loadSlotToRph('Selasa','11:00 - 12:00','2 Cekal','RBT Tahun 5'); autoGenerateSmartRph(); 'ok'`);
  const word = await ev(`(async function(){ const asalUrl = URL.createObjectURL, asalKlik = HTMLAnchorElement.prototype.click;
    let blob = null, nama = '', ralat = '';
    URL.createObjectURL = function (b) { blob = b; return asalUrl.call(URL, b); };
    HTMLAnchorElement.prototype.click = function () { nama = this.download || nama; };
    try { exportRphDocx(); } catch (e) { ralat = String(e.message); }
    for (let i = 0; i < 20 && !blob; i++) await new Promise(r => setTimeout(r, 300));
    URL.createObjectURL = asalUrl; HTMLAnchorElement.prototype.click = asalKlik;
    if (!blob) return { adaBlob: false, nama: nama, ralat: ralat };
    const buf = new Uint8Array(await blob.arrayBuffer());
    const teks = new TextDecoder('latin1').decode(buf.slice(0, Math.min(buf.length, 300000)));
    return { adaBlob: true, saiz: buf.length, zip: buf[0] === 0x50 && buf[1] === 0x4B, dokumen: teks.indexOf('word/document.xml') > -1, nama: nama, ralat: ralat }; })()`);
  ok('P15 jana Word: fail .docx sah (zip + word/document.xml)',
    word.adaBlob === true && word.zip === true && word.dokumen === true && word.saiz > 3000 && String(word.nama).indexOf('.docx') > -1,
    `saiz=${word.saiz} zip=${word.zip} dokumen=${word.dokumen} nama=${word.nama}`);

  /* ---------- P16: JANA PDF - tanda tangan fail %PDF ---------- */
  const pdf = await ev(`(async function(){ const asalUrl = URL.createObjectURL, asalKlik = HTMLAnchorElement.prototype.click;
    let blob = null, nama = '', ralat = '';
    URL.createObjectURL = function (b) { blob = b; return asalUrl.call(URL, b); };
    HTMLAnchorElement.prototype.click = function () { nama = this.download || nama; };
    try { exportRphPdf(); } catch (e) { ralat = String(e.message); }
    for (let i = 0; i < 60 && !blob; i++) await new Promise(r => setTimeout(r, 500));
    URL.createObjectURL = asalUrl; HTMLAnchorElement.prototype.click = asalKlik;
    if (!blob) return { adaBlob: false, nama: nama, ralat: ralat };
    const buf = new Uint8Array(await blob.arrayBuffer());
    const kepala = String.fromCharCode(buf[0], buf[1], buf[2], buf[3], buf[4]);
    const pratontonSelepas = ((document.getElementById('rphPreviewContainer') || { innerText: '' }).innerText || '').length;
    return { adaBlob: true, saiz: buf.length, pdf: kepala.indexOf('%PDF-') === 0, kepala: kepala, pratontonSelepas: pratontonSelepas, nama: nama, ralat: ralat }; })()`);
  ok('P16 jana PDF: fail bermula dengan %PDF (dokumen PDF sebenar)',
    pdf.adaBlob === true && pdf.pdf === true && pdf.saiz > 3000,
    `saiz=${pdf.saiz} kepala=${JSON.stringify(pdf.kepala)} nama=${pdf.nama || '(tiada)'}`);

  /* ---------- P17: CETAK - dokumen dicetak mengandungi kandungan RPH ---------- */
  // Nota: html2pdf memindahkan #rphPreviewContainer ke kontena tersembunyi SEMASA render dan
  // memulangkannya selepas selesai - jadi guna textContent (bukan innerText) + tunggu sehingga pulih.
  const cetak = await ev(`(async function(){ const pv = function(){ const e = document.getElementById('rphPreviewContainer'); return e ? (e.textContent || '').length : -1; };
    let pra = pv();
    loadSlotToRph('Selasa','11:00 - 12:00','2 Cekal','RBT Tahun 5'); autoGenerateSmartRph();
    for (let i = 0; i < 20 && pv() < 500; i++) await new Promise(r => setTimeout(r, 500));
    let dipanggil = 0; const asal = window.print;
    window.print = function () { dipanggil++; };
    printRphDocument();
    window.print = asal;
    const teks = (document.getElementById('rphPreviewContainer') || { textContent: '' }).textContent || '';
    return { pratontonSebelumJana: pra, dipanggil: dipanggil, panjang: teks.length, adaTajuk: teks.indexOf('PBL') > -1 || teks.indexOf('Artikel') > -1 }; })()`);
  ok('P17 cetak: dialog cetak dipanggil + dokumen RPH ada kandungan',
    cetak.dipanggil === 1 && cetak.panjang > 500 && cetak.adaTajuk === true, `panjang=${cetak.panjang} pra=${cetak.pratontonSebelumJana}`);

  /* ---------- P18: IMPORT JADUAL CSV (jalan alternatif bila AI belum aktif) ---------- */
  const csv = await ev(`(function(){ const sebelum = (jadualList || []).length;
    parseTimetableText('Hari,Masa,Kelas,Subjek\\nRabu,08:00 - 09:30,3 Bestari,RBT Tahun 6\\nKhamis,09:30 - 10:30,3 Bestari,RBT Tahun 6');
    const l = jadualList || [];
    return { sebelum: sebelum, selepas: l.length, adaRabu: l.some(function (s) { return s.hari === 'Rabu' && s.kelas === '3 Bestari'; }) }; })()`);
  ok('P18 import jadual CSV berfungsi (2 slot dibaca & diterapkan)',
    csv.selepas === 2 && csv.adaRabu === true, `slot=${csv.selepas}`);

  ok('P19 tiada ralat JS sepanjang perjalanan', errors.length === 0, errors.slice(0, 2).join(' | '));
  console.log(`\nRingkasan perjalanan guru baharu: ${out.length - fail}/${out.length} PASS  (URL: ${TEST_URL})`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('UJIAN GAGAL DIJALANKAN: ' + e.message); process.exit(2); });
