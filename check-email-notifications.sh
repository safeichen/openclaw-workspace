#!/bin/bash

# 邮件通知检查脚本
# 这个脚本会被OpenClaw定期调用，检查是否有新邮件通知需要推送

SCRIPT_DIR="/root/.openclaw/workspace/skills/imap-smtp-email/scripts"
LOG_FILE="$SCRIPT_DIR/logs/cron-push.log"
PUSH_SCRIPT="$SCRIPT_DIR/push-to-qqbot.js"
LAST_CHECK_FILE="$SCRIPT_DIR/last-check.txt"

# 创建必要的目录
mkdir -p "$SCRIPT_DIR/logs"

echo "📧 开始检查邮件通知..."
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "脚本目录: $SCRIPT_DIR"
echo "日志文件: $LOG_FILE"
echo ""

# 检查推送脚本是否存在
if [ ! -f "$PUSH_SCRIPT" ]; then
    echo "❌ 错误: 推送脚本不存在: $PUSH_SCRIPT"
    exit 1
fi

# 运行邮件检查
echo "🔄 运行邮件检查..."
cd "$SCRIPT_DIR"

# 运行推送脚本，捕获输出
OUTPUT=$(timeout 60 node "$PUSH_SCRIPT" 2>&1)
EXIT_CODE=$?

echo "📊 检查完成，退出码: $EXIT_CODE"
echo ""

# 分析输出
if echo "$OUTPUT" | grep -q "\[\[QQ_BOT_PUSH_START\]\]"; then
    echo "✅ 检测到新邮件通知！"
    echo ""
    
    # 提取通知内容
    NOTIFICATION=$(echo "$OUTPUT" | sed -n '/\[\[QQ_BOT_PUSH_START\]\]/,/\[\[QQ_BOT_PUSH_END\]\]/p')
    
    # 移除标记行
    NOTIFICATION=$(echo "$NOTIFICATION" | grep -v "\[\[QQ_BOT_PUSH_START\]\]" | grep -v "\[\[QQ_BOT_PUSH_END\]\]")
    
    echo "📋 通知内容:"
    echo "$NOTIFICATION"
    echo ""
    
    # 记录最后检查时间
    date '+%Y-%m-%d %H:%M:%S' > "$LAST_CHECK_FILE"
    
    # 这里应该通过QQ Bot发送通知
    # 由于我们无法直接调用message工具，我们将输出特定格式让主会话处理
    echo "[[EMAIL_NOTIFICATION]]"
    echo "$NOTIFICATION"
    echo "[[END_EMAIL_NOTIFICATION]]"
    
elif echo "$OUTPUT" | grep -q "\[\[NO_NEW_EMAIL\]\]"; then
    echo "ℹ️ 没有新邮件"
    # 记录最后检查时间
    date '+%Y-%m-%d %H:%M:%S' > "$LAST_CHECK_FILE"
else
    echo "⚠️ 邮件检查可能出错"
    echo "输出: $OUTPUT"
fi

echo ""
echo "📅 最后检查时间已更新"
echo "✅ 邮件通知检查完成"