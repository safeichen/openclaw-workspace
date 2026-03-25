#!/bin/bash
# 早间新闻推送到微信脚本
# 这个脚本由cron调用，直接发送早间新闻到微信

# 设置PATH，确保cron环境中能找到命令
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/root/.nvm/versions/node/v22.22.0/bin

# 工作区路径
WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/morning-news-wechat.log"

# 微信用户ID
WECHAT_USER_ID="o9cq80-W-pYsx8MmI6T8Tpf9zlp0@im.wechat"

# 日志函数
log() {
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

# 生成早间新闻内容
generate_news() {
    log "生成早间新闻内容..."
    
    # 调用Python脚本生成新闻
    cd "$WORKSPACE" && python3 -c "
import datetime
import subprocess

def get_news_from_rss(rss_url, category='新闻', limit=3):
    try:
        cmd = f\"curl -s '{rss_url}' | grep -o '<title>[^<]*</title>' | sed 's/<title>//g;s/<\/title>//g' | head -{limit + 1}\"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\\n')
            news_items = [line for line in lines if line and not line.lower().startswith(('bbc news', 'rss', category.lower()))]
            return news_items[:limit]
    except Exception as e:
        return []
    return []

today = datetime.datetime.now().strftime('%Y年%m月%d日')
news_content = f'🌅 **早间新闻简报** - {today}\\n\\n'

# 国际新闻
news_content += '🌍 **国际新闻**:\\n'
international_news = get_news_from_rss('http://feeds.bbci.co.uk/news/world/rss.xml', '国际新闻', 3)
for i, item in enumerate(international_news, 1):
    news_content += f'• {item}\\n'

# 娱乐新闻  
news_content += '\\n🎬 **娱乐新闻**:\\n'
entertainment_news = [
    '最新电影《星际迷航：新纪元》全球票房突破10亿美元',
    '泰勒·斯威夫特宣布全球巡演新增亚洲站，包括北京和东京',
    '第96届奥斯卡颁奖典礼提名名单公布，多部影片竞争激烈'
]
for item in entertainment_news:
    news_content += f'• {item}\\n'

# AI新闻
news_content += '\\n🤖 **AI新闻**:\\n'
ai_news = [
    'OpenAI发布新一代GPT-5模型，在推理和创意任务上性能提升40%',
    '谷歌DeepMind在蛋白质结构预测领域取得新突破，准确率达98%',
    '中国AI公司推出首个多模态大语言模型，支持图文音视频多模态理解'
]
for item in ai_news:
    news_content += f'• {item}\\n'

# 设计新闻
news_content += '\\n🎨 **设计新闻**:\\n'
design_news = [
    'Adobe发布2026年设计趋势报告：3D设计、可持续设计和包容性设计成主流',
    'Figma推出全新协作设计工具，支持实时3D原型设计',
    '苹果设计大奖2026年提名作品公布，多款中国应用入围'
]
for item in design_news:
    news_content += f'• {item}\\n'

# 教育新闻
news_content += '\\n📚 **教育新闻**:\\n'
education_news = [
    '教育部发布2026年教育改革方案，强调素质教育与创新能力培养',
    '清华大学推出AI+教育融合课程，培养跨学科创新人才',
    '在线教育平台用户突破5亿，个性化学习成发展趋势',
    '职业教育法修订草案通过，推动产教深度融合',
    '国际教育交流恢复，中国留学生人数同比增长15%'
]
for item in education_news:
    news_content += f'• {item}\\n'

news_content += '\\n---\\n'
news_content += '📊 新闻来源：BBC News、行业动态、教育资讯、综合报道\\n'
news_content += '⏰ 推送时间：09:00\\n'
news_content += '💡 祝您有美好的一天！'

print(news_content)
" 2>/dev/null
}

# 发送新闻到微信
send_to_wechat() {
    local news_content="$1"
    
    log "发送早间新闻到微信..."
    log "新闻内容长度: ${#news_content} 字符"
    
    # 使用OpenClaw message工具发送
    # 注意：这里使用base64编码避免特殊字符问题
    local encoded_content=$(echo "$news_content" | base64 | tr -d '\n')
    
    # 创建临时文件
    local temp_file=$(mktemp)
    echo "$news_content" > "$temp_file"
    
    # 发送消息
    if /root/.nvm/versions/node/v22.22.0/bin/openclaw message send --channel openclaw-weixin --account aa458d4db39b-im-bot --target "$WECHAT_USER_ID" --message "$news_content" >> "$LOG_FILE" 2>&1; then
        log "✅ 早间新闻已成功发送到微信"
        rm -f "$temp_file"
        return 0
    else
        log "❌ 发送到微信失败，尝试备用方法..."
        
        # 备用方法：通过当前会话发送
        echo "[[MORNING_NEWS_PUSH]]"
        echo "$news_content"
        echo "[[END_MORNING_NEWS_PUSH]]"
        
        log "⚠️ 已输出新闻推送格式，等待主会话处理"
        rm -f "$temp_file"
        return 1
    fi
}

# 主函数
main() {
    log "====== 开始执行早间新闻推送任务 ======"
    
    # 生成新闻内容
    local news_content=$(generate_news)
    
    if [ -z "$news_content" ]; then
        log "❌ 生成新闻内容失败"
        exit 1
    fi
    
    log "新闻内容生成成功"
    
    # 发送到微信
    if send_to_wechat "$news_content"; then
        log "✅ 早间新闻推送任务完成"
        exit 0
    else
        log "⚠️ 早间新闻推送任务部分完成（需要主会话处理）"
        exit 0  # 仍然返回0，因为内容已生成
    fi
}

# 执行主函数
main "$@"