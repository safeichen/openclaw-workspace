#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成「昀昀的早餐」二维码卡片（二维码 + 说明 + 备注）"""
import sys
import qrcode
from PIL import Image, ImageDraw, ImageFont

URL = sys.argv[1] if len(sys.argv) > 1 else "http://43.159.52.61/yunyun/"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/root/.openclaw/workspace/yunyun-order/yunyun-qr.png"
NOTE = sys.argv[3] if len(sys.argv) > 3 else (
    "这份早餐单是昀昀专属的，想吃啥就点啥，不用客气～\n"
    "口味、忌口、想吃 / 不想吃的，随时告诉我，我记在这里。"
)

FONT = "/usr/share/fonts/google-noto-cjk/NotoSansCJK-%s.ttc"
def font(size, weight="Regular"):
    return ImageFont.truetype(FONT % weight, size, index=2)  # index 2 = SC

W = 760
BG = (253, 248, 240)
INK = (17, 17, 17)
MUTED = (138, 133, 128)
ACCENT = (242, 106, 26)
NOTE_BG = (255, 248, 232)
NOTE_LINE = (255, 227, 163)
NOTE_T = (184, 134, 11)
NOTE_C = (122, 95, 26)

f_title = font(42, "Bold")
f_sub = font(24, "Regular")
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
                lines.append(cur)
                cur = ch
        lines.append(cur)
    return lines

# 先算高度
pad = 44
qr_box = W - pad * 2
note_w = W - pad * 2
tmp = Image.new("RGB", (10, 10))
d0 = ImageDraw.Draw(tmp)
note_lines = wrap(d0, NOTE, f_note, note_w - 56)
note_h = 56 + 34 + len(note_lines) * 32
H = pad + 56 + 40 + 40 + qr_box + 30 + note_h + 34 + 34 + pad

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
# 外框
d.rounded_rectangle([10, 10, W - 10, H - 10], radius=34, outline=(236, 233, 227), width=3)

y = pad
d.text((pad, y), "昀昀的早餐", font=f_title, fill=INK)
y += 56
d.text((pad, y), "扫一扫，点明天想吃的东西", font=f_sub, fill=MUTED)
y += 46

# 二维码白卡
card_pad = 26
d.rounded_rectangle([pad, y, pad + qr_box, y + qr_box], radius=28, fill=(255, 255, 255))
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=0)
qr.add_data(URL)
qr.make(fit=True)
qimg = qr.make_image(fill_color=(17, 17, 17), back_color=(255, 255, 255)).convert("RGB")
inner = qr_box - card_pad * 2
qimg = qimg.resize((inner, inner), Image.LANCZOS)
img.paste(qimg, (pad + card_pad, y + card_pad))
y += qr_box + 26

# 备注便签
d.rounded_rectangle([pad, y, pad + note_w, y + note_h], radius=22, fill=NOTE_BG, outline=NOTE_LINE, width=2)
d.text((pad + 28, y + 22), "昀昀的备注", font=f_note_t, fill=NOTE_T)
ty = y + 62
for line in note_lines:
    d.text((pad + 28, ty), line, font=f_note, fill=NOTE_C)
    ty += 32
y += note_h + 24

d.text((pad, y), URL, font=f_url, fill=(178, 172, 164))

img.save(OUT)
print("已生成:", OUT, img.size)
