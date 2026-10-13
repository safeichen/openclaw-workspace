#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每晚 20:00 提醒第二天早餐吃什么。
数据来源：
  1) 网页点单（breakfast-order/data/orders.json）—— 用户实际选的
  2) 周计划（breakfast-plan/state.json 的 current_week_plan）—— 文字选餐兜底
输出到 stdout，由主会话捕获并推送到 QQ。
"""
import json
import os
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE, "state.json")
ORDERS_FILE = "/root/.openclaw/workspace/breakfast-order/data/orders.json"

DAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default


def main():
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    tname = DAYS[tomorrow.weekday()]
    today_name = DAYS[now.weekday()]

    out = ["叮咚~ 明天早餐想吃点啥呀？🍳✨", f"（{tname} {tomorrow.strftime('%m/%d')}）", ""]

    # 1) 网页点单
    orders = load_json(ORDERS_FILE, {})
    lines = []
    for person, od in orders.items():
        items = od.get("items", [])
        if not items:
            continue
        s = "、".join(f"{i['name']}×{i['qty']}" if i.get("qty", 1) > 1 else i["name"] for i in items)
        ts = od.get("ts", "")
        t = f"（{ts[11:16]} 提交）" if ts else ""
        lines.append(f"  👤 {person}：{s}{t}")

    # 已点清单不在提醒里展示（改为提交时单独推送）；这里只负责邀请去挑
    out.append("扫扫这个小方块，挑几样喜欢的～")
    out.append("")
    out.append("早睡早起，才能长得高高壮壮 🌱💛")
    print("[[BREAKFAST_NIGHTLY]]")
    print("\n".join(out))
    print("[[QR]]")
    print(os.path.join(BASE, "order_qr.png"))
    print("[[END_BREAKFAST_NIGHTLY]]")


if __name__ == "__main__":
    main()
