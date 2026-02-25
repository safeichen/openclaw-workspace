# 📧 IMAP/SMTP邮件技能快速开始

## 🚀 3步开始读取邮件

### 步骤1: 配置邮箱
```bash
# 进入技能目录
cd /root/.openclaw/workspace/skills/imap-smtp-email

# 创建配置文件
cp .env.example .env

# 编辑配置文件
nano .env  # 或使用其他编辑器
```

### 步骤2: 填写邮箱信息（以QQ邮箱为例）
```bash
# .env 文件内容示例：
IMAP_HOST=imap.qq.com
IMAP_PORT=993
IMAP_USER=你的QQ号@qq.com
IMAP_PASS=你的16位授权码  # ⚠️ 不是QQ密码！
IMAP_TLS=true

SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=你的QQ号@qq.com
SMTP_PASS=你的16位授权码
```

### 步骤3: 测试连接
```bash
# 测试读取邮件
node scripts/imap.js check --limit 3

# 如果成功，你会看到类似：
# ✓ Connected to imap.qq.com:993
# ✓ Found 3 emails
# - [未读] 发件人: xxx 主题: xxx
```

## 📋 常用命令速查

### 读取邮件
```bash
# 查看最近5封邮件
node scripts/imap.js check --limit 5

# 查看未读邮件
node scripts/imap.js check --unseen

# 查看今天收到的邮件
node scripts/imap.js check --recent 1d
```

### 搜索邮件
```bash
# 搜索特定发件人
node scripts/imap.js search --from "service@qq.com"

# 搜索包含关键词的邮件
node scripts/imap.js search --subject "账单"

# 组合搜索
node scripts/imap.js search --unseen --from "alice@example.com" --limit 10
```

### 管理邮件
```bash
# 标记为已读
node scripts/imap.js mark-read <邮件UID>

# 标记为未读
node scripts/imap.js mark-unread <邮件UID>

# 列出所有邮箱文件夹
node scripts/imap.js list-mailboxes
```

### 发送邮件
```bash
# 发送简单邮件
node scripts/smtp.js send --to "friend@example.com" --subject "你好" --body "邮件内容"

# 发送HTML邮件
node scripts/smtp.js send --to "friend@example.com" --subject "HTML邮件" --html --body "<h1>标题</h1><p>内容</p>"

# 发送带附件的邮件
node scripts/smtp.js send --to "friend@example.com" --subject "报告" --body "请查看附件" --attach report.pdf
```

## 🔐 获取授权码指南

### QQ邮箱授权码
1. 登录 QQ邮箱网页版 (mail.qq.com)
2. 设置 → 账户 → POP3/IMAP/SMTP服务
3. 开启 IMAP/SMTP服务
4. 生成授权码（16位）
5. 在配置中使用这个授权码

### Gmail应用专用密码
1. 确保开启两步验证
2. 访问: https://myaccount.google.com/apppasswords
3. 生成应用专用密码
4. 在配置中使用这个密码

## 🚨 常见问题

### 连接失败
```bash
# 检查网络
ping imap.qq.com

# 检查端口
telnet imap.qq.com 993

# 检查配置
cat .env | grep -v "PASS"
```

### 认证失败
- ❌ 错误: 使用QQ密码
- ✅ 正确: 使用授权码
- ❌ 错误: 未开启IMAP服务
- ✅ 正确: 在网页版开启服务

### 权限问题
```bash
# 确保有执行权限
chmod +x scripts/*.js

# 确保能读取配置文件
chmod 600 .env
```

## 🎯 实用示例

### 示例1: 每日邮件摘要
```bash
# 查看今天的所有邮件
node scripts/imap.js check --recent 1d --limit 20

# 统计未读邮件数量
node scripts/imap.js check --unseen | grep "Found" | awk '{print $2}'
```

### 示例2: 自动处理特定邮件
```bash
# 搜索验证码邮件
node scripts/imap.js search --subject "验证码" --recent 30m

# 搜索账单邮件
node scripts/imap.js search --from "alipay.com" --recent 7d
```

### 示例3: 邮件备份
```bash
# 下载所有附件
node scripts/imap.js download <邮件UID> --dir ./attachments

# 导出邮件内容
node scripts/imap.js fetch <邮件UID> > email_backup.txt
```

## 📞 获取帮助

```bash
# 查看所有命令
node scripts/imap.js --help
node scripts/smtp.js --help

# 测试连接
node scripts/imap.js check --limit 1
node scripts/smtp.js test
```

## ⚡ 快速测试
```bash
# 一次性测试命令
cd /root/.openclaw/workspace/skills/imap-smtp-email && \
echo "测试邮件技能..." && \
node scripts/imap.js check --limit 1 2>&1 | head -20
```

现在就开始读取你的邮件吧！ 🎉