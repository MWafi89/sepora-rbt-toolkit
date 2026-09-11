# -*- coding: utf-8 -*-
"""SEPORA RBT TOOLKIT - Arkib RPH v2 patch
Tambah: auto-simpan janaan, edit rekod arkib, guna semula utk RPH berikutnya,
eksport/import JSON, fix rujukan template (formRphTahap hilang) + buang fungsi arkib bertindih.
"""
import io, re, sys, shutil, os

P = r"D:\SEPORA TOOLKIT\index.html"
s = io.open(P, encoding="utf-8").read()
orig = s

def rep(old, new, cnt=1, label=""):
    global s
    n = s.count(old)
    assert n == cnt, "ANCHOR %s: jumpa %d (jangka %d)\n%s" % (label, n, cnt, old[:120])
    s = s.replace(old, new, cnt)
    print("OK  %-42s (%d x)" % (label, cnt))

# ---------------------------------------------------------------- C1: hidden formRphTahap
rep(
"""            </div>

            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:1rem;">
              <div class="form-group">
                <label class="form-label">Jenis Pendekatan / Tajuk Projek</label>""",
"""            </div>

            <!-- Kunci templat PBL yang sedang aktif (dibaca oleh autoGenerateSmartRph & Arkib RPH) -->
            <input type="hidden" id="formRphTahap" value="4_kereta_idamanku">

            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:1rem;">
              <div class="form-group">
                <label class="form-label">Jenis Pendekatan / Tajuk Projek</label>""",
1, "C1 hidden #formRphTahap")

# ---------------------------------------------------------------- C2: track key dlm loadPblRbtTemplate
rep(
"""      const tmpl = PBL_TEMPLATES[key] || PBL_TEMPLATES["4_kereta_idamanku"];

      const formTahap = document.getElementById('formRphTahap');""",
"""      const tmpl = PBL_TEMPLATES[key] || PBL_TEMPLATES["4_kereta_idamanku"];
      window.__rphTemplKey = key;

      const formTahap = document.getElementById('formRphTahap');""",
1, "C2 __rphTemplKey")

# ---------------------------------------------------------------- C3: autoGenerate guna key sebenar
rep(
"""      let formTahapVal = document.getElementById('formRphTahap')?.value || "4_kereta_idamanku";
      if (formTahapVal == "4") formTahapVal = "4_kereta_idamanku";
      if (formTahapVal == "5") formTahapVal = "5_rumah_tangga";
      if (formTahapVal == "6") formTahapVal = "6_kereta_kawalan";""",
"""      let formTahapVal = document.getElementById('formRphTahap')?.value || window.__rphTemplKey || "4_kereta_idamanku";
      if (formTahapVal == "4") formTahapVal = "4_kereta_idamanku";
      if (formTahapVal == "5") formTahapVal = "5_rumah_tangga";
      if (formTahapVal == "6") formTahapVal = "6_kereta_kawalan";
      if (!PBL_TEMPLATES[formTahapVal]) formTahapVal = "4_kereta_idamanku";
      window.__rphTemplKey = formTahapVal;""",
1, "C3 autoGenerate templat key")

# ---------------------------------------------------------------- C4: auto-simpan di hujung autoGenerate
rep(
"""      // Papar janaan terkini di sidebar & kira badge Arkib
      updateSidebarJanaan();
      updateArkibBadge();
    }""",
"""      // Papar janaan terkini di sidebar & kira badge Arkib
      updateSidebarJanaan();
      updateArkibBadge();
      // AUTO-SIMPAN: setiap janaan masuk Arkib (rekod sedia ada dikemas kini, bukan bertindih)
      arkibAutoSimpan();
    }""",
1, "C4 panggil arkibAutoSimpan")

# ---------------------------------------------------------------- C5: ganti SEMUA blok arkib lama dgn Arkib v2
start_anchor = "    function saveCurrentGeneratedRph() {"
end_anchor = "    // ===== EKSPORT RPH: PDF & Word (.docx) ====="
i0 = s.index(start_anchor)
i1 = s.index(end_anchor)
assert i1 > i0
old_block = s[i0:i1]
assert "function deleteSavedRph" in old_block and old_block.count("function renderSavedRphTable") == 2, "blok lama tak seperti dijangka"
print("OK  blok arkib lama: %d aksara dibuang (2x render/save/view bertindih + delete)" % len(old_block))

