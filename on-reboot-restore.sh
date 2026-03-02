#!/bin/bash
# 系统重启后自动恢复OpenClaw服务

LOG_FILE="/root/.openclaw/workspace/reboot-recovery.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] INFO: ====== 系统重启后OpenClaw恢复开始 ======" >> "$LOG_FILE"

# 等待系统完全启动
sleep 45

# 1. 确保用户linger已启用
echo "[$TIMESTAMP] INFO: 检查用户linger状态..." >> "$LOG_FILE"
if ! loginctl show-user root | grep -q "Linger=yes"; then
    echo "[$TIMESTAMP] INFO: 启用用户linger..." >> "$LOG_FILE"
    loginctl enable-linger root
fi

# 2. 重新加载systemd用户配置
echo "[$TIMESTAMP] INFO: 重新加载systemd用户配置..." >> "$LOG_FILE"
systemctl --user daemon-reload

# 3. 启动OpenClaw网关服务
echo "[$TIMESTAMP] INFO: 启动OpenClaw网关服务..." >> "$LOG_FILE"
if systemctl --user start openclaw-gateway; then
    echo "[$TIMESTAMP] SUCCESS: OpenClaw网关服务启动成功" >> "$LOG_FILE"
    
    # 等待服务完全启动
    sleep 10
    
    # 验证服务状态
    if systemctl --user is-active openclaw-gateway >/dev/null 2>&1; then
        echo "[$TIMESTAMP] SUCCESS: 服务验证通过" >> "$LOG_FILE"
    else
        echo "[$TIMESTAMP] ERROR: 服务启动后未运行" >> "$LOG_FILE"
    fi
else
    echo "[$TIMESTAMP] ERROR: OpenClaw网关服务启动失败" >> "$LOG_FILE"
fi

# 4. 运行一次监控检查
echo "[$TIMESTAMP] INFO: 运行监控检查..." >> "$LOG_FILE"
if [ -x "/root/.openclaw/workspace/openclaw-monitor-enhanced.sh" ]; then
    /root/.openclaw/workspace/openclaw-monitor-enhanced.sh
    echo "[$TIMESTAMP] INFO: 监控检查完成" >> "$LOG_FILE"
fi

echo "[$TIMESTAMP] INFO: ====== 系统重启后OpenClaw恢复完成 ======" >> "$LOG_FILE"

# 发送QQ通知（如果服务可用）
if command -v openclaw >/dev/null 2>&1; then
    if systemctl --user is-active openclaw-gateway >/dev/null 2>&1; then
        openclaw message --channel qqbot --to "AE09E3EC4BCBB9BA31D09E71F47CB6FE" \
            --message "✅ **系统重启恢复完成**\n\n**时间**: $TIMESTAMP\n**状态**: OpenClaw服务已自动恢复\n**详情**: 系统重启后服务恢复成功，一切正常！\n\n🔄 监控系统已启用，将每5分钟检查一次服务状态。"
    fi
fi