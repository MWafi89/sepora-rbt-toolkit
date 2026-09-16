#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_addie_kurungan.py
=======================
Tambah RUJUKAN ADDIE dalam KURUNGAN pada timeline PBL.
JANGAN ubah label asal — PLAN / DO / CHECK / ACT kekal.

Sebelum:  "tajuk": "Perancangan & Idea (PLAN)"
Selepas:  "tajuk": "Perancangan & Idea (PLAN)"

          + medan baharu "kurunganAddie": "(ADDIE: Analysis & Design)"
            yang dipaparkan sebagai badge di sebelah tajuk.

Pemetaan (rujukan sahaja, bukan ganti label):
    PLAN  -> Analysis & Design
    DO    -> Develop
    CHECK -> Implementation
    ACT   -> Evaluation

Idempotent: selamat dijalankan berulang kali.
"""
import re
import sys
import os
import shutil

BASE = "/root/sepora-rbt-toolkit"
TARGETS = ["index.html", "sepora_rbt_toolkit.html"]
MARK = "ADDIE_KURUNGAN_V1"

# fasa asal -> rujukan ADDIE (dalam kurungan)
PETA = {
    "PLAN":  "(ADDIE: Analysis &amp; Design)",
    "DO":    "(ADDIE: Develop)",
    "CHECK": "(ADDIE: Implementation)",
    "ACT":   "(ADDIE: Evaluation)",
}

POLA = [
    (re.compile(r'"fasa":\s*"(PLAN|DO|CHECK|ACT)",(\s*\n\s*)"tajuk":\s*"([^"]*)"'),
     lambda m: '"fasa": "%s",%s"kurunganAddie": "%s",%s"tajuk": "%s"'
               % (m.group(1), m.group(2), PETA[m.group(1)], m.group(2), m.group(3))),
]


def patch_file(path, dry=False):
    p = os.path.join(BASE, path)
    if not os.path.exists(p):
        return f"SKIP (tiada): {p}"
    with open(p, "r", encoding="utf-8") as f:
        src = f.read()

    if MARK in src:
        return f"SUDAH DIPATCH: {path}"

    orig = len(src)
    total = 0
    for rx, repl in POLA:
        src, n = rx.subn(repl, src)
        total += n

    if total == 0:
        return f"GAGAL (tiada padanan): {path}"

    # Nota kecil di tajuk timeline: nyatakan timeline ini dipetakan ke ADDIE
    tl = 'Garis Masa 4 Fasa Pelaksanaan Projek (PBL Timeline)'
    if tl in src:
        src = src.replace(
            tl,
            'Garis Masa 4 Fasa Pelaksanaan Projek (PBL Timeline) '
            '<span style="font-size:0.72rem;font-weight:400;color:#64748b;">'
            '[rujukan model ADDIE]</span>', 1)

    src = src.replace("</script>", "/* " + MARK + " */\n</script>", 1)

    if not dry:
        shutil.copy2(p, p + ".bak_addiekur")
        with open(p, "w", encoding="utf-8") as f:
            f.write(src)

    return f"{path}: {total} fasa ditambah kurungan ADDIE ({orig} -> {len(src)} bytes)"


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    for t in TARGETS:
        print(patch_file(t, dry=dry))
