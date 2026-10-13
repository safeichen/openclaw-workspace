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
DAY_EMOJI = {"周一": "🟠", "周二": "🔴", "周三": "🟡", "周四": "🟢",
             "周五": "🔵", "周六": "🟣", "周日": "🟤"}


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
    days_ahead = 7 - today.weekday()
    if today.weekday() == 5:
        days_ahead = 2
    return today + timedelta(days=days_ahead)


def build():
    menu = load_menu()
    flat = {}
    lines = []
    idx = 1
    for cat in menu["categories"]:
        lines.append(f"\n{cat['icon']} 【{cat['name']}】")
        for it in cat["items"]:
            note = f" {it['note']}" if it.get("note") else ""
            lines.append(f"  {idx}.  {it.get('emoji','')} {it['name']}{note}")
            flat[str(idx)] = {"name": it["name"], "emoji": it.get("emoji", ""), "cat": cat["name"]}
            idx += 1
    flat["7"] = {"name": "其他", "emoji": "✍️", "cat": "其他"}

    monday = next_week_monday()
    sunday = monday + timedelta(days=6)
    st = load_state()
    st["flat_menu"] = flat
    st["week"] = {
        "monday": monday.isoformat(),
        "sunday": sunday.isoformat(),
        "pushed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_state(st)

    out = []
    out.append("╭──────────────────────╮")
    out.append("   🍳 下周早餐菜单")
    out.append("╰──────────────────────╯")
    out.append(f"🗓  {monday.strftime('%m/%d')} (周一) ~ {sunday.strftime('%m/%d')} (周日)")
    out.append("")
    out.append("┌ 请选餐 ┐")
    out += lines
    out.append("")
    out.append("━━━━━━━━━━━━━━")
    out.append("✏️ 回复格式（每天一行）：")
    for d in DAYS:
        out.append(f"  {DAY_EMOJI[d]} {d}：")
    out.append("")
    out.append("💡 例：周一：1 2   周三：5")
    out.append("   想加别的 → 「周一：其他 包子」")
    out.append("   不做早餐 → 「周六：休息」")
    out.append("━━━━━━━━━━━━━━")
    out.append("")
    out.append("选好后每晚 8 点提醒你第二天吃啥 🔔")
    return "\n".join(out)


if __name__ == "__main__":
    print("[[BREAKFAST_WEEKLY_MENU]]")
    print(build())
    print("[[END_BREAKFAST_WEEKLY_MENU]]")
