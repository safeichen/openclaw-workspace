#!/bin/bash
# 检查并转发早间新闻推送

LOG_FILE="/root/.openclaw/workspace/morning-news-cron.log"
TEMP_FILE="/tmp/morning-news-check.tmp"

# 检查日志文件中是否有未处理的早间新闻推送
if [ -f "$LOG_FILE" ]; then
    # 查找最近的[[MORNING_NEWS_PUSH]]标记
    if grep -q "\[\[MORNING_NEWS_PUSH\]\]" "$LOG_FILE"; then
        # 提取新闻内容
        # 使用awk提取两个标记之间的内容
        awk '/\[\[MORNING_NEWS_PUSH\]\]/{flag=1; next} /\[\[END_MORNING_NEWS_PUSH\]\]/{flag=0} flag' "$LOG_FILE" > "$TEMP_FILE"
        
        if [ -s "$TEMP_FILE" ]; then
            NEWS_CONTENT=$(cat "$TEMP_FILE")
            
            # 发送到微信
            WECHAT_USER_ID="o9cq807kCZ8f9w0SsniiqByxTCRY@im.wechat"
            
            echo "📰 发现未处理的早间新闻推送，正在转发到微信..."
            
            # 使用message工具发送
            if openclaw message send --channel openclaw-weixin --target "$WECHAT_USER_ID" --message "$NEWS_CONTENT" 2>/dev/null; then
                echo "✅ 早间新闻已成功转发到微信"
                
                # 标记为已处理（可选：清理日志中的标记）
                # 这里我们只是记录一下，不清除标记，以便调试
                echo "📝 早间新闻推送已处理于: $(date)"
            else
                echo "❌ 转发到微信失败"
            fi
            
            rm -f "$TEMP_FILE"
        fi
    fi
fi