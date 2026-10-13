#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成早餐点单页面的二维码"""
import sys
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask

url = sys.argv[1] if len(sys.argv) > 1 else "https://ipainting.cc/breakfast/"
out = sys.argv[2] if len(sys.argv) > 2 else "/root/.openclaw/workspace/breakfast-plan/qr.png"

qr = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_M,
    box_size=12,
    border=3,
)
qr.add_data(url)
qr.make(fit=True)

img = qr.make_image(
    image_factory=StyledPilImage,
    module_drawer=RoundedModuleDrawer(),
    color_mask=SolidFillColorMask(back_color=(255, 248, 240), front_color=(242, 106, 26)),
)
img.save(out)
print(f"二维码已生成: {out}")
print(f"内容: {url}")
