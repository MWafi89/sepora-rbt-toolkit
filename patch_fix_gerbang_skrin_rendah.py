#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F22 - Gerbang log masuk: butang daftar jatuh DI BAWAH LIPATAN pada skrin rendah.

BUKTI (CDP, viewport 980x344 = Chrome Android Pixel 7 dengan address bar + UI):
    gerbang clientHeight = 344, scrollHeight = 560   -> gerbang BOLEH skrol
    .delima-card tinggi  = 480px  (136px lebih tinggi daripada viewport)
    butang "Guru baharu?" y = 399 SEBELUM skrol  -> DI LUAR pandangan (vh 344)
    butang                 y = 183 SELEPAS skrol -> dalam pandangan
=> guru nampak skrin gerbang, tekan tempat butang sepatutnya, tiada apa berlaku.
   Nampak macam "telefon rosak" / "app rosak". Ia sebenarnya kad terlalu tinggi.

PEMBETULAN (dua lapis):
  1. Kad dibuat PADAT pada skrin rendah (media max-height:600px): logo, tajuk, nota,
     jarak dikurangkan -> butang daftar muat dalam satu skrin tanpa skrol.
  2. Butang daftar jadi elemen menonjol (bukan pautan halus) supaya mudah dilihat.
  3. Jaring keselamatan: butang daftar DIJAMIN boleh dicapai - jika kad masih lebih
     tinggi daripada skrin, gerbang di-skrol supaya butang kelihatan (boot + bila
     modal ditutup).

