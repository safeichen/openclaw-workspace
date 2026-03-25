#!/bin/bash
# 一次性学校选餐提醒脚本
# 只在2026年3月25日UTC时间12:00（北京时间20:00）执行一次

# 首先检查今天是不是3月25日
TODAY=$(date +%Y-%m-%d)
if [ "$TODAY" != "2026-03-25" ]; then
    echo "今天不是2026年3月25日，跳过执行"
    exit 0
fi

# 执行提醒脚本
/root/.openclaw/workspace/school-meal-reminder.sh

# 从crontab中删除自己
(crontab -l | grep -v "one-time-school-meal-reminder.sh") | crontab -
echo "已从crontab中删除一次性提醒任务"