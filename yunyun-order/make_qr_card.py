#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成「昀昀的早餐」童趣风二维码卡片（二维码 + 备注）"""
import sys
import math
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from PIL import Image, ImageDraw, ImageFont

URL = sys.argv[1] if len(sys.argv) > 1 else "https://ipainting.cc/yunyun/"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/root/.openclaw/workspace/yunyun-order/yunyun-qr.png"
NOTE = sys.argv[3] if len(sys.argv) > 3 else (
    "这份早餐单是昀昀专属的，想吃啥就点啥，不用客气～\n"
    "口味、忌口、想吃 / 不想吃的，随时告诉我，我记在这里。"
)

FONT = "/usr/share/fonts/google-noto-cjk/NotoSansCJK-%s.ttc"
def font(size, weight="Regular"):
    return ImageFont.truetype(FONT % weight, size, index=2)  # index 2 = SC

W = 760
BG = (255, 253, 247)
INK = (58, 50, 46)
MUTED = (150, 143, 136)
ORANGE = (255, 107, 74)
PINK = (255, 138, 174)
MINT = (94, 196, 152)
SKY = (110, 176, 240)
YELLOW = (255, 205, 92)

f_title = font(44, "Black")
f_sub = font(23, "Medium")
f_note_t = font(24, "Bold")
f_note = font(22, "Regular")
f_url = font(19, "Regular")

def wrap(draw, text, fnt, max_w):
    lines = []
    for raw in text.split("\n"):
        cur = ""
        for ch in raw:
            if draw.textlength(cur + ch, font=fnt) <= max_w:
                cur += ch
            else:
                lines.append(cur); cur = ch
        lines.append(cur)
    return lines

pad = 46
qr_box = W - pad * 2
note_w = W - pad * 2
tmp = Image.new("RGB", (10, 10))
d0 = ImageDraw.Draw(tmp)
note_lines = wrap(d0, NOTE, f_note, note_w - 64)
note_h = 64 + 34 + len(note_lines) * 33
H = pad + 70 + 42 + 44 + qr_box + 32 + note_h + 30 + 30 + pad

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# 童趣底纹：四角彩色圆点
def dot(x, y, r, color):
    d.ellipse([x - r, y - r, x + r, y + r], fill=color)

for (x, y, r, c) in [
    (W - 66, 48, 10, MINT), (W - 34, 92, 6, SKY),
    (28, 300, 6, SKY), (W - 28, 520, 6, PINK),
    (46, H - 52, 9, MINT), (W - 50, H - 48, 11, YELLOW),
]:
    dot(x, y, r, c)

# 圆角边框（糖果色）
d.rounded_rectangle([12, 12, W - 12, H - 12], radius=40, outline=ORANGE, width=4)

y = pad
d.text((pad, y), "昀昀的早餐", font=f_title, fill=ORANGE)
# 标题旁小爱心
hx, hy = pad + d.textlength("昀昀的早餐", font=f_title) + 16, y + 22
d.ellipse([hx, hy, hx + 16, hy + 16], fill=PINK)
d.ellipse([hx + 13, hy, hx + 29, hy + 16], fill=PINK)
d.polygon([(hx, hy + 12), (hx + 28, hy + 12), (hx + 14, hy + 32)], fill=PINK)
y += 70
d.text((pad, y), "扫一扫 · 点点明天想吃的", font=f_sub, fill=MUTED)
y += 44

# 二维码白卡
d.rounded_rectangle([pad, y, pad + qr_box, y + qr_box], radius=34, fill=(255, 255, 255),
                    outline=(255, 216, 168), width=5)
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=0)
qr.add_data(URL)
qr.make(fit=True)
qimg = qr.make_image(
    image_factory=StyledPilImage,
    module_drawer=RoundedModuleDrawer(),
    color_mask=RadialGradiantColorMask(
        back_color=(255, 255, 255),
        center_color=(233, 79, 100),
        edge_color=(123, 75, 214),
    ),
).convert("RGB")
inner = qr_box - 60
qimg = qimg.resize((inner, inner), Image.LANCZOS)
img.paste(qimg, (pad + 30, y + 30))
y += qr_box + 30

# 备注便签（薄荷绿）
d.rounded_rectangle([pad, y, pad + note_w, y + note_h], radius=26, fill=(234, 247, 238),
                    outline=(191, 227, 203), width=3)
d.text((pad + 32, y + 22), "昀昀的备注", font=f_note_t, fill=(47, 158, 99))
ty = y + 66
for line in note_lines:
    d.text((pad + 32, ty), line, font=f_note, fill=(64, 120, 90))
    ty += 33
y += note_h + 22

d.text((pad, y), URL, font=f_url, fill=(186, 178, 170))

img.save(OUT)
print("已生成:", OUT, img.size)
