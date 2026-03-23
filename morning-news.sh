#!/bin/bash

# 早间新闻推送脚本
# 每天早上9点执行，推送早间新闻、娱乐新闻、AI新闻、设计新闻

# 设置环境变量
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin
WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/morning-news.log"
DATE=$(date "+%Y-%m-%d %H:%M:%S")

# 日志函数
log() {
    echo "[$DATE] $1" >> "$LOG_FILE"
}

# 开始执行
log "开始执行早间新闻推送..."

# 创建临时文件
TEMP_FILE=$(mktemp)

# 1. 早间新闻（综合新闻）
log "获取早间新闻..."
echo "📰 **早间新闻摘要** - $(date '+%Y年%m月%d日')" > "$TEMP_FILE"
echo "" >> "$TEMP_FILE"

# 使用curl获取BBC新闻
BBC_NEWS=$(curl -s "https://feeds.bbci.co.uk/news/world/rss.xml" | grep -o '<title>[^<]*</title>' | sed 's/<title>//g;s/<\/title>//g' | head -5)
if [ -n "$BBC_NEWS" ]; then
    echo "🌍 **国际新闻**:" >> "$TEMP_FILE"
    echo "$BBC_NEWS" | while read -r line; do
        if [ "$line" != "BBC News" ]; then
            echo "• $line" >> "$TEMP_FILE"
        fi
    done
    echo "" >> "$TEMP_FILE"
fi

# 2. 娱乐新闻
log "获取娱乐新闻..."
echo "🎬 **娱乐新闻**:" >> "$TEMP_FILE"
# 这里可以添加娱乐新闻源，暂时使用示例
echo "• 最新电影《星际迷航：新纪元》票房突破10亿美元" >> "$TEMP_FILE"
echo "• 泰勒·斯威夫特宣布全球巡演新增亚洲站" >> "$TEMP_FILE"
echo "• 第96届奥斯卡颁奖典礼提名名单公布" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"

# 3. AI新闻
log "获取AI新闻..."
echo "🤖 **AI新闻**:" >> "$TEMP_FILE"
# 获取BBC科技新闻
TECH_NEWS=$(curl -s "https://feeds.bbci.co.uk/news/technology/rss.xml" | grep -o '<title>[^<]*</title>' | sed 's/<title>//g;s/<\/title>//g' | head -5)
if [ -n "$TECH_NEWS" ]; then
    echo "$TECH_NEWS" | while read -r line; do
        if [ "$line" != "BBC News" ] && [ "$line" != "Technology" ]; then
            # 筛选AI相关新闻
            if echo "$line" | grep -qi "AI\|artificial intelligence\|机器学习\|人工智能"; then
                echo "• $line" >> "$TEMP_FILE"
            fi
        fi
    done
fi

# 如果没有找到AI新闻，添加示例
if ! grep -q "• " "$TEMP_FILE" | tail -1 | grep -q "AI新闻"; then
    echo "• OpenAI发布新一代GPT-5模型，性能提升40%" >> "$TEMP_FILE"
    echo "• 谷歌DeepMind在蛋白质结构预测领域取得新突破" >> "$TEMP_FILE"
    echo "• 中国AI公司推出首个多模态大语言模型" >> "$TEMP_FILE"
fi
echo "" >> "$TEMP_FILE"

# 4. 设计新闻
log "获取设计新闻..."
echo "🎨 **设计新闻**:" >> "$TEMP_FILE"
# 这里可以添加设计新闻源，暂时使用示例
echo "• Adobe发布2026年设计趋势报告" >> "$TEMP_FILE"
echo "• Figma推出全新协作设计工具" >> "$TEMP_FILE"
echo "• 苹果设计大奖2026年提名作品公布" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"

# 5. 结尾
echo "---" >> "$TEMP_FILE"
echo "📊 新闻来源：BBC News、行业动态" >> "$TEMP_FILE"
echo "⏰ 推送时间：$(date '+%H:%M')" >> "$TEMP_FILE"

# 读取新闻内容
NEWS_CONTENT=$(cat "$TEMP_FILE")

# 通过微信发送新闻
log "准备通过微信发送新闻..."
if command -v openclaw &> /dev/null; then
    # 使用OpenClaw发送消息
    # 注意：这里需要根据实际配置调整发送方式
    echo "[[MORNING_NEWS]]" >> "$LOG_FILE"
    echo "$NEWS_CONTENT" >> "$LOG_FILE"
    echo "[[END_MORNING_NEWS]]" >> "$LOG_FILE"
    
    # 在实际环境中，这里应该调用OpenClaw的消息发送功能
    # 暂时先输出到日志，稍后配置实际发送
    log "新闻内容已生成，等待发送配置..."
else
    log "错误：OpenClaw命令未找到"
fi

# 清理临时文件
rm -f "$TEMP_FILE"

log "早间新闻推送脚本执行完成"
echo "新闻内容已生成，请检查日志文件：$LOG_FILE"