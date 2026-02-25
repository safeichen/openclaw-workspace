#!/bin/bash
# Git快速操作脚本

echo "🚀 Git快速助手"
echo "=============="

show_menu() {
    echo ""
    echo "📋 Git操作菜单"
    echo "--------------"
    echo "1. 仓库状态"
    echo "2. 添加并提交"
    echo "3. 推送到远程"
    echo "4. 拉取更新"
    echo "5. 查看提交历史"
    echo "6. 分支管理"
    echo "7. 克隆仓库"
    echo "8. 解决冲突"
    echo "9. 撤销操作"
    echo "10. 退出"
    echo ""
}

git_status() {
    echo "📊 仓库状态:"
    git status
}

git_add_commit() {
    echo "📝 添加并提交更改"
    
    read -p "提交说明: " commit_msg
    if [ -z "$commit_msg" ]; then
        commit_msg="更新 $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    echo "添加文件到暂存区..."
    git add .
    
    echo "提交更改..."
    git commit -m "$commit_msg"
    
    echo "✅ 提交完成: $commit_msg"
}

git_push() {
    echo "📤 推送到远程仓库"
    
    current_branch=$(git branch --show-current)
    echo "当前分支: $current_branch"
    
    read -p "远程名称 (默认: origin): " remote
    remote=${remote:-origin}
    
    read -p "分支名称 (默认: $current_branch): " branch
    branch=${branch:-$current_branch}
    
    echo "推送 $branch 到 $remote..."
    git push "$remote" "$branch"
}

git_pull() {
    echo "📥 拉取更新"
    
    current_branch=$(git branch --show-current)
    echo "当前分支: $current_branch"
    
    read -p "远程名称 (默认: origin): " remote
    remote=${remote:-origin}
    
    read -p "分支名称 (默认: $current_branch): " branch
    branch=${branch:-$current_branch}
    
    echo "从 $remote/$branch 拉取..."
    git pull "$remote" "$branch"
}

git_log() {
    echo "📜 提交历史"
    
    echo "选择查看方式:"
    echo "1. 简洁模式 (一行显示)"
    echo "2. 详细模式"
    echo "3. 图形模式"
    echo "4. 最近N条"
    read -p "选择 (1-4): " log_type
    
    case $log_type in
        1)
            git log --oneline -20
            ;;
        2)
            git log -10
            ;;
        3)
            git log --graph --oneline --all -20
            ;;
        4)
            read -p "显示条数: " count
            git log --oneline -${count:-10}
            ;;
        *)
            git log --oneline -10
            ;;
    esac
}

git_branch_manage() {
    echo "🌿 分支管理"
    
    echo "当前分支: $(git branch --show-current)"
    echo ""
    echo "所有分支:"
    git branch -a
    
    echo ""
    echo "分支操作:"
    echo "1. 创建新分支"
    echo "2. 切换分支"
    echo "3. 删除分支"
    echo "4. 合并分支"
    read -p "选择 (1-4): " branch_op
    
    case $branch_op in
        1)
            read -p "新分支名称: " new_branch
            git checkout -b "$new_branch"
            ;;
        2)
            read -p "切换到分支: " target_branch
            git checkout "$target_branch"
            ;;
        3)
            read -p "删除分支: " del_branch
            read -p "确认删除分支 $del_branch? (y/n): " confirm
            if [ "$confirm" = "y" ]; then
                git branch -d "$del_branch"
            fi
            ;;
        4)
            read -p "合并到当前分支的分支名: " merge_branch
            git merge "$merge_branch"
            ;;
    esac
}

git_clone() {
    echo "📦 克隆仓库"
    
    read -p "仓库URL: " repo_url
    if [ -z "$repo_url" ]; then
        echo "❌ 需要仓库URL"
        return
    fi
    
    read -p "目标目录 (留空使用仓库名): " target_dir
    
    if [ -z "$target_dir" ]; then
        git clone "$repo_url"
    else
        git clone "$repo_url" "$target_dir"
    fi
}

git_resolve_conflict() {
    echo "⚡ 冲突解决指南"
    
    echo "1. 查看冲突文件:"
    git status | grep "both modified"
    
    echo ""
    echo "2. 打开冲突文件，解决冲突标记:"
    echo "   <<<<<<< HEAD"
    echo "   你的代码"
    echo "   ======="
    echo "   他人代码"
    echo "   >>>>>>> branch-name"
    
    echo ""
    echo "3. 解决后标记为已解决:"
    echo "   git add <文件名>"
    
    echo ""
    echo "4. 完成解决:"
    echo "   git commit"
    
    echo ""
    read -p "是否已解决冲突并继续? (y/n): " resolved
    if [ "$resolved" = "y" ]; then
        git status
    fi
}

git_undo() {
    echo "↩️  撤销操作"
    
    echo "撤销选项:"
    echo "1. 撤销暂存 (git reset)"
    echo "2. 撤销提交 (git reset --soft)"
    echo "3. 丢弃更改 (git checkout --)"
    echo "4. 修改上次提交 (git commit --amend)"
    read -p "选择 (1-4): " undo_op
    
    case $undo_op in
        1)
            echo "撤销暂存的文件..."
            git reset HEAD
            ;;
        2)
            read -p "撤销到哪个提交? (默认: HEAD^): " commit_ref
            commit_ref=${commit_ref:-HEAD^}
            git reset --soft "$commit_ref"
            echo "✅ 已撤销提交，更改保留在工作区"
            ;;
        3)
            read -p "文件名 (全部输入.): " filename
            git checkout -- "$filename"
            ;;
        4)
            read -p "新的提交信息 (留空保持原样): " new_msg
            if [ -z "$new_msg" ]; then
                git commit --amend --no-edit
            else
                git commit --amend -m "$new_msg"
            fi
            ;;
    esac
}

# 主循环
main() {
    while true; do
        show_menu
        read -p "请选择操作 (1-10): " choice
        
        case $choice in
            1) git_status ;;
            2) git_add_commit ;;
            3) git_push ;;
            4) git_pull ;;
            5) git_log ;;
            6) git_branch_manage ;;
            7) git_clone ;;
            8) git_resolve_conflict ;;
            9) git_undo ;;
            10)
                echo "👋 退出Git助手"
                exit 0
                ;;
            *)
                echo "❌ 无效选择"
                ;;
        esac
        
        echo ""
        echo "----------------------------------------"
    done
}

# 检查是否在Git仓库中
if [ ! -d .git ] && [ "$1" != "clone" ]; then
    echo "⚠️  当前目录不是Git仓库"
    read -p "是否初始化新仓库? (y/n): " init_repo
    if [ "$init_repo" = "y" ]; then
        git init
        echo "✅ 已初始化Git仓库"
    else
        echo "请进入Git仓库目录或使用克隆功能"
        exit 1
    fi
fi

# 运行主程序
main