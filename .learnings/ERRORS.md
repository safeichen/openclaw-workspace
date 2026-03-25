# 错误记录

记录命令失败、异常和意外行为。

## 格式说明

每个错误条目应包含：
- **ID**: ERR-YYYYMMDD-XXX
- **优先级**: high (错误通常设为高优先级)
- **状态**: pending | in_progress | resolved | wont_fix
- **领域**: frontend | backend | infra | tests | docs | config
- **摘要**: 简要描述失败情况
- **错误**: 实际错误消息或输出
- **上下文**: 尝试的命令/操作、输入参数、环境详情
- **建议修复**: 如果可识别，可能的解决方案
- **元数据**: 可重现性、相关文件、参见链接等

---

