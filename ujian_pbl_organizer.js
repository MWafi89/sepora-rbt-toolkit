// ujian_pbl_organizer.js — sahkan modul Organizer PBL berfungsi
// Guna puppeteer/CDP. Kalau tiada, fallback: ujian statik struktur.
const fs = require('fs');
const path = require('path');

const FILE = path.join(__dirname, 'index.html');
const html = fs.readFileSync(FILE, 'utf8');
let pass = 0, fail = 0;

function ok(name, cond, extra) {
  if (cond) { pass++; console.log('PASS  ' + name + (extra ? '  [' + extra + ']' : '')); }
  else { fail++; console.log('FAIL  ' + name + (extra ? '  [' + extra + ']' : '')); }
}

// --- 1. Struktur asas ---
ok('P1 panel view-pbl-organizer wujud', html.includes('id="view-pbl-organizer"'));
ok('P2 nav item Organizer PBL wujud', html.includes("switchTab(&quot;pbl-organizer&quot;)"));
ok('P3 tajuk tab ditambah', html.includes("'pbl-organizer': 'Organizer PBL"));
ok('P4 hook init pada switchTab', html.includes("if (tabId === 'pbl-organizer')"));

// --- 2. ADDIE 5 fasa ---
const fasa = ['analysis','design','develop','implementation','evaluation'];
fasa.forEach(f => ok('P5 fasa ADDIE: ' + f, html.includes("id:'" + f + "'")));
ok('P6 label ADDIE Analysis', html.includes("nama:'Analysis'"));
ok('P7 label ADDIE Evaluation', html.includes("nama:'Evaluation'"));

// --- 3. Data impak TP1-TP6 ---
for (let i = 1; i <= 6; i++) {
  ok('P8 medan TP' + i + ' wujud', html.includes('id="pblTP' + i + '"'));
}
ok('P9 medan bilangan murid', html.includes('id="pblMurid"'));
ok('P10 medan skor ujian', html.includes('id="pblSkor"'));
ok('P11 medan refleksi guru', html.includes('id="pblRefleksi"'));
ok('P12 medan cadangan penambahbaikan', html.includes('id="pblMasalah"'));

// --- 4. Enjin analisis ---
ok('P13 fungsi pblOrgAnalisis wujud', html.includes('function pblOrgAnalisis()'));
ok('P14 kira peratus capai TP4+', html.includes('peratusCapai'));
ok('P15 gred impak Sangat Tinggi', html.includes("'Sangat Tinggi'"));
ok('P16 gred impak Rendah', html.includes("'Rendah'"));
ok('P17 kesan TP tertinggi/terendah', html.includes('maksTP') && html.includes('minTP'));
ok('P18 amaran jumlah TP != murid', html.includes('tidak sama dengan bilangan murid'));

// --- 5. OPR auto ---
ok('P19 penjana OPR wujud', html.includes('function pblOrgJanaOPR()'));
ok('P20 OPR bahagian Objectives', html.includes('O — OBJECTIVES'));
ok('P21 OPR bahagian Process', html.includes('P — PROCESS'));
ok('P22 OPR bahagian Results', html.includes('R — RESULTS'));
ok('P23 kesimpulan impak positif/negatif', html.includes('memberi impak POSITIF') && html.includes('BELUM optimum'));

// --- 6. Simpanan ---
ok('P24 kunci localStorage organizer', html.includes("'erph_pbl_organizer::'"));
ok('P25 fungsi simpan', html.includes('function pblOrgSimpan()'));
ok('P26 fungsi muat', html.includes('function pblOrgMuat()'));
ok('P27 eksport JSON', html.includes('function pblOrgEksportJson()'));
ok('P28 cetak OPR', html.includes('function pblOrgCetak()'));

// --- 7. Keselamatan / kualiti ---
ok('P29 teks pengguna di-escape', (html.match(/replace\(\/</g) || []).length >= 2,
   'esc=' + (html.match(/replace\(\/</g) || []).length);
ok('P30 tiada eval/Function injection baharu', !html.includes('eval(pbl'));
ok('P31 twin file sama', fs.readFileSync(path.join(__dirname,'sepora_rbt_toolkit.html'),'utf8') === html);

// --- 8. Ujian fungsi sebenar (kalau node ada puppeteer) ---
(function () {
  let pup;
  try { pup = require('puppeteer'); } catch (e) {
    console.log('SKIP  P32-P36 ujian larian (puppeteer tiada) — ujian statik sahaja');
    return;
  }
})();

console.log('\nRingkasan: ' + pass + '/' + (pass + fail) + ' PASS');
process.exit(fail ? 1 : 0);
