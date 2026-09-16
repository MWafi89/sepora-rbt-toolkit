# Makefile — arahan kanonik SEPORA RBT TOOLKIT
# Semua ujian guna chromium headless + CDP (tiada CI berbayar).
#   make test     -> suite penuh (82 pemeriksaan: kitaran hayat RPH, arkib, Drive, keselamatan, UX)
#   make journey  -> perjalanan pengguna BAHARU (guru) hujung-ke-hujung (13 pemeriksaan)
#   make masuk    -> jalan masuk guru (F24): 16 pemeriksaan, termasuk masuk 1 tekanan
#   make gerbang  -> SEMUA butang gerbang pada 4 saiz telefon (17 pemeriksaan, klik sebenar)
#                    (menggantikan ujian lama "Guru baharu?" yg butangnya dibuang di F28)
#   make daftar   -> daftar guru baharu SEBENAR (klik + taip) 8 pemeriksaan
#   make offline  -> app berfungsi TANPA INTERNET (PWA cache) 9 pemeriksaan
#   make sandaran -> sandaran manual Eksport/Import JSON (ganti Drive) 7 pemeriksaan
#   make verify   -> ujian statik + CDP ringkas (ujian_verify.sh)
#   make serve    -> hidang setempat pada http://127.0.0.1:8899 (guna TEST_URL=... utk ujian setempat)
.PHONY: test journey masuk gerbang daftar offline sandaran verify serve

test:
	@TEST_URL=$(TEST_URL) bash ujian_lengkap.sh

journey:
	@TEST_URL=$(TEST_URL) bash ujian_perjalanan.sh

masuk:
	@TEST_URL=$(TEST_URL) bash ujian_masuk.sh

gerbang:
	@TEST_URL=$(TEST_URL) bash ujian_gerbang_butang.sh

daftar:
	@TEST_URL=$(TEST_URL) bash ujian_daftar_realiti.sh

offline:
	@TEST_URL=$(TEST_URL) bash ujian_offline.sh

sandaran:
	@TEST_URL=$(TEST_URL) bash ujian_sandaran_manual.sh

verify:
	@bash ujian_verify.sh

serve:
	@python3 -m http.server 8899 --bind 127.0.0.1
