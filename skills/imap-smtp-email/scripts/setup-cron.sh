#!/bin/bash

# 邮件监控cron任务设置脚本
# 设置每5分钟检查一次新邮件

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NOTIFIER_SCRIPT="$SCRIPT_DIR/email-notifier.js"
CRON_JOB="*/5 * * * * cd $SCRIPT_DIR && node email-notifier.js >> $SCRIPT_DIR/logs/cron.log 2>&1"

echo "📧 设置邮件监控cron任务"
echo "脚本目录: $SCRIPT_DIR"
echo "通知脚本: $NOTIFIER_SCRIPT"
echo "Cron表达式: */5 * * * * (每5分钟)"
echo ""

# 创建日志目录
mkdir -p "$SCRIPT_DIR/logs"
echo "✅ 创建日志目录: $SCRIPT_DIR/logs"

# 检查Node.js脚本是否存在
if [ ! -f "$NOTIFIER_SCRIPT" ]; then
    echo "❌ 错误: 通知脚本不存在: $NOTIFIER_SCRIPT"
    exit 1
fi

echo "✅ 找到通知脚本"

# 给脚本添加执行权限
chmod +x "$NOTIFIER_SCRIPT"
chmod +x "$SCRIPT_DIR/email-monitor.js"
echo "✅ 设置脚本执行权限"

# 显示cron任务内容
echo ""
echo "📋 Cron任务内容:"
echo "$CRON_JOB"
echo ""

# 提示用户如何手动添加cron任务
echo "🔧 手动添加cron任务的方法:"
echo "1. 运行: crontab -e"
echo "2. 添加以下行:"
echo "   $CRON_JOB"
echo "3. 保存并退出"
echo ""

# 尝试使用OpenClaw的cron功能（如果可用）
echo "🔄 尝试使用OpenClaw cron功能..."
if command -v openclaw &> /dev/null; then
    echo "✅ 找到OpenClaw命令"
    
    # 检查是否已存在同名cron任务
    if openclaw cron list | grep -q "email-monitor"; then
        echo "⚠️  已存在email-monitor任务，先删除..."
        openclaw cron delete --name email-monitor
    fi
    
    # 创建新的cron任务
    echo "📝 创建OpenClaw cron任务..."
    openclaw cron add \
        --name "email-monitor" \
        --schedule "*/5 * * * *" \
        --command "cd $SCRIPT_DIR && node email-notifier.js" \
        --description "每5分钟检查新邮件并推送通知"
    
    if [ $? -eq 0 ]; then
        echo "✅ OpenClaw cron任务创建成功！"
        echo ""
        echo "📊 查看cron任务列表: openclaw cron list"
        echo "🔍 查看任务日志: openclaw cron logs --name email-monitor"
        echo "🗑️  删除任务: openclaw cron delete --name email-monitor"
    else
        echo "❌ OpenClaw cron任务创建失败"
        echo "请手动添加cron任务"
    fi
else
    echo "⚠️  未找到OpenClaw命令，请手动添加cron任务"
fi

echo ""
echo "🎉 设置完成！"
echo ""
echo "📝 下一步:"
echo "1. 系统将每5分钟自动检查新邮件"
echo "2. 发现新邮件时会通过QQ Bot推送通知"
echo "3. 查看日志: tail -f $SCRIPT_DIR/logs/cron.log"
echo "4. 查看通知记录: cat $SCRIPT_DIR/logs/notifications-text.log"
echo ""
echo "🔧 手动测试:"
echo "   cd $SCRIPT_DIR && node email-notifier.js"
echo ""