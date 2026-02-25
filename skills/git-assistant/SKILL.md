---
name: git-assistant
description: Git版本控制助手。提供常用的Git命令封装、工作流指导和自动化操作。
---

# Git Assistant Skill

Git版本控制助手，提供常用的Git命令封装和工作流指导。

## 功能特性

### 基础操作
- `git status` - 查看仓库状态
- `git add` - 添加文件到暂存区
- `git commit` - 提交更改
- `git push` - 推送到远程仓库
- `git pull` - 从远程拉取更新
- `git clone` - 克隆仓库

### 分支管理
- `git branch` - 分支操作
- `git checkout` - 切换分支
- `git merge` - 合并分支
- `git rebase` - 变基操作

### 历史查看
- `git log` - 查看提交历史
- `git diff` - 查看差异
- `git show` - 显示提交详情

### 高级功能
- 冲突解决指导
- 工作流建议（Git Flow, GitHub Flow）
- 自动化提交脚本
- 多仓库管理

## 快速开始

### 安装
```bash
# 确保Git已安装
git --version

# 使用技能
# 通过OpenClaw调用Git助手
```

### 基本使用示例

**查看仓库状态：**
```bash
git status
```

**添加并提交更改：**
```bash
git add .
git commit -m "提交说明"
git push origin main
```

**创建新分支：**
```bash
git checkout -b feature/new-feature
git push -u origin feature/new-feature
```

## 常用工作流

### 1. 日常开发流程
```bash
# 开始新功能
git checkout main
git pull origin main
git checkout -b feature/your-feature

# 开发完成后
git add .
git commit -m "完成新功能"
git push origin feature/your-feature

# 创建Pull Request（在GitHub/GitLab上）
```

### 2. 修复Bug流程
```bash
git checkout main
git pull origin main
git checkout -b hotfix/bug-description

# 修复bug
git add .
git commit -m "修复bug描述"
git push origin hotfix/bug-description
```

### 3. 代码审查流程
```bash
# 查看他人提交
git fetch origin
git checkout feature/other-feature
git log --oneline -10

# 测试他人代码
git diff main..feature/other-feature
```

## 脚本工具

### 自动化提交脚本
```bash
#!/bin/bash
# auto-commit.sh

commit_message="$1"
if [ -z "$commit_message" ]; then
    commit_message="自动提交 $(date '+%Y-%m-%d %H:%M:%S')"
fi

git add .
git commit -m "$commit_message"
git push origin $(git branch --show-current)
```

### 批量仓库更新
```bash
#!/bin/bash
# update-all-repos.sh

for dir in */; do
    if [ -d "$dir/.git" ]; then
        echo "更新仓库: $dir"
        cd "$dir"
        git pull
        cd ..
    fi
done
```

## 配置建议

### Git全局配置
```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
git config --global core.editor "vim"
git config --global color.ui auto
```

### 别名配置（~/.gitconfig）
```ini
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    lg = log --oneline --graph --all
    last = log -1 HEAD
    unstage = reset HEAD --
    undo = reset --soft HEAD^
```

## 故障排除

### 常见问题

**1. 权限被拒绝**
```bash
# 检查SSH密钥
ssh -T git@github.com

# 重新添加SSH密钥
ssh-add ~/.ssh/id_rsa
```

**2. 冲突解决**
```bash
# 查看冲突文件
git status

# 手动解决冲突后
git add .
git commit -m "解决冲突"
```

**3. 撤销操作**
```bash
# 撤销最后一次提交（保留更改）
git reset --soft HEAD^

# 撤销最后一次提交（丢弃更改）
git reset --hard HEAD^

# 撤销特定文件
git checkout -- filename
```

## 最佳实践

1. **提交信息规范**
   - 使用英文或清晰的中文
   - 第一行简短描述（<50字符）
   - 第二行空行
   - 第三行开始详细说明

2. **分支命名**
   - feature/功能名称
   - bugfix/问题描述
   - hotfix/紧急修复
   - release/版本号

3. **提交频率**
   - 小步提交，频繁提交
   - 每个提交解决一个问题
   - 保持提交历史的清晰

## 集成OpenClaw

### 作为技能使用
```bash
# 在OpenClaw中调用Git助手
# 例如：自动提交工作区更改
```

### 定时任务
```bash
# 每天自动备份
0 2 * * * cd /path/to/repo && git add . && git commit -m "每日备份" && git push
```

## 扩展功能

如需更多功能，可以：
1. 安装其他Git技能（git-essentials, git-workflows等）
2. 自定义脚本满足特定需求
3. 集成CI/CD工具

---

**注意**: 此技能提供Git操作指导，实际Git命令需要在终端中执行。