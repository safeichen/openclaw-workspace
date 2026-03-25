# 学习记录

记录纠正、知识差距和最佳实践。

## 格式说明

每个学习条目应包含：
- **ID**: LRN-YYYYMMDD-XXX
- **类别**: correction | knowledge_gap | best_practice
- **优先级**: low | medium | high | critical
- **状态**: pending | in_progress | resolved | promoted
- **领域**: frontend | backend | infra | tests | docs | config
- **摘要**: 一行描述
- **详情**: 完整上下文
- **建议行动**: 具体的修复或改进
- **元数据**: 来源、相关文件、标签等

---

## [LRN-20260325-001] skill_installation

**记录时间**: 2026-03-25T13:06:00Z
**优先级**: medium
**状态**: resolved
**领域**: config

### 摘要
成功安装 self-improving-agent 技能

### 详情
用户请求安装 self-improving-agent 技能。检查发现该技能已经安装在 `/root/.openclaw/workspace/skills/self-improving-agent/` 目录中。技能功能完整，包括错误记录、用户纠正捕获、功能请求跟踪等功能。

### 建议行动
1. 确保 `.learnings/` 目录存在并包含必要的模板文件
2. 在适当的时候触发技能记录功能
3. 定期审查学习记录以改进性能

### 元数据
- 来源: user_request
- 相关文件: /root/.openclaw/workspace/skills/self-improving-agent/SKILL.md
- 标签: skill_installation, self_improvement
- 模式键: skill.installation.verification

---

## [LRN-20260325-002] reminder_setup

**记录时间**: 2026-03-25T13:15:00Z
**优先级**: medium
**状态**: pending
**领域**: config

### 摘要
为用户设置学校选餐提醒

### 详情
用户请求在2026年3月25日晚上8点（北京时间20:00）提醒学校选餐。创建了以下设置：
1. 主提醒脚本：`school-meal-reminder.sh`
2. 一次性执行脚本：`one-time-school-meal-reminder.sh`
3. Cron任务：2026年3月25日UTC时间12:00执行
4. 系统集成：更新了HEARTBEAT.md和check-email-notifications.sh
5. 备用方案：如果WeChat发送失败，输出格式供主会话处理

### 建议行动
1. 在20:00（北京时间）检查提醒是否成功发送
2. 如果发送失败，通过主会话手动发送
3. 提醒执行后，验证cron任务是否已自动删除

### 元数据
- 来源: user_request
- 相关文件: /root/.openclaw/workspace/school-meal-reminder.sh
- 标签: reminder, scheduling, wechat
- 模式键: reminder.one_time.setup

---

## [LRN-20260325-003] reminder_execution

**记录时间**: 2026-03-25T20:00:00Z
**优先级**: medium
**状态**: partially_resolved
**领域**: config

### 摘要
学校选餐提醒已执行但微信发送失败

### 详情
学校选餐提醒在UTC时间12:00（北京时间20:00）按计划执行。一次性脚本成功运行并输出了提醒内容，但发送到微信时失败，错误信息为"contextToken is required"。脚本已自动从crontab中删除一次性任务。

### 建议行动
1. 解决WeChat通道的认证问题（contextToken配置）
2. 对于重要提醒，考虑使用备用通知渠道
3. 在WeChat认证问题解决前，手动发送重要提醒

### 元数据
- 来源: system_execution
- 相关文件: /root/.openclaw/workspace/school-meal-reminder.sh
- 标签: reminder, wechat, authentication
- 模式键: reminder.wechat.authentication.issue
- 参见链接: LRN-20260325-002

---

