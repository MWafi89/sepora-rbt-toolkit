# AUDIT KESELAMATAN — SEPORA RBT TOOLKIT

Tarikh: 2026-09-13 · Skop: `index.html` (twin `sepora_rbt_toolkit.html`), `sw.js`, `vercel.json`, `manifest.webmanifest`
Kaedah: reverse-engineering statik (baca kod + pola berisiko) + ujian tingkah laku CDP headless terhadap laman LIVE
Keputusan: **6 kelemahan ditemui, semuanya dibetulkan** · ujian `bash ujian_lengkap.sh` → **71/71 PASS**

## Ringkasan penemuan

| # | Tahap | Kelemahan | Bukti | Pembetulan | Ujian |
|---|-------|-----------|-------|------------|-------|
| W1 | Tinggi | Stored XSS melalui `docHtml` | `el.innerHTML = r.docHtml` (viewSavedRph); `docHtml` datang dari IMPORT fail JSON sandaran dan PULIH dari Google Drive | `arkibSanitizeHtml()` dibuang tag berbahaya + atribut `on*`/`srcdoc`/`javascript:`; dipakai pada render, import, dan pulih Drive | L62 |
| W2 | Tinggi | PIN guru disimpan teks biasa + dipaparkan pada skrin | `localStorage 'erph_auth_cred' = {email, password}`; `showDefaultLoginHelp()` papar "PIN: ..." | PBKDF2-SHA256 (60,000 iterasi) + garam rawak; migrasi automatik; paparan PIN dibuang | L63, L64 |
| W3 | Sederhana | Tiada SRI pada 5 pustaka CDN | font-awesome, pdf.js, mammoth, html2pdf, docx dimuat tanpa `integrity` | `integrity=sha384` + `crossorigin=anonymous` pada semua URL versi tetap | L67 |
| W4 | Sederhana | Tiada header keselamatan | Respon Vercel tiada CSP/XCTO/XFO | CSP (allowlist CDN + Google), `nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`, `Permissions-Policy`, HSTS | L68 + `curl -I` |
| W5 | Rendah | `esc()` tidak mengescape petikan | `value="${esc(x)}"` boleh dipecahkan dengan `"` | `esc()` escape `& < > " '` | L65 |
| W6 | Rendah | `showToast()` innerHTML mentah | Mesej (nama fail/kelas) boleh bawa HTML | Mesej melalui sanitizer | L66 |

## Disahkan BERSIH (tiada isu)

- Tiada rahsia/API key hardcoded dalam repo (kunci Gemini dibiar kosong untuk input guru).
- Service worker **tidak** cache panggilan API Google (`isDriveApi()`), dan tidak cache POST/PUT/PATCH — token tidak masuk Cache Storage.
- Skop OAuth minimum: `openid email profile https://www.googleapis.com/auth/drive.file` (app hanya nampak fail yang dia sendiri cipta).
- Log masuk Google menolak akaun bukan `@moe-dl.edu.my`; app tidak pernah menerima kata laluan DELIMa.
- Arkib dipisahkan ikut akaun (`erph_saved::<emel>`), log keluar membersihkan sesi + arkib dalam memori.

## Risiko baki (jujur, belum dibetulkan)

1. **Gerbang PIN ialah kawalan setempat, bukan pengesahan sebenar.** Sesiapa yang ada akses fizikal pada peranti + DevTools boleh memintasnya. PBKDF2 hanya melambatkan tekaan luar talian.
2. **Tiada sekatan cubaan log masuk** (cth. lengah selepas 5 cubaan gagal) — cadangan seterusnya.
3. **Arkib tidak disulitkan** semasa rehat (localStorage + fail JSON dalam Drive boleh dibaca sesiapa yang ada akses peranti/Drive).
4. **CSP masih membenarkan `'unsafe-inline'`** kerana app satu fail dengan pengendali inline; mitigasi XSS bergantung pada sanitizer (W1), bukan ketatnya CSP.
5. **`pdf.worker.min.js`** dimuat oleh pustaka pdf.js tanpa SRI (dalaman pustaka) — baki risiko rantaian bekalan yang kecil.
6. Client ID OAuth Google masih perlu diset oleh pemilik app sebelum sandaran Drive boleh berjalan.
7. **Lupa PIN (mod setempat)** — sejak W2, PIN tidak lagi boleh dilihat pada skrin. Pemulihan: guru log masuk guna **ID DELIMa** (jika ada Google), atau padam data laman lalu **import semula fail JSON sandaran** (arkib dalam peranti akan hilang, sebab itu Eksport Arkib perlu dibuat berkala — sudah diterangkan dalam PANDUAN_GDRIVE.md).

## Kelayakan ujian

- Statik: semakan pola (innerHTML + data mentah, kunci rahsia, atribut `integrity`).
- Tingkah laku (CDP headless, laman LIVE): L62 (XSS disuntik melalui rekod arkib → tiada skrip berjalan), L63/L64 (PIN hash + log masuk), L65 (esc), L66 (toast), L67 (SRI=5), L68 (0 pelanggaran CSP), L69 (0 ralat JS).
- Header: `curl -sSIL https://sepora-rbt-toolkit.vercel.app/` menunjukkan CSP, XCTO, XFO, Referrer-Policy, Permissions-Policy, HSTS.

Jalankan semula: `bash ujian_lengkap.sh` (61→71 pemeriksaan) atau `TEST_URL=http://127.0.0.1:8899/index.html bash ujian_lengkap.sh` untuk ujian setempat.
