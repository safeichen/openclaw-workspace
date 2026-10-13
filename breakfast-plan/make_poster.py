#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成适合打印的早餐点单海报（二维码 + 萌趣文案）"""
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageDraw, ImageFont

URL = "https://ipainting.cc/breakfast/"
OUT = "/root/.openclaw/workspace/breakfast-plan/poster_a4.png"

BG = (255, 250, 240)        # 奶白
INK = (74, 59, 45)          # 深棕
TINT = (255, 240, 220)      # 浅橙
ORANGE = (242, 106, 26)
MUTED = (150, 130, 110)

SANS_BOLD = "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Bold.ttc"
SANS_REG = "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc"
EMOJI = "/usr/share/fonts/google-noto-emoji-fonts/NotoEmoji-Regular.ttf"

def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.truetype(SANS_REG, size)

# 海报尺寸（略矮，更紧凑）
W, H = 1240, 1420
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# 顶部装饰淡色圆
d.ellipse([W-380, -260, W+180, 300], fill=TINT)
d.ellipse([-180, H-360, 300, H+120], fill=TINT)


def seg_width(text, f):
    b = d.textbbox((0, 0), text, font=f)
    return b[2] - b[0]


def center_combo(parts, y, size, gap=16):
    """parts: [(text, kind, color)] kind in {'t','e'}  t=文字 e=emoji;
    同一行水平居中对齐绘制，返回底部 y。"""
    f_txt = font(SANS_BOLD, size)
    f_emo = font(EMOJI, size)
    # 计算总宽
    widths = []
    for text, kind, _ in parts:
        f = f_emo if kind == "e" else f_txt
        widths.append(seg_width(text, f))
    total = sum(widths) + gap * (len(parts) - 1)
    x = (W - total) / 2
    for (text, kind, color), wd in zip(parts, widths):
        f = f_emo if kind == "e" else f_txt
        # 让基线大致一致
        b = d.textbbox((0, 0), text, font=f)
        d.text((x, y), text, font=f, fill=color)
        x += wd + gap
    return y + size


# 标题：🥣(橙) + 早餐吃什么呀(深棕)
y = 130
center_combo([("🥣", "e", ORANGE), ("早餐吃什么呀", "t", INK)], y, 100)

# 二维码（白底卡片）
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=16, border=2)
qr.add_data(URL)
qr.make(fit=True)
qimg = qr.make_image(
    image_factory=StyledPilImage,
    module_drawer=RoundedModuleDrawer(),
    eye_drawer=RoundedModuleDrawer(radius_ratio=1.0),
    color_mask=SolidFillColorMask(back_color=(255, 255, 255), front_color=ORANGE),
).convert("RGB")

qsize = 640
qimg = qimg.resize((qsize, qsize), Image.NEAREST)

card_pad = 42
card_x = (W - qsize - card_pad*2) / 2
card_y = 360
radius = 48
card = Image.new("RGB", (qsize + card_pad*2, qsize + card_pad*2), (255, 255, 255))
mask = Image.new("L", card.size, 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, card.size[0]-1, card.size[1]-1], radius=radius, fill=255)
shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
ImageDraw.Draw(shadow).rounded_rectangle(
    [card_x+6, card_y+10, card_x+card.size[0]+6, card_y+card.size[1]+10],
    radius=radius, fill=(200, 170, 140, 90))
img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
d = ImageDraw.Draw(img)
img.paste(card, (int(card_x), int(card_y)), mask)
img.paste(qimg, (int(card_x + card_pad), int(card_y + card_pad)))

# 底部小字
center_combo([("🍞🥟🍔", "e", ORANGE), ("好好吃饭，长高高", "t", INK), ("🌱💛", "e", ORANGE)],
             H - 240, 46)

img.save(OUT, quality=95)
print("海报已生成:", OUT)

pdf = "/root/.openclaw/workspace/breakfast-plan/poster_a4.pdf"
img.save(pdf, "PDF", resolution=150.0)
print("PDF 已生成:", pdf)