ARKIB = r"""    /* ============================================================
       ARKIB RPH v2 (2026-09-11)
       - Setiap "Jana RPH" auto-simpan ke Arkib sebagai Draf Dijana
       - "Simpan Janaan Semasa" kunci rekod + salinan dokumen penuh
       - Edit rekod arkib (modal) / sunting dokumen contenteditable lalu kemas kini
       - "Guna untuk RPH Baharu" = salinan rekod + tarikh dicadang +1 minggu
       - Eksport / Import JSON sebagai sandaran (storan pelayar terhad)
       ============================================================ */
    let currentArkibId = null;

    function arkibNow() { return new Date().toISOString(); }
    function escAttr(v) { return esc(String(v == null ? '' : v)).replace(/"/g, '&quot;'); }
    function arkibDMY(t) {
      const m = String(t == null ? '' : t).match(/(\d{1,2})\/(\d{1,2})\/(\d{4})/);
      if (!m) return '';
      return m[3] + '-' + ('0' + m[2]).slice(-2) + '-' + ('0' + m[1]).slice(-2);
    }
    function arkibISOtoDMY(d) {
      const p = String(d || '').split('-');
      return p.length === 3 ? p[2] + '/' + p[1] + '/' + p[0] : (d || '-');
    }
    function arkibShiftDate(iso, hari) {
      const m = String(iso || '').match(/^(\d{4})-(\d{2})-(\d{2})$/);
      if (!m) return iso || '';
      const d = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
      d.setDate(d.getDate() + (hari || 7));
      return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
    }
    function arkibNormalize(list) {
      if (!Array.isArray(list)) return [];
      return list.map(function (r) {
        r = r || {};
        return {
          id: Number(r.id) || Date.now(),
          templateKey: r.templateKey || '',
          hari: r.hari || 'Isnin',
          masa: r.masa || '08:00 - 09:30',
          kelas: r.kelas || '',
          subjek: r.subjek || 'RBT',
          minggu: r.minggu == null ? '' : String(r.minggu),
          tajuk: r.tajuk || 'Projek PBL RBT',
          sk: r.sk || '',
          sp: r.sp || '',
          bukuTeks: r.bukuTeks || '',
          pblMingguPelaksanaan: r.pblMingguPelaksanaan || '',
          pblTarikhMula: r.pblTarikhMula || '',
          pblTarikhHantar: r.pblTarikhHantar || '',
          nota: r.nota || '',
          status: r.status || 'Disimpan',
          saved: !!r.saved,
          auto: !!r.auto,
          created: r.created || '',
          dikemas: r.dikemas || '',
          docHtml: r.docHtml || ''
        };
      });
    }
    function arkibPersist() {
      try {
        localStorage.setItem('erph_saved', JSON.stringify(savedRphList));
        return true;
      } catch (e) {
        // Kuota pelayar penuh: kekalkan metadata, ringkaskan salinan dokumen rekod lama
        let drop = 0;
        for (let i = 5; i < savedRphList.length; i++) {
          if (savedRphList[i].docHtml) { savedRphList[i].docHtml = ''; drop++; }
        }
        try {
          localStorage.setItem('erph_saved', JSON.stringify(savedRphList));
          if (drop) showToast('Storan hampir penuh - salinan dokumen ' + drop + ' rekod lama diringkaskan (tarikh & maklumat kekal).');
          return true;
        } catch (e2) {
          showToast('Storan pelayar penuh. Guna "Eksport Arkib (JSON)" sebagai sandaran.');
          return false;
        }
      }
    }
    function arkibFormVal(id) { const el = document.getElementById(id); return el && el.value ? String(el.value).trim() : ''; }
    function arkibPrevTxt(id) { const el = document.getElementById(id); return el && el.innerText ? String(el.innerText).trim() : ''; }
    function arkibSetVal(id, val) {
      const el = document.getElementById(id);
      if (!el || val == null || val === '') return;
      if (el.tagName === 'SELECT') {
        const ok = Array.prototype.some.call(el.options || [], function (o) { return String(o.value) === String(val) || String(o.text) === String(val); });
        if (!ok) {
          try { const opt = document.createElement('option'); opt.value = String(val); opt.text = String(val); el.appendChild(opt); } catch (e) { }
        }
        try { el.value = String(val); } catch (e) { }
        return;
      }
      el.value = String(val);
    }
    function arkibSnapshot() {
      return {
        templateKey: arkibFormVal('formRphTahap') || (typeof window !== 'undefined' && window.__rphTemplKey ? window.__rphTemplKey : ''),
        hari: arkibFormVal('formRphHari') || arkibPrevTxt('previewHariTarikh'),
        masa: arkibFormVal('formRphMasa') || arkibPrevTxt('previewMasa'),
        kelas: arkibFormVal('formRphKelas') || arkibPrevTxt('previewKelas'),
        subjek: arkibFormVal('formRphSubjek') || arkibPrevTxt('previewSubjek'),
        minggu: arkibFormVal('formRphMinggu') || String((typeof currentWeek !== 'undefined' && currentWeek) ? currentWeek : ''),
        tajuk: arkibFormVal('formRphTajuk') || arkibPrevTxt('previewTajuk'),
        sk: arkibFormVal('formRphSk') || arkibPrevTxt('previewSK'),
        sp: arkibFormVal('formRphSp') || arkibPrevTxt('previewSP'),
        bukuTeks: arkibFormVal('formRphBukuTeks') || arkibPrevTxt('previewBukuTeksRef'),
        pblMingguPelaksanaan: arkibFormVal('formPblMingguPelaksanaan') || arkibPrevTxt('previewPblMingguTempoh'),
        pblTarikhMula: arkibFormVal('formPblTarikhMula') || arkibDMY(arkibPrevTxt('previewPblTarikhMula')),
        pblTarikhHantar: arkibFormVal('formPblTarikhHantar') || arkibDMY(arkibPrevTxt('previewPblTarikhHantar'))
      };
    }
    function arkibDocHtml() {
      const el = document.getElementById('rphPreviewContainer');
      return el ? el.innerHTML : '';
    }
    function arkibSameTarget(a, b) {
      return String(a.templateKey || '') === String(b.templateKey || '') &&
        String(a.minggu || '') === String(b.minggu || '') &&
        String(a.kelas || '') === String(b.kelas || '') &&
        String(a.hari || '') === String(b.hari || '');
    }
    function arkibFindRecord(snap) {
      if (currentArkibId) {
        const cur = savedRphList.find(function (r) { return r.id === currentArkibId; });
        if (cur && arkibSameTarget(cur, snap)) return cur;
      }
      return savedRphList.find(function (r) { return arkibSameTarget(r, snap); });
    }
    function applyArkibToForm(r) {
      arkibSetVal('formRphTahap', r.templateKey);
      arkibSetVal('formRphHari', r.hari);
      arkibSetVal('formRphMasa', r.masa);
      arkibSetVal('formRphKelas', r.kelas);
      arkibSetVal('formRphSubjek', r.subjek);
      arkibSetVal('formRphMinggu', r.minggu);
      arkibSetVal('formRphTajuk', r.tajuk);
      arkibSetVal('formRphSk', r.sk);
      arkibSetVal('formRphSp', r.sp);
      arkibSetVal('formRphBukuTeks', r.bukuTeks);
      arkibSetVal('formPblMingguPelaksanaan', r.pblMingguPelaksanaan);
      arkibSetVal('formPblTarikhMula', r.pblTarikhMula);
      arkibSetVal('formPblTarikhHantar', r.pblTarikhHantar);
    }
    function updateArkibSelectedInfo() {
      const box = document.getElementById('arkibSelectedInfo');
      if (!box) return;
      const r = currentArkibId ? savedRphList.find(function (x) { return x.id === currentArkibId; }) : null;
      if (!r) { box.innerHTML = 'Tiada rekod dipilih. Klik <strong>Papar</strong> pada senarai di bawah untuk buka &amp; sunting sesuatu RPH.'; return; }
      box.innerHTML = 'Rekod dipilih: <strong>' + esc(r.tajuk) + '</strong> &bull; ' + esc(r.kelas || '-') + ' &bull; M' + esc(r.minggu || '-') +
        ' &bull; Status: <strong>' + esc(r.status || '-') + '</strong>' + (r.dikemas ? ' &bull; dikemas kini ' + esc(String(r.dikemas).slice(0, 16).replace('T', ' ')) : '');
    }

    /* --- Auto-simpan setiap janaan (tanpa ganggu proses jana) --- */
    function arkibAutoSimpan() {
      try {
        const snap = arkibSnapshot();
        if (!snap.tajuk) return;
        let rec = arkibFindRecord(snap);
        if (rec) {
          Object.assign(rec, snap, { dikemas: arkibNow() });
          if (!rec.saved) rec.status = 'Draf Dijana';
        } else {
          rec = Object.assign({ id: Date.now(), created: arkibNow(), auto: true, saved: false, status: 'Draf Dijana', nota: '', docHtml: '' }, snap);
          savedRphList.unshift(rec);
        }
        currentArkibId = rec.id;
        arkibPersist();
        renderSavedRphTable();
        updateArkibBadge();
        updateDashboardMetrics();
        updateArkibSelectedInfo();
      } catch (e) { /* jangan sesekali ganggu penjanaan RPH */ }
    }

    /* --- Simpan manual (kunci rekod + salinan dokumen penuh) --- */
    function saveCurrentGeneratedRph(forceNew) {
      const snap = arkibSnapshot();
      if (!snap.tajuk) { showToast('Tiada RPH untuk disimpan. Tekan "Jana RPH" dahulu.'); return; }
      const now = arkibNow();
      let rec = forceNew ? null : arkibFindRecord(snap);
      if (rec) {
        Object.assign(rec, snap, { dikemas: now });
        rec.saved = true;
        if (!rec.status || rec.status === 'Draf Dijana') rec.status = 'Disimpan';
      } else {
        rec = Object.assign({ id: Date.now(), created: now, auto: false, saved: true, status: 'Disimpan', nota: '', docHtml: '' }, snap);
        savedRphList.unshift(rec);
      }
      rec.docHtml = arkibDocHtml();
      currentArkibId = rec.id;
      arkibPersist();
      renderSavedRphTable();
      updateArkibBadge();
      updateDashboardMetrics();
      updateArkibSelectedInfo();
      showToast('RPH "' + rec.tajuk + '" ' + (forceNew ? 'disimpan sebagai rekod baharu' : 'disimpan ke Arkib') + ' (' + (rec.pblMingguPelaksanaan || 'M' + rec.minggu) + ').');
    }

    /* --- Jadual arkib --- */
    function renderSavedRphTable() {
      const tbody = document.getElementById('savedRphTableBody');
      const recentList = document.getElementById('recentRphList');
      if (!tbody) return;

      if (!savedRphList.length) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:1.5rem; color:var(--text-muted);">
          Belum ada RPH disimpan. Bina RPH pada modul Bina RPH - setiap janaan akan tersimpan di sini secara automatik.<br>
          <button class="btn btn-primary btn-sm" style="margin-top:0.6rem;" onclick="switchTab('bina-rph')"><i class="fa-solid fa-wand-magic-sparkles"></i> Bina RPH Sekarang</button>
        </td></tr>`;
        if (recentList) {
          recentList.innerHTML = `<p style="color:var(--text-muted); font-size:0.85rem;">Tiada RPH dibina lagi. Mulakan dengan menekan butang <strong>Bina RPH</strong>.</p>`;
        }
        updateArkibSelectedInfo();
        return;
      }

      tbody.innerHTML = savedRphList.map(r => `
        <tr${r.id === currentArkibId ? ' style="background:rgba(26,115,232,0.06);"' : ''}>
          <td><strong>${esc(r.hari)}</strong></td>
          <td><span class="badge" style="background:var(--primary-light); color:var(--primary); font-weight:700; padding:2px 8px; border-radius:4px;">M${esc(r.minggu)}</span></td>
          <td>
            <div style="font-size:0.8rem; font-weight:600; color:var(--primary);">${esc(r.pblMingguPelaksanaan || '-')}</div>
            <div style="font-size:0.75rem; color:#dc2626; margin-top:2px;">
              <i class="fa-solid fa-flag-checkered"></i> <strong>Hantar:</strong> ${esc(arkibISOtoDMY(r.pblTarikhHantar))}
            </div>
          </td>
          <td>${esc(r.masa)}</td>
          <td>${esc(r.kelas)} - ${esc(r.subjek)}</td>
          <td>${esc(r.tajuk)}${r.nota ? ' <i class="fa-solid fa-note-sticky" title="Ada nota guru" style="color:#f59e0b;"></i>' : ''}</td>
          <td>
            <span class="badge" style="background:var(--secondary-light); color:var(--secondary); font-weight:700; padding:2px 8px; border-radius:4px;"><i class="fa-solid fa-circle-check"></i> ${esc(r.status || 'Disimpan')}</span>
            <div style="font-size:0.68rem; color:var(--text-muted); margin-top:3px;">${esc(String(r.dikemas || r.created || '').slice(0, 16).replace('T', ' '))}</div>
          </td>
          <td style="text-align:center; white-space:nowrap;">
            <button class="btn btn-sm btn-primary" onclick="viewSavedRph(${r.id})" title="Buka dokumen RPH"><i class="fa-solid fa-eye"></i> Papar</button>
            <button class="btn btn-sm btn-outline" onclick="openArkibEditModal(${r.id})" title="Edit maklumat rekod"><i class="fa-solid fa-pen-to-square"></i></button>
            <button class="btn btn-sm btn-outline" style="color:#7c3aed; border-color:#c4b5fd;" onclick="reuseArkibRph(${r.id})" title="Guna rekod ini untuk RPH baharu (tarikh +1 minggu)"><i class="fa-solid fa-clone"></i></button>
            <button class="btn btn-sm btn-outline" style="color:var(--danger);" onclick="deleteSavedRph(${r.id})" title="Padam rekod"><i class="fa-solid fa-trash"></i></button>
          </td>
        </tr>
      `).join('');

      if (recentList) {
        recentList.innerHTML = savedRphList.slice(0, 3).map(r => `
          <div style="padding:0.75rem 0; border-bottom:1px solid var(--surface-border); display:flex; justify-content:space-between; align-items:center; gap:0.5rem;">
            <div>
              <div style="font-weight:600; font-size:0.9rem;">${esc(r.tajuk)}</div>
              <div style="font-size:0.78rem; color:var(--text-muted);">${esc(r.hari)} &bull; ${esc(r.kelas)} &bull; M${esc(r.minggu)} | <span style="color:#dc2626; font-weight:600;">Hantar: ${esc(arkibISOtoDMY(r.pblTarikhHantar))}</span></div>
            </div>
            <button class="btn btn-sm btn-outline" onclick="viewSavedRph(${r.id})"><i class="fa-solid fa-arrow-right"></i></button>
          </div>
        `).join('');
      }
      updateArkibSelectedInfo();
    }

    function viewSavedRph(id) {
      const r = savedRphList.find(item => item.id === id);
      if (!r) return;
      currentArkibId = r.id;
      if (r.templateKey) { try { loadPblRbtTemplate(r.templateKey); } catch (e) { } }
      applyArkibToForm(r);
      switchTab('bina-rph');
      const el = document.getElementById('rphPreviewContainer');
      if (el && r.docHtml) {
        el.innerHTML = r.docHtml;
        updateSidebarJanaan();
        showToast('Dokumen RPH "' + r.tajuk + '" dibuka dari salinan arkib. Sunting terus, kemudian tekan "Kemas Kini Rekod Terpilih".');
      } else {
        autoGenerateSmartRph();
        showToast('RPH "' + r.tajuk + '" dibuka berserta tarikh hantar PBL!');
      }
      renderSavedRphTable();
    }

    /* --- Guna semula rekod untuk RPH berikutnya --- */
    function reuseArkibRph(id) {
      const src = savedRphList.find(function (x) { return x.id === id; });
      if (!src) return;
      closeModalDirectly();
      const copy = Object.assign({}, src, {
        id: Date.now(), created: arkibNow(), dikemas: arkibNow(),
        status: 'Draf Dijana', saved: false, auto: false, docHtml: '',
        pblTarikhMula: arkibShiftDate(src.pblTarikhMula, 7),
        pblTarikhHantar: arkibShiftDate(src.pblTarikhHantar, 7)
      });
      Object.assign(copy, arkibTempohDariTarikh(copy));
      savedRphList.unshift(copy);
      currentArkibId = copy.id;
      arkibPersist(); renderSavedRphTable(); updateArkibBadge(); updateDashboardMetrics(); updateArkibSelectedInfo();
      if (copy.templateKey) { try { loadPblRbtTemplate(copy.templateKey); } catch (e) { } }
      applyArkibToForm(copy);
      switchTab('bina-rph');
      autoGenerateSmartRph();
      showToast('RPH baharu dari rekod "' + src.tajuk + '" (tarikh dicadang +1 minggu). Kemas kini tarikh/minggu lalu tekan "Simpan Janaan Semasa".');
    }
    function arkibTempohDariTarikh(r) {
      const m = String(r.pblTarikhMula || '').match(/^(\d{4})-(\d{2})-(\d{2})$/);
      const h = String(r.pblTarikhHantar || '').match(/^(\d{4})-(\d{2})-(\d{2})$/);
      if (!m || !h) return {};
      const d1 = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
      const d2 = new Date(Number(h[1]), Number(h[2]) - 1, Number(h[3]));
      if (isNaN(d1) || isNaN(d2) || d2 < d1) return {};
      const nWk = Math.max(1, Math.ceil(Math.round((d2 - d1) / 86400000) / 7));
      const w1 = (parseInt(r.minggu, 10) || (typeof currentWeek !== 'undefined' ? currentWeek : 12));
      return { pblMingguPelaksanaan: 'Minggu ' + w1 + ' hingga Minggu ' + (w1 + nWk - 1) + ' (' + nWk + ' Minggu)' };
    }

    /* --- Edit rekod arkib (modal) --- */
    function openArkibEditModal(id) {
      const r = savedRphList.find(function (x) { return x.id === id; });
      if (!r) return;
      currentArkibId = r.id;
      const statusOpts = ['Draf Dijana', 'Disimpan', 'Sedang Dilaksana', 'Selesai Dilaksana', 'Disemak Pentadbir'];
      const html = `
        <div class="card-header">
          <h3><i class="fa-solid fa-pen-to-square" style="color:var(--primary); margin-right:6px;"></i> Edit Rekod Arkib RPH</h3>
          <button class="btn-icon" onclick="closeModalDirectly()"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.85rem;">
          Kemas kini maklumat rekod ini. Perubahan disimpan dalam Arkib dan boleh diguna semula untuk RPH berikutnya.
        </p>
        <form onsubmit="submitArkibEdit(event, ${r.id})">
          <div class="form-group">
            <label class="form-label">Tajuk / Projek PdPc</label>
            <input type="text" id="arkibEditTajuk" class="form-control" value="${escAttr(r.tajuk)}">
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem;">
            <div class="form-group">
              <label class="form-label">Tarikh / Hari</label>
              <input type="text" id="arkibEditHari" class="form-control" value="${escAttr(r.hari)}">
            </div>
            <div class="form-group">
              <label class="form-label">Minggu</label>
              <input type="number" min="1" max="42" id="arkibEditMinggu" class="form-control" value="${escAttr(r.minggu)}">
            </div>
            <div class="form-group">
              <label class="form-label">Masa</label>
              <input type="text" id="arkibEditMasa" class="form-control" value="${escAttr(r.masa)}">
            </div>
            <div class="form-group">
              <label class="form-label">Kelas</label>
              <input type="text" id="arkibEditKelas" class="form-control" value="${escAttr(r.kelas)}">
            </div>
            <div class="form-group">
              <label class="form-label">Subjek</label>
              <input type="text" id="arkibEditSubjek" class="form-control" value="${escAttr(r.subjek)}">
            </div>
            <div class="form-group">
              <label class="form-label">Status</label>
              <select id="arkibEditStatus" class="form-select">
                ${statusOpts.map(s => `<option${s === r.status ? ' selected' : ''}>${s}</option>`).join('')}
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Tarikh Mula PBL</label>
              <input type="date" id="arkibEditTarikhMula" class="form-control" value="${escAttr(r.pblTarikhMula)}">
            </div>
            <div class="form-group">
              <label class="form-label">Tarikh Hantar PBL</label>
              <input type="date" id="arkibEditTarikhHantar" class="form-control" value="${escAttr(r.pblTarikhHantar)}">
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Tempoh Pelaksanaan (Minggu ...)</label>
            <input type="text" id="arkibEditTempoh" class="form-control" value="${escAttr(r.pblMingguPelaksanaan)}">
          </div>
          <div class="form-group">
            <label class="form-label">Standard Kandungan (SK)</label>
            <input type="text" id="arkibEditSk" class="form-control" value="${escAttr(r.sk)}">
          </div>
          <div class="form-group">
            <label class="form-label">Standard Pembelajaran (SP)</label>
            <textarea id="arkibEditSp" class="form-control" rows="3">${esc(r.sp)}</textarea>
          </div>
          <div class="form-group">
            <label class="form-label">Nota / Catatan Guru</label>
            <textarea id="arkibEditNota" class="form-control" rows="3" placeholder="cth: tambah aktiviti pemulihan, tarikh hantar ditunda...">${esc(r.nota)}</textarea>
          </div>
          <div style="display:flex; justify-content:space-between; gap:0.5rem; flex-wrap:wrap;">
            <button type="button" class="btn btn-outline" style="color:#7c3aed; border-color:#c4b5fd;" onclick="reuseArkibRph(${r.id})"><i class="fa-solid fa-clone"></i> Guna untuk RPH Baharu</button>
            <div style="display:flex; gap:0.5rem;">
              <button type="button" class="btn btn-outline" onclick="closeModalDirectly()">Batal</button>
              <button type="submit" class="btn btn-primary"><i class="fa-solid fa-floppy-disk"></i> Simpan Perubahan</button>
            </div>
          </div>
        </form>`;
      openModal(html);
    }

    function submitArkibEdit(ev, id) {
      if (ev && ev.preventDefault) ev.preventDefault();
      const r = savedRphList.find(function (x) { return x.id === id; });
      if (!r) return;
      const v = function (i) { const el = document.getElementById(i); return el && el.value != null ? String(el.value).trim() : ''; };
      r.tajuk = v('arkibEditTajuk') || r.tajuk;
      r.hari = v('arkibEditHari') || r.hari;
      r.minggu = v('arkibEditMinggu') || r.minggu;
      r.masa = v('arkibEditMasa') || r.masa;
      r.kelas = v('arkibEditKelas');
      r.subjek = v('arkibEditSubjek') || r.subjek;
      r.pblTarikhMula = v('arkibEditTarikhMula');
      r.pblTarikhHantar = v('arkibEditTarikhHantar');
      r.pblMingguPelaksanaan = v('arkibEditTempoh') || r.pblMingguPelaksanaan;
      r.sk = v('arkibEditSk');
      r.sp = v('arkibEditSp');
      r.nota = v('arkibEditNota');
      const st = document.getElementById('arkibEditStatus');
      if (st && st.value) r.status = st.value;
      r.saved = (r.status !== 'Draf Dijana');
      Object.assign(r, arkibTempohDariTarikh(r));
      r.dikemas = arkibNow();
      arkibPersist(); renderSavedRphTable(); updateArkibBadge(); updateDashboardMetrics(); updateArkibSelectedInfo();
      closeModalDirectly();
      showToast('Rekod arkib "' + r.tajuk + '" dikemas kini.');
    }

    /* --- Kemas kini rekod drpd suntingan dokumen (contenteditable) --- */
    function updateArkibFromPreview() {
      if (!currentArkibId) { showToast('Tiada rekod dipilih. Tekan "Papar" pada senarai arkib dahulu.'); return; }
      const r = savedRphList.find(function (x) { return x.id === currentArkibId; });
      if (!r) { showToast('Rekod tidak dijumpai dalam arkib.'); return; }
      const pv = function (id) { const el = document.getElementById(id); return el && el.innerText ? String(el.innerText).trim() : ''; };
      const mgg = (pv('previewMinggu').match(/\d+/) || [])[0];
      Object.assign(r, {
        hari: pv('previewHariTarikh') || r.hari,
        masa: pv('previewMasa') || r.masa,
        kelas: pv('previewKelas') || r.kelas,
        subjek: pv('previewSubjek') || r.subjek,
        minggu: mgg || r.minggu,
        tajuk: pv('previewTajuk') || r.tajuk,
        sk: pv('previewSK') || r.sk,
        sp: pv('previewSP') || r.sp,
        bukuTeks: pv('previewBukuTeksRef') || r.bukuTeks,
        pblMingguPelaksanaan: pv('previewPblMingguTempoh') || r.pblMingguPelaksanaan,
        pblTarikhMula: arkibDMY(pv('previewPblTarikhMula')) || r.pblTarikhMula,
        pblTarikhHantar: arkibDMY(pv('previewPblTarikhHantar')) || r.pblTarikhHantar,
        docHtml: arkibDocHtml(),
        dikemas: arkibNow(),
        saved: true
      });
      if (!r.status || r.status === 'Draf Dijana') r.status = 'Disimpan';
      arkibPersist(); renderSavedRphTable(); updateArkibBadge(); updateDashboardMetrics(); updateArkibSelectedInfo();
      showToast('Rekod "' + r.tajuk + '" dikemas kini bersama suntingan dokumen.');
    }

    /* --- Padam --- */
    function deleteSavedRph(id) {
      const r = savedRphList.find(function (x) { return x.id === id; });
      if (!r) return;
      const html = `
        <div class="card-header">
          <h3><i class="fa-solid fa-triangle-exclamation" style="color:var(--danger); margin-right:6px;"></i> Padam Rekod Arkib</h3>
          <button class="btn-icon" onclick="closeModalDirectly()"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div style="background:var(--danger-light); border:1px solid rgba(234,67,53,0.3); border-radius:8px; padding:1rem; margin-bottom:1rem;">
          <p style="font-size:0.9rem; font-weight:600; color:var(--danger); margin-bottom:0.4rem;">Adakah anda pasti mahu memadam rekod ini?</p>
          <p style="font-size:0.95rem; font-weight:700; color:var(--text); margin-bottom:0.3rem;">"${esc(r.tajuk)}"</p>
          <p style="font-size:0.82rem; color:var(--text-muted);">${esc(r.kelas || '-')} &bull; M${esc(r.minggu || '-')} &bull; Hantar: ${esc(arkibISOtoDMY(r.pblTarikhHantar))}</p>
        </div>
        <div style="display:flex; justify-content:flex-end; gap:0.5rem;">
          <button class="btn btn-outline" onclick="closeModalDirectly()">Batal</button>
          <button class="btn btn-danger" onclick="executeArkibDelete(${r.id})"><i class="fa-solid fa-trash"></i> Ya, Padam</button>
        </div>`;
      openModal(html);
    }
    function executeArkibDelete(id) {
      const r = savedRphList.find(function (x) { return x.id === id; });
      savedRphList = savedRphList.filter(function (item) { return item.id !== id; });
      if (currentArkibId === id) currentArkibId = null;
      arkibPersist(); closeModalDirectly(); renderSavedRphTable(); updateArkibBadge(); updateDashboardMetrics(); updateArkibSelectedInfo();
      showToast('Rekod RPH ' + (r ? '"' + r.tajuk + '" ' : '') + 'dipadam daripada arkib.');
    }

    /* --- Sandaran: eksport / import JSON --- */
    function exportArkibJson() {
      if (!savedRphList.length) { showToast('Arkib kosong - tiada rekod untuk dieksport.'); return; }
      const data = { app: 'SEPORA RBT TOOLKIT', jenis: 'arkib-rph', versi: 2, tarikh: arkibNow(), rekod: savedRphList };
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'arkib_rph_sepora_' + arkibNow().slice(0, 10) + '.json';
      document.body.appendChild(a); a.click(); document.body.removeChild(a);
      showToast('Arkib (' + savedRphList.length + ' rekod) dieksport sebagai fail JSON.');
    }
    function importArkibJson(ev) {
      const f = ev && ev.target && ev.target.files ? ev.target.files[0] : null;
      if (!f) return;
      const target = ev.target;
      const rd = new FileReader();
      rd.onload = function () {
        try {
          const data = JSON.parse(rd.result);
          const rows = Array.isArray(data) ? data : (data.rekod || data.records || []);
          const norm = arkibNormalize(rows);
          let added = 0;
          norm.forEach(function (n) {
            const dup = savedRphList.some(function (x) {
              return x.id === n.id || (x.tajuk === n.tajuk && String(x.minggu) === String(n.minggu) && String(x.kelas) === String(n.kelas));
            });
            if (!dup) { savedRphList.push(n); added++; }
          });
          savedRphList.sort(function (a, b) { return (Number(b.id) || 0) - (Number(a.id) || 0); });
          arkibPersist(); renderSavedRphTable(); updateArkibBadge(); updateDashboardMetrics(); updateArkibSelectedInfo();
          showToast('Import selesai - ' + added + ' rekod ditambah (arkib kini ' + savedRphList.length + ' rekod).');
        } catch (e) {
          showToast('Fail JSON tidak sah atau rosak.');
        }
        if (target) target.value = '';
      };
      rd.readAsText(f);
    }

"""

