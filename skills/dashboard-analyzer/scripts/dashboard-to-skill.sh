#!/bin/bash
# dashboard-to-skill.sh - 看板扫描 + 自动生成 Skill 文件
# 用法: bash scripts/dashboard-to-skill.sh <URL> [看板名称] [输出目录]

set -e

URL="$1"
DASHBOARD_NAME="${2:-dashboard_skill}"
OUTPUT_DIR="${3:-./generated_skills}"

if [ -z "$URL" ]; then
  echo "❌ 用法: bash scripts/dashboard-to-skill.sh <看板URL> [看板名称] [输出目录]"
  echo ""
  echo "示例:"
  echo "  bash scripts/dashboard-to-skill.sh https://metabase.internal/dash/42 dau-analysis ./my-skills"
  exit 1
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SCAN_DIR="/tmp/dashboard_scan_$TIMESTAMP"
SKILL_DIR="$OUTPUT_DIR/$DASHBOARD_NAME"

mkdir -p "$SCAN_DIR" "$SKILL_DIR"

echo "============================================"
echo "  📊 看板 → Skill 转换工具"
echo "  看板URL: $URL"
echo "  Skill名: $DASHBOARD_NAME"
echo "  输出: $SKILL_DIR"
echo "============================================"

# Step 1: 扫描页面
echo ""
echo "🔍 [1/4] 扫描看板页面..."

agent-browser set viewport 1920 1080
agent-browser open "$URL"
agent-browser wait --load networkidle 2>/dev/null || agent-browser wait 5000

# 截图
agent-browser screenshot --full "$SCAN_DIR/screenshot.png"
echo "  ✅ 截图完成"

# 获取页面文本内容
agent-browser eval "
const el = document.querySelector('body');
if (el) console.log(el.innerText.substring(0, 10000));
" 2>&1 | head -300 > "$SCAN_DIR/page_text.txt" || true

# 获取页面标题
agent-browser get title 2>/dev/null > "$SCAN_DIR/title.txt" || true

# 获取交互元素
agent-browser snapshot -i 2>/dev/null > "$SCAN_DIR/interactive.txt" || true

echo "  ✅ 页面扫描完成"

# Step 2: 提取筛选器
echo ""
echo "🎛️ [2/4] 提取筛选条件..."

FILTERS_OUTPUT=""

# 检测下拉框
agent-browser eval "
const filters = [];
document.querySelectorAll('select, [role=\"combobox\"], [role=\"listbox\"], .ant-select, .el-select, .filter-item, [class*=\"filter\"]').forEach(el => {
  const label = el.labels?.[0]?.textContent?.trim() || el.getAttribute('aria-label')?.trim() || el.getAttribute('placeholder')?.trim() || el.id || el.className;
  const options = Array.from(el.querySelectorAll('option, [role=\"option\"]')).map(o => o.textContent?.trim() || o.getAttribute('value')).filter(Boolean);
  filters.push({type: 'select', label, options, tag: el.tagName});
});

// 日期选择器
document.querySelectorAll('[type=\"date\"], [type=\"datetime\"], [placeholder*=\"日期\"], [placeholder*=\"时间\"], .ant-picker, .el-date-editor, .date-picker').forEach(el => {
  const label = el.labels?.[0]?.textContent?.trim() || el.getAttribute('aria-label')?.trim() || el.placeholder?.trim() || el.id;
  filters.push({type: 'date', label, tag: el.tagName});
});

// 输入框
document.querySelectorAll('input[type=\"text\"], input:not([type]), [contenteditable]').forEach(el => {
  const label = el.labels?.[0]?.textContent?.trim() || el.getAttribute('aria-label')?.trim() || el.placeholder?.trim() || el.id;
  if (label && !label.includes('search') && !label.includes('搜索')) {
    filters.push({type: 'text', label, tag: el.tagName});
  }
});

console.log(JSON.stringify(filters, null, 2));
" 2>&1 | grep -A999 '^\[' > "$SCAN_DIR/filters.json" 2>/dev/null || echo '[]' > "$SCAN_DIR/filters.json"

echo "  ✅ 筛选条件已提取"

# Step 3: 提取图表
echo ""
echo "📈 [3/4] 提取图表信息..."

