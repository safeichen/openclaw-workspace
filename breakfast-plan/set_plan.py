#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析用户的选择回复，写入 current_week_plan。
用法：
  python3 set_plan.py "周一：1 5 9" "周二：2 3" ...
或从 stdin 读多行。
也可单日：python3 set_plan.py --day 周一 1 5 9
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE, "state.json")
DAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"week": {}, "flat_menu": {}, "current_week_plan": {}}


def save_state(st):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)


def names_for(nums, flat):
    out = []
    for n in nums:
        n = n.strip()
        if not n:
            continue
        if n in flat:
            out.append(flat[n]["name"])
        else:
            out.append(n)  # 允许自定义菜名
    return out


def main():
    st = load_state()
    flat = st.get("flat_menu", {})
    plan = st.get("current_week_plan", {})

    args = sys.argv[1:]
    if args and args[0] == "--day":
        day = args[1]
        nums = args[2:]
        plan[day] = names_for(nums, flat)
    else:
        for line in args:
            for seg in line.splitlines():
                if not seg.strip():
                    continue
                if "：" in seg:
                    day, rest = seg.split("：", 1)
                elif ":" in seg:
                    day, rest = seg.split(":", 1)
                else:
                    continue
                day = day.strip()
                if day not in DAYS:
                    continue
                nums = rest.replace(",", " ").split()
                plan[day] = names_for(nums, flat)

    st["current_week_plan"] = plan
    st["plan_updated_at"] = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_state(st)
    print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
