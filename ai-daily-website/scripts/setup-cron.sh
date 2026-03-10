#!/bin/bash

# AI Daily Insights 定时任务设置脚本
# 设置每天自动更新内容的cron任务

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPDATE_SCRIPT="$SCRIPT_DIR/update-content.sh"
CRON_LOG="$SCRIPT_DIR/cron.log"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}设置 AI Daily Insights 自动更新任务...${NC}"
echo "脚本目录: $SCRIPT_DIR"
echo "更新脚本: $UPDATE_SCRIPT"
echo ""

# 检查脚本是否存在
if [ ! -f "$UPDATE_SCRIPT" ]; then
    echo "错误: 更新脚本不存在: $UPDATE_SCRIPT"
    exit 1
fi

# 确保脚本可执行
chmod +x "$UPDATE_SCRIPT"

# 创建cron任务
echo "创建cron任务..."
echo ""

# 显示当前用户的cron任务
echo "当前cron任务:"
crontab -l 2>/dev/null || echo "暂无cron任务"
echo ""

# 添加新的cron任务
CRON_JOB="0 9 * * * $UPDATE_SCRIPT >> $CRON_LOG 2>&1"
CRON_COMMENT="# AI Daily Insights - 每天上午9点自动更新内容"

echo "将添加以下cron任务:"
echo "  $CRON_COMMENT"
echo "  $CRON_JOB"
echo ""

# 询问用户确认
read -p "是否添加此cron任务？(y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 备份当前cron
    crontab -l > "$SCRIPT_DIR/cron_backup_$(date +%Y%m%d_%H%M%S).txt" 2>/dev/null || true
    
    # 添加新任务
    (crontab -l 2>/dev/null | grep -v "AI Daily Insights"; echo "$CRON_COMMENT"; echo "$CRON_JOB") | crontab -
    
    echo -e "${GREEN}✓ cron任务添加成功！${NC}"
    echo ""
    
    # 显示更新后的cron任务
    echo "更新后的cron任务:"
    crontab -l
    echo ""
    
    # 测试运行一次
    echo "测试运行更新脚本..."
    echo "================================"
    "$UPDATE_SCRIPT"
    echo "================================"
    echo ""
    
    echo -e "${GREEN}✓ 设置完成！${NC}"
    echo ""
    echo "📅 定时任务已配置:"
    echo "  • 每天上午9点自动更新"
    echo "  • 日志文件: $CRON_LOG"
    echo "  • 数据目录: $(dirname "$SCRIPT_DIR")/data"
    echo ""
    echo "🔧 手动运行更新:"
    echo "  $UPDATE_SCRIPT"
    echo ""
    echo "📋 查看cron任务:"
    echo "  crontab -l"
    echo ""
    echo "🗑️  删除cron任务:"
    echo "  crontab -e  # 然后删除相关行"
else
    echo "已取消设置cron任务。"
    echo ""
    echo "你可以手动运行更新脚本:"
    echo "  $UPDATE_SCRIPT"
    echo ""
    echo "或者稍后手动设置cron任务:"
    echo "  crontab -e"
    echo "  添加: 0 9 * * * $UPDATE_SCRIPT >> $CRON_LOG 2>&1"
fi

# 创建系统服务配置（可选）
echo ""
echo "可选: 创建systemd服务（用于Linux系统服务管理）"
read -p "是否创建systemd服务？(y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    SERVICE_FILE="/etc/systemd/system/ai-daily-update.service"
    TIMER_FILE="/etc/systemd/system/ai-daily-update.timer"
    
    echo "创建systemd服务文件..."
    
    # 创建服务文件
    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=AI Daily Insights Content Update
After=network.target

[Service]
Type=oneshot
User=$(whoami)
WorkingDirectory=$(dirname "$SCRIPT_DIR")
ExecStart=$UPDATE_SCRIPT
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # 创建定时器文件
    sudo tee "$TIMER_FILE" > /dev/null << EOF
[Unit]
Description=Daily update for AI Daily Insights
Requires=ai-daily-update.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF
    
    echo "启用并启动定时器..."
    sudo systemctl daemon-reload
    sudo systemctl enable ai-daily-update.timer
    sudo systemctl start ai-daily-update.timer
    
    echo -e "${GREEN}✓ systemd服务配置完成！${NC}"
    echo ""
    echo "📅 systemd定时器状态:"
    sudo systemctl status ai-daily-update.timer
    echo ""
    echo "📋 查看下次运行时间:"
    sudo systemctl list-timers ai-daily-update.timer
fi

echo ""
echo "🎉 自动更新系统配置完成！"
echo "网站现在可以每天自动更新AI资讯和论文内容。"