# Stock Analysis 技能使用指南

## 技能状态
✅ **已安装** - Stock Analysis 技能已经成功安装并可用

## 安装位置
- 技能路径: `/root/.agents/skills/stock-analysis`
- 已链接到: OpenClaw 代理

## 主要功能

### 1. 股票分析
分析美国股票，支持8个分析维度：
- 基本面分析
- 技术分析
- 估值指标
- 市场情绪
- 风险分析
- 行业对比
- 收益预测
- 投资建议

### 2. 加密货币分析
分析前20大加密货币（按市值）：
- 市场分类（大/中/小盘）
- 类别（智能合约L1、DeFi、支付等）
- BTC相关性（30天）
- 动量指标（RSI、价格区间）
- 市场环境（VIX、整体市场状况）

### 3. 投资组合管理
- 创建和管理投资组合
- 添加/删除资产
- 定期性能报告（每日/每周/每月/每季度/每年）

## 基本用法示例

### 分析单个股票：
```bash
cd /root/.agents/skills/stock-analysis
uv run scripts/analyze_stock.py AAPL
```

### 分析多个股票：
```bash
uv run scripts/analyze_stock.py AAPL MSFT GOOGL
```

### 分析加密货币：
```bash
uv run scripts/analyze_stock.py BTC-USD
uv run scripts/analyze_stock.py ETH-USD SOL-USD
```

### JSON输出格式：
```bash
uv run scripts/analyze_stock.py AAPL --output json
```

## 支持的加密货币
BTC-USD, ETH-USD, BNB-USD, SOL-USD, XRP-USD, ADA-USD, DOGE-USD, AVAX-USD, DOT-USD, MATIC-USD, LINK-USD, ATOM-USD, UNI-USD, LTC-USD, BCH-USD, XLM-USD, ALGO-USD, VET-USD, FIL-USD, NEAR-USD

## 注意事项
1. 只传递股票代码作为参数，不要添加额外文本
2. 确保已安装 `uv` 工具（Python包管理器）
3. 技能使用 Yahoo Finance 数据，需要网络连接

## 测试安装
技能已通过测试并显示在全局技能列表中：
```
npx skills list -g
```

技能名称: `stock-analysis`
安装状态: ✅ 已链接到 OpenClaw 代理