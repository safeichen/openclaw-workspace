#!/bin/bash
# 设置OpenClaw自动备份cron任务

echo "🕙 配置OpenClaw自动备份定时任务"
echo "================================"

BACKUP_SCRIPT="/root/.openclaw/workspace/auto-backup.sh"
CRON_TIME="0 22 * * *"  # 每天晚上10点
CRON_USER="root"
CRON_JOB="$CRON_TIME $BACKUP_SCRIPT >> /root/.openclaw/workspace/cron.log 2>&1"

# 检查备份脚本
check_backup_script() {
    echo "🔧 检查备份脚本..."
    
    if [ ! -f "$BACKUP_SCRIPT" ]; then
        echo "❌ 备份脚本不存在: $BACKUP_SCRIPT"
        return 1
    fi
    
    if [ ! -x "$BACKUP_SCRIPT" ]; then
        echo "⚠️  备份脚本没有执行权限，正在修复..."
        chmod +x "$BACKUP_SCRIPT"
    fi
    
    echo "✅ 备份脚本检查通过"
    return 0
}

# 测试备份脚本
test_backup_script() {
    echo "🧪 测试备份脚本..."
    
    if "$BACKUP_SCRIPT" --test; then
        echo "✅ 备份脚本测试通过"
        return 0
    else
        echo "❌ 备份脚本测试失败"
        return 1
    fi
}

# 设置cron任务
setup_cron() {
    echo "📅 设置cron定时任务..."
    
    # 检查是否已有相同任务
    existing_job=$(crontab -l 2>/dev/null | grep -F "$BACKUP_SCRIPT")
    
    if [ -n "$existing_job" ]; then
        echo "⚠️  已存在备份任务:"
        echo "   $existing_job"
        
        read -p "是否替换现有任务? (y/N): " replace
        if [ "$replace" != "y" ]; then
            echo "❌ 取消设置"
            return 1
        fi
        
        # 移除现有任务
        crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT" | crontab -
        echo "✅ 已移除现有任务"
    fi
    
    # 添加新任务
    (crontab -l 2>/dev/null; echo "# OpenClaw自动备份 - 每天晚上10点"; echo "$CRON_JOB") | crontab -
    
    if [ $? -eq 0 ]; then
        echo "✅ cron任务设置成功"
        echo ""
        echo "📋 任务详情:"
        echo "   时间: $CRON_TIME (每天晚上10点)"
        echo "   脚本: $BACKUP_SCRIPT"
        echo "   用户: $CRON_USER"
        echo "   日志: /root/.openclaw/workspace/cron.log"
        return 0
    else
        echo "❌ cron任务设置失败"
        return 1
    fi
}

# 验证cron任务
verify_cron() {
    echo "🔍 验证cron任务..."
    
    crontab -l 2>/dev/null | grep -A2 -B2 "OpenClaw自动备份"
    
    if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
        echo "✅ cron任务验证成功"
        return 0
    else
        echo "❌ cron任务验证失败"
        return 1
    fi
}

# 创建日志轮转配置
setup_log_rotation() {
    echo "📝 设置日志轮转..."
    
    logrotate_conf="/etc/logrotate.d/openclaw-backup"
    
    cat > "$logrotate_conf" << 'EOF'
/root/.openclaw/workspace/backup.log
/root/.openclaw/workspace/cron.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF
    
    if [ $? -eq 0 ]; then
        echo "✅ 日志轮转配置已创建: $logrotate_conf"
        echo "   保留最近7天的日志，每天轮转"
        return 0
    else
        echo "⚠️  日志轮转配置创建失败（可能需要sudo权限）"
        return 1
    fi
}

# 显示管理命令
show_management_commands() {
    echo ""
    echo "🛠️  管理命令:"
    echo "   查看cron任务: crontab -l"
    echo "   编辑cron任务: crontab -e"
    echo "   手动运行备份: $BACKUP_SCRIPT"
    echo "   测试备份脚本: $BACKUP_SCRIPT --test"
    echo "   查看备份日志: tail -f /root/.openclaw/workspace/backup.log"
    echo "   查看cron日志: tail -f /root/.openclaw/workspace/cron.log"
    echo ""
    echo "📅 下次执行时间:"
    echo "   今天晚上10点 (22:00)"
    echo ""
    echo "🔔 注意事项:"
    echo "   1. 确保SSH密钥已添加到GitHub"
    echo "   2. 确保有网络连接"
    echo "   3. 定期检查备份日志"
    echo "   4. 重要更改建议手动提交"
}

# 主函数
main() {
    echo "开始配置OpenClaw自动备份系统..."
    echo ""
    
    # 检查备份脚本
    if ! check_backup_script; then
        exit 1
    fi
    
    # 测试备份脚本
    if ! test_backup_script; then
        echo "⚠️  备份脚本测试失败，是否继续设置cron? (y/N): "
        read continue_setup
        if [ "$continue_setup" != "y" ]; then
            exit 1
        fi
    fi
    
    # 设置cron任务
    if ! setup_cron; then
        exit 1
    fi
    
    # 验证cron任务
    verify_cron
    
    # 设置日志轮转
    setup_log_rotation
    
    # 显示管理命令
    show_management_commands
    
    echo ""
    echo "🎉 OpenClaw自动备份配置完成！"
    echo "   每天晚上10点自动提交并推送到GitHub"
}

# 处理命令行参数
case "$1" in
    "--remove")
        echo "🗑️  移除自动备份任务..."
        crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT" | crontab -
        echo "✅ 已移除自动备份任务"
        ;;
    "--status")
        echo "📊 自动备份状态:"
        crontab -l 2>/dev/null | grep -A2 -B2 "OpenClaw"
        echo ""
        echo "📁 备份文件:"
        ls -la /root/.openclaw/workspace/*.log 2>/dev/null
        ;;
    "--test-run")
        echo "🚀 测试运行备份脚本..."
        "$BACKUP_SCRIPT"
        ;;
    "--help"|"-h")
        echo "OpenClaw自动备份配置脚本"
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  --remove     移除自动备份任务"
        echo "  --status     查看备份状态"
        echo "  --test-run   测试运行备份"
        echo "  --help, -h   显示帮助"
        echo ""
        echo "无参数: 配置自动备份系统"
        ;;
    *)
        main
        ;;
esac