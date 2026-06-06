---
name: dashboard-analyzer
description: 分析看板页面，自动提取筛选条件、图表类型、维度、指标，生成可用的 Skill 配置。
read_when:
  - 需要分析一个看板页面并生成对应的数据查询 Skill
  - 想把现有看板转化为 AI 可调用的数据工具
metadata:
  emoji: 📊
  requires:
    bins: [agent-browser, node]
---

# Dashboard Analyzer - 看板扫描转 Skill

自动扫描看板页面，提取结构化信息并生成对应的 Skill 文件。

## 使用方法

```bash
# 基本用法：扫描看板页面
openclaw run dashboard-analyzer --url "https://your-dashboard-url.com"

# 指定输出目录
openclaw run dashboard-analyzer --url "..." --output ./my-skills

# 附带额外页面分析信息
openclaw run dashboard-analyzer --url "..." --note "这个看板用的是 dau 底表"
```

## 输出

运行后会生成：

1. **扫描报告** - 页面上的筛选器、图表、维度、指标清单
2. **Skill 文件** - 可直接放入 OpenClaw skills 目录使用的完整 Skill
3. **SQL 模板** - 基于识别出的维度和指标生成的查询骨架

## 工作原理

使用 agent-browser 打开页面并执行以下扫描：

1. 截图 + AI 分析页面布局
2. 识别筛选器控件（下拉框、日期选择、输入框等）
3. 识别图表类型和其包含的维度/指标
4. 分析网络请求捕获数据 API
5. 生成结构化的 Skill 配置
