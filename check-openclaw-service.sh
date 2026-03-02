#!/bin/bash
# OpenClaw服务监控脚本
# 检查OpenClaw服务状态，如果停止则自动重启

LOG_FILE="/root/.openclaw/workspace/openclaw-monitor.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 检查OpenClaw命令是否可用
check_command() {
    if ! command -v openclaw >/dev/null 2>&1; then
        echo "[$TIMESTAMP] ERROR: openclaw命令不可用" >> "$LOG_FILE"
        return 1
    fi
    return 0
}

# 检查OpenClaw网关服务状态
check_service() {
    if ! systemctl --user is-active openclaw-gateway >/dev/null 2>&1; then
        echo "[$TIMESTAMP] WARNING: OpenClaw网关服务已停止" >> "$LOG_FILE"
        
        # 尝试重启服务
        echo "[$TIMESTAMP] INFO: 正在重启OpenClaw网关服务..." >> "$LOG_FILE"
        if systemctl --user restart openclaw-gateway; then
            echo "[$TIMESTAMP] SUCCESS: 服务重启成功" >> "$LOG_FILE"
            
            # 等待服务完全启动
            sleep 5
            
            # 验证服务状态
            if systemctl --user is-active openclaw-gateway >/dev/null 2>&1; then
                echo "[$TIMESTAMP] SUCCESS: 服务验证通过，运行正常" >> "$LOG_FILE"
            else
                echo "[$TIMESTAMP] ERROR: 服务重启后仍未运行" >> "$LOG_FILE"
            fi
        else
            echo "[$TIMESTAMP] ERROR: 服务重启失败" >> "$LOG_FILE"
        fi
        return 1
    fi
    return 0
}

# 检查OpenClaw状态命令
check_status() {
    if openclaw status --brief >/dev/null 2>&1; then
        echo "[$TIMESTAMP] INFO: OpenClaw状态检查通过" >> "$LOG_FILE"
        return 0
    else
        echo "[$TIMESTAMP] WARNING: OpenClaw状态检查失败" >> "$LOG_FILE"
        return 1
    fi
}

# 主监控逻辑
main() {
    echo "[$TIMESTAMP] INFO: 开始OpenClaw服务监控检查" >> "$LOG_FILE"
    
    # 检查1: 命令可用性
    if ! check_command; then
        echo "[$TIMESTAMP] ERROR: 跳过后续检查，openclaw命令不可用" >> "$LOG_FILE"
        return 1
    fi
    
    # 检查2: 服务状态
    if check_service; then
        echo "[$TIMESTAMP] INFO: 服务运行正常" >> "$LOG_FILE"
    else
        echo "[$TIMESTAMP] WARNING: 服务状态异常，已尝试恢复" >> "$LOG_FILE"
    fi
    
    # 检查3: 状态命令
    check_status
    
    echo "[$TIMESTAMP] INFO: 监控检查完成" >> "$LOG_FILE"
    echo "----------------------------------------" >> "$LOG_FILE"
}

# 执行主函数
main "$@"