s = s[:i0] + ARKIB + s[i1:]

# ---------------------------------------------------------------- C6: toolbar Arkib
rep(
"""          <div class="card">
            <div class="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Tarikh / Hari</th>""",
"""          <div class="card" style="border-left:4px solid #059669;">
            <div class="card-header">
              <h3 style="font-size:1.05rem;"><i class="fa-solid fa-box-archive" style="color:#059669; margin-right:6px;"></i> Simpan, Edit &amp; Guna Semula RPH</h3>
              <span style="font-size:0.8rem; color:var(--text-muted);">Janaan tersimpan automatik &bull; boleh diedit &amp; diguna untuk RPH berikutnya</span>
            </div>
            <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.75rem;">
              Setiap kali <strong>Jana RPH</strong> ditekan, RPH terus masuk Arkib sebagai <em>Draf Dijana</em>.
              Tekan <strong>Simpan Janaan Semasa</strong> untuk mengunci rekod + menyimpan salinan penuh dokumen (termasuk suntingan tajuk/tarikh pada dokumen).
            </p>
            <div style="display:flex; gap:0.5rem; flex-wrap:wrap; align-items:center;">
              <button class="btn btn-primary" onclick="saveCurrentGeneratedRph()"><i class="fa-solid fa-floppy-disk"></i> Simpan Janaan Semasa</button>
              <button class="btn btn-outline" onclick="saveCurrentGeneratedRph(true)"><i class="fa-solid fa-plus"></i> Simpan sebagai Rekod Baharu</button>
              <button class="btn btn-outline" onclick="updateArkibFromPreview()"><i class="fa-solid fa-rotate"></i> Kemas Kini Rekod Terpilih</button>
              <button class="btn btn-outline" style="border-color:#c4b5fd; color:#6d28d9;" onclick="exportArkibJson()"><i class="fa-solid fa-file-export"></i> Eksport Arkib (JSON)</button>
              <button class="btn btn-outline" style="border-color:#c4b5fd; color:#6d28d9;" onclick="document.getElementById('arkibImportInput').click()"><i class="fa-solid fa-file-import"></i> Import Arkib (JSON)</button>
              <input type="file" id="arkibImportInput" accept="application/json,.json" style="display:none" onchange="importArkibJson(event)">
            </div>
            <div id="arkibSelectedInfo" style="margin-top:0.6rem; font-size:0.8rem; color:var(--text-muted);">Tiada rekod dipilih.</div>
          </div>

          <div class="card" style="margin-top:1rem;">
            <div class="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Tarikh / Hari</th>""",
1, "C6 toolbar Arkib")

