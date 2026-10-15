#!/bin/bash
# 系统重启后自动恢复 OpenClaw 服务
#
# 注意：本脚本由「系统级」systemd 服务 openclaw-recovery.service 以 root 身份运行，
# 而 openclaw-gateway 是「用户级」服务。系统服务上下文里默认没有 XDG_RUNTIME_DIR/DBUS，
# 直接跑 `systemctl --user` 会失败 —— 这是之前重启后网关起不来的根因，必须手动导出。

LOG_FILE="/root/.openclaw/workspace/reboot-recovery.log"
export XDG_RUNTIME_DIR="/run/user/0"
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/0/bus"
OPENCLAW_BIN="/root/.nvm/versions/node/v22.22.0/bin/openclaw"
QQ_TARGET="AE09E3EC4BCBB9BA31D09E71F47CB6FE"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }

log "INFO: ====== 系统重启后OpenClaw恢复开始 ======"

# 等待系统基本就绪
sleep 30

# 1. 确保用户 linger 已启用
if ! loginctl show-user root 2>/dev/null | grep -q "Linger=yes"; then
    log "INFO: 启用用户linger..."
    loginctl enable-linger root
fi

# 2. 等待用户级 systemd 管理器就绪（最多 60s）
for i in $(seq 1 30); do
    if systemctl --user show-environment >/dev/null 2>&1; then
        break
    fi
    sleep 2
done
systemctl --user daemon-reload 2>>"$LOG_FILE"

# 3. 重启网关服务（带重试）
ok=0
for i in $(seq 1 5); do
    log "INFO: 第 $i 次尝试启动 OpenClaw 网关服务..."
    if systemctl --user restart openclaw-gateway 2>>"$LOG_FILE"; then
        sleep 8
        if systemctl --user is-active openclaw-gateway >/dev/null 2>&1; then
            ok=1
            log "SUCCESS: OpenClaw 网关服务已启动 (pid $(systemctl --user show -p MainPID --value openclaw-gateway))"
            break
        fi
    fi
    sleep 5
done
if [ "$ok" != "1" ]; then
    log "ERROR: OpenClaw 网关服务启动失败（已重试 5 次）"
fi

# 4. 运行一次监控检查
if [ -x "/root/.openclaw/workspace/openclaw-monitor-enhanced.sh" ]; then
    /root/.openclaw/workspace/openclaw-monitor-enhanced.sh >/dev/null 2>&1
    log "INFO: 监控检查完成"
fi

# 5. 发送 QQ 通知（正确的子命令/参数：message send + --account + --target）
if [ "$ok" = "1" ] && [ -x "$OPENCLAW_BIN" ]; then
    "$OPENCLAW_BIN" message send --channel qqbot --account 102845116 \
        --target "$QQ_TARGET" \
        --message "✅ 系统重启恢复完成
时间: $(date '+%Y-%m-%d %H:%M:%S')
状态: OpenClaw 服务已自动恢复" >>"$LOG_FILE" 2>&1
fi

log "INFO: ====== 系统重启后OpenClaw恢复完成 ======"
