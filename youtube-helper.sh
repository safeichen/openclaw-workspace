#!/bin/bash
# YouTube视频处理助手

echo "🎬 YouTube视频处理工具"
echo "======================"

if [ $# -eq 0 ]; then
    echo "使用方法:"
    echo "  $0 <YouTube链接> [选项]"
    echo ""
    echo "选项:"
    echo "  --summary    获取视频摘要"
    echo "  --transcript 获取视频字幕"
    echo "  --info       获取视频信息"
    echo "  --all        获取所有信息"
    echo ""
    echo "示例:"
    echo "  $0 https://youtu.be/dQw4w9WgXcQ --summary"
    echo "  $0 https://www.youtube.com/watch?v=VIDEO_ID --transcript"
    exit 1
fi

URL="$1"
OPTION="${2:---all}"

echo "处理链接: $URL"
echo "选项: $OPTION"
echo ""

# 检查是否安装了必要的工具
check_tools() {
    echo "🔧 检查工具..."
    
    # 检查curl
    if command -v curl &> /dev/null; then
        echo "  ✅ curl已安装"
    else
        echo "  ❌ curl未安装"
        return 1
    fi
    
    # 检查jq
    if command -v jq &> /dev/null; then
        echo "  ✅ jq已安装"
    else
        echo "  ⚠️ jq未安装，将使用简化输出"
    fi
    
    # 检查python3
    if command -v python3 &> /dev/null; then
        echo "  ✅ python3已安装"
    else
        echo "  ⚠️ python3未安装"
    fi
    
    echo ""
}

# 提取视频ID
extract_video_id() {
    local url="$1"
    
    # 处理各种YouTube链接格式
    if [[ "$url" == *"youtu.be/"* ]]; then
        # youtu.be格式
        echo "$url" | sed 's|.*youtu.be/||' | cut -d'?' -f1 | cut -d'&' -f1
    elif [[ "$url" == *"youtube.com/watch"* ]]; then
        # youtube.com格式
        echo "$url" | sed 's|.*v=||' | cut -d'&' -f1
    elif [[ "$url" == *"youtube.com/embed/"* ]]; then
        # embed格式
        echo "$url" | sed 's|.*embed/||' | cut -d'?' -f1
    else
        echo "无法识别的YouTube链接格式"
        return 1
    fi
}

# 获取视频信息
get_video_info() {
    local video_id="$1"
    
    echo "📊 获取视频信息..."
    echo "视频ID: $video_id"
    echo ""
    
    # 这里可以添加调用YouTube API的代码
    # 目前先返回模拟数据
    echo "标题: [需要YouTube API密钥获取]"
    echo "频道: [需要YouTube API密钥获取]"
    echo "时长: [需要YouTube API密钥获取]"
    echo "发布时间: [需要YouTube API密钥获取]"
    echo "观看次数: [需要YouTube API密钥获取]"
    echo ""
}

# 获取视频摘要（模拟）
get_video_summary() {
    echo "📝 视频摘要:"
    echo "------------"
    echo "这是一个YouTube视频处理工具的演示。"
    echo "要获取真实视频摘要，需要:"
    echo "1. YouTube Data API v3密钥"
    echo "2. 或者使用第三方服务如summarize CLI"
    echo ""
    echo "建议的解决方案:"
    echo "1. 申请YouTube API密钥: https://console.cloud.google.com/apis"
    echo "2. 安装summarize CLI: npm install -g @steipete/summarize"
    echo "3. 设置API密钥: export GEMINI_API_KEY=your_key"
    echo "4. 使用: summarize \"$URL\" --youtube auto"
    echo ""
}

# 获取字幕（模拟）
get_transcript() {
    echo "📄 视频字幕:"
    echo "----------"
    echo "要获取YouTube视频字幕，需要:"
    echo "1. YouTube Transcript API访问权限"
    echo "2. 或者使用youtube-transcript-api等工具"
    echo ""
    echo "Python示例代码:"
    cat << 'PYTHONCODE'
from youtube_transcript_api import YouTubeTranscriptApi

# 获取字幕
transcript = YouTubeTranscriptApi.get_transcript(video_id)

# 打印字幕
for entry in transcript:
    print(f"{entry['start']:.1f}s: {entry['text']}")
PYTHONCODE
    echo ""
}

# 主程序
main() {
    check_tools
    
    VIDEO_ID=$(extract_video_id "$URL")
    if [ $? -ne 0 ]; then
        echo "错误: $VIDEO_ID"
        exit 1
    fi
    
    case "$OPTION" in
        --info)
            get_video_info "$VIDEO_ID"
            ;;
        --summary)
            get_video_summary
            ;;
        --transcript)
            get_transcript
            ;;
        --all|*)
            get_video_info "$VIDEO_ID"
            get_video_summary
            get_transcript
            ;;
    esac
    
    echo "🎯 下一步建议:"
    echo "1. 安装完整的YouTube Watcher技能（等待ClawHub速率限制恢复）"
    echo "2. 配置YouTube API密钥"
    echo "3. 或使用现有的summarize技能（需要安装CLI）"
    echo ""
    echo "💡 提示: 你可以先提供YouTube链接，我会尝试用现有方法处理"
}

main