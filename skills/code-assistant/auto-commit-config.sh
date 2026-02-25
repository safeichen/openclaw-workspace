#!/bin/bash
# 编程代码自动提交配置
# 自动提交生成的代码到指定Git仓库

echo "🤖 编程代码自动提交配置"
echo "======================"

# 默认配置
DEFAULT_REPO="git@github.com:safeichen/toos.git"
CODE_DIR="/root/.openclaw/workspace/generated-code"
CONFIG_FILE="/root/.openclaw/workspace/.code-auto-commit"

# 颜色定义
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

# 加载配置
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
        log_info "配置已加载"
    else
        # 默认配置
        AUTO_COMMIT_ENABLED="true"
        TARGET_REPO="$DEFAULT_REPO"
        CODE_DIR="$CODE_DIR"
        BRANCH="main"
        COMMIT_PREFIX="代码生成: "
        
        # 保存默认配置
        save_config
    fi
}

# 保存配置
save_config() {
    cat > "$CONFIG_FILE" << EOF
# 编程代码自动提交配置
AUTO_COMMIT_ENABLED="$AUTO_COMMIT_ENABLED"
TARGET_REPO="$TARGET_REPO"
CODE_DIR="$CODE_DIR"
BRANCH="$BRANCH"
COMMIT_PREFIX="$COMMIT_PREFIX"
EOF
    log_success "配置已保存到 $CONFIG_FILE"
}

# 初始化代码目录
init_code_dir() {
    log_info "初始化代码目录: $CODE_DIR"
    
    mkdir -p "$CODE_DIR"
    
    if [ ! -d "$CODE_DIR/.git" ]; then
        log_info "初始化Git仓库..."
        cd "$CODE_DIR"
        git init
        
        # 添加.gitignore
        cat > .gitignore << 'GITIGNOREEOF'
# 编译输出
__pycache__/
*.pyc
*.pyo
*.pyd
*.so
*.dll

# 包目录
node_modules/
vendor/
dist/
build/
*.egg-info/

# 环境文件
.env
.env.local
.env.*.local

# 日志文件
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# 运行时数据
*.pid
*.seed
*.pid.lock

# 系统文件
.DS_Store
Thumbs.db
GITIGNOREEOF
        
        log_success "代码目录已初始化"
    else
        log_info "代码目录已是Git仓库"
    fi
}

# 配置Git仓库
setup_git_repo() {
    log_info "配置Git远程仓库..."
    
    cd "$CODE_DIR"
    
    # 检查当前远程
    current_remote=$(git remote get-url origin 2>/dev/null || echo "")
    
    if [ -n "$current_remote" ] && [ "$current_remote" != "$TARGET_REPO" ]; then
        log_warning "当前远程仓库: $current_remote"
        read -p "是否更改为 $TARGET_REPO? (y/N): " change_repo
        if [ "$change_repo" = "y" ]; then
            git remote remove origin
            git remote add origin "$TARGET_REPO"
            log_success "远程仓库已更新"
        fi
    elif [ -z "$current_remote" ]; then
        git remote add origin "$TARGET_REPO"
        log_success "远程仓库已添加"
    else
        log_info "远程仓库已配置: $TARGET_REPO"
    fi
    
    # 检查SSH连接
    log_info "测试GitHub SSH连接..."
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        log_success "GitHub SSH连接正常"
    else
        log_error "GitHub SSH连接失败"
        return 1
    fi
}

