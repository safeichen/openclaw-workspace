#!/bin/bash
# OpenClaw Git自动化脚本
# 自动管理OpenClaw工作区的Git操作

echo "🦞 OpenClaw Git自动化"
echo "===================="

WORKSPACE_DIR="/root/.openclaw/workspace"
CONFIG_DIR="/root/.openclaw"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Git配置
check_git_config() {
    log_info "检查Git配置..."
    
    # 检查用户配置
    user_name=$(git config --global user.name)
    user_email=$(git config --global user.email)
    
    if [ -z "$user_name" ] || [ -z "$user_email" ]; then
        log_warning "Git用户信息未配置"
        read -p "配置Git用户信息? (y/n): " configure
        
        if [ "$configure" = "y" ]; then
            read -p "用户名: " git_user
            read -p "邮箱: " git_email
            
            git config --global user.name "$git_user"
            git config --global user.email "$git_email"
            log_success "Git用户信息已配置"
        fi
    else
        log_info "Git用户: $user_name <$user_email>"
    fi
}

# 初始化OpenClaw工作区Git仓库
init_workspace_repo() {
    log_info "初始化OpenClaw工作区Git仓库..."
    
    cd "$WORKSPACE_DIR"
    
    if [ -d .git ]; then
        log_info "工作区已经是Git仓库"
        return 0
    fi
    
    log_info "初始化Git仓库..."
    git init
    
    # 创建.gitignore
    cat > .gitignore << 'EOF'
# OpenClaw工作区.gitignore

# 临时文件
*.tmp
*.temp
*.log
*.pid
*.swp
*~

# 缓存文件
.cache/
.cache/*
node_modules/
__pycache__/
*.pyc

# 配置文件（包含敏感信息）
.env
*.env
config.local.*
secrets.*
credentials.*

# 系统文件
.DS_Store
Thumbs.db
desktop.ini

# 备份文件
*.bak
*.backup

# 大文件
*.zip
*.tar
*.gz
*.7z

# 媒体文件（可根据需要调整）
*.mp3
*.mp4
*.avi
*.mov

# 特定目录
tmp/
temp/
logs/
EOF
    
    log_success "Git仓库已初始化"
    log_info ".gitignore文件已创建"
}

# 自动提交工作区更改
auto_commit_workspace() {
    log_info "自动提交工作区更改..."
    
    cd "$WORKSPACE_DIR"
    
    if [ ! -d .git ]; then
        log_error "工作区不是Git仓库"
        init_workspace_repo
    fi
    
    # 检查是否有更改
    if git status --porcelain | grep -q .; then
        log_info "检测到未提交的更改"
        
        # 显示更改摘要
        echo "更改摘要:"
        git status --short
        
        # 自动生成提交信息
        commit_msg="工作区更新 $(date '+%Y-%m-%d %H:%M:%S')"
        
        # 尝试从更改中提取有意义的提交信息
        changed_files=$(git status --porcelain | wc -l)
        if [ "$changed_files" -eq 1 ]; then
            file_change=$(git status --porcelain | awk '{print $2}')
            commit_msg="更新 $file_change"
        fi
        
        read -p "提交说明 (默认: '$commit_msg'): " custom_msg
        if [ -n "$custom_msg" ]; then
            commit_msg="$custom_msg"
        fi
        
        # 添加并提交
        git add .
        git commit -m "$commit_msg"
        
        log_success "已提交更改: $commit_msg"
        
        # 询问是否推送
        read -p "推送到远程仓库? (y/n): " push_confirm
        if [ "$push_confirm" = "y" ]; then
            git_push_workspace
        fi
    else
        log_info "没有检测到更改"
    fi
}

# 推送到远程仓库
git_push_workspace() {
    log_info "推送到远程仓库..."
    
    cd "$WORKSPACE_DIR"
    
    # 检查远程仓库
    remote_url=$(git remote get-url origin 2>/dev/null || echo "")
    
    if [ -z "$remote_url" ]; then
        log_warning "未配置远程仓库"
        read -p "添加远程仓库? (y/n): " add_remote
        
        if [ "$add_remote" = "y" ]; then
            read -p "远程仓库URL: " remote_url_input
            if [ -n "$remote_url_input" ]; then
                git remote add origin "$remote_url_input"
                remote_url="$remote_url_input"
                log_success "远程仓库已添加"
            else
                log_error "需要远程仓库URL"
                return 1
            fi
        else
            return 0
        fi
    fi
    
    log_info "远程仓库: $remote_url"
    
    # 获取当前分支
    current_branch=$(git branch --show-current)
    
    # 推送
    log_info "推送分支: $current_branch"
    if git push -u origin "$current_branch"; then
        log_success "推送成功"
    else
        log_error "推送失败"
        return 1
    fi
}

# 从远程拉取更新
git_pull_workspace() {
    log_info "从远程拉取更新..."
    
    cd "$WORKSPACE_DIR"
    
    # 检查远程仓库
    if ! git remote get-url origin >/dev/null 2>&1; then
        log_error "未配置远程仓库"
        return 1
    fi
    
    current_branch=$(git branch --show-current)
    
    log_info "拉取分支: $current_branch"
    if git pull origin "$current_branch"; then
        log_success "拉取成功"
    else
        log_error "拉取失败，可能有冲突"
        return 1
    fi
}

# 备份OpenClaw配置
backup_openclaw_config() {
    log_info "备份OpenClaw配置..."
    
    backup_dir="$WORKSPACE_DIR/backups"
    mkdir -p "$backup_dir"
    
    timestamp=$(date '+%Y%m%d_%H%M%S')
    backup_file="$backup_dir/openclaw_config_$timestamp.tar.gz"
    
    # 备份关键配置文件
    tar -czf "$backup_file" \
        "$CONFIG_DIR/openclaw.json" \
        "$CONFIG_DIR/agents/" \
        "$WORKSPACE_DIR/AGENTS.md" \
        "$WORKSPACE_DIR/SOUL.md" \
        "$WORKSPACE_DIR/USER.md" \
        "$WORKSPACE_DIR/IDENTITY.md" \
        "$WORKSPACE_DIR/MEMORY.md" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log_success "配置已备份到: $backup_file"
        
        # 添加到Git
        cd "$WORKSPACE_DIR"
        git add "$backup_file"
        git commit -m "备份OpenClaw配置 $timestamp"
        
        log_info "备份文件已提交到Git"
    else
        log_error "备份失败"
    fi
}

# 查看Git状态
show_git_status() {
    log_info "Git状态概览"
    
    cd "$WORKSPACE_DIR"
    
    if [ ! -d .git ]; then
        log_error "工作区不是Git仓库"
        return 1
    fi
    
    echo ""
    echo "📊 仓库信息:"
    echo "-----------"
    echo "位置: $WORKSPACE_DIR"
    echo "分支: $(git branch --show-current)"
    
    remote_url=$(git remote get-url origin 2>/dev/null || echo "未设置")
    echo "远程: $remote_url"
    
    echo ""
    echo "📝 未提交的更改:"
    echo "--------------"
    git status --short
    
    echo ""
    echo "📜 最近提交:"
    echo "-----------"
    git log --oneline -5
    
    echo ""
    echo "🌿 分支列表:"
    echo "-----------"
    git branch -a
}

# 设置定时自动提交
setup_auto_commit_cron() {
    log_info "设置定时自动提交..."
    
    echo "定时自动提交选项:"
    echo "1. 每小时自动提交"
    echo "2. 每天自动提交"
    echo "3. 每周自动提交"
    echo "4. 自定义时间"
    echo "5. 取消"
    
    read -p "选择 (1-5): " cron_choice
    
    case $cron_choice in
        1)
            cron_time="0 * * * *"
            ;;
        2)
            cron_time="0 2 * * *"  # 每天凌晨2点
            ;;
        3)
            cron_time="0 2 * * 0"  # 每周日凌晨2点
            ;;
        4)
            read -p "输入cron表达式 (如: '0 2 * * *'): " custom_cron
            cron_time="$custom_cron"
            ;;
        5)
            log_info "取消设置"
            return
            ;;
        *)
            log_error "无效选择"
            return
            ;;
    esac
    
    # 创建cron任务
    cron_cmd="$cron_time cd $WORKSPACE_DIR && $WORKSPACE_DIR/skills/git-assistant/scripts/openclaw-git-auto.sh --auto-commit"
    
    log_info "将添加cron任务:"
    echo "$cron_cmd"
    
    read -p "确认添加? (y/n): " confirm
    if [ "$confirm" = "y" ]; then
        (crontab -l 2>/dev/null; echo "$cron_cmd") | crontab -
        log_success "定时任务已添加"
    fi
}

# 主菜单
main_menu() {
    while true; do
        echo ""
        echo "🦞 OpenClaw Git自动化菜单"
        echo "========================"
        echo "1. 初始化工作区Git仓库"
        echo "2. 自动提交工作区更改"
        echo "3. 推送到远程仓库"
        echo "4. 从远程拉取更新"
        echo "5. 备份OpenClaw配置"
        echo "6. 查看Git状态"
        echo "7. 设置定时自动提交"
        echo "8. 检查Git配置"
        echo "9. 退出"
        echo ""
        
        read -p "请选择 (1-9): " choice
        
        case $choice in
            1) init_workspace_repo ;;
            2) auto_commit_workspace ;;
            3) git_push_workspace ;;
            4) git_pull_workspace ;;
            5) backup_openclaw_config ;;
            6) show_git_status ;;
            7) setup_auto_commit_cron ;;
            8) check_git_config ;;
            9)
                log_info "退出OpenClaw Git自动化"
                exit 0
                ;;
            *)
                log_error "无效选择"
                ;;
        esac
        
        echo ""
        echo "----------------------------------------"
    done
}

# 命令行参数处理
case "$1" in
    "--auto-commit")
        auto_commit_workspace
        ;;
    "--init")
        init_workspace_repo
        ;;
    "--push")
        git_push_workspace
        ;;
    "--pull")
        git_pull_workspace
        ;;
    "--status")
        show_git_status
        ;;
    "--backup")
        backup_openclaw_config
        ;;
    "--help"|"-h")
        echo "OpenClaw Git自动化脚本"
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  --auto-commit    自动提交工作区更改"
        echo "  --init           初始化工作区Git仓库"
        echo "  --push           推送到远程仓库"
        echo "  --pull           从远程拉取更新"
        echo "  --status         查看Git状态"
        echo "  --backup         备份OpenClaw配置"
        echo "  --help, -h       显示帮助"
        echo ""
        echo "无参数: 显示交互式菜单"
        ;;
    *)
        # 显示主菜单
        check_git_config
        main_menu
        ;;
esac