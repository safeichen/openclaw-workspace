# HEARTBEAT.md - 定期检查任务

## 邮件监控
- 每3小时检查一次新邮件
- 发现新邮件时通过ClawBot推送通知
- 检查脚本: /root/.openclaw/workspace/check-email-notifications.sh

## 检查逻辑
1. 运行邮件检查脚本
2. 如果检测到新邮件通知，通过ClawBot发送
3. 记录检查时间，避免重复通知

## 其他定期任务
- 检查系统状态
- 检查OpenClaw服务运行状态
- 检查重要更新
- 检查内存文件（确保每日memory/YYYY-MM-DD.md存在）

## 执行命令
当收到heartbeat时，运行:
```bash
/root/.openclaw/workspace/check-email-notifications.sh
```

## 内存文件检查逻辑
1. 检查今天的memory/YYYY-MM-DD.md文件是否存在
2. 如果不存在，创建基本的内存文件模板
3. 记录系统状态和重要事件
4. 如果连续多天缺失，创建补全文件

## 检查频率说明
- 邮件监控：每3小时检查一次
- 其他系统状态检查：每次heartbeat时都检查
- 内存文件检查：每天第一次heartbeat时检查
- 如果检测到新邮件，立即通过ClawBot通知

## 通知格式
如果发现新邮件，输出格式为:
```
[[EMAIL_NOTIFICATION]]
[邮件通知内容]
[[END_EMAIL_NOTIFICATION]]
```

如果发现早间新闻推送，输出格式为:
```
[[MORNING_NEWS_PUSH]]
[早间新闻内容]
[[END_MORNING_NEWS_PUSH]]
```

如果发现AI资讯提醒，输出格式为:
```
[[AI_NEWS_REMINDER]]
[AI资讯内容]
[[END_AI_NEWS_REMINDER]]
```

主会话需要捕获这些输出并通过相应渠道发送（邮件通知→ClawBot，早间新闻→微信，AI资讯→微信）。