agent-browser eval "
const charts = [];

// 扫描所有可能包含图表的容器
document.querySelectorAll('div[class], section[class]').forEach(el => {
  const rect = el.getBoundingClientRect();
  if (rect.width < 200 || rect.height < 100) return;

  // 找标题
  const titleEl = el.querySelector('h1, h2, h3, h4, h5, .title, .card-title, .panel-title, .chart-title, .widget-title');
  const title = titleEl?.textContent?.trim() || '';

  // 找 canvas (ECharts 等)
  const canvases = el.querySelectorAll('canvas');
  const svgs = el.querySelectorAll('svg');
  const tables = el.querySelectorAll('table');

  if (canvases.length > 0 || (svgs.length > 0 && svgs.length < 20)) {
    // 尝试获取图表的数据
    if (title) charts.push({title, type: canvases.length > 0 ? 'canvas_chart' : 'svg_chart', rect: {w: rect.width, h: rect.height}});

    // 从周围的文本猜测图表类型
    const text = el.textContent?.substring(0, 500) || '';
    if (text.includes('趋势') || text.includes('趋势图') || text.includes('折线')) charts[charts.length-1].guess_type = 'line';
    if (text.includes('占比') || text.includes('比例') || text.includes('饼图') || text.includes('环形')) charts[charts.length-1].guess_type = 'pie';
    if (text.includes('柱状') || text.includes('柱形') || text.includes('对比')) charts[charts.length-1].guess_type = 'bar';
    if (text.includes('表格') || text.includes('明细')) charts[charts.length-1].guess_type = 'table';
    if (text.includes('排行')) charts[charts.length-1].guess_type = 'ranking';
  }
});

// 提取表格数据作为可能的维度/指标
const tables = document.querySelectorAll('table');
tables.forEach((table, i) => {
  const headers = Array.from(table.querySelectorAll('th')).map(h => h.textContent?.trim()).filter(Boolean);
  const rows = Array.from(table.querySelectorAll('tr')).slice(0, 5).map(r =>
    Array.from(r.querySelectorAll('td')).map(d => d.textContent?.trim())
  );
  if (headers.length > 0) {
    charts.push({title: '数据表格 ' + (i+1), type: 'data_table', headers, sample: rows.filter(r => r.length > 0).slice(0,3)});
  }
});

console.log(JSON.stringify(charts, null, 2));
" 2>&1 | grep -A999 '^\[' > "$SCAN_DIR/charts.json" 2>/dev/null || echo '[]' > "$SCAN_DIR/charts.json"

echo "  ✅ 图表信息已提取"

# Step 4: 捕获网络请求
echo ""
echo "🌐 [4/4] 捕获数据 API..."

agent-browser eval "
const entries = performance.getEntriesByType('resource');
const apis = [];
entries.forEach(entry => {
  const url = entry.name;
  if (entry.initiatorType === 'fetch' || entry.initiatorType === 'xmlhttprequest' || 
      url.includes('api') || url.includes('/v1/') || url.includes('/v2/') ||
      url.includes('graphql') || url.includes('query') || url.includes('data') || 
      url.endsWith('.json') || url.includes('datasource') || url.includes('dashboard')) {
    try {
      const parsed = new URL(url);
      apis.push({
        url: parsed.origin + parsed.pathname,
        params: parsed.searchParams.toString(),
        duration: Math.round(entry.duration) + 'ms'
      });
    } catch(e) {}
  }
});
console.log(JSON.stringify(apis, null, 2));
" 2>&1 | grep -A999 '^\[' > "$SCAN_DIR/apis.json" 2>/dev/null || echo '[]' > "$SCAN_DIR/apis.json"

echo "  ✅ 网络请求已捕获"

agent-browser close 2>/dev/null || true

# 生成汇总
echo ""
echo "📝 生成看板概览..."
echo ""

PAGE_TITLE=$(cat "$SCAN_DIR/title.txt" 2>/dev/null || echo "$DASHBOARD_NAME")

echo "页面标题: $PAGE_TITLE"
echo ""

# 显示筛选器
echo "--- 筛选条件 ---"
if [ -f "$SCAN_DIR/filters.json" ]; then
  cat "$SCAN_DIR/filters.json" | python3 -c "
