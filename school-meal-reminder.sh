#!/bin/bash
# 学校选餐提醒脚本
# 今天晚上8点（北京时间）执行

# 设置PATH，确保cron环境中能找到命令
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/root/.nvm/versions/node/v22.22.0/bin

# 工作区路径
WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/school-meal-reminder.log"

# 微信用户ID（根据您的微信ID设置）
WECHAT_USER_ID="o9cq80-W-pYsx8MmI6T8Tpf9zlp0@im.wechat"
# WeChat账户ID
WECHAT_ACCOUNT="aa458d4db39b-im-bot"

# 日志函数
log() {
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

# 发送到微信
send_reminder() {
    local message="⏰ **学校选餐提醒**\n\n📅 时间：2026年3月25日 20:00（晚上8点）\n📋 事项：学校选餐\n💡 提醒：记得去学校系统选择明天的餐食哦！\n\n🍽️ 今日推荐：\n• 营养均衡套餐\n• 特色风味餐\n• 健康轻食选项\n\n✅ 完成选餐后可以标记为已完成！"
    
    log "开始发送学校选餐提醒到微信..."
    log "消息内容: 学校选餐提醒 - 2026年3月25日 20:00"
    
    # 创建临时文件
    local temp_file=$(mktemp)
    echo -e "$message" > "$temp_file"
    
    # 发送消息
    if /root/.nvm/versions/node/v22.22.0/bin/openclaw message send \
        --channel openclaw-weixin \
        --account "$WECHAT_ACCOUNT" \
        --target "$WECHAT_USER_ID" \
        --message "$message" >> "$LOG_FILE" 2>&1; then
        
        log "✅ 学校选餐提醒已成功发送到微信"
        rm -f "$temp_file"
        return 0
    else
        log "❌ 发送到微信失败，尝试备用方法..."
        
        # 输出备用格式，让主会话能够捕获并发送
        echo "[[SCHOOL_MEAL_REMINDER]]"
        echo -e "$message"
        echo "[[END_SCHOOL_MEAL_REMINDER]]"
        
        log "⚠️ 已输出提醒格式，等待主会话处理"
        rm -f "$temp_file"
        return 1
    fi
}

# 主函数
main() {
    log "====== 开始执行学校选餐提醒任务 ======"
    log "提醒时间: 2026-03-25 20:00 (北京时间)"
    log "提醒内容: 学校选餐"
    
    # 发送提醒
    if send_reminder; then
        log "✅ 学校选餐提醒任务执行成功"
    else
        log "⚠️ 学校选餐提醒任务部分完成（需要主会话处理）"
    fi
    
    log "====== 学校选餐提醒任务执行完成 ======"
}

# 执行主函数
main "$@"