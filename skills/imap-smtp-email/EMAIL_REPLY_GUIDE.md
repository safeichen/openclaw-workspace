# 📧 邮件回复指南

## 🚀 快速开始

### 方法1: 使用回复工具（推荐）
```bash
# 查看邮件列表，获取邮件UID
node scripts/imap.js check --limit 5

# 使用回复工具
node reply_email.js <邮件UID> --body "你的回复内容"

# 示例
node reply_email.js 12345 --body "收到，谢谢分享！"
```

### 方法2: 手动回复
```bash
# 1. 查看邮件详情，获取发件人
node scripts/imap.js fetch 12345

# 2. 发送回复
node scripts/smtp.js send --to "原发件人@example.com" --subject "Re: 原主题" --body "回复内容"
```

## 📋 回复功能详解

### 1. 简单回复
```bash
# 查看未读邮件
node scripts/imap.js check --unseen --limit 10

# 回复第一封未读邮件
node reply_email.js 123 --body "已收到，正在处理"
```

### 2. 包含原邮件内容的回复
```bash
node reply_email.js 123 --body "针对您的问题：" --include-original
```

### 3. 带抄送/密送的回复
```bash
# 抄送给其他人
node reply_email.js 123 --body "请查收" --cc "manager@example.com,team@example.com"

# 密送
node reply_email.js 123 --body "内部回复" --bcc "internal@example.com"
```

### 4. 批量回复未读邮件
```bash
#!/bin/bash
# 批量回复未读邮件脚本

# 获取未读邮件UID列表
uids=$(node scripts/imap.js check --unseen --json | grep -o '"uid":"[^"]*"' | cut -d'"' -f4)

for uid in $uids; do
  echo "回复邮件 UID: $uid"
  node reply_email.js $uid --body "自动回复：已收到您的邮件，我们会在24小时内处理。"
done
```

## 🎯 实用场景

### 场景1: 自动确认收到
```bash
# 自动回复所有未读邮件
node scripts/imap.js check --unseen --json | grep -o '"uid":"[^"]*"' | while read line; do
  uid=$(echo $line | cut -d'"' -f4)
  node reply_email.js $uid --body "您好！已收到您的邮件，我们会尽快处理。"
done
```

### 场景2: 技术支持回复模板
```bash
# 创建回复模板
REPLY_TEMPLATE="感谢您联系技术支持。

我们已经收到您的问题，预计在2小时内给您回复。

问题描述已记录：
- 问题ID: TECH-$(date +%Y%m%d-%H%M%S)
- 提交时间: $(date '+%Y-%m-%d %H:%M:%S')

如有紧急问题，请拨打热线：400-xxx-xxxx"

# 回复邮件
node reply_email.js 12345 --body "$REPLY_TEMPLATE" --include-original
```

### 场景3: 会议邀请回复
```bash
# 会议确认回复
node reply_email.js 12345 --body "会议邀请已确认，我会准时参加。

参会信息：
- 姓名: 你的名字
- 部门: 技术部
- 联系方式: 你的电话" --cc "assistant@example.com"
```

## 🔧 高级功能

### 1. 智能回复（基于邮件内容）
```javascript
// smart_reply.js - 智能回复脚本
const email = getEmailContent(uid);
const category = classifyEmail(email);

let reply = "";
switch(category) {
  case "question":
    reply = "感谢您的提问，我们正在研究...";
    break;
  case "complaint":
    reply = "很抱歉给您带来不便，我们会立即处理...";
    break;
  case "feedback":
    reply = "感谢您的反馈，这对我们很重要...";
    break;
  default:
    reply = "已收到您的邮件，谢谢！";
}

node reply_email.js uid --body reply;
```

### 2. 定时自动回复
```bash
# 使用cron定时检查并回复
# 编辑crontab: crontab -e
# 每30分钟检查一次未读邮件并自动回复
*/30 * * * * cd /path/to/imap-smtp-email && node scripts/imap.js check --unseen --json | grep -q '"unread":true' && node auto_reply.js
```

### 3. 邮件转发+回复
```bash
# 转发邮件并回复发件人
node scripts/smtp.js send --to "forward@example.com" --subject "FW: 原主题" --body "请处理此邮件" --attach "原邮件内容"
node reply_email.js 123 --body "您的邮件已转发给相关部门处理"
```

## ⚙️ 配置建议

### 1. 创建回复模板目录
```bash
mkdir -p templates/
echo "感谢您的来信！我们已收到并会尽快处理。" > templates/acknowledge.txt
echo "问题已记录，工单号: TICKET-\$(date +%Y%m%d%H%M%S)" > templates/support.txt
```

### 2. 使用模板回复
```bash
# 使用模板回复
template=$(cat templates/acknowledge.txt)
node reply_email.js 123 --body "$template"
```

### 3. 记录回复历史
```bash
# 记录回复日志
log_reply() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - UID: $1 - To: $2" >> reply_history.log
}

# 在回复脚本中添加日志
node reply_email.js $uid --body "$reply" && log_reply $uid $recipient
```

## 🚨 注意事项

### 安全建议
1. **不要自动回复所有邮件** - 避免回复垃圾邮件
2. **检查发件人** - 确认是可信的发件人
3. **避免信息泄露** - 不要在自动回复中包含敏感信息
4. **设置回复频率限制** - 避免被标记为垃圾邮件

### 最佳实践
1. **先测试后使用** - 先用测试邮箱验证
2. **保留原邮件上下文** - 使用 `--include-original`
3. **个性化回复** - 尽量个性化，避免完全模板化
4. **及时标记已读** - 回复后标记原邮件为已读

## 📞 故障排除

### 常见问题
```bash
# 问题: 回复失败
# 解决: 检查SMTP配置
node scripts/smtp.js test

# 问题: 找不到邮件
# 解决: 确认邮件UID
node scripts/imap.js check --limit 20

# 问题: 回复内容格式错误
# 解决: 转义特殊字符
node reply_email.js 123 --body "回复内容\"带引号\"需要转义"
```

### 调试模式
```bash
# 启用详细日志
DEBUG=* node reply_email.js 123 --body "测试"
```

现在你可以轻松地回复邮件了！ 🎉