#!/bin/bash
# 每周六 9:00 推送下周早餐菜单
cd /root/.openclaw/workspace/breakfast-plan
python3 push_weekly_menu.py >> weekly.log 2>&1
