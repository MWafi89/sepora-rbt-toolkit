import re
import json

pbl_templates = {
    # TAHUN 4
    "4_kereta_idamanku": {
        "tahap": "4_kereta_idamanku",
        "kelas": "4 Dinamik",
        "subjek": "Reka Bentuk dan Teknologi (RBT)",
        "tajuk": "PBL 1: Reka Bentuk 'Kereta Idamanku' (Unit 2)",
        "bukuTeks": "Buku Teks RBT Tahun 4 (Unit 2: Reka Bentuk Produk, ms 30-44)",
        "sk": "2.2 Reka Bentuk Produk Tema Kenderaan",
        "sp": "2.2.1 Mengenal pasti komponen; 2.2.3 Menghasilkan lakaran kereta; 2.2.4 Menghasilkan model; 2.2.5 Membuat penilaian.",
        "integrasi": "Sains (Sifat Bahan), Matematik (Ukuran), Bahasa Melayu (Pembentangan)",
        "drivingQuestion": "\"Bagaimanakah kita dapat merekabentuk sebuah kereta mainan idaman menggunakan bahan terpakai yang kukuh dan estetik?\"",
        "integrasiRows": "<tr><td><strong>RBT (Teras)</strong></td><td>Mengenal pasti dan membina model reka bentuk kenderaan.</td></tr><tr><td><strong>Sains</strong></td><td>Memilih bahan kitar semula yang sesuai.</td></tr><tr><td><strong>Matematik</strong></td><td>Mengukur dan memotong bahan mengikut lakaran.</td></tr>",
        "objektif": ["Mengenal pasti komponen reka bentuk kenderaan.", "Menghasilkan satu model kereta idaman menggunakan bahan kitar semula."],
        "kriteria": ["Model kereta mempunyai 4 roda yang seimbang.", "Binaan kukuh dan menarik."],
        "setInduksi": "Guru menunjukkan pelbagai jenis kereta mainan. Guru bersoal jawab dengan murid tentang kereta idaman mereka.",
        "langkah": "• <strong>Langkah 1 (Lakaran - 20 minit):</strong> Murid melukis lakaran reka bentuk kereta idaman.<br>• <strong>Langkah 2 (Pembinaan - 45 minit):</strong> Memotong kotak, menyambung roda dan menghias.<br>• <strong>Langkah 3 (Pembentangan - 25 minit):</strong> Murid menguji kereta dan membentangkan kepada kelas.",
        "penutup": "Sesi pembentangan dan soal jawab. Guru membuat kesimpulan.",
        "bbm": "Kotak, Penutup Botol, Lidi, Gam, Gunting, Hub RBT SEPORA",
        "rubrik": "• TP1-TP2: Menyatakan komponen asas.<br>• TP3-TP4: Membina kereta idaman mengikut lakaran.<br>• TP5-TP6: Menghasilkan kereta idaman yang inovatif, kukuh dan kemas."
    },
    "4_pen3d": {
        "tahap": "4_pen3d",
        "kelas": "4 Dinamik",
        "subjek": "Reka Bentuk dan Teknologi (RBT)",
        "tajuk": "PBL 2: Pengenalan Kepada Teknologi Keychain 3D Pen (Unit 3)",
        "bukuTeks": "Buku Teks RBT Tahun 4 (Unit 3, ms 45-60)",
        "sk": "2.2 Reka Bentuk Produk Menggunakan Pen 3D",
        "sp": "2.2.1 Mengenal pasti fungsi pen 3D; 2.2.4 Menghasilkan model produk menggunakan pen 3D.",
        "integrasi": "Sains (Takat Lebur Polimer PLA), Matematik (Geometri Ruang 3D)",
        "drivingQuestion": "\"Bagaimanakah kita dapat memanfaatkan teknologi pen 3D untuk membuat keychain nama yang unik dan menarik?\"",
        "integrasiRows": "<tr><td><strong>RBT (Teras)</strong></td><td>Menghasilkan keychain menggunakan pen 3D.</td></tr><tr><td><strong>Sains</strong></td><td>Memahami proses pemanasan dan pemejalan plastik.</td></tr>",
        "objektif": ["Mengenal pasti bahagian utama pen 3D.", "Menghasilkan keychain berhuruf nama sendiri menggunakan pen 3D."],
        "kriteria": ["Keychain dapat dibaca dengan jelas dan kukuh.", "Cantuman lapisan filamen sekata."],
        "setInduksi": "Guru menunjukkan video pembuatan keychain menggunakan pen 3D.",
        "langkah": "• <strong>Langkah 1 (Lakaran & Stensil - 20 minit):</strong> Murid melukis huruf di atas kertas lapik.<br>• <strong>Langkah 2 (Pengoperasian Pen 3D - 45 minit):</strong> Menyemperit filamen mengikut huruf.<br>• <strong>Langkah 3 (Kemasan - 25 minit):</strong> Memasang cincin keychain pada huruf.",
        "penutup": "Murid mempamerkan hasil keychain 3D. Guru memberi peneguhan positif.",
        "bbm": "Pen 3D, Filamen PLA, Kertas Alas, Cincin Keychain, Hub RBT SEPORA",
        "rubrik": "• TP1-TP2: Mengetahui fungsi pen 3D.<br>• TP3-TP4: Menggunakan pen 3D dengan betul.<br>• TP5-TP6: Menghasilkan keychain yang sangat kemas dan kreatif."
    },
    "4_jahitan": {
        "tahap": "4_jahitan",
        "kelas": "4 Dinamik",
        "subjek": "Reka Bentuk dan Teknologi (RBT)",
        "tajuk": "PBL 3: Pengenalan Kepada Teknologi Jahitan (Unit 3)",
        "bukuTeks": "Buku Teks RBT Tahun 4 (Unit 3: Artikel Jahitan, ms 42-58)",
        "sk": "4.3 Reka Bentuk Artikel Jahitan",
        "sp": "4.3.4 Menyediakan alatan, bahan dan pola; 4.3.5 Menghasilkan artikel jahitan tangan.",
        "integrasi": "Sains (Sifat Bahan Fabrik), Matematik (Ukuran Pola)",
        "drivingQuestion": "\"Bagaimanakah kita boleh menggunakan jahitan tangan untuk membina bekas simpanan alatan kecil yang berguna?\"",
        "integrasiRows": "<tr><td><strong>RBT (Teras)</strong></td><td>Mengenal pasti alatan jahitan dan menjahit jahitan asas.</td></tr>",
        "objektif": ["Mengenal pasti jenis mata jahitan.", "Menghasilkan artikel jahitan berpoket mudah."],
        "kriteria": ["Mata jahitan lurus dan kukuh.", "Cantuman fabrik tidak tertetas."],
        "setInduksi": "Guru menunjukkan sarung telefon atau bekas pensel yang dijahit tangan.",
        "langkah": "• <strong>Langkah 1 (Penyediaan Pola - 20 minit):</strong> Melukis dan memindahkan pola ke fabrik.<br>• <strong>Langkah 2 (Menjahit - 45 minit):</strong> Menjahit menggunakan jahitan jelujur dan kia.<br>• <strong>Langkah 3 (Kemasan - 25 minit):</strong> Menghias artikel dan menyembunyikan hujung benang.",
        "penutup": "Gallery walk artikel jahitan.",
        "bbm": "Fabrik, Benang, Jarum Jahit Tangan, Gunting, Hub RBT SEPORA",
        "rubrik": "• TP1-TP2: Mengenal pasti alatan dan jenis mata jahitan asas.<br>• TP5-TP6: Menghasilkan artikel jahitan tangan yang sangat kukuh dan cantik."
    },
    "4_pembungkusan": {
        "tahap": "4_pembungkusan",
        "kelas": "4 Dinamik",
        "subjek": "Reka Bentuk dan Teknologi (RBT)",
        "tajuk": "PBL 4: Reka Bentuk Pembungkusan (Unit 4)",
        "bukuTeks": "Buku Teks RBT Tahun 4 (Unit 4: Pembungkusan, ms 60-70)",
        "sk": "3.1 Reka Bentuk Pembungkusan",
        "sp": "3.1.4 Menghasilkan lakaran bermaklumat pembungkusan; 3.1.5 Membina model pembungkusan.",
        "integrasi": "Sains (Kitar Semula), Matematik (Bentangan Geometri 3D)",
        "drivingQuestion": "\"Bagaimanakah kita dapat menghasilkan pembungkusan kotak cenderamata yang unik daripada bahan kitar semula?\"",
        "integrasiRows": "<tr><td><strong>RBT (Teras)</strong></td><td>Membina model pembungkusan berlabel.</td></tr>",
        "objektif": ["Menghasilkan lakaran bentangan pembungkusan.", "Membina model pembungkusan menggunakan kadbod."],
        "kriteria": ["Model terbentuk dengan betul daripada bentangan.", "Pembungkusan kukuh untuk menampung objek ringan."],
        "setInduksi": "Guru menunjuk pelbagai contoh pembungkusan produk di pasaran.",
        "langkah": "• <strong>Langkah 1 (Lakaran - 20 minit):</strong> Melukis bentangan 3D.<br>• <strong>Langkah 2 (Pemotongan & Lipatan - 45 minit):</strong> Memotong kadbod dan melipat ikut garisan.<br>• <strong>Langkah 3 (Hiasan - 25 minit):</strong> Menghias kotak dengan label bermaklumat.",
        "penutup": "Pembentangan kumpulan.",
        "bbm": "Kadbod Kitar Semula, Pembaris, Gunting, Gam, Hub RBT SEPORA",
        "rubrik": "• TP1-TP2: Melakar pembungkusan asas.<br>• TP5-TP6: Menghasilkan pembungkusan kukuh, bermaklumat dan menarik."
    },
    "4_makanan": {
        "tahap": "4_makanan",
        "kelas": "4 Dinamik",
        "subjek": "Reka Bentuk dan Teknologi (RBT)",
        "tajuk": "PBL 5: Reka Bentuk Makanan (Unit 5)",
        "bukuTeks": "Buku Teks RBT Tahun 4 (Unit 5: Reka Bentuk Makanan)",
        "sk": "5.1 Reka Bentuk Makanan",
        "sp": "5.1.3 Melakar reka bentuk pembungkusan makanan; 5.1.4 Menghasilkan reka bentuk makanan.",
        "integrasi": "Sains (Khasiat Pemakanan), PSV (Warna dan Bentuk)",
        "drivingQuestion": "\"Bagaimanakah kita dapat menyediakan dan menyusun bekal bento makanan yang sihat serta menarik untuk murid sekolah?\"",
        "integrasiRows": "<tr><td><strong>RBT (Teras)</strong></td><td>Menghasilkan susunan reka bentuk makanan dalam bento.</td></tr>",
        "objektif": ["Merancang menu sihat.", "Menyediakan bento makanan yang kreatif dan menarik."],
        "kriteria": ["Bento mempunyai keseimbangan nutrisi.", "Kreativiti dan kekemasan susun atur makanan."],
        "setInduksi": "Guru menayangkan gambar bento dari Jepun yang kreatif dan comel.",
        "langkah": "• <strong>Langkah 1 (Perancangan Menu - 20 minit):</strong> Melakar susun atur bento.<br>• <strong>Langkah 2 (Penyediaan Makanan - 45 minit):</strong> Menyusun bahan makanan sedia dimakan ke dalam bekas.<br>• <strong>Langkah 3 (Hiasan - 25 minit):</strong> Menghias bento dengan potongan sayur/buah.",
        "penutup": "Sesi menilai bento kawan-kawan.",
        "bbm": "Bekas Bento, Buah-buahan, Sayuran, Roti, Hub RBT SEPORA",
        "rubrik": "• TP1-TP2: Menyatakan jenis-jenis makanan.<br>• TP5-TP6: Bento dihasilkan dengan sangat kreatif, bersih dan seimbang nutrisi."
    },
    "4_pengaturcaraan": {
        "tahap": "4_pengaturcaraan",
        "kelas": "4 Dinamik",
        "subjek": "Reka Bentuk dan Teknologi (RBT)",
        "tajuk": "PBL 6: Reka Bentuk Pengaturcaraan (Unit 6)",
        "bukuTeks": "Buku Teks RBT Tahun 4 (Unit 6: Pengaturcaraan Scratch)",
        "sk": "1.1 Asas Reka Bentuk Pengaturcaraan",
        "sp": "1.1.2 Mengenal pasti algoritma; 1.1.4 Membangunkan algoritma penyelesaian masalah.",
        "integrasi": "Matematik (Koordinat), Sains (Logik)",
        "drivingQuestion": "\"Bagaimanakah kita dapat menghasilkan pergerakan dan bunyi watak (sprite) dalam perisian Scratch mengikut urutan yang betul?\"",
        "integrasiRows": "<tr><td><strong>RBT (Teras)</strong></td><td>Membina pseudokod dan memindahkan logik ke blok Scratch.</td></tr>",
        "objektif": ["Membina algoritma untuk pergerakan sprite.", "Menguji pengaturcaraan di dalam Scratch."],
        "kriteria": ["Sprite bergerak mengikut arahan kod blok tanpa ralat.", "Memasukkan bunyi dan teks pada masa yang tepat."],
        "setInduksi": "Guru menunjukkan animasi mudah yang dihasilkan dari perisian Scratch.",
        "langkah": "• <strong>Langkah 1 (Perancangan - 20 minit):</strong> Menulis carta alir pergerakan.<br>• <strong>Langkah 2 (Pengekodan - 45 minit):</strong> Menyusun blok kod pada antara muka Scratch.<br>• <strong>Langkah 3 (Nyahpepijat - 25 minit):</strong> Menguji kod dan membaiki kesilapan.",
        "penutup": "Tayangan hasil pengaturcaraan setiap murid.",
        "bbm": "Komputer/Laptop, Perisian Scratch, Hub RBT SEPORA",
        "rubrik": "• TP1-TP2: Mengenal antara muka Scratch.<br>• TP5-TP6: Pengaturcaraan bebas ralat, menarik dan menggunakan pelbagai blok arahan."
    },

    # TAHUN 5
    "5_rumah_tangga": {
        "tahap": "5_rumah_tangga",
        "kelas": "5 Inovatif",
        "subjek": "Reka Bentuk dan Teknologi (RBT)",
        "tajuk": "PBL 1: Teknologi Rumah Tangga Artikel Jahitan (Unit 1)",
        "bukuTeks": "Buku Teks RBT Tahun 5 (Unit 1: Teknologi Rumah Tangga, ms 1-18)",
        "sk": "4.3 Reka Bentuk Artikel Jahitan",
        "sp": "4.3.4 Menyediakan bahan; 4.3.5 Menghasilkan artikel jahitan dengan hiasan sulaman.",
        "integrasi": "Sains (Kekuatan Gentian), PSV (Prinsip Harmoni Warna)",
        "drivingQuestion": "\"Bagaimanakah kita boleh menghasilkan artikel jahitan hiasan serbaguna yang tahan lasak dan menarik?\"",
        "integrasiRows": "<tr><td><strong>RBT (Teras)</strong></td><td>Memotong kain berpandukan pola dan menjahit artikel hiasan.</td></tr>",
        "objektif": ["Menghasilkan artikel jahitan dengan mata jahitan yang kemas.", "Menghias artikel jahitan dengan hiasan tambahan."],
        "kriteria": ["Jahitan kukuh dan tidak tertetas.", "Hiasan dipasang dengan kemas dan menarik."],
        "setInduksi": "Guru mempamerkan hasil jahitan sarung kusyen.",
        "langkah": "• <strong>Langkah 1 (Lakaran - 20 minit):</strong> Melukis pola artikel.<br>• <strong>Langkah 2 (Menjahit - 45 minit):</strong> Mencantumkan kain dengan jahitan tangan.<br>• <strong>Langkah 3 (Kemasan - 25 minit):</strong> Menghias permukaan dengan butang/renda.",
        "penutup": "Pameran dan penilaian rakan sebaya.",
        "bbm": "Fabrik, Benang, Jarum Jahit Tangan, Renda/Butang, Hub RBT SEPORA",
        "rubrik": "• TP1-TP2: Mengenal pasti alatan jahitan.<br>• TP5-TP6: Artikel jahitan sangat kemas, kreatif dan bernilai komersial."
    },
    "5_kipas_solar": {
        "tahap": "5_kipas_solar",
        "kelas": "5 Inovatif",
        "subjek": "Reka Bentuk dan Teknologi (RBT)",
        "tajuk": "PBL 2: Tabung Kipas Solar (Unit 2)",
        "bukuTeks": "Buku Teks RBT Tahun 5 (Unit 2: Tenaga Boleh Baharu)",
        "sk": "6.5 Reka Bentuk Tenaga Boleh Baharu",
        "sp": "6.5.3 Membina litar dengan peranti output; 6.5.4 Menguji fungsi panel solar dan kipas.",
        "integrasi": "Sains (Tenaga Suria), Matematik (Anggaran Kos)",
        "drivingQuestion": "\"Bagaimanakah kita boleh merekabentuk tabung yang dilengkapi kipas mini berkuasa solar untuk menyejukkan bilik kecil?\"",
        "integrasiRows": "<tr><td><strong>RBT (Teras)</strong></td><td>Membina tabung dari bahan kitar semula dan melengkapkannya dengan litar solar.</td></tr>",
        "objektif": ["Membina bekas tabung yang kukuh.", "Menyambungkan panel solar mini dengan motor kipas."],
        "kriteria": ["Kipas berfungsi di bawah cahaya matahari langsung.", "Binaan tabung kemas dan kreatif."],
        "setInduksi": "Guru menayangkan video alat mainan berkuasa solar.",
        "langkah": "• <strong>Langkah 1 (Binaan Asas - 25 minit):</strong> Menyediakan botol/kotak sebagai tabung.<br>• <strong>Langkah 2 (Pemasangan Litar - 35 minit):</strong> Menyambungkan wayar dari panel solar ke motor DC.<br>• <strong>Langkah 3 (Pengujian - 30 minit):</strong> Menguji kipas di luar kelas (kawasan bercahaya matahari).",
        "penutup": "Perbincangan kepentingan tenaga hijau.",
        "bbm": "Botol Plastik/Kotak, Motor DC Kecil, Kipas Mini, Panel Solar Mini, Wayar, Hub RBT SEPORA",
        "rubrik": "• TP1-TP2: Mengetahui fungsi panel solar.<br>• TP5-TP6: Litar berfungsi cemerlang dan reka bentuk kotak tabung sangat kreatif."
    },
    "5_atmega": {
        "tahap": "5_atmega",
        "kelas": "5 Inovatif",
        "subjek": "Reka Bentuk dan Teknologi (RBT)",
        "tajuk": "PBL 3: Pengaturcaraan Kit ATMEGA328P (Unit 3)",
        "bukuTeks": "Buku Teks RBT Tahun 5 (Unit 3: Reka Bentuk Pengaturcaraan)",
        "sk": "6.5 Reka Bentuk Pengaturcaraan",
        "sp": "6.5.2 Menghasilkan carta alir; 6.5.3 Membina litar dan memuat naik atur cara pada mikropengawal.",
        "integrasi": "Sains (Litar Elektrik), Bahasa Inggeris (Kosa kata kod pengaturcaraan)",
        "drivingQuestion": "\"Bagaimanakah kita dapat memprogramkan cip ATMEGA328P untuk mengawal nyalaan lampu LED?\"",
        "integrasiRows": "<tr><td><strong>RBT (Teras)</strong></td><td>Menulis baris kod (atau blok) untuk mengawal litar LED menggunakan kit ATMEGA328P.</td></tr>",
        "objektif": ["Menyambungkan litar LED ke papan mikropengawal.", "Memuat naik program untuk menyalakan dan memadamkan LED (Blink)."],
        "kriteria": ["Sambungan litar betul tanpa ralat.", "LED berkelip mengikut masa (delay) yang ditetapkan dalam kod."],
        "setInduksi": "Guru menunjukkan papan litar mikropengawal (Arduino/ATMEGA) yang sedang berkelip.",
        "langkah": "• <strong>Langkah 1 (Lakaran Skematik - 20 minit):</strong> Melakar litar asas LED & Perintang ke Pin 13.<br>• <strong>Langkah 2 (Pemasangan - 30 minit):</strong> Menyambung komponen di atas breadboard.<br>• <strong>Langkah 3 (Pengaturcaraan - 40 minit):</strong> Menaip dan memuat naik kod (Blink/Blockly) dan memerhati hasilnya.",
        "penutup": "Membincangkan aplikasi mikropengawal dalam mesin basuh atau lampu isyarat.",
        "bbm": "Kit ATMEGA328P / Arduino Uno, Breadboard, LED, Perintang, Kabel USB, Hub RBT SEPORA",
        "rubrik": "• TP1-TP2: Mengenal pasti komponen asas papan.<br>• TP5-TP6: Murid berjaya memuat naik kod, mengubah masa kelipan, dan litar berfungsi sempurna."
    },
    "5_tanaman": {
        "tahap": "5_tanaman",
        "kelas": "5 Inovatif",
        "subjek": "Reka Bentuk dan Teknologi (RBT)",
        "tajuk": "PBL 4: Tanaman Konvensional (Unit 4)",
        "bukuTeks": "Buku Teks RBT Tahun 5 (Unit 4: Teknologi Pertanian)",
        "sk": "5.1 Reka Bentuk Pertanian",
        "sp": "5.1.3 Melakar sistem penanaman; 5.1.4 Menanam benih di dalam bekas.",
        "integrasi": "Sains (Keperluan Tumbesaran Tumbuhan), Matematik (Nisbah Tanah)",
        "drivingQuestion": "\"Bagaimanakah kita boleh merancang dan mengurus projek penanaman sayuran berdaun menggunakan kaedah konvensional di kawasan sekolah?\"",
        "integrasiRows": "<tr><td><strong>RBT (Teras)</strong></td><td>Menyediakan medium tanaman, menyemai biji benih, dan merawat anak benih.</td></tr>",
        "objektif": ["Menyediakan campuran medium tanaman yang betul (nisbah J.I.S).", "Menyemai biji benih sayuran berdaun ke dalam polibeg/bekas."],
        "kriteria": ["Nisbah campuran tanah mematuhi standard.", "Anak benih tumbuh dan disiram dengan cara yang betul."],
        "setInduksi": "Guru membawa beberapa polibeg berisi anak pokok sayuran.",
        "langkah": "• <strong>Langkah 1 (Persediaan - 30 minit):</strong> Murid menyukat dan mencampur tanah loam, bahan organik dan pasir laut.<br>• <strong>Langkah 2 (Semaian - 30 minit):</strong> Memasukkan medium ke dalam polibeg dan menyemai biji benih.<br>• <strong>Langkah 3 (Penyelenggaraan - 30 minit):</strong> Meletakkan tag nama tanaman, menyiram dan menempatkan polibeg di ruang redup.",
        "penutup": "Guru menasihatkan murid menjadualkan penyiraman bergilir.",
        "bbm": "Polibeg, Tanah Loam, Baja Organik, Pasir, Biji Benih Sayuran, Sudip Tangan, Hub RBT SEPORA",
        "rubrik": "• TP1-TP2: Menyatakan medium tanaman.<br>• TP5-TP6: Campuran tepat, tanaman diurus dengan komitmen tinggi sehingga bercambah sihat."
    },

    # TAHUN 6
    "6_kereta_kawalan": {
        "tahap": "6_kereta_kawalan",
        "kelas": "6 Cemerlang",
        "subjek": "Reka Bentuk dan Teknologi (RBT)",
        "tajuk": "PBL 1: Kereta Kawalan Saya (Unit 1)",
        "bukuTeks": "Buku Teks RBT Tahun 6 (Unit 1: Aplikasi Sistem Elektromekanikal)",
        "sk": "1.1 Aplikasi Reka Bentuk Elektromekanikal",
        "sp": "1.1.2 Mengenal pasti elemen; 1.1.4 Membina sistem kereta kawalan asas.",
        "integrasi": "Sains (Litar & Motor), Matematik (Kelajuan)",
        "drivingQuestion": "\"Bagaimanakah kita boleh membina sebuah kereta kawalan yang boleh bergerak maju dan undur menggunakan sistem motor dan suis kawalan berwayar?\"",
        "integrasiRows": "<tr><td><strong>RBT (Teras)</strong></td><td>Membina dan menyambung litar motor kenderaan kawalan.</td></tr>",
        "objektif": ["Memasang komponen mekanikal roda dan motor.", "Menyambungkan litar suis untuk mengawal arah putaran motor (maju/undur)."],
        "kriteria": ["Kereta dapat bergerak apabila butang ditekan.", "Arah pergerakan motor terkawal dan tidak berlaku litar pintas."],
        "setInduksi": "Guru menunjukkan sebuah kereta mainan remote control dan membongkar cara ia beroperasi.",
        "langkah": "• <strong>Langkah 1 (Pemasangan Casis - 30 minit):</strong> Memasang roda, gandar, dan motor DC pada casis.<br>• <strong>Langkah 2 (Pendawaian Alat Kawalan - 40 minit):</strong> Memateri atau menyambung wayar dari kotak suis ke motor DC (litar H-Bridge asas / suis togol).<br>• <strong>Langkah 3 (Pengujian - 20 minit):</strong> Menguji kereta di lantai kelas.",
        "penutup": "Ujian ketangkasan pergerakan kereta di laluan lurus.",
        "bbm": "Kit Kereta Mainan, Motor DC, Suis Togol, Bateri AA & Pemegang, Hub RBT SEPORA",
        "rubrik": "• TP1-TP2: Mengenal pasti komponen motor dan suis.<br>• TP5-TP6: Kereta dapat dikawal maju undur dengan sempurna dan reka bentuk kemas."
    },
    "6_auto_plant": {
        "tahap": "6_auto_plant",
        "kelas": "6 Cemerlang",
        "subjek": "Reka Bentuk dan Teknologi (RBT)",
        "tajuk": "PBL 2: Auto Plant Watering (Unit 2)",
        "bukuTeks": "Buku Teks RBT Tahun 6 (Unit 2)",
        "sk": "5.2 Reka Bentuk Sistem Robotik",
        "sp": "5.2.2 Menjelaskan fungsi elemen sensor dan pam; 5.2.4 Memuat naik atur cara mikropengawal.",
        "integrasi": "Sains (Keperluan Tumbuhan & Elektrik), Matematik (Sipadu cecair)",
        "drivingQuestion": "\"Bagaimanakah kita dapat membina sebuah sistem pintar yang menyiram tanaman secara automatik apabila kelembapan tanah kritikal?\"",
        "integrasiRows": "<tr><td><strong>RBT (Teras)</strong></td><td>Memasang penderia kelembapan tanah, pam air, mikropengawal dan mengkod logik automatik.</td></tr>",
        "objektif": ["Menyambung pam air mini dan penderia kelembapan pada mikropengawal.", "Memprogram mikropengawal untuk mengaktifkan pam apabila tanah kering."],
        "kriteria": ["Pam air menyiram air tepat ke sasaran apabila tanah kering.", "Sistem berhenti secara automatik setelah tanah cukup lembap."],
        "setInduksi": "Guru menayangkan projek pengairan pintar berskala besar dan mengajak murid menirunya dalam skala pasu bunga.",
        "langkah": "• <strong>Langkah 1 (Pemasangan Litar - 30 minit):</strong> Menyambung sensor kelembapan tanah dan relay pam ke pin mikropengawal.<br>• <strong>Langkah 2 (Pengkodan - 30 minit):</strong> Menyusun blok arahan (Jika lembapan < 30% -> Hidupkan Pam).<br>• <strong>Langkah 3 (Ujian Lapangan - 30 minit):</strong> Memasukkan sensor ke tanah pasu yang berbeza (kering vs basah) dan mencatat pemerhatian.",
        "penutup": "Pembentangan projek pengairan pintar kumpulan.",
        "bbm": "Mikropengawal, Sensor Kelembapan, Pam Air 5V, Relay, Bateri/USB Power, Pasu Tanaman, Hub RBT SEPORA",
        "rubrik": "• TP1-TP2: Mengenal pasti penderia dan mikropengawal.<br>• TP5-TP6: Sistem berfungsi 100% automatik, kalibrasi penderia tepat dan pembentangan meyakinkan."
    },
    "6_penghasilan": {
        "tahap": "6_penghasilan",
        "kelas": "6 Cemerlang",
        "subjek": "Reka Bentuk dan Teknologi (RBT)",
        "tajuk": "PBL 3: Penghasilan Produk (Unit 3)",
        "bukuTeks": "Buku Teks RBT Tahun 6 (Unit 3)",
        "sk": "6.5 Reka Bentuk Produk Gabungan",
        "sp": "6.5.3 Membina produk gabungan teknologi; 6.5.4 Menguji, menilai fungsi dan membuat penambahbaikan.",
        "integrasi": "Sains (Teknologi bahan), Seni Visual (Reka Bentuk Luaran & Estetika)",
        "drivingQuestion": "\"Bagaimanakah kita dapat menggabungkan dua atau lebih teknologi asas (elektromekanikal, mikropengawal, sensor) ke dalam satu reka bentuk produk baharu yang inovatif?\"",
        "integrasiRows": "<tr><td><strong>RBT (Teras)</strong></td><td>Menghasilkan produk berfungsi sepenuhnya menggabungkan pelbagai aplikasi pengetahuan.</td></tr>",
        "objektif": ["Merancang lakaran produk inovasi.", "Membina sebuah produk gabungan teknologi yang menyelesaikan masalah dalam kehidupan harian."],
        "kriteria": ["Produk mempunyai elemen mekanikal/elektrik/pengaturcaraan.", "Binaan kukuh, selamat dan kemas."],
        "setInduksi": "Guru membincangkan pertandingan inovasi peringkat daerah dan memberi dorongan murid untuk mereka cipta.",
        "langkah": "• <strong>Langkah 1 (Perbincangan Idea & Lakaran - 30 minit):</strong> Mengilhamkan produk (contoh: kipas meja pintar berlampu).<br>• <strong>Langkah 2 (Proses Penghasilan - 40 minit):</strong> Membina kerangka produk dan memasang komponen teknologi yang digabungkan.<br>• <strong>Langkah 3 (Pembentangan & Showcase - 20 minit):</strong> Murid membentangkan kos, kelebihan, dan kelemahan untuk ditambah baik.",
        "penutup": "Pameran hasil inovasi kelas.",
        "bbm": "Bahan kitar semula, Gam Panas, Motor DC, Lampu LED, Suis/Sensor, Bateri, Hub RBT SEPORA",
        "rubrik": "• TP1-TP2: Boleh menyatakan produk gabungan.<br>• TP5-TP6: Projek gabungan teknologi sangat unik, berfungsi dengan lancar, selamat, dan dibentangkan dengan jelas dan yakin."
    }
}