# ---------------------------------------------------------------- C7: switchTab refresh arkib
rep(
"""        const sidebar = document.getElementById('sidebar');
        const backdrop = document.getElementById('sidebarBackdrop');
        if (sidebar && sidebar.classList.contains('open')) {
          sidebar.classList.remove('open');
          if (backdrop) backdrop.classList.remove('active');
        }""",
"""        const sidebar = document.getElementById('sidebar');
        const backdrop = document.getElementById('sidebarBackdrop');
        if (sidebar && sidebar.classList.contains('open')) {
          sidebar.classList.remove('open');
          if (backdrop) backdrop.classList.remove('active');
        }

        // Segarkan Arkib setiap kali tab Simpan/Cetak dibuka
        if (tabId === 'simpan-cetak') {
          renderSavedRphTable();
          updateArkibBadge();
          updateArkibSelectedInfo();
        }""",
1, "C7 switchTab refresh arkib")

# ---------------------------------------------------------------- C8: init
rep(
"""      renderBbmGrid();
      renderSavedRphTable();
      updateDashboardMetrics();

      loadPblRbtTemplate(5);""",
"""      renderBbmGrid();
      savedRphList = arkibNormalize(savedRphList);
      arkibPersist();
      renderSavedRphTable();
      updateArkibBadge();
      updateArkibSelectedInfo();
      updateDashboardMetrics();

      loadPblRbtTemplate(5);""",
1, "C8 init normalize + badge")

