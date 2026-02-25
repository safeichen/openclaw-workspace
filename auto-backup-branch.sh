#!/bin/bash
# 修改自动备份分支配置

echo "🌿 自动备份分支配置工具"
echo "======================"

CONFIG_FILE="/root/.openclaw/workspace/auto-backup.sh"
BACKUP_BRANCH=""

# 获取当前配置
get_current_config() {
    echo "当前配置:"
    echo "----------"
    
    # 从auto-backup.sh中提取推送命令
    grep -n "git push origin" "$CONFIG_FILE" | head -5
    
    echo ""
    echo "当前分支: $(cd /root/.openclaw/workspace && git branch --show-current)"
    echo "远程分支: $(cd /root/.openclaw/workspace && git remote show origin | grep 'HEAD branch' | cut -d: -f2)"
}

# 修改备份分支
change_backup_branch() {
    echo "选择备份分支策略:"
    echo "1. main分支（默认，直接推送）"
    echo "2. backup/auto分支（专用备份分支）"
    echo "3. 每日分支（backup/YYYYMMDD）"
    echo "4. 自定义分支"
    echo ""
    
    read -p "请选择 (1-4): " choice
    
    case $choice in
        1)
            BACKUP_BRANCH='$current_branch'  # 使用当前分支
            echo "✅ 设置为推送到当前分支（main）"
            ;;
        2)
            BACKUP_BRANCH="backup/auto"
            echo "✅ 设置为推送到 backup/auto 分支"
            ;;
        3)
            BACKUP_BRANCH='backup/$(date +%Y%m%d)'
            echo "✅ 设置为推送到每日备份分支"
            ;;
        4)
            read -p "请输入分支名称: " custom_branch
            BACKUP_BRANCH="$custom_branch"
            echo "✅ 设置为推送到 $custom_branch 分支"
            ;;
        *)
            echo "❌ 无效选择"
            return 1
            ;;
    esac
    
    # 备份原文件
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup"
    
    # 修改推送命令
    sed -i "s/git push origin \"\$current_branch\"/git push origin \"$BACKUP_BRANCH\"/g" "$CONFIG_FILE"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "📝 配置已更新:"
        grep "git push origin" "$CONFIG_FILE"
        return 0
    else
        echo "❌ 配置更新失败"
        return 1
    fi
}

# 创建备份分支
create_backup_branch() {
    if [[ "$BACKUP_BRANCH" != '\$current_branch' ]]; then
        echo "创建分支: $BACKUP_BRANCH"
        cd /root/.openclaw/workspace
        
        # 创建分支
        git checkout -b "$BACKUP_BRANCH" 2>/dev/null || git checkout "$BACKUP_BRANCH"
        
        # 推送到远程
        git push -u origin "$BACKUP_BRANCH"
        
        echo "✅ 分支创建并推送到远程"
    fi
}

# 显示帮助
show_help() {
    echo "分支策略说明:"
    echo "-------------"
    echo "1. main分支 - 简单直接，适合个人项目"
    echo "2. backup/auto - 专用备份分支，保持main干净"
    echo "3. 每日分支 - 每天创建新分支，历史清晰"
    echo "4. 自定义 - 根据需要设置"
    echo ""
    echo "当前自动备份会在每天晚上10点执行，推送到配置的分支。"
}

# 主函数
main() {
    get_current_config
    
    echo ""
    read -p "是否修改备份分支配置? (y/N): " modify
    
    if [ "$modify" = "y" ]; then
        if change_backup_branch; then
            read -p "是否立即创建并切换到该分支? (y/N): " create_now
            if [ "$create_now" = "y" ]; then
                create_backup_branch
            fi
        fi
    fi
    
    echo ""
    show_help
}

# 执行
case "$1" in
    "--reset")
        echo "恢复默认配置..."
        cp "$CONFIG_FILE.backup" "$CONFIG_FILE" 2>/dev/null || echo "没有备份文件"
        ;;
    "--current")
        get_current_config
        ;;
    "--help"|"-h")
        show_help
        ;;
    *)
        main
        ;;
esac