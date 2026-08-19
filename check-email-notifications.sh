#!/bin/bash

# 邮件通知检查脚本
# 这个脚本会被OpenClaw定期调用，检查是否有新邮件通知需要推送

# 确保 node 在 PATH 中（cron 环境 PATH 很精简）
export PATH="/root/.nvm/versions/node/v22.22.0/bin:$PATH"

# 如果上面路径不适用，自动探测 node
if ! command -v node >/dev/null 2>&1; then
    for NODE_CAND in /root/.nvm/versions/node/*/bin/node /usr/local/bin/node /usr/bin/node; do
        if [ -x "$NODE_CAND" ]; then
            export PATH="$(dirname "$NODE_CAND"):$PATH"
            break
        fi
    done
fi

SCRIPT_DIR="/root/.openclaw/workspace/skills/imap-smtp-email/scripts"
LOG_FILE="$SCRIPT_DIR/logs/cron-push.log"
PUSH_SCRIPT="$SCRIPT_DIR/push-to-clawbot.js"
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

# 检查早间新闻推送
echo ""
echo "📰 检查早间新闻推送..."
MORNING_NEWS_LOG="/root/.openclaw/workspace/morning-news-cron.log"

if [ -f "$MORNING_NEWS_LOG" ] && grep -q "\[\[MORNING_NEWS_PUSH\]\]" "$MORNING_NEWS_LOG"; then
    echo "✅ 检测到未处理的早间新闻推送"
    
    # 提取新闻内容
    NEWS_CONTENT=$(awk '/\[\[MORNING_NEWS_PUSH\]\]/{flag=1; next} /\[\[END_MORNING_NEWS_PUSH\]\]/{flag=0} flag' "$MORNING_NEWS_LOG")
    
    if [ -n "$NEWS_CONTENT" ]; then
        echo "📋 早间新闻内容已提取"
        echo ""
        echo "[[MORNING_NEWS_PUSH]]"
        echo "$NEWS_CONTENT"
        echo "[[END_MORNING_NEWS_PUSH]]"
    else
        echo "⚠️ 无法提取早间新闻内容"
    fi
else
    echo "ℹ️ 没有未处理的早间新闻推送"
fi

# 检查AI资讯提醒
echo ""
echo "🤖 检查AI资讯提醒..."
AI_NEWS_LOG="/root/.openclaw/workspace/ai-news-cron.log"

if [ -f "$AI_NEWS_LOG" ] && grep -q "\[\[AI_NEWS_REMINDER\]\]" "$AI_NEWS_LOG"; then
    echo "✅ 检测到未处理的AI资讯提醒"
    
    # 提取AI资讯内容
    AI_CONTENT=$(awk '/\[\[AI_NEWS_REMINDER\]\]/{flag=1; next} /\[\[END_AI_NEWS_REMINDER\]\]/{flag=0} flag' "$AI_NEWS_LOG")
    
    if [ -n "$AI_CONTENT" ]; then
        echo "📋 AI资讯内容已提取"
        echo ""
        echo "[[AI_NEWS_REMINDER]]"
        echo "$AI_CONTENT"
        echo "[[END_AI_NEWS_REMINDER]]"
    else
        echo "⚠️ 无法提取AI资讯内容"
    fi
else
    echo "ℹ️ 没有未处理的AI资讯提醒"
fi

# 检查AI每日报告
echo ""
echo "📋 检查AI每日报告..."
AI_DAILY_REPORT_LOG="/root/.openclaw/workspace/ai-daily-report-cron.log"

if [ -f "$AI_DAILY_REPORT_LOG" ] && grep -q "\[\[AI_DAILY_REPORT\]\]" "$AI_DAILY_REPORT_LOG"; then
    echo "✅ 检测到未处理的AI每日报告"
    
    # 提取AI每日报告内容
    AI_DAILY_CONTENT=$(awk '/\[\[AI_DAILY_REPORT\]\]/{flag=1; next} /\[\[END_AI_DAILY_REPORT\]\]/{flag=0} flag' "$AI_DAILY_REPORT_LOG")
    
    if [ -n "$AI_DAILY_CONTENT" ]; then
        echo "📋 AI每日报告内容已提取"
        echo ""
        echo "[[AI_DAILY_REPORT]]"
        echo "$AI_DAILY_CONTENT"
        echo "[[END_AI_DAILY_REPORT]]"
    else
        echo "⚠️ 无法提取AI每日报告内容"
    fi
else
    echo "ℹ️ 没有未处理的AI每日报告"
fi

# 检查学校选餐提醒
echo ""
echo "🏫 检查学校选餐提醒..."
SCHOOL_MEAL_LOG="/root/.openclaw/workspace/school-meal-cron.log"

if [ -f "$SCHOOL_MEAL_LOG" ] && grep -q "\[\[SCHOOL_MEAL_REMINDER\]\]" "$SCHOOL_MEAL_LOG"; then
    echo "✅ 检测到未处理的学校选餐提醒"
    
    # 提取学校选餐提醒内容
    SCHOOL_MEAL_CONTENT=$(awk '/\[\[SCHOOL_MEAL_REMINDER\]\]/{flag=1; next} /\[\[END_SCHOOL_MEAL_REMINDER\]\]/{flag=0} flag' "$SCHOOL_MEAL_LOG")
    
    if [ -n "$SCHOOL_MEAL_CONTENT" ]; then
        echo "📋 学校选餐提醒内容已提取"
        echo ""
        echo "[[SCHOOL_MEAL_REMINDER]]"
        echo "$SCHOOL_MEAL_CONTENT"
        echo "[[END_SCHOOL_MEAL_REMINDER]]"
    else
        echo "⚠️ 无法提取学校选餐提醒内容"
    fi
else
    echo "ℹ️ 没有未处理的学校选餐提醒"
fi

echo "✅ 邮件通知检查完成"