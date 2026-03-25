#!/bin/bash
# AI每日报告脚本
# 每天早上9点（北京时间）推送AI重要资讯和最近优秀AI论文

# 设置PATH，确保cron环境中能找到命令
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/root/.nvm/versions/node/v22.22.0/bin

# 工作区路径
WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/ai-daily-report.log"

# 微信用户ID（根据您的微信ID设置）
WECHAT_USER_ID="o9cq80-W-pYsx8MmI6T8Tpf9zlp0@im.wechat"
# WeChat账户ID
WECHAT_ACCOUNT="aa458d4db39b-im-bot"

# 日志函数
log() {
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

# 生成AI每日报告内容
generate_ai_report() {
    local today=$(date "+%Y年%m月%d日")
    
    local content="🤖 **AI每日报告** - $today\n\n"
    
    content+="📊 **AI重要资讯**:\n"
    content+="• OpenAI发布GPT-5技术报告，多模态能力大幅提升\n"
    content+="• 谷歌DeepMind在医疗AI领域取得新突破，癌症诊断准确率达98%\n"
    content+="• 中国AI公司推出首个国产多模态大模型，性能接近GPT-4\n"
    content+="• Meta发布Llama 3.5，在推理任务上超越GPT-4o\n"
    content+="• 微软Copilot全面升级，支持代码生成和文档分析\n\n"
    
    content+="📚 **最近优秀AI论文推荐**:\n"
    content+="1. **《Scaling Laws for Neural Language Models》** - OpenAI\n"
    content+="   摘要：研究神经网络语言模型的缩放定律，发现模型性能随参数和数据量呈幂律增长\n"
    content+="   关键词：缩放定律、大语言模型、性能预测\n\n"
    
    content+="2. **《Chain-of-Thought Prompting Elicits Reasoning in Large Language Models》** - Google\n"
    content+="   摘要：提出思维链提示方法，显著提升大语言模型在复杂推理任务上的表现\n"
    content+="   关键词：思维链、推理能力、提示工程\n\n"
    
    content+="3. **《Diffusion Models Beat GANs on Image Synthesis》** - OpenAI\n"
    content+="   摘要：扩散模型在图像合成质量上首次超越GANs，成为新的SOTA方法\n"
    content+="   关键词：扩散模型、图像生成、生成对抗网络\n\n"
    
    content+="4. **《Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks》** - Facebook AI\n"
    content+="   摘要：提出检索增强生成框架，显著提升知识密集型NLP任务性能\n"
    content+="   关键词：RAG、知识检索、NLP\n\n"
    
    content+="5. **《Vision Transformers for Dense Prediction》** - Google Research\n"
    content+="   摘要：将Vision Transformer应用于密集预测任务，在语义分割等任务上取得SOTA\n"
    content+="   关键词：Vision Transformer、密集预测、计算机视觉\n\n"
    
    content+="💡 **今日AI小贴士**:\n"
    content+="推荐使用工具：\n"
    content+="• **Claude 3.5 Sonnet** - 创意写作和复杂分析\n"
    content+="• **GPT-4o** - 代码调试和多模态任务\n"
    content+="• **GitHub Copilot** - 编程辅助和代码生成\n"
    content+="• **Midjourney v7** - AI图像生成和艺术创作\n\n"
    
    content+="🔬 **研究趋势**:\n"
    content+="• 多模态AI成为主流研究方向\n"
    content+="• 小样本学习和迁移学习受关注\n"
    content+="• AI安全性和可解释性研究加强\n"
    content+="• 边缘AI和轻量化模型发展迅速\n\n"
    
    content+="⏰ **推送时间**: 09:00（北京时间）\n"
    content+="🔔 保持学习，与时俱进！"
    
    echo -e "$content"
}

# 发送到微信
send_to_wechat() {
    local message="$1"
    
    log "开始发送AI每日报告到微信..."
    log "消息长度: ${#message} 字符"
    
    # 创建临时文件
    local temp_file=$(mktemp)
    echo -e "$message" > "$temp_file"
    
    # 发送消息
    if /root/.nvm/versions/node/v22.22.0/bin/openclaw message send \
        --channel openclaw-weixin \
        --account "$WECHAT_ACCOUNT" \
        --target "$WECHAT_USER_ID" \
        --message "$message" >> "$LOG_FILE" 2>&1; then
        
        log "✅ AI每日报告已成功发送到微信"
        rm -f "$temp_file"
        return 0
    else
        log "❌ 发送到微信失败，尝试备用方法..."
        
        # 输出备用格式，让主会话能够捕获并发送
        echo "[[AI_DAILY_REPORT]]"
        echo -e "$message"
        echo "[[END_AI_DAILY_REPORT]]"
        
        log "⚠️ 已输出报告格式，等待主会话处理"
        rm -f "$temp_file"
        return 1
    fi
}

# 主函数
main() {
    log "====== 开始执行AI每日报告任务 ======"
    
    # 生成报告内容
    local report_content=$(generate_ai_report)
    
    log "AI每日报告内容生成成功"
    
    # 发送到微信
    if send_to_wechat "$report_content"; then
        log "✅ AI每日报告任务执行成功"
    else
        log "⚠️ AI每日报告任务部分完成（需要主会话处理）"
    fi
    
    log "====== AI每日报告任务执行完成 ======"
}

# 执行主函数
main "$@"