import json, sys
try:
  data = json.load(sys.stdin)
  if data:
    for f in data:
      label = f.get('label', '?')
      ftype = f.get('type', '?')
      options = f.get('options', [])
      if options:
        print(f'  [{ftype}] {label} = {options[:8]}')
      else:
        print(f'  [{ftype}] {label}')
  else:
    print('  (自动识别未命中，需人工确认)')
except:
  print('  (解析失败)')
" 2>/dev/null || echo "  (请查看 $SCAN_DIR/filters.json)"
fi

echo ""
echo "--- 图表 ---"
if [ -f "$SCAN_DIR/charts.json" ]; then
  cat "$SCAN_DIR/charts.json" | python3 -c "
import json, sys
try:
  data = json.load(sys.stdin)
  if data:
    for c in data:
      title = c.get('title', '?')
      ctype = c.get('type', c.get('guess_type', '?'))
      headers = c.get('headers', [])
      if headers:
        print(f'  [{ctype}] {title} → 字段: {headers}')
      else:
        print(f'  [{ctype}] {title}')
  else:
    print('  (未识别到图表)')
except:
  print('  (解析失败)')
" 2>/dev/null || echo "  (请查看 $SCAN_DIR/charts.json)"
fi

echo ""
echo "--- 数据 API ---"
if [ -f "$SCAN_DIR/apis.json" ]; then
  cat "$SCAN_DIR/apis.json" | python3 -c "
import json, sys
try:
  data = json.load(sys.stdin)
  if data:
    for a in data[:5]:
      print(f'  {a.get(\"url\",\"?\")}')
      if a.get('params'): print(f'    参数: {a[\"params\"]}')
  else:
    print('  (未捕获到数据 API)')
except:
  print('  (解析失败)')
" 2>/dev/null || echo "  (请查看 $SCAN_DIR/apis.json)"
fi

# 生成 SKILL.md
echo ""
echo "📄 生成 Skill 文件..."
echo ""