# 自动提交代码
auto_commit_code() {
    local file_path="$1"
    local description="$2"
    
    if [ "$AUTO_COMMIT_ENABLED" != "true" ]; then
        log_info "自动提交已禁用"
        return 0
    fi
    
    if [ ! -f "$file_path" ]; then
        log_error "文件不存在: $file_path"
        return 1
    fi
    
    log_info "自动提交代码文件: $(basename "$file_path")"
    
    # 复制文件到代码目录
    filename=$(basename "$file_path")
    target_path="$CODE_DIR/$filename"
    
    # 避免覆盖同名文件
    counter=1
    while [ -f "$target_path" ]; do
        name="${filename%.*}"
        ext="${filename##*.}"
        if [ "$ext" = "$filename" ]; then
            # 没有扩展名
            target_path="$CODE_DIR/${name}_${counter}"
        else
            target_path="$CODE_DIR/${name}_${counter}.${ext}"
        fi
        counter=$((counter + 1))
    done
    
    cp "$file_path" "$target_path"
    log_info "文件已复制到: $target_path"
    
    # 提交到Git
    cd "$CODE_DIR"
    
    git add "$(basename "$target_path")"
    
    commit_msg="${COMMIT_PREFIX}${description}"
    if git commit -m "$commit_msg"; then
        log_success "代码已提交: $commit_msg"
        
        # 推送到远程
        if git push origin "$BRANCH"; then
            log_success "代码已推送到 $TARGET_REPO"
            
            # 显示提交信息
            echo ""
            echo "📋 提交详情:"
            echo "  文件: $(basename "$target_path")"
            echo "  提交: $commit_msg"
            echo "  仓库: $TARGET_REPO"
            echo "  分支: $BRANCH"
            echo ""
            
            return 0
        else
            log_error "推送失败"
            return 1
        fi
    else
        log_warning "提交失败（可能没有更改）"
        return 2
    fi
}

# 手动提交代码
manual_commit() {
    echo "📤 手动提交代码"
    echo "--------------"
    
    read -p "代码文件路径: " file_path
    read -p "提交描述: " description
    
    if [ -z "$description" ]; then
        description="编程助手生成的代码"
    fi
    
    auto_commit_code "$file_path" "$description"
}

