#!/usr/bin/env python3
"""
空色りえの名刺（91×55mm・塗り足し3mm付き・600dpi）を生成する。

出力: design/business-card/{front,back}.png / business-card.pdf（印刷用）/ preview.png
使い方: python3 scripts/make_business_card.py   (Pillow・numpy・segno が必要)
"""

from pathlib import Path

import segno
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "design" / "business-card"
LOGO = ROOT / "design" / "logo-1920x1006.png"
MARK = ROOT / "design" / "icon-1024-transparent.png"

# ---- 掲載内容（ここを書き換えると名刺に反映されます） ----
NAME = "空色りえ"
ROLE = "詩人 / エッセイスト"
BRAND = "Rie-Utopia"
TAGLINE = "生きた証を書きとめていく。"
SITE_URL = "https://rie-utopia.com"
LINES = [  # (ラベル, 表示する文字)
    ("WEB", "rie-utopia.com"),
    ("INSTAGRAM", "@rieutopia"),
    ("X", "@rieUtopia"),
    ("NOTE", "note.com/riesorairo_"),
]
EXTRA = []  # 例: [("MAIL", "xxx@example.com")] を追加すると連絡先の行が増えます

# ---- 寸法 ----
DPI = 600
TRIM_W, TRIM_H, BLEED = 91, 55, 3  # mm


def mm(v):
    return round(v / 25.4 * DPI)


def pt(v):
    return round(v / 72 * DPI)


W, H = mm(TRIM_W + BLEED * 2), mm(TRIM_H + BLEED * 2)
OX = OY = mm(BLEED)  # 仕上がり位置の原点

INK = (11, 27, 58)
MUTED = (61, 78, 117)
BLUE = (45, 87, 224)
MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
GOTHIC_W3 = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
GOTHIC_W6 = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"


def font(path, size_pt, index=0):
    return ImageFont.truetype(path, pt(size_pt), index=index)


def text(draw, x, y, s, f, fill, spacing=0.0, anchor="ls"):
    """文字間隔つきで描画。x,y は mm（仕上がり原点）、y は文字のベースライン。"""
    px, py = OX + mm(x), OY + mm(y)
    if spacing == 0:
        draw.text((px, py), s, font=f, fill=fill, anchor=anchor)
        return
    for ch in s:
        draw.text((px, py), ch, font=f, fill=fill, anchor="ls")
        px += f.getlength(ch) + pt(spacing)


def text_width(s, f, spacing=0.0):
    return sum(f.getlength(ch) + pt(spacing) for ch in s) - pt(spacing)


def aurora(strength=1.0):
    base = Image.new("RGB", (W, H), (255, 255, 255))
    blobs = [
        ([-0.25, -0.9, 0.38, 0.5], (110, 150, 255), 0.75),
        ([0.62, 0.35, 1.3, 1.9], (100, 195, 255), 0.75),
        ([0.7, -0.8, 1.25, 0.3], (185, 170, 255), 0.45),
    ]
    for (x0, y0, x1, y1), color, st in blobs:
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).ellipse([x0 * W, y0 * H, x1 * W, y1 * H], fill=int(255 * st * strength))
        m = m.filter(ImageFilter.GaussianBlur(mm(9)))
        base.paste(Image.new("RGB", (W, H), color), (0, 0), m)
    return base


def trimmed(path):
    im = Image.open(path).convert("RGBA")
    return im.crop(im.getchannel("A").getbbox())


