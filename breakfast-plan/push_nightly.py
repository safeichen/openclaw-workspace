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

    out = ["🥣 【明早早餐提醒】", f"明天 {tname}（{tomorrow.strftime('%m/%d')}）", ""]

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

    if lines:
        out.append("📋 已点：")
        out += lines
        out.append("")
        out.append("想改就点这里 👉 http://ipainting.cc/breakfast/")
    else:
        # 2) 周计划兜底
        st = load_json(STATE_FILE, {})
        plan = st.get("current_week_plan", {})
        items = plan.get(tname) or plan.get(str(tomorrow.weekday())) or []
        if items and items != ["休息"] and items != "__REST__":
            out.append("📋 明早吃：")
            for it in items:
                out.append(f"  • {it}")
            out.append("")
            out.append("想改就点这里 👉 http://ipainting.cc/breakfast/")
        elif items in (["休息"], ["__REST__"]):
            out.append("明早休息，不做早餐 🛌")
        else:
            out.append("明天还没点早餐哦～")
            out.append("👉 点这里选：http://ipainting.cc/breakfast/")

    out.append("")
    out.append("早睡早起，好好吃饭 💪")
    print("[[BREAKFAST_NIGHTLY]]")
    print("\n".join(out))
    print("[[QR]]")
    print(os.path.join(BASE, "order_qr.png"))
    print("[[END_BREAKFAST_NIGHTLY]]")


if __name__ == "__main__":
    main()
