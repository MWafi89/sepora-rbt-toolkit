#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_pbl_organizer.py
======================
Tambah modul "Organizer PBL" ke SEPORA RBT TOOLKIT:
  1. Tab/panel baru : view-pbl-organizer
  2. Timeline 5 fasa ADDIE (Analysis-Design-Develop-Implementation-Evaluation)
  3. Status tracker per fasa (Belum / Sedang / Siap) + tarikh
  4. Borang Data Impak (bilangan murid, TP1-TP6, skor ujian, refleksi)
  5. Enjin auto-analisis  -> % capai TP, min/max, gred impak, kesimpulan
  6. Penjana OPR automatik (Objectives-Process-Results)
  7. Simpan ke localStorage kunci 'erph_pbl_organizer::<emel>'
Idempotent: selamat dijalankan berulang kali.
"""
import re
import sys
import os
import shutil
import datetime

BASE = "/root/sepora-rbt-toolkit"
TARGETS = ["index.html", "sepora_rbt_toolkit.html"]
MARK = "/* ===== [PBL ORGANIZER v1] ====="

# ----------------------------------------------------------------------------
# 1) CSS + HTML PANEL
# ----------------------------------------------------------------------------
CSS_ANCHOR = "    .view-panel.active {"

CSS_BLOCK = r"""    /* ===== [PBL ORGANIZER v1] ===== */
    .pbl-org-grid { display:grid; grid-template-columns:1fr; gap:14px; }
    .pbl-card { background:var(--card-bg,#fff); border:1px solid var(--border,#e5e7eb); border-radius:12px; padding:14px; }
    .pbl-card h3 { margin:0 0 10px; font-size:1rem; display:flex; align-items:center; gap:8px; }
    .addie-track { display:flex; flex-direction:column; gap:8px; }
    .addie-row { display:flex; align-items:flex-start; gap:10px; border-left:4px solid #cbd5e1; background:#f8fafc; border-radius:8px; padding:10px 12px; }
    .addie-row[data-status="sedang"] { border-left-color:#f59e0b; background:#fffbeb; }
    .addie-row[data-status="siap"]   { border-left-color:#059669; background:#ecfdf5; }
    .addie-num { flex:0 0 26px; height:26px; border-radius:50%; background:#e2e8f0; color:#334155; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:0.75rem; }
    .addie-row[data-status="sedang"] .addie-num { background:#f59e0b; color:#fff; }
    .addie-row[data-status="siap"]   .addie-num { background:#059669; color:#fff; }
    .addie-body { flex:1; min-width:0; }
    .addie-title { font-weight:600; font-size:0.88rem; margin-bottom:2px; }
    .addie-desc { font-size:0.78rem; color:#64748b; line-height:1.45; }
    .addie-ctl { display:flex; gap:6px; flex-wrap:wrap; margin-top:8px; align-items:center; }
    .addie-ctl select, .addie-ctl input { font-size:0.75rem; padding:4px 6px; border:1px solid #cbd5e1; border-radius:6px; background:#fff; }
    .pbl-field { margin-bottom:10px; }
    .pbl-field label { display:block; font-size:0.78rem; font-weight:600; margin-bottom:4px; color:#334155; }
    .pbl-field input, .pbl-field select, .pbl-field textarea { width:100%; font-size:0.82rem; padding:7px 9px; border:1px solid #cbd5e1; border-radius:7px; box-sizing:border-box; }
    .pbl-tp-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(88px,1fr)); gap:8px; }
    .pbl-tp-grid .pbl-field { margin-bottom:0; }
    .impak-stat { display:grid; grid-template-columns:repeat(auto-fit,minmax(110px,1fr)); gap:10px; margin-bottom:12px; }
    .impak-box { background:#f1f5f9; border-radius:10px; padding:10px; text-align:center; }
    .impak-box .val { font-size:1.35rem; font-weight:800; color:#0f172a; line-height:1.1; }
    .impak-box .lbl { font-size:0.68rem; color:#64748b; text-transform:uppercase; letter-spacing:0.4px; margin-top:2px; }
    .impak-good { background:#ecfdf5; } .impak-good .val { color:#047857; }
    .impak-warn { background:#fffbeb; } .impak-warn .val { color:#b45309; }
    .impak-bad  { background:#fef2f2; } .impak-bad  .val { color:#b91c1c; }
    .opr-doc { background:#fff; border:1px dashed #cbd5e1; border-radius:10px; padding:14px; font-size:0.82rem; line-height:1.6; }
    .opr-doc h4 { margin:0 0 6px; font-size:0.88rem; color:#047857; }
    .opr-doc ul { margin:4px 0 12px; padding-left:1.2rem; }
    .pbl-badge { display:inline-block; font-size:0.65rem; font-weight:700; padding:2px 8px; border-radius:10px; }
    .pbl-badge.belum { background:#e2e8f0; color:#475569; }
    .pbl-badge.sedang{ background:#fef3c7; color:#b45309; }
    .pbl-badge.siap  { background:#d1fae5; color:#047857; }
    @media print { .no-print { display:none !important; } }
    /* ===== [/PBL ORGANIZER v1] ===== */

"""

HTML_PANEL = r"""
        <!-- ===== [PBL ORGANIZER v1] ===== -->
        <section id="view-pbl-organizer" class="view-panel">
          <div class="page-header">
            <h1 class="page-title"><i class="fa-solid fa-diagram-project"></i> Organizer PBL (ADDIE)</h1>
            <p style="font-size:0.85rem; color:#64748b; margin-top:4px;">
              Timeline projek &amp; data impak. Setiap guru boleh lihat fasa mana projek sedang berada,
              isi result, dan sistem kira analisis impak serta OPR secara automatik.
            </p>
          </div>

          <div class="pbl-org-grid">

            <!-- A. PEMILIH PROJEK -->
            <div class="pbl-card no-print">
              <h3><i class="fa-solid fa-list-check"></i> Pilih Projek PBL</h3>
              <div class="pbl-field">
                <label>Templat PBL (Tahun / Tajuk)</label>
                <select id="pblOrgProjek" onchange="pblOrgTukarProjek()"></select>
              </div>
              <div style="font-size:0.78rem; color:#64748b;">
                <strong>Kelas:</strong> <span id="pblOrgKelas">-</span> &nbsp;|&nbsp;
                <strong>Subjek:</strong> <span id="pblOrgSubjek">-</span>
              </div>
            </div>

            <!-- B. TIMELINE ADDIE -->
            <div class="pbl-card">
              <h3><i class="fa-solid fa-timeline"></i> Timeline 5 Fasa ADDIE</h3>
              <div class="addie-track" id="pblAddieTrack"></div>
              <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;" class="no-print">
                <button class="btn btn-outline btn-sm" onclick="pblOrgSetSemuaSiap()">
                  <i class="fa-solid fa-circle-check"></i> Tanda Semua Siap
                </button>
                <button class="btn btn-outline btn-sm" onclick="pblOrgResetFasa()">
                  <i class="fa-solid fa-rotate-left"></i> Reset Fasa
                </button>
                <span id="pblOrgProgres" style="font-size:0.78rem; font-weight:700; color:#047857; align-self:center;"></span>
              </div>
            </div>

            <!-- C. DATA IMPAK -->
            <div class="pbl-card">
              <h3><i class="fa-solid fa-chart-simple"></i> Data Impak (Isi Result)</h3>
              <div class="pbl-tp-grid">
                <div class="pbl-field">
                  <label>Bil. Murid</label>
                  <input type="number" id="pblMurid" min="0" oninput="pblOrgKira()">
                </div>
                <div class="pbl-field">
                  <label>TP1</label><input type="number" id="pblTP1" min="0" oninput="pblOrgKira()">
                </div>
                <div class="pbl-field">
                  <label>TP2</label><input type="number" id="pblTP2" min="0" oninput="pblOrgKira()">
                </div>
                <div class="pbl-field">
                  <label>TP3</label><input type="number" id="pblTP3" min="0" oninput="pblOrgKira()">
                </div>
                <div class="pbl-field">
                  <label>TP4</label><input type="number" id="pblTP4" min="0" oninput="pblOrgKira()">
                </div>
                <div class="pbl-field">
                  <label>TP5</label><input type="number" id="pblTP5" min="0" oninput="pblOrgKira()">
                </div>
                <div class="pbl-field">
                  <label>TP6</label><input type="number" id="pblTP6" min="0" oninput="pblOrgKira()">
                </div>
              </div>
              <div class="pbl-field" style="margin-top:10px;">
                <label>Purata Skor Ujian / Rubrik (%) — jika ada</label>
                <input type="number" id="pblSkor" min="0" max="100" oninput="pblOrgKira()" placeholder="contoh: 78">
              </div>
              <div class="pbl-field">
                <label>Refleksi / Komen Guru</label>
                <textarea id="pblRefleksi" rows="3" oninput="pblOrgKira()" placeholder="Contoh: Murid lebih yakin bekerja dalam kumpulan selepas fasa Develop..."></textarea>
              </div>
              <div class="pbl-field">
                <label>Masalah / Cadangan Penambahbaikan</label>
                <textarea id="pblMasalah" rows="2" oninput="pblOrgKira()" placeholder="Contoh: Bahan kitar semula kurang, perlu stok awal..."></textarea>
              </div>
            </div>

            <!-- D. AUTO ANALISIS -->
            <div class="pbl-card">
              <h3><i class="fa-solid fa-brain"></i> Analisis Impak Automatik</h3>
              <div class="impak-stat" id="pblStatBox"></div>
              <div id="pblKesimpulan" style="font-size:0.84rem; line-height:1.65; background:#f8fafc; border-radius:9px; padding:12px;"></div>
            </div>

            <!-- E. OPR AUTO -->
            <div class="pbl-card">
              <h3><i class="fa-solid fa-file-lines"></i> OPR (Objectives • Process • Results) — Auto</h3>
              <div class="opr-doc" id="pblOprDoc">Isi data impak untuk jana OPR.</div>
              <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;" class="no-print">
                <button class="btn btn-outline btn-sm" onclick="pblOrgJanaOPR()">
                  <i class="fa-solid fa-wand-magic-sparkles"></i> Jana Semula OPR
                </button>
                <button class="btn btn-outline btn-sm" onclick="pblOrgCetak()">
                  <i class="fa-solid fa-print"></i> Cetak
                </button>
                <button class="btn btn-outline btn-sm" onclick="pblOrgEksportJson()">
                  <i class="fa-solid fa-file-export"></i> Eksport JSON
                </button>
              </div>
            </div>

          </div>
        </section>
        <!-- ===== [/PBL ORGANIZER v1] ===== -->
"""

# ----------------------------------------------------------------------------
# 2) NAV ITEM
# ----------------------------------------------------------------------------
NAV_ANCHOR = """        <a class="nav-item" onclick="switchTab(&quot;simpan-cetak&quot;)">"""
NAV_BLOCK = """        <a class="nav-item" onclick="switchTab(&quot;pbl-organizer&quot;)">
          <i class="fa-solid fa-diagram-project"></i> Organizer PBL
        </a>
"""

# ----------------------------------------------------------------------------
# 3) JS MODUL
# ----------------------------------------------------------------------------
JS_ANCHOR = "    function arkibAutoSimpan() {"

JS_BLOCK = r"""    /* ===== [PBL ORGANIZER v1] ===== */
    var PBL_ADDIE_FASA = [
      { id:'analysis',       nama:'Analysis',       label:'Analisis',        desc:'Kenal pasti masalah, profil murid, keperluan & soalan pemacu (driving question).' },
      { id:'design',         nama:'Design',         label:'Reka Bentuk',     desc:'Rangka aktiviti, objektif, kriteria kejayaan, bahan & pembahagian minggu.' },
      { id:'develop',        nama:'Develop',        label:'Pembangunan',     desc:'Bina bahan/modul/prototaip. RPH & langkah amali dilaksanakan di sini.' },
      { id:'implementation', nama:'Implementation', label:'Pelaksanaan',     desc:'Jalankan projek dengan murid, pemantauan mingguan & dokumentasi.' },
      { id:'evaluation',     nama:'Evaluation',     label:'Penilaian Impak', desc:'Kumpul result, analisis impak, refleksi & penambahbaikan (WAJIB ada data).' }
    ];

    function pblOrgKey() {
      var emel = '';
      try { emel = (typeof arkibKey === 'function' ? arkibKey() : '') || ''; } catch (e) { }
      if (!emel) emel = 'default';
      return 'erph_pbl_organizer::' + emel;
    }

    var pblOrgStore = {};
    function pblOrgMuat() {
      try { pblOrgStore = JSON.parse(localStorage.getItem(pblOrgKey())) || {}; } catch (e) { pblOrgStore = {}; }
      if (typeof pblOrgStore !== 'object' || !pblOrgStore) pblOrgStore = {};
    }
    function pblOrgSimpan() {
      try { localStorage.setItem(pblOrgKey(), JSON.stringify(pblOrgStore)); } catch (e) { }
    }
    function pblOrgRekod(key) {
      if (!pblOrgStore[key]) pblOrgStore[key] = { fasa:{}, impak:{}, opr:'' };
      var r = pblOrgStore[key];
      if (!r.fasa) r.fasa = {};
      if (!r.impak) r.impak = {};
      return r;
    }

    function pblOrgSenaraiProjek() {
      var out = [];
      try {
        Object.keys(PBL_TEMPLATES || {}).forEach(function (k) {
          var t = PBL_TEMPLATES[k] || {};
          out.push({ key:k, tajuk:(t.tajuk || k) + (t.kelas ? ' — ' + t.kelas : '') });
        });
      } catch (e) { }
      return out;
    }

    function pblOrgInit() {
      pblOrgMuat();
      var sel = document.getElementById('pblOrgProjek');
      if (!sel) return;
      var senarai = pblOrgSenaraiProjek();
      var semasa = sel.value;
      sel.innerHTML = senarai.map(function (p) {
        return '<option value="' + p.key + '">' + p.tajuk.replace(/</g,'&lt;') + '</option>';
      }).join('');
      if (semasa && senarai.some(function(p){return p.key===semasa;})) sel.value = semasa;
      pblOrgTukarProjek();
    }

    function pblOrgTukarProjek() {
      var sel = document.getElementById('pblOrgProjek');
      if (!sel) return;
      var key = sel.value;
      var t = {};
      try { t = (PBL_TEMPLATES || {})[key] || {}; } catch (e) { }
      var kEl = document.getElementById('pblOrgKelas');
      var sEl = document.getElementById('pblOrgSubjek');
      if (kEl) kEl.textContent = t.kelas || '-';
      if (sEl) sEl.textContent = t.subjek || '-';
      pblOrgRenderFasa(key);
      pblOrgIsiBorang(key);
      pblOrgKira();
    }

    function pblOrgRenderFasa(key) {
      var track = document.getElementById('pblAddieTrack');
      if (!track) return;
      var rec = pblOrgRekod(key);
      track.innerHTML = PBL_ADDIE_FASA.map(function (f, i) {
        var st = (rec.fasa[f.id] && rec.fasa[f.id].status) || 'belum';
        var tk = (rec.fasa[f.id] && rec.fasa[f.id].tarikh) || '';
        var label = { belum:'Belum Mula', sedang:'Sedang Jalan', siap:'Siap' }[st] || 'Belum Mula';
        var opt = ['belum','sedang','siap'].map(function (v) {
          var nm = { belum:'Belum Mula', sedang:'Sedang Jalan', siap:'Siap' }[v];
          return '<option value="' + v + '"' + (v === st ? ' selected' : '') + '>' + nm + '</option>';
        }).join('');
        return '<div class="addie-row" data-status="' + st + '">' +
            '<div class="addie-num">' + (i + 1) + '</div>' +
            '<div class="addie-body">' +
              '<div class="addie-title">' + f.nama + ' (' + f.label + ') ' +
                '<span class="pbl-badge ' + st + '">' + label + '</span></div>' +
              '<div class="addie-desc">' + f.desc + '</div>' +
              '<div class="addie-ctl no-print">' +
                '<select onchange="pblOrgSetFasa(\'' + f.id + '\', this.value)">' + opt + '</select>' +
                '<input type="date" value="' + tk + '" onchange="pblOrgSetTarikh(\'' + f.id + '\', this.value)">' +
              '</div>' +
            '</div></div>';
      }).join('');
      pblOrgProgres(key);
    }

    function pblOrgSetFasa(fid, val) {
      var key = (document.getElementById('pblOrgProjek') || {}).value;
      if (!key) return;
      var rec = pblOrgRekod(key);
      if (!rec.fasa[fid]) rec.fasa[fid] = {};
      rec.fasa[fid].status = val;
      if (val === 'siap' && !rec.fasa[fid].tarikh) {
        rec.fasa[fid].tarikh = new Date().toISOString().slice(0, 10);
      }
      pblOrgSimpan();
      pblOrgRenderFasa(key);
      pblOrgKira();
    }
    function pblOrgSetTarikh(fid, val) {
      var key = (document.getElementById('pblOrgProjek') || {}).value;
      if (!key) return;
      var rec = pblOrgRekod(key);
      if (!rec.fasa[fid]) rec.fasa[fid] = {};
      rec.fasa[fid].tarikh = val;
      pblOrgSimpan();
      pblOrgKira();
    }
    function pblOrgSetSemuaSiap() {
      var key = (document.getElementById('pblOrgProjek') || {}).value;
      if (!key) return;
      var rec = pblOrgRekod(key);
      var today = new Date().toISOString().slice(0, 10);
      PBL_ADDIE_FASA.forEach(function (f) {
        if (!rec.fasa[f.id]) rec.fasa[f.id] = {};
        rec.fasa[f.id].status = 'siap';
        if (!rec.fasa[f.id].tarikh) rec.fasa[f.id].tarikh = today;
      });
      pblOrgSimpan(); pblOrgRenderFasa(key); pblOrgKira();
      if (typeof showToast === 'function') showToast('Semua 5 fasa ADDIE ditanda Siap.');
    }
    function pblOrgResetFasa() {
      var key = (document.getElementById('pblOrgProjek') || {}).value;
      if (!key) return;
      var rec = pblOrgRekod(key);
      rec.fasa = {};
      pblOrgSimpan(); pblOrgRenderFasa(key); pblOrgKira();
      if (typeof showToast === 'function') showToast('Fasa ADDIE direset.');
    }
    function pblOrgProgres(key) {
      var el = document.getElementById('pblOrgProgres');
      if (!el) return;
      var rec = pblOrgRekod(key);
      var siap = PBL_ADDIE_FASA.filter(function (f) { return (rec.fasa[f.id] || {}).status === 'siap'; }).length;
      var sedang = PBL_ADDIE_FASA.filter(function (f) { return (rec.fasa[f.id] || {}).status === 'sedang'; }).length;
      el.textContent = 'Progres: ' + siap + '/5 siap' + (sedang ? ' • ' + sedang + ' sedang jalan' : '');
      el.style.color = siap === 5 ? '#047857' : (siap >= 3 ? '#b45309' : '#b91c1c');
    }

    /* --- Borang data impak --- */
    var PBL_IMPAK_FIELDS = ['pblMurid','pblTP1','pblTP2','pblTP3','pblTP4','pblTP5','pblTP6','pblSkor','pblRefleksi','pblMasalah'];
    function pblOrgIsiBorang(key) {
      var rec = pblOrgRekod(key);
      var imp = rec.impak || {};
      PBL_IMPAK_FIELDS.forEach(function (id) {
        var el = document.getElementById(id);
        if (!el) return;
        var v = imp[id];
        el.value = (v === undefined || v === null) ? '' : v;
      });
    }
    function pblOrgBacaBorang() {
      var imp = {};
      PBL_IMPAK_FIELDS.forEach(function (id) {
        var el = document.getElementById(id);
        if (!el) return;
        imp[id] = el.value;
      });
      return imp;
    }
    function pblNum(v) { var n = parseFloat(v); return isNaN(n) ? 0 : n; }

    /* --- Enjin analisis impak --- */
    function pblOrgAnalisis() {
      var imp = pblOrgBacaBorang();
      var murid = pblNum(imp.pblMurid);
      var tp = [1,2,3,4,5,6].map(function (i) { return pblNum(imp['pblTP' + i]); });
      var jumlahTP = tp.reduce(function (a, b) { return a + b; }, 0);
      // capai TP4+ = memuaskan ke atas (TP4,5,6)
      var capai = tp[3] + tp[4] + tp[5];
      var peratusCapai = jumlahTP > 0 ? (capai / jumlahTP) * 100 : 0;
      var skor = pblNum(imp.pblSkor);
      var gred, gredKelas;
      if (peratusCapai >= 80) { gred = 'Sangat Tinggi'; gredKelas = 'impak-good'; }
      else if (peratusCapai >= 60) { gred = 'Tinggi'; gredKelas = 'impak-good'; }
      else if (peratusCapai >= 40) { gred = 'Sederhana'; gredKelas = 'impak-warn'; }
      else if (peratusCapai > 0)  { gred = 'Rendah'; gredKelas = 'impak-bad'; }
      else { gred = 'Tiada Data'; gredKelas = ''; }
      var minTP = tp.indexOf(Math.min.apply(null, tp)) + 1;
      var maksTP = tp.indexOf(Math.max.apply(null, tp)) + 1;
      return { murid:murid, tp:tp, jumlahTP:jumlahTP, capai:capai, peratusCapai:peratusCapai,
               skor:skor, gred:gred, gredKelas:gredKelas, minTP:minTP, maksTP:maksTP,
               impak:imp, adaData: jumlahTP > 0 };
    }

    function pblOrgKira() {
      var key = (document.getElementById('pblOrgProjek') || {}).value;
      if (!key) return;
      var rec = pblOrgRekod(key);
      rec.impak = pblOrgBacaBorang();
      pblOrgSimpan();
      pblOrgProgres(key);
      var a = pblOrgAnalisis();
      var box = document.getElementById('pblStatBox');
      var kes = document.getElementById('pblKesimpulan');
      if (box) {
        if (!a.adaData) {
          box.innerHTML = '<div class="impak-box"><div class="val">—</div><div class="lbl">Belum ada data</div></div>';
        } else {
          box.innerHTML =
            '<div class="impak-box"><div class="val">' + a.murid + '</div><div class="lbl">Bil. Murid</div></div>' +
            '<div class="impak-box ' + a.gredKelas + '"><div class="val">' + a.peratusCapai.toFixed(1) + '%</div><div class="lbl">Capai TP4+</div></div>' +
            '<div class="impak-box"><div class="val">' + a.capai + '/' + a.jumlahTP + '</div><div class="lbl">Murid TP4+</div></div>' +
            '<div class="impak-box"><div class="val">' + (a.skor ? a.skor + '%' : '—') + '</div><div class="lbl">Skor Ujian</div></div>' +
            '<div class="impak-box ' + a.gredKelas + '"><div class="val" style="font-size:0.95rem;">' + a.gred + '</div><div class="lbl">Gred Impak</div></div>';
        }
      }
      if (kes) kes.innerHTML = pblOrgKesimpulanHtml(a);
      pblOrgJanaOPR();
    }

    function pblOrgKesimpulanHtml(a) {
      if (!a.adaData) {
        return '<em style="color:#64748b;">Belum ada data impak. Isi bilangan murid mengikut TP di atas — analisis akan dijana automatik.</em>';
      }
      var out = [];
      out.push('<strong>Ringkasan Impak:</strong> Daripada <strong>' + a.murid + '</strong> murid yang dinilai, ' +
               '<strong>' + a.capai + '</strong> murid (' + a.peratusCapai.toFixed(1) + '%) mencapai TP4 dan ke atas. ' +
               'Gred impak keseluruhan: <strong>' + a.gred + '</strong>.');
      out.push('<strong>Taburan TP:</strong> ' + a.tp.map(function (v, i) {
        return 'TP' + (i + 1) + '=' + v;
      }).join(', ') + '.');
      if (a.murid > 0 && a.jumlahTP !== a.murid) {
        out.push('<span style="color:#b45309;">⚠ Jumlah TP (' + a.jumlahTP + ') tidak sama dengan bilangan murid (' + a.murid + '). Sila semak data.</span>');
      }
      out.push('<strong>Kekuatan:</strong> Pencapaian tertinggi pada <strong>TP' + a.maksTP + '</strong>.');
      out.push('<strong>Kelemahan:</strong> Pencapaian terendah pada <strong>TP' + a.minTP + '</strong> — fokus pemulihan di sini.');
      if (a.skor) {
        var verdict = a.skor >= 70 ? 'MENCAPAI sasaran' : (a.skor >= 50 ? 'HAMPIR mencapai sasaran' : 'BELUM mencapai sasaran');
        out.push('<strong>Skor Ujian/Rubrik:</strong> ' + a.skor + '% — ' + verdict + ' (sasaran 70%).');
      }
      var ref = (a.impak.pblRefleksi || '').trim();
      if (ref) out.push('<strong>Refleksi Guru:</strong> ' + ref.replace(/</g, '&lt;'));
      var mas = (a.impak.pblMasalah || '').trim();
      if (mas) out.push('<strong>Penambahbaikan:</strong> ' + mas.replace(/</g, '&lt;'));
      return out.join('<br><br>');
    }

    /* --- Penjana OPR --- */
    function pblOrgJanaOPR() {
      var doc = document.getElementById('pblOprDoc');
      if (!doc) return;
      var key = (document.getElementById('pblOrgProjek') || {}).value;
      if (!key) { doc.textContent = 'Pilih projek dahulu.'; return; }
      var t = {};
      try { t = (PBL_TEMPLATES || {})[key] || {}; } catch (e) { }
      var a = pblOrgAnalisis();
      var rec = pblOrgRekod(key);
      var siap = PBL_ADDIE_FASA.filter(function (f) { return (rec.fasa[f.id] || {}).status === 'siap'; }).length;

      var html = '';
      html += '<h4>TAJUK PROJEK</h4><div>' + (t.tajuk || key) + '<br>' +
              '<strong>Kelas:</strong> ' + (t.kelas || '-') + ' | <strong>Subjek:</strong> ' + (t.subjek || '-') + '<br>' +
              '<strong>SK:</strong> ' + (t.sk || '-') + '<br>' +
              '<strong>SP:</strong> ' + (t.sp || '-') + '</div>';

      html += '<h4>O — OBJECTIVES (Objektif)</h4><ul>';
      var obj = Array.isArray(t.objektif) ? t.objektif : [];
      if (obj.length) { obj.forEach(function (o) { html += '<li>' + o + '</li>'; }); }
      else { html += '<li>' + (t.drivingQuestion || 'Menyelesaikan masalah melalui projek PBL.') + '</li>'; }
      html += '</ul>';

      html += '<h4>P — PROCESS (Proses / ADDIE)</h4><ul>';
      PBL_ADDIE_FASA.forEach(function (f) {
        var st = (rec.fasa[f.id] || {});
        var badge = { belum:'Belum', sedang:'Sedang', siap:'Siap' }[st.status || 'belum'];
        var tk = st.tarikh ? ' (' + st.tarikh + ')' : '';
        html += '<li><strong>' + f.nama + '</strong> — ' + badge + tk + '. ' + f.desc + '</li>';
      });
      html += '</ul><div style="font-size:0.78rem;color:#64748b;">Progres fasa: ' + siap + '/5 siap.</div>';

      html += '<h4>R — RESULTS (Hasil &amp; Impak)</h4>';
      if (!a.adaData) {
        html += '<div style="color:#b45309;">Data impak belum diisi. Sila isi bilangan murid mengikut TP untuk jana bahagian Results secara automatik.</div>';
      } else {
        html += '<ul>';
        html += '<li><strong>Bilangan murid dinilai:</strong> ' + a.murid + '</li>';
        html += '<li><strong>Murid mencapai TP4+:</strong> ' + a.capai + ' (' + a.peratusCapai.toFixed(1) + '%)</li>';
        html += '<li><strong>Taburan TP:</strong> ' + a.tp.map(function (v, i) { return 'TP' + (i + 1) + '=' + v; }).join(', ') + '</li>';
        if (a.skor) html += '<li><strong>Purata skor ujian/rubrik:</strong> ' + a.skor + '%</li>';
        html += '<li><strong>Gred impak:</strong> ' + a.gred + '</li>';
        html += '<li><strong>Kekuatan:</strong> TP' + a.maksTP + ' | <strong>Perlu pemulihan:</strong> TP' + a.minTP + '</li>';
        html += '</ul>';
        html += '<div style="background:#ecfdf5;border-radius:8px;padding:9px;font-size:0.8rem;"><strong>Kesimpulan Impak:</strong> ' +
                (a.peratusCapai >= 60
                  ? 'Projek PBL ini memberi impak POSITIF — majoriti murid mencapai TP4 ke atas. Model ADDIE berjaya dilaksanakan.'
                  : 'Projek dilaksanakan tetapi impak BELUM optimum — hanya ' + a.peratusCapai.toFixed(1) + '% mencapai TP4+. Perlu penambahbaikan pada fasa Develop/Implementation.') +
                '</div>';
        var ref = (a.impak.pblRefleksi || '').trim();
        if (ref) html += '<div style="margin-top:8px;"><strong>Refleksi Guru:</strong> ' + ref.replace(/</g, '&lt;') + '</div>';
        var mas = (a.impak.pblMasalah || '').trim();
        if (mas) html += '<div style="margin-top:6px;"><strong>Cadangan Penambahbaikan:</strong> ' + mas.replace(/</g, '&lt;') + '</div>';
      }
      doc.innerHTML = html;
      rec.opr = html;
      pblOrgSimpan();
    }

    function pblOrgCetak() {
      var key = (document.getElementById('pblOrgProjek') || {}).value;
      var t = {}; try { t = (PBL_TEMPLATES || {})[key] || {}; } catch (e) { }
      var doc = document.getElementById('pblOprDoc');
      if (!doc) return;
      var w = window.open('', '_blank');
      if (!w) { if (typeof showToast === 'function') showToast('Pelayar sekat tetingkap cetak.'); return; }
      w.document.write('<html><head><title>OPR - ' + (t.tajuk || 'PBL') + '</title>' +
        '<style>body{font-family:Arial,sans-serif;padding:28px;font-size:12pt;line-height:1.6;}' +
        'h4{color:#047857;margin:16px 0 5px;font-size:13pt;border-bottom:1px solid #d1d5db;padding-bottom:3px;}' +
        'ul{margin:5px 0 12px;padding-left:20px;}</style></head><body>' + doc.innerHTML + '</body></html>');
      w.document.close();
      setTimeout(function () { w.print(); }, 400);
    }

    function pblOrgEksportJson() {
      var json = {};
      Object.keys(pblOrgStore).forEach(function (k) {
        var r = pblOrgStore[k];
        json[k] = { fasa:r.fasa || {}, impak:r.impak || {} };
      });
      var blob = new Blob([JSON.stringify(json, null, 2)], { type:'application/json' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'organizer_pbl_' + new Date().toISOString().slice(0, 10) + '.json';
      a.click();
    }

    /* ===== [/PBL ORGANIZER v1] ===== */

"""


def patch_file(path, dry=False):
    p = os.path.join(BASE, path)
    if not os.path.exists(p):
        return f"SKIP (tiada): {p}"
    with open(p, "r", encoding="utf-8") as f:
        src = f.read()

    if MARK in src:
        return f"SUDAH DIPATCH: {path}"

    orig_len = len(src)
    changes = []

    # 1) CSS
    if CSS_ANCHOR in src:
        src = src.replace(CSS_ANCHOR, CSS_BLOCK + CSS_ANCHOR, 1)
        changes.append("css")
    else:
        changes.append("css=MISS")

    # 2) NAV
    if NAV_ANCHOR in src:
        src = src.replace(NAV_ANCHOR, NAV_BLOCK + NAV_ANCHOR, 1)
        changes.append("nav")
    else:
        changes.append("nav=MISS")

    # 3) HTML PANEL -> insert before closing of view-simpan-cetak? Better: before "</div>" of main content
    # Find the last </section> before the sidebar close / scripts. Use marker: the view-simpan-cetak section start,
    # insert panel right before it (so ordering stays sane).
    sec_anchor = '        <section id="view-simpan-cetak" class="view-panel">'
    if sec_anchor in src:
        src = src.replace(sec_anchor, HTML_PANEL + "\n" + sec_anchor, 1)
        changes.append("panel")
    else:
        changes.append("panel=MISS")

    # 4) TITLE in switchTab
    title_anchor = "          'simpan-cetak': 'Arkib & Cetakan RPH'"
    if title_anchor in src:
        src = src.replace(title_anchor, title_anchor + ",\n          'pbl-organizer': 'Organizer PBL (Timeline ADDIE & Impak)'", 1)
        changes.append("title")
    else:
        changes.append("title=MISS")

    # 5) JS
    if JS_ANCHOR in src:
        src = src.replace(JS_ANCHOR, JS_BLOCK + JS_ANCHOR, 1)
        changes.append("js")
    else:
        changes.append("js=MISS")

    # 6) hook init on switchTab
    hook_anchor = "        if (tabId === 'simpan-cetak') { try { syncRphMirror(); } catch (e) { } }"
    if hook_anchor in src:
        src = src.replace(hook_anchor,
            hook_anchor + "\n        if (tabId === 'pbl-organizer') { try { pblOrgInit(); } catch (e) { } }", 1)
        changes.append("hook")
    else:
        changes.append("hook=MISS")

    if not dry:
        shutil.copy2(p, p + ".bak_pblorg")
        with open(p, "w", encoding="utf-8") as f:
            f.write(src)

    return f"{path}: {', '.join(changes)} ({orig_len} -> {len(src)} bytes)"


if __name__ == "__main__":
    for t in TARGETS:
        print(patch_file(t, dry=("--dry" in sys.argv)))
