# 🦞 OpenClaw Git 使用指南

## 📦 已安装的Git技能

### 1. git-assistant (自定义技能)
**位置**: `/root/.openclaw/workspace/skills/git-assistant/`
**功能**: Git版本控制助手，提供常用命令封装和工作流指导

### 2. 可用脚本
- `git-quick.sh` - 交互式Git操作菜单
- `openclaw-git-auto.sh` - OpenClaw专用Git自动化

## 🚀 快速开始

### 方法1: 使用Git快速助手
```bash
cd /root/.openclaw/workspace
./skills/git-assistant/scripts/git-quick.sh
```

### 方法2: 使用OpenClaw Git自动化
```bash
cd /root/.openclaw/workspace
./skills/git-assistant/scripts/openclaw-git-auto.sh
```

### 方法3: 直接使用Git命令
```bash
# 进入工作区
cd /root/.openclaw/workspace

# 初始化Git仓库（如果尚未初始化）
git init

# 查看状态
git status

# 添加文件
git add .

# 提交更改
git commit -m "提交说明"

# 推送到远程（需要先配置远程仓库）
git remote add origin <仓库URL>
git push -u origin main
```

## 🔧 配置Git

### 1. 配置用户信息
```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
git config --global core.editor "vim"
```

### 2. 配置SSH密钥（用于GitHub等）
```bash
# 生成SSH密钥
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 查看公钥
cat ~/.ssh/id_rsa.pub

# 添加到GitHub: Settings → SSH and GPG keys → New SSH key
```

## 📁 OpenClaw工作区Git管理

### 初始化工作区Git仓库
```bash
cd /root/.openclaw/workspace
./skills/git-assistant/scripts/openclaw-git-auto.sh --init
```

### 自动提交工作区更改
```bash
# 交互式提交
./skills/git-assistant/scripts/openclaw-git-auto.sh

# 或直接自动提交
./skills/git-assistant/scripts/openclaw-git-auto.sh --auto-commit
```

### 备份OpenClaw配置
```bash
./skills/git-assistant/scripts/openclaw-git-auto.sh --backup
```

## 🎯 常用工作流

### 1. 日常开发流程
```bash
# 1. 开始新功能
git checkout main
git pull origin main
git checkout -b feature/功能名称

# 2. 开发
# ... 编写代码 ...

# 3. 提交更改
git add .
git commit -m "完成功能描述"

# 4. 推送到远程
git push origin feature/功能名称

# 5. 创建Pull Request（在GitHub/GitLab界面）
```

### 2. 修复Bug流程
```bash
# 1. 创建修复分支
git checkout main
git pull origin main
git checkout -b hotfix/问题描述

# 2. 修复问题
# ... 修复代码 ...

# 3. 提交修复
git add .
git commit -m "修复问题描述"

# 4. 合并到主分支
git checkout main
git merge hotfix/问题描述
git push origin main
```

### 3. 代码审查流程
```bash
# 1. 获取他人代码
git fetch origin
git checkout feature/他人功能分支

# 2. 查看更改
git log --oneline -10
git diff main..feature/他人功能分支

# 3. 测试代码
# ... 运行测试 ...

# 4. 提供反馈后
git checkout main
```

## ⚡ 实用命令速查

### 基础命令
```bash
git status                  # 查看状态
git add <文件>             # 添加文件
git commit -m "消息"       # 提交更改
git push                   # 推送到远程
git pull                   # 从远程拉取
git clone <URL>           # 克隆仓库
```

### 分支管理
```bash
git branch                 # 查看分支
git branch <分支名>        # 创建分支
git checkout <分支名>      # 切换分支
git checkout -b <分支名>   # 创建并切换
git merge <分支名>         # 合并分支
git branch -d <分支名>     # 删除分支
```

### 历史查看
```bash
git log                    # 查看提交历史
git log --oneline          # 简洁显示
git log --graph --all      # 图形化显示
git show <提交ID>          # 显示提交详情
git diff                   # 查看差异
```

### 撤销操作
```bash
git reset HEAD <文件>      # 撤销暂存
git reset --soft HEAD^     # 撤销提交（保留更改）
git reset --hard HEAD^     # 撤销提交（丢弃更改）
git checkout -- <文件>     # 丢弃工作区更改
git commit --amend         # 修改上次提交
```

## 🔄 集成到OpenClaw工作流

### 定时自动提交
```bash
# 设置每小时自动提交
0 * * * * cd /root/.openclaw/workspace && ./skills/git-assistant/scripts/openclaw-git-auto.sh --auto-commit
```

### 在技能中使用Git
```python
# 在Python技能中调用Git
import subprocess

def git_auto_commit():
    """自动提交OpenClaw工作区"""
    result = subprocess.run(
        ["./skills/git-assistant/scripts/openclaw-git-auto.sh", "--auto-commit"],
        cwd="/root/.openclaw/workspace",
        capture_output=True,
        text=True
    )
    return result.stdout
```

### 在心跳检查中加入Git状态
```bash
# 在HEARTBEAT.md中添加
- 检查Git状态：是否有未提交的更改
- 自动提交重要更改
- 备份关键配置文件
```

## 🛠️ 故障排除

### 常见问题

**1. 权限被拒绝 (Permission denied)**
```bash
# 检查SSH密钥
ssh -T git@github.com

# 重新添加密钥
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

**3. 误删文件恢复**
```bash
# 查看删除历史
git log --diff-filter=D --summary

# 恢复文件
git checkout <提交ID>^ -- <文件路径>
```

**4. 大文件处理**
```bash
# 使用Git LFS（如果需要）
git lfs install
git lfs track "*.psd"
git add .gitattributes
```

## 📊 最佳实践

### 提交规范
1. **提交信息格式**:
   ```
   类型(范围): 简短描述
   
   详细描述（可选）
   
   关闭的问题（可选）
   ```

2. **类型说明**:
   - `feat`: 新功能
   - `fix`: 修复bug
   - `docs`: 文档更新
   - `style`: 代码格式
   - `refactor`: 重构
   - `test`: 测试相关
   - `chore`: 构建过程或辅助工具

### 分支策略
- `main`: 主分支，稳定版本
- `develop`: 开发分支
- `feature/*`: 功能分支
- `hotfix/*`: 紧急修复
- `release/*`: 发布分支

### 工作区管理
- 定期提交OpenClaw配置更改
- 备份重要记忆文件
- 使用.gitignore排除临时文件
- 设置定时自动备份

## 🎉 开始使用

### 第一步：初始化
```bash
cd /root/.openclaw/workspace
./skills/git-assistant/scripts/openclaw-git-auto.sh --init
```

### 第二步：配置远程仓库（可选）
```bash
git remote add origin <你的仓库URL>
```

### 第三步：开始使用
```bash
# 使用交互式菜单
./skills/git-assistant/scripts/git-quick.sh

# 或使用自动化脚本
./skills/git-assistant/scripts/openclaw-git-auto.sh
```

现在你可以开始使用Git管理你的OpenClaw工作区和项目了！ 🚀