Guna:  python3 patch_fix_gerbang_skrin_rendah.py index.html sepora_rbt_toolkit.html
Idempotent: penanda F22 sudah wujud -> rc 0 tanpa perubahan.
Gagal-lantang: setiap jangkar mesti tepat 1x; jika tidak -> rc 1, fail TIDAK diubah.
"""
import sys, os, shutil, time, hashlib

MARK = 'F22-GERBANG-SKRIN-RENDAH'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def tampal(src):
    if MARK in src:
        return src, False

    # ---------- 1. Kad padat pada skrin rendah ----------
    old_card = """    @media (max-width: 480px) { .delima-card { width: 100%; } }"""
    new_card = """    @media (max-width: 480px) { .delima-card { width: 100%; } }
    /* [MARK1] Kad gerbang MESTI muat dalam skrin rendah.
       Diukur: tinggi kad 480px pada viewport 344px -> butang daftar di hujung kad
       jatuh 55px di bawah lipatan, jadi guru "tekan x dapat". Padatkan supaya
       butang daftar kelihatan tanpa skrol. */
    @media (max-height: 600px) {
      .delima-gate { padding: 0.5rem 0.7rem 0.9rem; }
      .delima-card { padding: 0.7rem 0.85rem 1rem; margin: 0 auto 0.6rem; border-radius: 14px; }
      .delima-card img { width: 40px !important; height: 40px !important; border-radius: 10px !important; }
      .delima-card h1 { font-size: 1rem; margin: 0.25rem 0 0.05rem; }
      .delima-card .delima-sub { font-size: 0.7rem; margin-bottom: 0.5rem; }
      .delima-note { font-size: 0.68rem; line-height: 1.35; margin-bottom: 0.45rem; }
      .delima-status { font-size: 0.68rem; padding: 0.4rem 0.5rem; margin-bottom: 0.45rem; }
      .delima-google { padding: 0.55rem 0.7rem; font-size: 0.82rem; }
      .delima-toggle { font-size: 0.72rem; padding: 3px; }
      .daftar-cta { padding: 0.55rem 0.7rem; font-size: 0.78rem; margin-top: 0.5rem; }
      .delima-foot { margin-top: 0.45rem; font-size: 0.66rem; }
      .delima-local { margin-top: 0.5rem; padding-top: 0.5rem; }
    }
    /* [MARK1] CTA daftar - butang sebenar yang menonjol, bukan pautan halus.
       Jarak bawah diberi supaya footer (.delima-foot) TIDAK bertindih dengan butang
       pada skrin rendah - titik tengah butang mesti bebas untuk boleh ditekan. */
    .daftar-cta {
      display: block; width: 100%; margin-top: 0.7rem; margin-bottom: 0.35rem;
      padding: 0.7rem 0.8rem; box-sizing: border-box; position: relative; z-index: 1;
      background: rgba(26,115,232,0.10); border: 1.5px solid rgba(26,115,232,0.55);
      color: var(--primary); font-weight: 700; font-size: 0.83rem; border-radius: 10px;
      cursor: pointer; line-height: 1.35; text-align: center;
    }
    .daftar-cta:hover, .daftar-cta:active { background: rgba(26,115,232,0.18); }
    .daftar-cta i { margin-right: 5px; }""".replace('MARK1', MARK)
    assert src.count(old_card) == 1, 'jangkar @media 480px tidak unik/tidak jumpa'
    src = src.replace(old_card, new_card, 1)

    # ---------- 2. Gerbang: jangan potong atas, elak skrol berganda ----------
    old_gate = """      display: flex; align-items: center; justify-content: center;
      padding: 1rem; box-sizing: border-box; overflow-y: auto; overflow-x: hidden;
      background: linear-gradient(135deg, #0b57d0 0%, #1a73e8 45%, #34a853 100%);
    }"""
    new_gate = """      /* [MARK2] align-items:center MEMOTONG hujung kad pada skrin rendah.
         Guna flex-start + overflow-y:auto supaya kandungan tinggi boleh diskrol. */
      display: flex; align-items: flex-start; justify-content: center;
      padding: max(0.7rem, env(safe-area-inset-top)) 1rem max(1.2rem, env(safe-area-inset-bottom));
      box-sizing: border-box; overflow-y: auto; overflow-x: hidden;
      -webkit-overflow-scrolling: touch; overscroll-behavior: contain;
      background: linear-gradient(135deg, #0b57d0 0%, #1a73e8 45%, #34a853 100%);
    }""".replace('MARK2', MARK)
    assert src.count(old_gate) == 1, 'jangkar isi .delima-gate tidak unik/tidak jumpa'
    src = src.replace(old_gate, new_gate, 1)

    # ---------- 3. Butang daftar: id + kelas ----------
    old_btn = """      <button class="delima-toggle" style="margin-top:0.45rem; border-color:rgba(26,115,232,0.45); color:var(--primary);" onclick="openDaftarModal(true, true)">
        <i class="fa-solid fa-user-plus"></i> Guru baharu? Daftar guna ID DELIMa anda sendiri
      </button>"""
    new_btn = """      <button type="button" id="btnDaftarGuruBaharu" class="delima-toggle daftar-cta" onclick="openDaftarModal(true, true)">
        <i class="fa-solid fa-user-plus"></i> Guru baharu? Daftar guna ID DELIMa anda sendiri
      </button>"""
    assert src.count(old_btn) == 1, 'jangkar butang daftar tidak unik/tidak jumpa'
    src = src.replace(old_btn, new_btn, 1)

    # ---------- 4. Jaring keselamatan: pastikan butang daftar boleh dicapai ----------
    old_fn = """    function tutupDaftarDariGerbang() { window.__modalWajib = false; closeModalDirectly(); }"""
    new_fn = """    function tutupDaftarDariGerbang() { window.__modalWajib = false; closeModalDirectly(); }
    // [MARK3] Jaring keselamatan: pada skrin rendah butang daftar boleh jatuh di bawah
    // lipatan. Skrol gerbang supaya ia kelihatan (dipanggil selepas modal ditutup & pada boot).
    function pastikanButangDaftarKelihatan() {
      try {
        var g = document.getElementById('privacyLockScreen');
        var b = document.getElementById('btnDaftarGuruBaharu');
        if (!g || !b) return;
        if (getComputedStyle(g).display === 'none') return;
        var r = b.getBoundingClientRect();
        if (r.bottom > window.innerHeight - 8 || r.top < 0) {
          g.scrollTop = g.scrollHeight;
        }
      } catch (e) { }
    }""".replace('MARK3', MARK)
    assert src.count(old_fn) == 1, 'jangkar tutupDaftarDariGerbang tidak unik/tidak jumpa'
    src = src.replace(old_fn, new_fn, 1)

    # ---------- 5. Panggil jaring pada boot ----------
    old_boot = """    window.addEventListener('DOMContentLoaded', () => {"""
    new_boot = """    window.addEventListener('DOMContentLoaded', () => {
      // [MARK4] skrin rendah: pastikan butang daftar kelihatan bila gerbang dipaparkan
      setTimeout(function () { try { pastikanButangDaftarKelihatan(); } catch (e) { } }, 400);""".replace('MARK4', MARK)
    assert src.count(old_boot) == 1, 'jangkar DOMContentLoaded tidak unik/tidak jumpa'
    src = src.replace(old_boot, new_boot, 1)

    return src, True


def main():
    if len(sys.argv) < 2:
        print('Guna: python3 patch_fix_gerbang_skrin_rendah.py <index.html> [twin.html]')
        return 1
    for p in sys.argv[1:]:
        if not os.path.isfile(p):
            print('GAGAL: fail tidak wujud -> ' + p)
            return 1
        src = open(p, encoding='utf-8').read()
        before = sha(p)
        try:
            out, changed = tampal(src)
        except AssertionError as e:
            print('GAGAL BERSIH (%s): %s - fail TIDAK diubah' % (p, e))
            return 1
        if not changed:
            print('LANGKAU (%s): penanda %s sudah wujud' % (p, MARK))
            continue
        os.makedirs('/tmp/sepora_bak', exist_ok=True)
        bak = '/tmp/sepora_bak/%s.bak-f22-%s' % (os.path.basename(p), time.strftime('%Y%m%d-%H%M%S'))
        shutil.copy2(p, bak)
        open(p, 'w', encoding='utf-8').write(out)
        print('TAMPAL OK (%s)\n  backup : %s\n  sha    : %s -> %s' % (p, bak, before[:16], sha(p)[:16]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