# 从扫描结果提取信息来填充 skill 模板
FILTER_PARAMS=""
if [ -f "$SCAN_DIR/filters.json" ]; then
  FILTER_PARAMS=$(python3 -c "
import json
try:
  with open('$SCAN_DIR/filters.json') as f:
    data = json.load(f)
  params = []
  for f in data:
    label = f.get('label', 'param')
    ftype = f.get('type', 'string')
    options = f.get('options', [])
    if ftype == 'date':
      params.append({'name': label, 'type': 'string', 'description': f'{label} 日期筛选', 'required': False})
    elif options:
      params.append({'name': label, 'type': 'string', 'enum': options[:10], 'description': f'{label} 筛选', 'required': False})
    else:
      params.append({'name': label, 'type': 'string', 'description': f'{label} 筛选', 'required': False})
  print(json.dumps(params, ensure_ascii=False))
except:
  print('[]')
" 2>/dev/null || echo '[]')
fi

CHART_INFO=""
if [ -f "$SCAN_DIR/charts.json" ]; then
  CHART_INFO=$(python3 -c "
import json
try:
  with open('$SCAN_DIR/charts.json') as f:
    data = json.load(f)
  lines = []
  for c in data:
    title = c.get('title', '')
    ctype = c.get('type', c.get('guess_type', 'chart'))
    headers = c.get('headers', [])
    sample = c.get('sample', [])
    if headers:
      lines.append(f\"  - **{title}** ({ctype}): {', '.join(headers)}\")
    else:
      lines.append(f\"  - **{title}** ({ctype})\")
  if not lines:
    lines.append('  - (自动识别未命中，需人工确认)')
  print('\n'.join(lines))
except:
  print('  - (解析失败)')
" 2>/dev/null || echo '  - (解析失败)')
fi

# 生成 SKILL.md
cat > "$SKILL_DIR/SKILL.md" << SKILLEOF
---
name: $DASHBOARD_NAME
description: 看板「$PAGE_TITLE」的数据查询 Skill，支持按条件筛选并返回结构化数据。
read_when:
  - 查询 $PAGE_TITLE 相关的数据
  - 需要 $DASHBOARD_NAME 的统计分析结果
metadata:
  emoji: 📊
  dashboard_url: $URL
  scan_time: $(date '+%Y-%m-%d %H:%M:%S')
---

# $DASHBOARD_NAME - $PAGE_TITLE

## 功能说明

查询看板「$PAGE_TITLE」的数据。支持按条件筛选，返回结构化的图表数据。

## 筛选参数

$(python3 -c "
import json
params = json.loads('$FILTER_PARAMS')
if params:
  for p in params:
    name = p.get('name', '?')
    ptype = p.get('type', 'string')
    desc = p.get('description', '')
    required = p.get('required', False)
    enum = p.get('enum', [])
    req_str = '必填' if required else '可选'
    if enum:
      print(f'- **{name}** ({ptype}, {req_str}): {desc}，可选值: {chr(10)+chr(10)}  '.join(enum[:10]))
    else:
      print(f'- **{name}** ({ptype}, {req_str}): {desc}')
else:
  print('（扫描未自动识别到筛选参数，请补充确认）')
" 2>/dev/null)

## 数据输出

扫描到以下数据内容：

$CHART_INFO

> ⚠️ 以上信息由自动扫描生成，建议人工核对确认。
> 确认后补充 SQL 查询逻辑即可使用。

## 使用示例

\`\`\`
openclaw run $DASHBOARD_NAME --time_range last_7d
openclaw run $DASHBOARD_NAME --region 华东 --time_range 2026-01-01~2026-03-01
\`\`\`
SKILLEOF

echo "  ✅ SKILL.md 已生成 → $SKILL_DIR/SKILL.md"

# 生成可执行的查询脚本模板
cat > "$SKILL_DIR/scripts/query.py" << 'PYEOF'
#!/usr/bin/env python3
"""
数据查询脚本模板
从看板扫描结果自动生成，需要补充实际的 SQL 逻辑
"""
import json
import sys

def query_dashboard(params):
    """
    查询看板数据
    
    参数说明（从看板扫描结果提取，请根据实际情况调整）：
    - time_range: 时间范围
    - region: 地区筛选
    """
    
    # TODO: 替换为实际的 SQL 查询逻辑
    # 示例：
    # conn = get_db_connection()
    # sql = "SELECT ... WHERE date BETWEEN %(start)s AND %(end)s"
    # result = conn.query(sql, params)
    
    result = {
        "status": "pending",
        "message": "请补充实际的 SQL 查询逻辑",
        "params": params
    }
    
    return result

if __name__ == "__main__":
    # 从命令行参数解析
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--time_range", help="时间范围")
    parser.add_argument("--region", help="地区")
    args = parser.parse_args()
    
    params = {k: v for k, v in vars(args).items() if v is not None}
    result = query_dashboard(params)
    print(json.dumps(result, ensure_ascii=False, indent=2))
PYEOF

chmod +x "$SKILL_DIR/scripts/query.py" 2>/dev/null || true

mkdir -p "$SKILL_DIR/scripts"

echo "  ✅ 查询脚本模板已生成 → $SKILL_DIR/scripts/query.py"

# 保存扫描原始数据
cp "$SCAN_DIR"/*.json "$SKILL_DIR/" 2>/dev/null || true
cp "$SCAN_DIR"/*.txt "$SKILL_DIR/" 2>/dev/null || true

# 输出汇总
echo ""
echo "============================================"
echo "  ✅ 转换完成！"
echo ""
echo "  生成的 Skill 位置:"
echo "    $SKILL_DIR/"
echo ""
echo "  文件结构:"
echo "    SKILL.md          - Skill 描述定义"
echo "    scripts/query.py  - 数据查询脚本（需补充 SQL）"
echo "    filters.json      - 扫描到的筛选条件"
echo "    charts.json       - 扫描到的图表信息"
echo "    apis.json         - 捕获的数据 API"
echo "    screenshot.png    - 看板截图"
echo ""
echo "  下一步:"
echo "    1. 检查 SKILL.md 中的参数和输出是否正确"
echo "    2. 补充 scripts/query.py 中的 SQL 查询"
echo "    3. 将 $SKILL_DIR 放在 OpenClaw skills 目录下即可使用"
echo "============================================"