io.open(P, "w", encoding="utf-8", newline="") .write(s)
print("\n--- index.html ditulis: %d -> %d aksara ---" % (len(orig), len(s)))
shutil.copyfile(P, r"D:\SEPORA TOOLKIT\sepora_rbt_toolkit.html")
print("twin disalin -> sepora_rbt_toolkit.html")

# ---------------------------------------------------------------- VERIFIKASI
s2 = io.open(P, encoding="utf-8").read()
for k in ["function saveCurrentGeneratedRph", "function renderSavedRphTable", "function viewSavedRph",
          "function deleteSavedRph", "function syncRphWithWeek"]:
    print("count %-34s = %d" % (k, s2.count(k)))
blk = s2[s2.index("const PBL_TEMPLATES = {"):s2.index("function handleDropdownTahunChange")]
keys = re.findall(r'^\s+"([0-9][a-z0-9_]+)": \{', blk, re.M)
print("PBL_TEMPLATES keys =", len(keys))
for bad in ["4_kotak", "5_lampu_auto", "5_rumah_pintar", "5_akuaponik", "6_penggera", "6_robotik", "6_robot_solar", "6_kenderaan_solar"]:
    assert bad not in s2, "kunci lama dijumpai: " + bad
print("blacklist = 0 OK")
i = s2.index("const formTahapVal") if "const formTahapVal" in s2 else s2.index("let formTahapVal")
print("formTahapVal sekarang:", s2[i:i+140].split("\n")[0])
