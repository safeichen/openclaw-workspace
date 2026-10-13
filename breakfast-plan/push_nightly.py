#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每晚 20:00 提醒第二天早餐吃什么。
从 state.json 读取本周计划（current_week_plan: {周几: [菜名,...]}），
输出明天对应的菜单。
"""
import json
import os
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE, "state.json")

DAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def main():
    st = load_state()
    plan = st.get("current_week_plan", {})   # {"周一": ["小笼包","水煮蛋"], ...}

    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    tname = DAYS[tomorrow.weekday()]

    out = [f"🥣 【明早早餐提醒】", f"明天是 {tname}（{tomorrow.strftime('%m/%d')}）", ""]

    items = plan.get(tname) or plan.get(str(tomorrow.weekday())) or []
    if not items:
        out.append("明天还没安排早餐～")
        out.append("回复菜名即可临时加上，例如：明早 小笼包 豆浆")
    elif items == "__REST__" or items == ["休息"]:
        out.append("明天休息，不做早餐 🛌")
    else:
        out.append("明早吃：")
        for it in items:
            out.append(f"  • {it}")
        out.append("")
        out.append("早睡早起，好好吃饭 💪")

    print("[[BREAKFAST_NIGHTLY]]")
    print("\n".join(out))
    print("[[END_BREAKFAST_NIGHTLY]]")


if __name__ == "__main__":
    main()
