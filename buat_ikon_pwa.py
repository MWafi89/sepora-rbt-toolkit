# -*- coding: utf-8 -*-
"""Jana ikon PWA SEPORA RBT TOOLKIT (192/512/maskable/apple) + manifest + sw.js"""
import os, io, json
from PIL import Image, ImageDraw, ImageFont

ROOT = r"D:\SEPORA TOOLKIT"
ICONS = os.path.join(ROOT, "icons")
os.makedirs(ICONS, exist_ok=True)

FONTS = [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf"]

def font(size):
    for f in FONTS:
        if os.path.exists(f):
            try: return ImageFont.truetype(f, size)
            except Exception: pass
    return ImageFont.load_default()

def gradient(size, c1=(26, 115, 232), c2=(11, 87, 208)):
    img = Image.new("RGB", (size, size), c1)
    d = ImageDraw.Draw(img)
    for y in range(size):
        t = y / max(1, size - 1)
        col = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        d.line([(0, y), (size, y)], fill=col)
    return img

def rounded(img, radius_ratio=0.22):
    size = img.size[0]
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * radius_ratio), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out

def draw_icon(size, maskable=False):
    img = gradient(size)
    d = ImageDraw.Draw(img)
    # jalur putih bawah (aksen)
    bar_h = int(size * 0.055)
    d.rectangle([0, size - bar_h - int(size * 0.055), size, size - int(size * 0.055)], fill=(255, 255, 255, 255))
    scale = 0.80 if maskable else 0.88  # safe zone utk maskable
    f_main = font(int(size * 0.30 * scale))
    f_sub = font(int(size * 0.115 * scale))
    txt = "RBT"
    bbox = d.textbbox((0, 0), txt, font=f_main)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    cx, cy = size / 2, size * (0.455 if not maskable else 0.44)
    d.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1]), txt, font=f_main, fill=(255, 255, 255))
    sub = "SEPORA"
    sb = d.textbbox((0, 0), sub, font=f_sub)
    sw, sh = sb[2] - sb[0], sb[3] - sb[1]
    d.text((cx - sw / 2 - sb[0], cy + th * 0.95 - sh / 2 - sb[1]), sub, font=f_sub, fill=(255, 255, 255, 235))
    if maskable:
        return img.convert("RGBA")  # full-bleed + selamat
    return rounded(img, 0.22)

jobs = [
    ("icon-192.png", 192, False),
    ("icon-512.png", 512, False),
    ("icon-maskable-192.png", 192, True),
    ("icon-maskable-512.png", 512, True),
    ("apple-touch-icon.png", 180, False),
    ("favicon-32.png", 32, False),
]
for name, size, maskable in jobs:
    img = draw_icon(size, maskable)
    p = os.path.join(ICONS, name)
    img.save(p, "PNG", optimize=True)
    print("ikon:", p, os.path.getsize(p), "bait")

manifest = {
    "name": "SEPORA RBT TOOLKIT - e-RPH & PBL RBT",
    "short_name": "SEPORA RBT",
    "description": "Sistem Pembina RPH & Inovasi PBL RBT SK Poring - arkib RPH, cetak PDF/Word, sandaran Google Drive DELIMa.",
    "lang": "ms",
    "dir": "ltr",
    "start_url": "/?sumber=pwa",
    "scope": "/",
    "display": "standalone",
    "display_override": ["standalone", "minimal-ui", "browser"],
    "orientation": "any",
    "background_color": "#f6f8fb",
    "theme_color": "#1a73e8",
    "categories": ["education", "productivity"],
    "icons": [
        {"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "/icons/icon-maskable-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
        {"src": "/icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
    "shortcuts": [
        {"name": "Bina RPH", "url": "/?tab=bina-rph"},
        {"name": "Arkib RPH", "url": "/?tab=simpan-cetak"},
    ],
}
with io.open(os.path.join(ROOT, "manifest.webmanifest"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print("manifest.webmanifest ditulis")
