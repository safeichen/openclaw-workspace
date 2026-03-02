#!/bin/bash
# OpenClaw增强监控脚本
# 包含服务监控、自动恢复和QQ通知功能

# 设置完整的PATH环境变量，确保cron环境下命令可用
export PATH="/root/.nvm/versions/node/v22.22.0/bin:/root/.local/share/pnpm:/usr/local/bin:/usr/bin:/bin:/root/.local/bin:/root/bin"
export NVM_DIR="/root/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # 加载nvm
export PNPM_HOME="/root/.local/share/pnpm"

LOG_FILE="/root/.openclaw/workspace/openclaw-monitor.log"
QQ_USER_ID="AE09E3EC4BCBB9BA31D09E71F47CB6FE"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 发送QQ通知函数
send_qq_notification() {
    local message="$1"
    local level="$2"  # INFO, WARNING, ERROR
    
    # 构建markdown消息
    local markdown_content=""
    case "$level" in
        "ERROR")
            markdown_content="❌ **OpenClaw监控告警**\n\n**时间**: $TIMESTAMP\n**级别**: 🔴 严重错误\n**详情**: $message\n\n⚠️ 需要立即处理！"
            ;;
        "WARNING")
            markdown_content="⚠️ **OpenClaw监控警告**\n\n**时间**: $TIMESTAMP\n**级别**: 🟡 警告\n**详情**: $message\n\n🔧 已尝试自动恢复"
            ;;
        "INFO")
            markdown_content="✅ **OpenClaw监控通知**\n\n**时间**: $TIMESTAMP\n**级别**: 🟢 信息\n**详情**: $message"
            ;;
        *)
            markdown_content="📢 **OpenClaw监控**\n\n**时间**: $TIMESTAMP\n**详情**: $message"
            ;;
    esac
    
    # 记录日志
    echo "[$TIMESTAMP] [$level] QQ通知: $message" >> "$LOG_FILE"
    
    # 发送QQ消息（如果openclaw命令可用）
    if command -v openclaw >/dev/null 2>&1; then
        if openclaw message --channel qqbot --to "$QQ_USER_ID" --message "$markdown_content" >/dev/null 2>&1; then
            echo "[$TIMESTAMP] [$level] QQ通知发送成功" >> "$LOG_FILE"
        else
            echo "[$TIMESTAMP] [$level] QQ通知发送失败" >> "$LOG_FILE"
        fi
    fi
}

# 检查OpenClaw命令是否可用
check_command() {
    if ! command -v openclaw >/dev/null 2>&1; then
        local msg="openclaw命令不可用，可能系统正在重启或安装有问题"
        echo "[$TIMESTAMP] ERROR: $msg" >> "$LOG_FILE"
        send_qq_notification "$msg" "ERROR"
        return 1
    fi
    return 0
}

# 检查OpenClaw网关服务状态
check_service() {
    if ! systemctl --user is-active openclaw-gateway >/dev/null 2>&1; then
        local msg="OpenClaw网关服务已停止"
        echo "[$TIMESTAMP] WARNING: $msg" >> "$LOG_FILE"
        send_qq_notification "$msg" "WARNING"
        
        # 尝试重启服务
        echo "[$TIMESTAMP] INFO: 正在重启OpenClaw网关服务..." >> "$LOG_FILE"
        if systemctl --user restart openclaw-gateway; then
            local success_msg="服务重启成功"
            echo "[$TIMESTAMP] SUCCESS: $success_msg" >> "$LOG_FILE"
            send_qq_notification "$success_msg" "INFO"
            
            # 等待服务完全启动
            sleep 10
            
            # 验证服务状态
            if systemctl --user is-active openclaw-gateway >/dev/null 2>&1; then
                local verify_msg="服务验证通过，运行正常"
                echo "[$TIMESTAMP] SUCCESS: $verify_msg" >> "$LOG_FILE"
                send_qq_notification "$verify_msg" "INFO"
            else
                local verify_fail_msg="服务重启后仍未运行"
                echo "[$TIMESTAMP] ERROR: $verify_fail_msg" >> "$LOG_FILE"
                send_qq_notification "$verify_fail_msg" "ERROR"
            fi
        else
            local restart_fail_msg="服务重启失败"
            echo "[$TIMESTAMP] ERROR: $restart_fail_msg" >> "$LOG_FILE"
            send_qq_notification "$restart_fail_msg" "ERROR"
        fi
        return 1
    fi
    return 0
}

# 检查OpenClaw状态
check_status() {
    if openclaw status --brief >/dev/null 2>&1; then
        echo "[$TIMESTAMP] INFO: OpenClaw状态检查通过" >> "$LOG_FILE"
        return 0
    else
        local msg="OpenClaw状态检查失败"
        echo "[$TIMESTAMP] WARNING: $msg" >> "$LOG_FILE"
        send_qq_notification "$msg" "WARNING"
        return 1
    fi
}

# 检查系统资源
check_resources() {
    local memory_threshold=90  # 内存使用率阈值%
    local disk_threshold=80    # 磁盘使用率阈值%
    
    # 检查内存
    local mem_usage=$(free | awk '/Mem:/ {printf "%.0f", $3/$2*100}')
    if [ "$mem_usage" -gt "$memory_threshold" ]; then
        local msg="内存使用率过高: ${mem_usage}% (阈值: ${memory_threshold}%)"
        echo "[$TIMESTAMP] WARNING: $msg" >> "$LOG_FILE"
        send_qq_notification "$msg" "WARNING"
    fi
    
    # 检查磁盘
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt "$disk_threshold" ]; then
        local msg="根分区磁盘使用率过高: ${disk_usage}% (阈值: ${disk_threshold}%)"
        echo "[$TIMESTAMP] WARNING: $msg" >> "$LOG_FILE"
        send_qq_notification "$msg" "WARNING"
    fi
}

# 主监控逻辑
main() {
    echo "[$TIMESTAMP] INFO: ====== OpenClaw增强监控开始 ======" >> "$LOG_FILE"
    
    # 检查1: 命令可用性
    if ! check_command; then
        echo "[$TIMESTAMP] ERROR: 跳过后续检查" >> "$LOG_FILE"
        return 1
    fi
    
    # 检查2: 服务状态
    if check_service; then
        echo "[$TIMESTAMP] INFO: 服务运行正常" >> "$LOG_FILE"
    fi
    
    # 检查3: 状态命令
    check_status
    
    # 检查4: 系统资源（每小时检查一次）
    local current_minute=$(date +%M)
    if [ "$current_minute" = "00" ] || [ "$current_minute" = "30" ]; then
        check_resources
    fi
    
    echo "[$TIMESTAMP] INFO: ====== OpenClaw增强监控完成 ======" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
}

# 执行主函数
main "$@"