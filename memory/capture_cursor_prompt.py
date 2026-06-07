"""
Cursor 请求抓取 - 只提取 System Prompt + 用户消息
Windows/macOS/Linux 通用
"""

import json
import os
import re
from datetime import datetime
from mitmproxy import http

TARGET_DOMAINS = ["api2.cursor.sh", "api.cursor.sh", "cursor.sh"]


def request(flow: http.HTTPFlow) -> None:
    url = flow.request.pretty_url

    # 只抓 Cursor 的 API 请求
    if not any(d in url for d in TARGET_DOMAINS):
        return
    if flow.request.method != "POST":
        return

    # 解析请求体
    body_str = flow.request.get_text() or ""
    if not body_str:
        return

    try:
        body = json.loads(body_str)
    except json.JSONDecodeError:
        return

    # 提取 messages
    messages = body.get("messages", [])
    if not messages:
        return

    # 输出内容
    output = []
    output.append(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"🌐 {url}")

    # 模型信息
    model = body.get("model", body.get("engine", "未知"))
    output.append(f"🧠 模型: {model}")
    output.append("")

    # ========== System Prompt ==========
    system_msgs = [m for m in messages if m.get("role") == "system"]
    if system_msgs:
        output.append("=" * 60)
        output.append("【SYSTEM PROMPT - 系统提示词】")
        output.append("=" * 60)
        for msg in system_msgs:
            content = msg.get("content", "")
            if isinstance(content, list):
                content = "\n".join(
                    p.get("text", "") for p in content if p.get("type") == "text"
                )
            output.append(content)

    # ========== 用户消息 ==========
    user_msgs = [m for m in messages if m.get("role") == "user"]
    if user_msgs:
        output.append("")
        output.append("=" * 60)
        output.append("【USER MESSAGES - 用户消息】")
        output.append("=" * 60)
        for i, msg in enumerate(user_msgs[-5:], 1):  # 最近5条
            content = msg.get("content", "")
            if isinstance(content, list):
                texts = []
                for p in content:
                    if p.get("type") == "text":
                        texts.append(p.get("text", ""))
                    elif p.get("type") == "image":
                        texts.append("[图片附件]")
                content = "\n".join(texts)
            output.append(f"\n--- 用户消息 #{i} ---")
            output.append(content)
            output.append("")

    # 保存文件
    os.makedirs("cursor_prompts", exist_ok=True)
    safe_url = re.sub(r'[^a-zA-Z0-9]', '_', url)[:50]
    filename = f"cursor_prompts/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_url}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    print(f"\n✅ 已保存: {filename}")
    print(f"   模型: {model}")
    print(f"   总消息数: {len(messages)}")
    print(f"   System: {len(system_msgs)}, User: {len(user_msgs)}")
