#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每晚 20:00 提醒第二天早餐吃什么。
直接输出【最终要发送的完整消息体】：只推送这一张海报图。
主会话/投递只需把 stdout 原文发出去，不要添加任何自己的文字。
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))


def main():
    qr = os.path.join(BASE, "poster_a4.png")
    print(f"<qqmedia>{qr}</qqmedia>")


if __name__ == "__main__":
    main()
