#!/bin/bash
# 每晚 20:00 提醒明早吃什么
cd /root/.openclaw/workspace/breakfast-plan
python3 push_nightly.py >> nightly.log 2>&1
