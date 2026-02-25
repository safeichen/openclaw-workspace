#!/bin/bash
# OpenClaw工作区自动备份脚本
# 每天晚上10点自动提交并推送到GitHub

echo "🦞 OpenClaw自动备份脚本"
echo "======================"
echo "执行时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

WORKSPACE_DIR="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE_DIR/backup.log"
MAX_LOG_SIZE=10485760  # 10MB

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO") color=$BLUE ;;
        "SUCCESS") color=$GREEN ;;
        "WARNING") color=$YELLOW ;;
        "ERROR") color=$RED ;;
        *) color=$NC ;;
    esac
    
    echo -e "${color}[$level]${NC} $message"
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# 检查日志文件大小，如果太大则轮转
rotate_log() {
    if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE") -gt $MAX_LOG_SIZE ]; then
        mv "$LOG_FILE" "$LOG_FILE.old"
        log_message "INFO" "日志文件已轮转"
    fi
}

# 检查Git配置
check_git_config() {
    log_message "INFO" "检查Git配置..."
    
    cd "$WORKSPACE_DIR"
    
    # 检查是否在Git仓库中
    if [ ! -d .git ]; then
        log_message "ERROR" "当前目录不是Git仓库"
        return 1
    fi
    
    # 检查远程仓库配置
    if ! git remote get-url origin >/dev/null 2>&1; then
        log_message "ERROR" "未配置远程仓库"
        return 1
    fi
    
    # 检查SSH连接
    log_message "INFO" "测试GitHub SSH连接..."
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        log_message "SUCCESS" "GitHub SSH连接正常"
    else
        log_message "WARNING" "GitHub SSH连接可能有问题"
    fi
    
    return 0
}

# 自动提交更改
auto_commit() {
    log_message "INFO" "开始自动提交..."
    
    cd "$WORKSPACE_DIR"
    
    # 检查是否有更改
    if git status --porcelain | grep -q .; then
        # 统计更改
        changed_files=$(git status --porcelain | wc -l)
        log_message "INFO" "检测到 $changed_files 个文件有更改"
        
        # 显示更改摘要
        echo "更改摘要:"
        git status --short | head -10
        
        # 生成提交信息
        commit_date=$(date '+%Y-%m-%d')
        commit_time=$(date '+%H:%M:%S')
        commit_msg="自动备份: $commit_date $commit_time"
        
        # 尝试提取有意义的更改描述
        changed_list=$(git status --short | awk '{print $2}' | head -5 | tr '\n' ', ' | sed 's/, $//')
        if [ -n "$changed_list" ]; then
            commit_msg="自动备份: 更新 $changed_list - $commit_date $commit_time"
        fi
        
        # 添加所有更改
        log_message "INFO" "添加文件到暂存区..."
        git add .
        
        # 提交
        log_message "INFO" "提交更改: $commit_msg"
        if git commit -m "$commit_msg"; then
            log_message "SUCCESS" "提交成功: $commit_msg"
            return 0
        else
            log_message "ERROR" "提交失败"
            return 1
        fi
    else
        log_message "INFO" "没有检测到更改，跳过提交"
        return 2
    fi
}

# 推送到远程
push_to_remote() {
    log_message "INFO" "推送到GitHub..."
    
    cd "$WORKSPACE_DIR"
    current_branch=$(git branch --show-current)
    
    log_message "INFO" "推送分支: $current_branch"
    if git push origin "$current_branch"; then
        log_message "SUCCESS" "推送成功"
        return 0
    else
        log_message "ERROR" "推送失败"
        
        # 尝试先拉取再推送（处理冲突）
        log_message "INFO" "尝试先拉取更新..."
        if git pull --rebase origin "$current_branch"; then
            log_message "INFO" "拉取成功，重新推送..."
            if git push origin "$current_branch"; then
                log_message "SUCCESS" "推送成功（经过拉取）"
                return 0
            fi
        fi
        
        return 1
    fi
}

