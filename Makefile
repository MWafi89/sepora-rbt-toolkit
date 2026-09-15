# Makefile — arahan kanonik SEPORA RBT TOOLKIT
# Semua ujian guna chromium headless + CDP (tiada CI berbayar).
#   make test     -> suite penuh (82 pemeriksaan: kitaran hayat RPH, arkib, Drive, keselamatan, UX)
#   make journey  -> perjalanan pengguna BAHARU (guru) hujung-ke-hujung (13 pemeriksaan)
#   make masuk    -> jalan masuk guru (F24): 16 pemeriksaan, termasuk masuk 1 tekanan
#   make klik     -> klik SEBENAR butang "Guru baharu?" pada 3 saiz skrin (6 pemeriksaan)
#   make verify   -> ujian statik + CDP ringkas (ujian_verify.sh)
#   make serve    -> hidang setempat pada http://127.0.0.1:8899 (guna TEST_URL=... utk ujian setempat)
.PHONY: test journey masuk klik verify serve

test:
	@TEST_URL=$(TEST_URL) bash ujian_lengkap.sh

journey:
	@TEST_URL=$(TEST_URL) bash ujian_perjalanan.sh

masuk:
	@TEST_URL=$(TEST_URL) bash ujian_masuk.sh

klik:
	@TEST_URL=$(TEST_URL) bash ujian_klik_daftar.sh

verify:
	@bash ujian_verify.sh

serve:
	@python3 -m http.server 8899 --bind 127.0.0.1
