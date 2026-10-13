#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成适合打印的早餐点单海报（二维码 + 萌趣文案）"""
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageDraw, ImageFont

URL = "http://ipainting.cc/breakfast/"
OUT = "/root/.openclaw/workspace/breakfast-plan/poster_a4.png"

BG = (255, 250, 240)        # 奶白
INK = (74, 59, 45)          # 深棕
TINT = (255, 240, 220)      # 浅橙
ORANGE = (242, 106, 26)
MUTED = (150, 130, 110)

SANS_BOLD = "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Bold.ttc"
SANS_REG = "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc"

def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.truetype("/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc", size)

# A4 @150dpi ≈ 1240x1754
W, H = 1240, 1754
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# 顶部装饰淡色圆
d.ellipse([W-380, -260, W+180, 300], fill=TINT)
d.ellipse([-180, H-360, 300, H+120], fill=TINT)

def center(text, y, f, fill, shadow=None):
    bbox = d.textbbox((0, 0), text, font=f)
    w = bbox[2] - bbox[0]
    x = (W - w) / 2
    if shadow:
        d.text((x+2, y+2), text, font=f, fill=shadow)
    d.text((x, y), text, font=f, fill=fill)
    return y + (bbox[3]-bbox[1])

# 标题
y = 190
center("🍳 早餐吃什么呀", y, font(SANS_BOLD, 100), INK)

# 二维码（白底卡片）
from qrcode.image.styles.moduledrawers.pil import CircleModuleDrawer
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=16, border=2)
qr.add_data(URL)
qr.make(fit=True)
qimg = qr.make_image(
    image_factory=StyledPilImage,
    module_drawer=RoundedModuleDrawer(),
    eye_drawer=RoundedModuleDrawer(radius_ratio=1.0),   # 定位角也圆角，跟内部协调
    color_mask=SolidFillColorMask(back_color=(255, 255, 255), front_color=ORANGE),
).convert("RGB")

qsize = 720
qimg = qimg.resize((qsize, qsize), Image.NEAREST)

# 白色圆角卡片
card_pad = 46
card_x = (W - qsize - card_pad*2) / 2
card_y = 420
radius = 48
card = Image.new("RGB", (qsize + card_pad*2, qsize + card_pad*2), (255, 255, 255))
mask = Image.new("L", card.size, 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, card.size[0]-1, card.size[1]-1], radius=radius, fill=255)
# 阴影
shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
ImageDraw.Draw(shadow).rounded_rectangle(
    [card_x+6, card_y+10, card_x+card.size[0]+6, card_y+card.size[1]+10],
    radius=radius, fill=(200, 170, 140, 90))
img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
d = ImageDraw.Draw(img)
img.paste(card, (int(card_x), int(card_y)), mask)
img.paste(qimg, (int(card_x + card_pad), int(card_y + card_pad)))

# 二维码下方提示
y = int(card_y + card.size[1] + 70)
center("📱 手机扫一扫", y, font(SANS_BOLD, 56), INK)

# 底部小字
center("🍞🥟🍔  好好吃饭，长高高  🌱💛", H - 180, font(SANS_REG, 46), ORANGE)

img.save(OUT, quality=95)
print("海报已生成:", OUT)

# 顺带出个打印用 PDF（A4）
pdf = "/root/.openclaw/workspace/breakfast-plan/poster_a4.pdf"
img.save(pdf, "PDF", resolution=150.0)
print("PDF 已生成:", pdf)
