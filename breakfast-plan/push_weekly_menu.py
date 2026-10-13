#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每周六 9:00 推送下周早餐菜单，供选择。
输出到 stdout，由主会话（agent）捕获并通过 QQ 发送。
同时把"待选区"写入 state.json，供用户回复编号时解析。
"""
import json
import os
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE, "menu.json")
STATE_FILE = os.path.join(BASE, "state.json")

DAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def load_menu():
    with open(MENU_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"week": {}, "flat_menu": {}, "current_week_plan": {}}


def save_state(st):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)


def next_week_monday():
    today = datetime.now().date()
    # 下周一
    days_ahead = 7 - today.weekday()  # weekday(): Mon=0
    if today.weekday() == 5:  # 周六当天推送，下周一是 +2
        days_ahead = 2
    return today + timedelta(days=days_ahead)


def build():
    menu = load_menu()
    # 展平成带编号的列表
    flat = {}
    lines = []
    idx = 1
    for cat in menu["categories"]:
        lines.append(f"\n{cat['icon']} 【{cat['name']}】")
        for it in cat["items"]:
            note = f" - {it['note']}" if it.get("note") else ""
            lines.append(f"  {idx}. {it.get('emoji','')} {it['name']}{note}")
            flat[str(idx)] = {"name": it["name"], "emoji": it.get("emoji", ""), "cat": cat["name"]}
            idx += 1

    monday = next_week_monday()
    sunday = monday + timedelta(days=6)
    st = load_state()
    st["flat_menu"] = flat
    st["week"] = {
        "monday": monday.isoformat(),
        "sunday": sunday.isoformat(),
        "pushed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "picks": {},          # {day: [item_names]}
        "selected": False,
    }
    save_state(st)

    header = [
        f"🍳 【下周早餐菜单】( {monday.strftime('%m/%d')} ~ {sunday.strftime('%m/%d')} )",
        "",
        "请回复每天想吃的编号，格式示例👇",
        "  周一：1 5 9",
        "  周二：2 3",
        "  （每天一行，空格分隔编号）",
        "  也可以回复「套餐A」等自定义，或「休息」表示当天不做。",
    ]
    body = "\n".join(header + lines)
    body += "\n\n📅 回复示例（复制修改）：\n"
    for i, d in enumerate(DAYS):
        body += f"{d}：\n"
    body += "\n选好后我每周汇总，每晚 8 点提醒第二天吃什么。"
    return body


if __name__ == "__main__":
    print("[[BREAKFAST_WEEKLY_MENU]]")
    print(build())
    print("[[END_BREAKFAST_WEEKLY_MENU]]")
