# HEARTBEAT.md - 定期检查任务

## 邮件监控
- 每3小时检查一次新邮件
- 发现新邮件时通过QQ Bot推送通知
- 检查脚本: /root/.openclaw/workspace/check-email-notifications.sh

## 检查逻辑
1. 运行邮件检查脚本
2. 如果检测到新邮件通知，通过QQ Bot发送
3. 记录检查时间，避免重复通知

## 其他定期任务
- 检查系统状态
- 检查OpenClaw服务运行状态
- 检查重要更新

## 执行命令
当收到heartbeat时，运行:
```bash
/root/.openclaw/workspace/check-email-notifications.sh
```

## 检查频率说明
- 邮件监控：每3小时检查一次
- 其他系统状态检查：每次heartbeat时都检查
- 如果检测到新邮件，立即通过QQ Bot通知

## 通知格式
如果发现新邮件，输出格式为:
```
[[EMAIL_NOTIFICATION]]
[邮件通知内容]
[[END_EMAIL_NOTIFICATION]]
```

主会话需要捕获这个输出并通过QQ Bot发送。