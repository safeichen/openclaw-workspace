#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每晚 20:00 提醒第二天早餐吃什么。
直接输出【最终要发送的完整消息体】（含 <qqmedia> 标签），供投递使用。
主会话/投递只需把 stdout 原文发出去，不要添加任何自己的文字。
"""
import os
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
DAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def main():
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    tname = DAYS[tomorrow.weekday()]

    body = (
        "叮咚~ 明天早餐想吃点啥呀？🍳✨\n"
        f"（{tname} {tomorrow.strftime('%m/%d')}）\n\n"
        "扫扫这个小方块，挑几样喜欢的～\n\n"
        "早睡早起，才能长得高高壮壮 🌱💛"
    )
    qr = os.path.join(BASE, "poster_a4.png")
    # 最终消息体：文字 + 紧接着的图片标签
    print(body)
    print(f"<qqmedia>{qr}</qqmedia>")


if __name__ == "__main__":
    main()
