# 🤖 编程代码自动提交指南

## 🎯 配置目标

**所有编程助手生成的代码自动提交到：**
```
git@github.com:safeichen/toos.git
```

**除非特别指定其他仓库**

## 📦 已配置的系统

### 1. 自动提交配置脚本
- `auto-commit-config.sh` - 完整的自动提交管理系统
- 支持：初始化、配置、手动提交、历史查看

### 2. 集成代码生成器
- `code-generator-with-commit.py` - 带自动提交的代码生成器
- 支持：Python、JavaScript、Bash代码生成和自动提交

### 3. 默认配置
- **目标仓库**: `git@github.com:safeichen/toos.git`
- **代码目录**: `/root/.openclaw/workspace/generated-code`
- **分支**: `main`
- **提交前缀**: `代码生成: `

## 🚀 快速开始

### 方法1：使用集成代码生成器
```bash
cd /root/.openclaw/workspace
python3 skills/code-assistant/scripts/code-generator-with-commit.py
```

### 方法2：使用配置管理工具
```bash
cd /root/.openclaw/workspace
./skills/code-assistant/auto-commit-config.sh
```

### 方法3：命令行快速生成
```bash
# 生成Python代码并自动提交
python3 skills/code-assistant/scripts/code-generator-with-commit.py python "数据处理函数" code.py

# 生成JavaScript代码并自动提交
python3 skills/code-assistant/scripts/code-generator-with-commit.py js "React组件" component.js

# 生成Bash脚本并自动提交
python3 skills/code-assistant/scripts/code-generator-with-commit.py bash "部署脚本" deploy.sh
```

## 🔧 配置管理

### 查看当前配置
```bash
./skills/code-assistant/auto-commit-config.sh --config
```

### 初始化系统
```bash
./skills/code-assistant/auto-commit-config.sh --init
```

### 手动提交代码
```bash
./skills/code-assistant/auto-commit-config.sh --commit /path/to/code.py "代码描述"
```

## 📁 代码目录结构

```
/root/.openclaw/workspace/generated-code/
├── .git/                    # Git仓库
├── .gitignore              # Git忽略规则
├── generated_20250225_143022.py
├── generated_20250225_143045.js
└── generated_20250225_143107.sh
```

## 🎯 使用流程

### 1. 生成代码时
```python
# 使用编程助手生成代码后，自动：
# 1. 保存到 generated-code/ 目录
# 2. 自动提交到本地Git
# 3. 推送到 GitHub toos 仓库
# 4. 显示提交信息
```

### 2. 查看提交历史
```bash
cd /root/.openclaw/workspace/generated-code
git log --oneline
```

### 3. 访问GitHub仓库
- **URL**: https://github.com/safeichen/toos
- **分支**: `main`
- **内容**: 所有自动提交的代码文件

## ⚙️ 自定义配置

### 更改目标仓库
```bash
# 编辑配置文件
nano /root/.openclaw/workspace/.code-auto-commit

# 或使用配置工具
./skills/code-assistant/auto-commit-config.sh
# 选择"配置管理" → "更改目标仓库"
```

### 禁用自动提交
```bash
# 临时禁用
./skills/code-assistant/auto-commit-config.sh
# 选择"配置管理" → "启用/禁用自动提交"

# 或直接编辑配置文件
echo 'AUTO_COMMIT_ENABLED="false"' >> /root/.openclaw/workspace/.code-auto-commit
```

## 🔗 与编程助手集成

### 在编程助手中使用
```bash
# 1. 运行编程助手
./skills/code-assistant/scripts/quick-code.sh

# 2. 生成的代码会自动保存并提交
# 3. 查看提交结果
```

### 自定义代码生成
```python
# 在Python脚本中使用
from skills.code-assistant.scripts.code-generator-with-commit import CodeGeneratorWithCommit

generator = CodeGeneratorWithCommit()
generator.generate_python_code(
    "我的Python函数",
    "def hello():\n    print('Hello, World!')"
)
```

## 📊 监控和管理

### 查看提交统计
```bash
cd /root/.openclaw/workspace/generated-code
git shortlog -sn  # 提交统计
git log --oneline --graph  # 提交历史图
git status  # 当前状态
```

### 清理旧文件
```bash
# 查看文件大小
du -sh /root/.openclaw/workspace/generated-code

# 清理30天前的文件（谨慎操作）
find /root/.openclaw/workspace/generated-code -name "generated_*" -mtime +30 -delete
```

## 🚨 故障排除

### SSH连接问题
```bash
# 测试GitHub连接
ssh -T git@github.com

# 重新生成SSH密钥
ssh-keygen -t rsa -b 4096 -C "984203519@qq.com"
# 添加公钥到GitHub
```

### Git推送失败
```bash
# 拉取最新更改
cd /root/.openclaw/workspace/generated-code
git pull --rebase origin main

# 强制推送（谨慎使用）
git push -f origin main
```

### 文件冲突
```bash
# 查看冲突
git status

# 解决冲突后
git add .
git commit -m "解决冲突"
git push origin main
```

## 🎉 开始使用

### 第一步：初始化
```bash
./skills/code-assistant/auto-commit-config.sh --init
```

### 第二步：测试生成
```bash
python3 skills/code-assistant/scripts/code-generator-with-commit.py
# 选择"生成Python代码"
# 输入描述和代码
# 观察自动提交过程
```

### 第三步：验证提交
```bash
# 查看本地提交
cd /root/.openclaw/workspace/generated-code
git log --oneline -3

# 访问GitHub验证
# https://github.com/safeichen/toos
```

## 📞 需要帮助？

### 查看日志
```bash
# 查看自动提交日志
tail -f /root/.openclaw/workspace/generated-code/.git/logs/HEAD
```

### 重置配置
```bash
# 删除配置文件重新开始
rm /root/.openclaw/workspace/.code-auto-commit
./skills/code-assistant/auto-commit-config.sh --init
```

### 手动操作
```bash
# 如果自动提交失败，可以手动操作
cd /root/.openclaw/workspace/generated-code
git add .
git commit -m "手动提交"
git push origin main
```

---

**现在所有编程助手生成的代码都会自动提交到 `git@github.com:safeichen/toos.git`！** 🚀