def paste_center(canvas, im, cx_mm, cy_mm, width_mm):
    s = mm(width_mm) / im.width
    im = im.resize((mm(width_mm), round(im.height * s)), Image.LANCZOS)
    canvas.alpha_composite(im, (OX + mm(cx_mm) - im.width // 2, OY + mm(cy_mm) - im.height // 2))
    return im


def front():
    img = aurora(1.0).convert("RGBA")
    d = ImageDraw.Draw(img)
    paste_center(img, trimmed(LOGO), TRIM_W / 2, 24, 62)
    f = font(MINCHO, 7.5, 0)
    w_mm = text_width(TAGLINE, f, 2.2) / DPI * 25.4
    text(d, TRIM_W / 2 - w_mm / 2, 42.5, TAGLINE, f, (39, 64, 122), spacing=2.2)
    return img.convert("RGB")


def back():
    img = aurora(0.55).convert("RGBA")
    # 読みやすさのため、情報エリアは白を重ねる
    veil = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    ImageDraw.Draw(veil).rectangle([0, 0, W, H], fill=(255, 255, 255, 120))
    img.alpha_composite(veil)
    d = ImageDraw.Draw(img)

    left = 7.0
    # 名前・肩書
    text(d, left, 16.8, NAME, font(MINCHO, 19, 1), INK, spacing=1.5)
    text(d, left, 23.6, ROLE, font(GOTHIC_W3, 7), MUTED, spacing=1.2)
    text(d, left, 28.2, BRAND, font(GOTHIC_W6, 6.5), BLUE, spacing=1.6)

    # 区切りのグラデーション線
    x0, x1, y = OX + mm(left), OX + mm(left + 40), OY + mm(30.6)
    for i in range(x1 - x0):
        t = i / (x1 - x0)
        c = (round(51 + (0 - 51) * t), round(102 + (128 - 102) * t), 255)
        d.line([(x0 + i, y), (x0 + i, y + 5)], fill=c)

    # リンク一覧
    rows = LINES + EXTRA
    label_f, value_f = font(GOTHIC_W6, 5.2), font(GOTHIC_W3, 7)
    top, pitch = 36.4, 4.0
    for i, (label, value) in enumerate(rows):
        base = top + i * pitch
        text(d, left, base, label, label_f, BLUE, spacing=0.8)
        text(d, left + 19.5, base, value, value_f, INK, spacing=0.3)

    # QR（サイトのトップへ）
    matrix = list(segno.make(SITE_URL, error="m", micro=False).matrix)
    n = len(matrix)
    size = mm(21)
    qimg = Image.new("RGB", (n, n), "white")
    px = qimg.load()
    for y, row in enumerate(matrix):
        for x, bit in enumerate(row):
            if bit:
                px[x, y] = INK
    qimg = qimg.resize((size, size), Image.NEAREST)
    qx, qy = OX + mm(TRIM_W - 7 - 21), OY + mm(TRIM_H - 7 - 21)
    pad = mm(1.6)
    ImageDraw.Draw(img).rounded_rectangle(
        [qx - pad, qy - pad, qx + size + pad, qy + size + pad], radius=mm(1.5), fill=(255, 255, 255, 255)
    )
    img.paste(qimg, (qx, qy))
    # 右上のマーク
    paste_center(img, trimmed(MARK), TRIM_W - 7 - 21 / 2, 15, 17)
    return img.convert("RGB")


def with_guides(im):
    """確認用: 仕上がり線(赤)と安全領域(青)を重ねる"""
    g = im.convert("RGBA")
    d = ImageDraw.Draw(g)
    d.rectangle([OX, OY, OX + mm(TRIM_W), OY + mm(TRIM_H)], outline=(255, 60, 60, 255), width=3)
    d.rectangle([OX + mm(4), OY + mm(4), OX + mm(TRIM_W - 4), OY + mm(TRIM_H - 4)],
                outline=(60, 120, 255, 200), width=2)
    return g.convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    f_img, b_img = front(), back()
    f_img.save(OUT / "front.png", dpi=(DPI, DPI), optimize=True)
    b_img.save(OUT / "back.png", dpi=(DPI, DPI), optimize=True)
    f_img.save(OUT / "business-card.pdf", save_all=True, append_images=[b_img], resolution=DPI)

    # 確認用シート（ガイド線つき・縮小）
    gf, gb = with_guides(f_img), with_guides(b_img)
    pw = 1100
    s = pw / W
    a, b = gf.resize((pw, round(H * s)), Image.LANCZOS), gb.resize((pw, round(H * s)), Image.LANCZOS)
    sheet = Image.new("RGB", (pw * 2 + 90, a.height + 60), (236, 239, 246))
    sheet.paste(a, (30, 30))
    sheet.paste(b, (pw + 60, 30))
    sheet.save(OUT / "preview.png")
    print(f"生成: {W}x{H}px ({TRIM_W + BLEED * 2}x{TRIM_H + BLEED * 2}mm @{DPI}dpi) -> {OUT}")


if __name__ == "__main__":
    main()
