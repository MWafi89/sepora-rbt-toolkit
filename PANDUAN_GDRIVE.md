# PANDUAN: Pasang Aplikasi + Log Masuk DELIMa + Sandaran Google Drive

SEPORA RBT TOOLKIT (e-RPH RBT) kini:

1. **Boleh dipasang (PWA)** pada telefon Android/iPhone dan laptop — muncul sebagai ikon aplikasi, boleh buka tanpa internet.
2. **Wajib log masuk** — ID DELIMa (@moe-dl.edu.my) atau mod setempat (emel + PIN).
3. **Arkib RPH kekal** — disimpan dalam peranti (localStorage) DAN disandarkan ke fail JSON dalam **Google Drive akaun DELIMa guru**.

---

## A. Cara pasang pada peranti

### Android (Chrome)
1. Buka `https://sepora-rbt-toolkit.vercel.app`
2. Ketik butang **Pasang** di bar atas (atau menu ⋮ → *Install app / Add to Home screen*).
3. Ikon **SEPORA RBT** muncul di skrin utama.

### iPhone / iPad (mesti Safari)
1. Buka laman dalam **Safari**.
2. Ketik **Share** → **Add to Home Screen** → **Add**.

### Laptop / Komputer (Chrome / Edge)
1. Klik ikon **pasang** (monitor/⊞) di hujung kanan bar alamat.
2. Atau menu ⋮ → *Install SEPORA RBT TOOLKIT*.

> Selepas dipasang: aplikasi berjalan penuh skrin, arkib kekal dalam peranti, dan boleh dibuka walaupun kelas tiada internet.

---

## B. Log masuk WAJIB

| Pilihan | Bila guna | Sandaran Drive |
|---|---|---|
| **Log Masuk dengan ID DELIMa** (Google) | Disyorkan — akaun @moe-dl.edu.my | ✅ Automatik ke Google Drive guru |
| **Mod setempat** (emel + PIN) | Bila Drive belum diset / tiada internet | ❌ Guna "Eksport Arkib (JSON)" sahaja |

Default mod setempat (boleh tukar melalui butang profil → *Profil & Log Masuk*):
- Emel: `cikgu.rahmah@moe-dl.edu.my`
- PIN: `1234`

---

## C. Setelan Sandaran Google Drive (sekali sahaja, ~5 minit)

Butang **Log Masuk dengan ID DELIMa** memerlukan **OAuth Client ID** daripada Google Cloud (percuma).
Dalam aplikasi: tekan **"Setelan sandaran Google Drive (Client ID)"** di bawah gerbang log masuk — ringkasan langkah ada di situ.

### Langkah penuh

1. Buka <https://console.cloud.google.com/> → log masuk dengan akaun **DELIMa** guru (atau akaun pentadbir).
2. **Create Project** → nama: `SEPORA RBT TOOLKIT` → Create.
3. **APIs & Services → Library** → cari **Google Drive API** → **Enable**.
4. **APIs & Services → OAuth consent screen**:
   - User type: **Internal** (kalau akaun sekolah/Workspace) atau **External**.
   - App name: `SEPORA RBT TOOLKIT`, support email: emel guru.
   - Scopes: tambah `.../auth/drive.file` (rujukan: hanya fail yang dicipta aplikasi ini).
   - Kalau External: tambah emel guru sebagai **Test user** (atau tekan *Publish* untuk guru sekolah).
5. **APIs & Services → Credentials → Create Credentials → OAuth client ID**:
   - Application type: **Web application**
   - Name: `SEPORA RBT Web`
   - **Authorised JavaScript origins** — tambah SEMUA yang berkaitan:
     - `https://sepora-rbt-toolkit.vercel.app`
     - (jika guna domain sendiri) `https://<domain-anda>`
     - (untuk ujian laptop) `http://localhost`
   - **Authorised redirect URIs** — tidak perlu (aliran token Google Identity Services tanpa redirect).
6. **Create** → salin **Client ID** (`1234...apps.googleusercontent.com`).
7. Dalam aplikasi: **Setelan sandaran Google Drive** → tampal Client ID → **Simpan & cuba log masuk**.
   (Client ID disimpan dalam pelayar guru sahaja; ia bukan rahsia — ia memang awam untuk aplikasi web.)

### Di mana data disimpan?
- Fail: **`SEPORA_RPH_ARKIB.json`** dalam **My Drive** akaun DELIMa guru (boleh dilihat & dimuat turun guru sendiri).
- Skop `drive.file`: aplikasi hanya boleh menyentuh fail yang dicipta olehnya sendiri — **tidak** boleh membaca fail lain guru.
- Fail mengandungi: maklumat RPH (tajuk, kelas, minggu, SK/SP, tarikh mula/hantar, nota) + salinan penuh dokumen yang disimpan.
- Auto-sandaran: selepas setiap perubahan arkib (jika diaktifkan dalam halaman **Arkib & Cetakan**).

### Tukar guru / tukar akaun
Panel **Drive** ( klik chip *Drive:* di bar atas) → **Log keluar** → log masuk dengan akaun DELIMa yang lain.
Untuk elak rekod bercampur, tekan **Pulih dari Drive** selepas log masuk akaun baharu.

---

## D. Sandaran manual (tanpa Google Cloud)

Kalau Client ID belum sedia:
1. Halaman **Arkib & Cetakan** → **Eksport Arkib (JSON)** → fail `arkib_rph_sepora_YYYY-MM-DD.json` dimuat turun.
2. Muat naik fail itu ke **Google Drive** guru (boleh terus simpan dalam Drive DELIMa).
3. Untuk pulih: **Import Arkib (JSON)** pada peranti baharu.

Cara ini berkesan untuk guru yang mahu kawalan penuh tanpa setelan OAuth.

---

## E. Nota penting: guna alamat https, bukan fail tempatan

Log masuk Google & sandaran Drive hanya berfungsi melalui **https**:
- ✅ `https://sepora-rbt-toolkit.vercel.app` (juga selepas dipasang sebagai aplikasi)
- ⚠️ Membuka fail `index.html` terus dari cakera (file://) — hanya **mod setempat** berfungsi, Drive tidak.

## F. Had & nota jujur

- **Google Drive memerlukan Client ID sendiri** — tidak boleh dikongsi oleh aplikasi pihak ketiga. Tanpa ia, butang DELIMa membuka panduan setelan (bukan gagal senyap).
- Ada sekolah yang menyekat aplikasi luar pada akaun Workspace. Jika Google menyatakan *"Access blocked"*, pentadbir ICT sekolah perlu meluluskan aplikasi (OAuth consent) — gunakan mod setempat sementara.
- Token Google disimpan dalam memori sesi sahaja (bukan pada cakera) — lebih selamat, tetapi auto-sandaran perlu log masuk semula selepas sesi tamat (~1 jam jika tutup aplikasi).
- Storan pelayar (localStorage) had ~5MB. Bila hampir penuh, sistem mengekalkan metadata rekod dan hanya meringkaskan salinan dokumen rekod lama (dengan notis).