# 备份关键配置文件
backup_config_files() {
    log_message "INFO" "备份关键配置文件..."
    
    backup_dir="$WORKSPACE_DIR/backups"
    mkdir -p "$backup_dir"
    
    timestamp=$(date '+%Y%m%d_%H%M%S')
    backup_file="$backup_dir/config_backup_$timestamp.tar.gz"
    
    # 备份重要配置文件
    tar -czf "$backup_file" \
        "/root/.openclaw/openclaw.json" \
        "$WORKSPACE_DIR/AGENTS.md" \
        "$WORKSPACE_DIR/SOUL.md" \
        "$WORKSPACE_DIR/USER.md" \
        "$WORKSPACE_DIR/IDENTITY.md" \
        "$WORKSPACE_DIR/MEMORY.md" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        backup_size=$(du -h "$backup_file" | cut -f1)
        log_message "SUCCESS" "配置已备份到: $backup_file ($backup_size)"
        
        # 添加到Git（可选）
        read -p "是否将备份文件添加到Git? (y/N): " add_to_git
        if [ "$add_to_git" = "y" ]; then
            git add "$backup_file"
            git commit -m "添加配置文件备份 $timestamp"
        fi
    else
        log_message "WARNING" "配置文件备份失败"
    fi
}

# 生成备份报告
generate_report() {
    log_message "INFO" "生成备份报告..."
    
    report_file="$WORKSPACE_DIR/backup_report_$(date '+%Y%m%d').txt"
    
    {
        echo "=== OpenClaw自动备份报告 ==="
        echo "生成时间: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        
        echo "1. Git状态:"
        cd "$WORKSPACE_DIR"
        echo "   分支: $(git branch --show-current)"
        echo "   远程: $(git remote get-url origin)"
        echo "   最后提交: $(git log --oneline -1)"
        echo ""
        
        echo "2. 文件更改统计:"
        changed_count=$(git status --porcelain | wc -l)
        echo "   未提交更改: $changed_count 个文件"
        if [ $changed_count -gt 0 ]; then
            echo "   更改列表:"
            git status --short | head -5 | sed 's/^/     /'
        fi
        echo ""
        
        echo "3. 仓库大小:"
        echo "   文件总数: $(find . -type f -not -path "./.git/*" | wc -l)"
        echo "   目录大小: $(du -sh . | cut -f1)"
        echo ""
        
        echo "4. 备份日志:"
        tail -5 "$LOG_FILE" 2>/dev/null | sed 's/^/   /'
        
    } > "$report_file"
    
    log_message "SUCCESS" "备份报告已生成: $report_file"
}

# 主函数
main() {
    log_message "INFO" "开始OpenClaw工作区自动备份"
    
    # 轮转日志
    rotate_log
    
    # 检查Git配置
    if ! check_git_config; then
        log_message "ERROR" "Git配置检查失败，备份中止"
        exit 1
    fi
    
    # 自动提交
    commit_result=0
    auto_commit || commit_result=$?
    
    # 只有提交成功或没有更改时才推送
    if [ $commit_result -eq 0 ] || [ $commit_result -eq 2 ]; then
        # 推送到远程
        if push_to_remote; then
            log_message "SUCCESS" "自动备份完成"
        else
            log_message "ERROR" "备份完成但推送失败"
        fi
    else
        log_message "WARNING" "提交失败，跳过推送"
    fi
    
    # 可选：备份配置文件
    read -p "是否备份关键配置文件? (y/N): " backup_config
    if [ "$backup_config" = "y" ]; then
        backup_config_files
    fi
    
    # 生成报告
    generate_report
    
    log_message "INFO" "自动备份流程结束"
    echo ""
    echo "📊 备份摘要:"
    echo "   - 日志文件: $LOG_FILE"
    echo "   - 报告文件: backup_report_$(date '+%Y%m%d').txt"
    echo "   - 查看状态: git status"
    echo ""
}

# 处理命令行参数
case "$1" in
    "--test")
        echo "🧪 测试模式"
        echo "测试Git配置..."
        check_git_config
        echo "测试自动提交..."
        auto_commit
        ;;
    "--setup-cron")
        echo "🕙 设置cron定时任务..."
        setup_cron_job
        ;;
    "--help"|"-h")
        echo "OpenClaw自动备份脚本"
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  --test        测试模式（不实际提交推送）"
        echo "  --setup-cron  设置cron定时任务"
        echo "  --help, -h    显示帮助"
        echo ""
        echo "无参数: 执行完整备份流程"
        ;;
    *)
        # 执行主函数
        main
        ;;
esac