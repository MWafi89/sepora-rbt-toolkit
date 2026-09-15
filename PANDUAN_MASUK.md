# CARA MASUK — Pengguna Baharu (Guru)

App: **https://sepora-rbt-toolkit.vercel.app** (boleh tambah ke skrin utama telefon:
Chrome/Edge → menu ⋮ → *Add to Home screen*).

---

## LALUAN TERPANTAS (selepas kemas kini [F24]) — cuba ini dulu

1. Buka **https://sepora-rbt-toolkit.vercel.app** .
2. Skrin log masuk sekarang **sudah terbuka** dan emel anda sudah terisi — cuma taip PIN anda
   dan tekan butang besar **Masuk**.
3. Kalau ini peranti yang pernah anda log masuk (dan anda **tidak** menekan *Kunci Skrin*),
   akan ada butang biru **Masuk pantas (akaun ini)** — satu tekanan, terus masuk, tiada taip apa-apa.
4. Peranti baharu / guru baharu: tekan **Guru baharu?** (butang di bawah butang *Masuk*),
   pilih **Pilihan B — Guna tanpa Google**, isi Nama + ID DELIMa (cth `g-57258425`) + PIN anda,
   tekan **Daftar & Mula Guna** — anda terus masuk tanpa menunggu apa-apa lagi.


### Kalau paparan nampak pelik / butang tak boleh ditekan

Kemas kini terkini sudah membetulkan tiga masalah yang membuat guru tidak boleh masuk:
butang Google yang jatuh di luar skrin pada telefon kecil, notifikasi yang menutup butang
"Guru baharu?", dan kad gerbang yang terlalu tinggi. Kalau telefon anda masih tunjuk
paparan lama: **tutup app sepenuhnya, buka semula** (paparan baru akan dimuat).

### Kalau butang "Log Masuk dengan ID DELIMa" tidak membawa ke mana

Butang Google itu **belum diaktifkan untuk sekolah ini** (pemilik app perlu pasang Client ID
sekali sahaja). Bila ditekan, app akan beritahu perkara itu dan menunjukkan butang yang
**memang berfungsi**. Jangan tunggu Google — guna jalan ini:

1. Tekan **Guru baharu? Daftar guna ID DELIMa anda sendiri**
2. Pilih **Pilihan B — Guna tanpa Google (offline)**
3. Isi Nama + ID DELIMa (cth `g-57258425`) + PIN anda → **Daftar & Mula Guna**

Semua ciri RPH berfungsi penuh melalui jalan ini; hanya sandaran automatik ke Google Drive
yang menunggu Client ID dipasang.

> Nota: *Lupa PIN?* sekarang membuka skrin daftar (laluan pulih sebenar), bukan sekadar mesej.
> Kalau anda tekan *Kunci Skrin* atau *Log Keluar*, butang *Masuk pantas* dimatikan —
> itu memang disengajakan supaya telefon yang dipinjam orang lain tidak boleh masuk arkib anda.


---

## Pilihan 1 (DISYORKAN) — guna akaun Google sekolah (ID DELIMa)

1. Buka app. Skrin pertama: **SEPORA RBT TOOLKIT**.
2. Tekan **Log Masuk dengan ID DELIMa**.
3. Pilih akaun **@moe-dl.edu.my** anda (kalau belum masuk Google, taip emel + kata laluan
   DELIMa **pada halaman Google sendiri** — app ini tidak pernah menerima kata laluan itu).
4. Sahkan kebenaran skop *Google Drive (drive.file)*. App hanya nampak fail yang dia sendiri cipta.
5. Siap. Pilih waktu dalam **Jadual** → tekan jana RPH → **Simpan**.
6. Sandaran: buka chip **Drive** di bar atas → **Sandaran sekarang**. Salinan masuk ke folder
   **SEPORATOOLKIT** dalam Drive anda (`SEPORA_RPH_ARKIB.json`). Auto-sandaran dihidupkan
   secara automatik selepas log masuk DELIMa.

> Nota: pilihan ini perlu **Client ID OAuth** dipasang sekali oleh pemilik app
> (rujuk `PANDUAN_GDRIVE.md`). Sebelum itu, guna Pilihan 2.

---

## Pilihan 2 — guna tanpa Google (semua ada dalam telefon anda)

1. Buka app → pada gerbang, tekan **Guru baharu? Daftar guna ID DELIMa anda sendiri**
   (tekan sekali lagi kalau peranti ini sudah ada akaun orang lain).
2. Pilih **Pilihan B — Guna tanpa Google** dan isi:
   - **Nama Guru** — nama penuh anda,
   - **ID DELIMa atau emel anda** — boleh taip `g-57258425` (ID DELIMa) atau emel penuh; ID akan
     dijadikan `g-57258425@moe-dl.edu.my`,
   - **PIN sendiri** — minimum 4 aksara, **jangan guna 1234**. PIN ini disimpan dalam bentuk
     **hash** (bukan teks biasa) dan tidak dipaparkan pada skrin.
3. Tekan **Daftar & Mula Guna**.
4. Siap. Arkib anda disimpan bawah akaun anda (`erph_saved::<emel-anda>`) — guru lain tidak bercampur.
5. Lain kali buka app: gerbang sudah terisi **emel anda** → taip PIN anda → masuk.

---

## Kalau terlupa PIN (mod setempat)

- Kalau anda pernah log masuk Google: tekan **Log Masuk dengan ID DELIMa** (tidak perlu PIN).
- Kalau tidak: padam data laman (Chrome → Tetapan laman → Padam data) lalu **import semula** fail
  **Eksport Arkib (JSON)** anda. Sebab itu **buat Eksport Arkib berkala** — tab *Simpan/Cetak* →
  *Eksport Arkib (JSON)* → simpan fail itu dalam Drive/WhatsApp diri sendiri.

## Keselamatan (apa yang app ini buat & tidak buat)

- **Tidak** menyimpan kata laluan DELIMa. Log masuk Google disahkan oleh Google/MOE sendiri.
- PIN setempat disimpan sebagai **PBKDF2-SHA256 + garam** (60,000 iterasi).
- Fail sandaran yang diimport/pulih dari Drive **dinyahbahaya** dahulu (buang skrip/atribut on*)
  sebelum dipaparkan — fail daripada orang lain tidak boleh menyuntik kod.
- Pustaka luar (pdf.js, mammoth, html2pdf, docx, font-awesome) dikunci dengan **SRI sha384**.
- Laman dihidangkan dengan **CSP** + header keselamatan lain (lihat `AUDIT_KESELAMATAN.md`).

## Untuk pemilik app (sekali sahaja)

1. Pasang **Client ID OAuth** (rujuk `PANDUAN_GDRIVE.md`) supaya butang ID DELIMa berfungsi untuk semua guru.
2. Sebelum Client ID dipasang, arahkan guru guna **Pilihan 2** dahulu.