# 查看提交历史
view_history() {
    echo "📜 提交历史"
    echo "----------"
    
    cd "$CODE_DIR"
    
    echo "最近5次提交:"
    git log --oneline -5
    
    echo ""
    echo "文件统计:"
    echo "  总文件数: $(find . -type f -not -path "./.git/*" | wc -l)"
    echo "  目录大小: $(du -sh . | cut -f1)"
}

# 配置管理
config_management() {
    echo "⚙️  配置管理"
    echo "-----------"
    
    echo "当前配置:"
    echo "  自动提交: $AUTO_COMMIT_ENABLED"
    echo "  目标仓库: $TARGET_REPO"
    echo "  代码目录: $CODE_DIR"
    echo "  分支: $BRANCH"
    echo "  提交前缀: $COMMIT_PREFIX"
    echo ""
    
    echo "配置选项:"
    echo "1. 启用/禁用自动提交"
    echo "2. 更改目标仓库"
    echo "3. 更改代码目录"
    echo "4. 更改分支"
    echo "5. 更改提交前缀"
    echo "6. 返回"
    echo ""
    
    read -p "选择配置项 (1-6): " config_choice
    
    case $config_choice in
        1)
            if [ "$AUTO_COMMIT_ENABLED" = "true" ]; then
                AUTO_COMMIT_ENABLED="false"
                log_info "已禁用自动提交"
            else
                AUTO_COMMIT_ENABLED="true"
                log_info "已启用自动提交"
            fi
            save_config
            ;;
        2)
            read -p "新的Git仓库URL: " new_repo
            if [ -n "$new_repo" ]; then
                TARGET_REPO="$new_repo"
                save_config
                log_success "目标仓库已更新"
            fi
            ;;
        3)
            read -p "新的代码目录: " new_dir
            if [ -n "$new_dir" ]; then
                CODE_DIR="$new_dir"
                save_config
                log_success "代码目录已更新"
            fi
            ;;
        4)
            read -p "新的分支名称: " new_branch
            if [ -n "$new_branch" ]; then
                BRANCH="$new_branch"
                save_config
                log_success "分支已更新"
            fi
            ;;
        5)
            read -p "新的提交前缀: " new_prefix
            if [ -n "$new_prefix" ]; then
                COMMIT_PREFIX="$new_prefix"
                save_config
                log_success "提交前缀已更新"
            fi
            ;;
    esac
}

# 集成到编程助手
setup_integration() {
    echo "🔗 集成配置"
    echo "-----------"
    
    echo "将自动提交集成到编程助手..."
    
    # 创建包装脚本
    wrapper_script="/root/.openclaw/workspace/skills/code-assistant/scripts/code-with-commit.sh"
    
    cat > "$wrapper_script" << 'WRAPPEREOF'
#!/bin/bash
# 编程助手包装脚本 - 自动提交生成的代码

# 加载配置
CONFIG_FILE="/root/.openclaw/workspace/.code-auto-commit"
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo "❌ 自动提交配置未找到"
    exit 1
fi

# 生成代码（这里调用实际的编程助手）
# 假设代码生成到临时文件
TEMP_FILE="/tmp/generated_code_$(date +%s).py"

# 这里应该是实际的代码生成逻辑
# 例如: python-helper.py "$@" > "$TEMP_FILE"

echo "📝 生成的代码保存到: $TEMP_FILE"
echo "这是示例代码，实际使用时需要替换为真正的代码生成逻辑"

# 自动提交
if [ "$AUTO_COMMIT_ENABLED" = "true" ]; then
    echo "🤖 自动提交到: $TARGET_REPO"
    # 调用自动提交函数
    /root/.openclaw/workspace/skills/code-assistant/auto-commit-config.sh --commit "$TEMP_FILE" "编程助手生成"
fi
WRAPPEREOF
    
    chmod +x "$wrapper_script"
    
    log_success "包装脚本已创建: $wrapper_script"
    echo ""
    echo "💡 使用方式:"
    echo "  直接运行: $wrapper_script"
    echo "  或在编程助手中集成此脚本"
}

# 主菜单
main_menu() {
    while true; do
        echo ""
        echo "🤖 编程代码自动提交系统"
        echo "========================"
        echo "1. 初始化配置"
        echo "2. 手动提交代码"
        echo "3. 查看提交历史"
        echo "4. 配置管理"
        echo "5. 集成设置"
        echo "6. 测试自动提交"
        echo "7. 退出"
        echo ""
        
        read -p "请选择 (1-7): " main_choice
        
        case $main_choice in
            1)
                load_config
                init_code_dir
                setup_git_repo
                ;;
            2)
                manual_commit
                ;;
            3)
                view_history
                ;;
            4)
                config_management
                ;;
            5)
                setup_integration
                ;;
            6)
                echo "🧪 测试自动提交..."
                test_file="/tmp/test_code_$(date +%s).py"
                echo "# 测试代码 $(date)" > "$test_file"
                echo "print('Hello, Auto Commit!')" >> "$test_file"
                auto_commit_code "$test_file" "测试自动提交"
                rm -f "$test_file"
                ;;
            7)
                echo "👋 退出"
                exit 0
                ;;
            *)
                echo "❌ 无效选择"
                ;;
        esac
    done
}

# 命令行参数处理
case "$1" in
    "--commit")
        if [ $# -ge 3 ]; then
            auto_commit_code "$2" "$3"
        else
            echo "用法: $0 --commit <文件路径> <描述>"
        fi
        ;;
    "--init")
        load_config
        init_code_dir
        setup_git_repo
        ;;
    "--config")
        config_management
        ;;
    "--help"|"-h")
        echo "编程代码自动提交系统"
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  --commit <文件> <描述>  自动提交代码"
        echo "  --init                  初始化配置"
        echo "  --config                配置管理"
        echo "  --help, -h             显示帮助"
        echo ""
        echo "无参数: 显示交互式菜单"
        ;;
    *)
        # 显示主菜单
        load_config
        main_menu
        ;;
esac