def main():
    file_path = "sepora_rbt_toolkit.html"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # We want to replace the `const PBL_TEMPLATES = { ... };` with our new definitions.
    # Because there's a lot of content, let's use regex to find the start and end.
    
    start_str = "const PBL_TEMPLATES = {"
    end_str = "function handleDropdownTahunChange"
    
    start_idx = content.find(start_str)
    end_idx = content.find(end_str)
    
    if start_idx == -1 or end_idx == -1:
        print("Could not find the injection points.")
        return
        
    new_pbl_str = "const PBL_TEMPLATES = " + json.dumps(pbl_templates, indent=4, ensure_ascii=False) + ";\n\n    "
    
    # replace everything from start_idx to end_idx with new_pbl_str + end_str
    new_content = content[:start_idx] + new_pbl_str + content[end_idx:]
    
    # Let's also update the fallback logic in loadPblRbtTemplate
    # The current fallback is:
    # let key = levelKey;
    # if (key == 4 || key == "4") key = "4_pengaturcaraan";
    # if (key == 5 || key == "5") key = "5_rumah_pintar";
    # if (key == 6 || key == "6") key = "6_robot_solar";
    # We should update it to fallback to the first element of each year.
    new_fallback = """let key = levelKey;
      if (key == 4 || key == "4") key = "4_kereta_idamanku";
      if (key == 5 || key == "5") key = "5_rumah_tangga";
      if (key == 6 || key == "6") key = "6_kereta_kawalan";"""
      
    old_fallback = """let key = levelKey;
      if (key == 4 || key == "4") key = "4_pengaturcaraan";
      if (key == 5 || key == "5") key = "5_rumah_pintar";
      if (key == 6 || key == "6") key = "6_robot_solar";"""
      
    new_content = new_content.replace(old_fallback, new_fallback)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("Done generating full templates and updating HTML.")

if __name__ == "__main__":
    main()
