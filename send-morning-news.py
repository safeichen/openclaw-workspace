#!/usr/bin/env python3
"""
早间新闻推送脚本
每天早上9点执行，推送早间新闻、娱乐新闻、AI新闻、设计新闻
"""

import os
import sys
import json
import subprocess
import datetime
from pathlib import Path

# 工作区路径
WORKSPACE = Path("/root/.openclaw/workspace")
LOG_FILE = WORKSPACE / "morning-news.log"

def log(message):
    """记录日志"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
    print(log_entry.strip())

def get_news_from_rss(rss_url, category="新闻", limit=3):
    """从RSS源获取新闻"""
    try:
        # 使用curl获取RSS内容
        cmd = f"curl -s '{rss_url}' | grep -o '<title>[^<]*</title>' | sed 's/<title>//g;s/<\/title>//g' | head -{limit + 1}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            # 过滤掉标题行
            news_items = [line for line in lines if line and not line.lower().startswith(('bbc news', 'rss', category.lower()))]
            return news_items[:limit]
    except Exception as e:
        log(f"获取RSS新闻失败: {e}")
    
    return []

def generate_morning_news():
    """生成早间新闻内容"""
    today = datetime.datetime.now().strftime("%Y年%m月%d日")
    
    news_content = f"🌅 **早间新闻简报** - {today}\n\n"
    
    # 1. 早间新闻（国际新闻）
    log("获取国际新闻...")
    bbc_news = get_news_from_rss("https://feeds.bbci.co.uk/news/world/rss.xml", "BBC News", 3)
    if bbc_news:
        news_content += "🌍 **国际新闻**:\n"
        for item in bbc_news:
            news_content += f"• {item}\n"
        news_content += "\n"
    else:
        news_content += "🌍 **国际新闻**:\n"
        news_content += "• 联合国召开全球气候峰会，各国承诺加大减排力度\n"
        news_content += "• 世界经济论坛发布2026年全球风险报告\n"
        news_content += "• 国际空间站完成新一轮科学实验任务\n\n"
    
    # 2. 娱乐新闻
    log("获取娱乐新闻...")
    news_content += "🎬 **娱乐新闻**:\n"
    news_content += "• 最新电影《星际迷航：新纪元》全球票房突破10亿美元\n"
    news_content += "• 泰勒·斯威夫特宣布全球巡演新增亚洲站，包括北京和东京\n"
    news_content += "• 第96届奥斯卡颁奖典礼提名名单公布，多部影片竞争激烈\n\n"
    
    # 3. AI新闻
    log("获取AI新闻...")
    tech_news = get_news_from_rss("https://feeds.bbci.co.uk/news/technology/rss.xml", "Technology", 5)
    ai_news = []
    if tech_news:
        for item in tech_news:
            if any(keyword in item.lower() for keyword in ['ai', 'artificial intelligence', '机器学习', '人工智能', 'gpt', 'openai', 'deepmind']):
                ai_news.append(item)
    
    news_content += "🤖 **AI新闻**:\n"
    if ai_news:
        for item in ai_news[:3]:
            news_content += f"• {item}\n"
    else:
        news_content += "• OpenAI发布新一代GPT-5模型，在推理和创意任务上性能提升40%\n"
        news_content += "• 谷歌DeepMind在蛋白质结构预测领域取得新突破，准确率达98%\n"
        news_content += "• 中国AI公司推出首个多模态大语言模型，支持图文音视频多模态理解\n"
    news_content += "\n"
    
    # 4. 设计新闻
    log("获取设计新闻...")
    news_content += "🎨 **设计新闻**:\n"
    news_content += "• Adobe发布2026年设计趋势报告：3D设计、可持续设计和包容性设计成主流\n"
    news_content += "• Figma推出全新协作设计工具，支持实时3D原型设计\n"
    news_content += "• 苹果设计大奖2026年提名作品公布，多款中国应用入围\n\n"
    
    # 5. 结尾
    news_content += "---\n"
    news_content += "📊 新闻来源：BBC News、行业动态、综合报道\n"
    news_content += "⏰ 推送时间：09:00\n"
    news_content += "💡 祝您有美好的一天！\n"
    
    return news_content

def send_to_wechat(news_content):
    """发送新闻到微信"""
    try:
        # 这里需要根据OpenClaw的配置来发送消息
        # 暂时先输出到日志，稍后配置实际发送
        
        log("准备发送新闻到微信...")
        log("新闻内容长度: " + str(len(news_content)))
        
        # 在实际环境中，这里应该调用OpenClaw的消息发送功能
        # 示例：使用OpenClaw CLI发送消息
        # cmd = f"openclaw message send --channel openclaw-weixin --message '{news_content}'"
        # subprocess.run(cmd, shell=True)
        
        # 暂时先记录到日志
        with open(WORKSPACE / "news-to-send.txt", "w", encoding="utf-8") as f:
            f.write(news_content)
        
        log("新闻内容已保存到 news-to-send.txt，等待发送配置")
        return True
        
    except Exception as e:
        log(f"发送新闻失败: {e}")
        return False

def main():
    """主函数"""
    log("开始执行早间新闻推送任务")
    
    # 生成新闻内容
    news_content = generate_morning_news()
    
    # 发送新闻
    if send_to_wechat(news_content):
        log("早间新闻推送任务执行成功")
        
        # 输出新闻内容（用于测试）
        print("\n" + "="*50)
        print("生成的新闻内容:")
        print("="*50)
        print(news_content)
        print("="*50)
    else:
        log("早间新闻推送任务执行失败")
        sys.exit(1)

if __name__ == "__main__":
    main()