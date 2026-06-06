#!/bin/bash
# dashboard-scan.sh - 看板扫描工具（精简版）
# 只提取：筛选参数 + 图表及维度指标
# SQL 留空你自己填
# 用法: bash dashboard-scan.sh <看板URL> [看板名称]

set -e

URL="$1"
SKILL_NAME="${2:-my_dashboard}"
OUTPUT_DIR="./skills/$SKILL_NAME"

if [ -z "$URL" ]; then
  echo "❌ 用法: bash dashboard-scan.sh <看板URL> [看板名称]"
  echo "  示例: bash dashboard-scan.sh https://metabase.internal/dash/42 dau-dashboard"
  exit 1
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TMPDIR="/tmp/dash_scan_$TIMESTAMP"
mkdir -p "$TMPDIR" "$OUTPUT_DIR/scripts"

echo "========================================"
echo " 📊 看板扫描工具"
echo " URL: $URL"
echo " 输出: $OUTPUT_DIR"
echo "========================================"

# 1. 打开页面
echo ""
echo "[1/4] 打开看板..."
agent-browser set viewport 1920 1080 2>/dev/null
agent-browser open "$URL"
agent-browser wait --load networkidle 2>/dev/null || agent-browser wait 5000

# 截图（备查）
agent-browser screenshot --full "$TMPDIR/screenshot.png" 2>/dev/null
echo "  ✅ 页面已加载"

# 2. 提取筛选参数
echo ""
echo "[2/4] 提取筛选条件..."

cat > "$TMPDIR/extract_filters.js" << 'JSEOF'
// 提取页面上所有筛选器控件
const filters = [];

// 下拉框
document.querySelectorAll('select, [role="combobox"], [role="listbox"], .ant-select, .el-select').forEach(el => {
  const label = el.labels?.[0]?.textContent?.trim() 
    || el.getAttribute('aria-label')?.trim() 
    || el.getAttribute('placeholder')?.trim()
    || el.id || el.className;
  const opts = Array.from(el.querySelectorAll('option, [role="option"]')).map(o => o.textContent?.trim() || o.value).filter(Boolean);
  filters.push({类型: "下拉选择", 名称: label, 可选值: opts.slice(0,20)});
});

// 日期选择
document.querySelectorAll('[type="date"], [type="datetime"], .ant-picker, .el-date-editor').forEach(el => {
  const label = el.labels?.[0]?.textContent?.trim() || el.getAttribute('aria-label')?.trim() || el.placeholder?.trim() || el.id;
  filters.push({类型: "日期选择", 名称: label || "日期范围", 可选值: []});
});

// 输入框
document.querySelectorAll('input[type="text"], input:not([type]):not([type="hidden"])').forEach(el => {
  const label = el.labels?.[0]?.textContent?.trim() || el.placeholder?.trim() || el.getAttribute('aria-label')?.trim();
  if (label && !label.toLowerCase().includes('search') && label.length > 1) {
    filters.push({类型: "文本输入", 名称: label, 可选值: []});
  }
});

// 按钮组
document.querySelectorAll('[role="tab"], [role="radio"], .btn-group button, .ant-radio-button-wrapper').forEach(el => {
  const text = el.textContent?.trim();
  const parent = el.closest('[class*="filter"], [class*="toolbar"], [class*="header"]') || el.parentElement;
  const groupName = parent?.getAttribute('aria-label') || parent?.querySelector('label, .label')?.textContent?.trim() || '筛选组';
  if (text && text.length < 20) {
    filters.push({类型: "选项按钮", 名称: groupName, 可选值: [text]});
  }
});
// 去重合并同组选项
const merged = {};
filters.forEach(f => {
  const key = f.名称;
  if (!merged[key]) {
    merged[key] = f;
  } else if (f.可选值.length > 0) {
    const existing = new Set(merged[key].可选值);
    f.可选值.forEach(v => existing.add(v));
    merged[key].可选值 = [...existing];
  }
});
console.log(JSON.stringify(Object.values(merged), null, 2));
JSEOF

agent-browser eval "$(cat $TMPDIR/extract_filters.js)" 2>&1 | grep -A999 '^\[' > "$TMPDIR/filters.json" 2>/dev/null || echo '[]' > "$TMPDIR/filters.json"

echo "  ✅ 筛选条件提取完成"

# 3. 提取图表清单
echo ""
echo "[3/4] 提取图表和维度指标..."

cat > "$TMPDIR/extract_charts.js" << 'JSEOF'
const charts = [];

// 查找图表卡片/容器
const cardSelectors = [
  '.card', '.panel', '.widget', '[class*="card"]', '[class*="panel"]', 
  '[class*="widget"]', '[class*="chart"]', '[class*="dashboard-item"]',
  '[class*="grid-item"]', 'section', 'article'
];

document.querySelectorAll(cardSelectors.join(',')).forEach(el => {
  const rect = el.getBoundingClientRect();
  if (rect.width < 180 || rect.height < 80) return;
  
  // 找标题
  const titleEl = el.querySelector('h1, h2, h3, h4, h5, .title, .card-title, .chart-title, [class*="title"]');
  const title = titleEl?.textContent?.trim() || '';
  if (!title) return;
  
  // 检测图表类型
  let chartType = '未知';
  const innerHTML = el.innerHTML.toLowerCase();
  const innerText = el.textContent || '';
  
  if (el.querySelector('canvas')) chartType = '图表(canvas)';
  else if (el.querySelector('svg')) {
    const svgs = el.querySelectorAll('svg');
    const texts = el.querySelectorAll('text');
    if (svgs.length <= 3 && texts.length > 5) chartType = '图表(svg)';
    else chartType = '图表元素';
  }
  else if (el.querySelector('table, .table, [class*="table"]')) chartType = '数据表格';
  else if (innerText.length > 50 && innerText.length < 500) chartType = '指标卡片(KPI)';
  
  // 提取维度和指标（从表头和上下文）
  let dimensions = [];
  let metrics = [];
  
  // 从表头中提取
  el.querySelectorAll('th, [class*="header"], [class*="label"], .axis-label, [class*="legend"]').forEach(h => {
    const text = h.textContent?.trim();
    if (text && text.length < 30) {
      // 判断是维度还是指标
      if (/日期|时间|地区|城市|省份|渠道|来源|品类|类型|分类|部门|产品|用户|性别|年龄/.test(text)) {
        dimensions.push(text);
      } else if (/数|率|额|比|量|值|占比|增速|环比|同比|DAU|MAU|GMV|UV|PV|ARPU/.test(text)) {
        metrics.push(text);
      } else {
        metrics.push(text); // 默认当指标
      }
    }
  });
  
  // 如果表头没提取到，从图表周围文本中猜
  if (dimensions.length === 0 && metrics.length === 0) {
    const lines = innerText.split('\n').map(l => l.trim()).filter(l => l.length < 20 && l.length > 1);
    lines.forEach(text => {
      if (/日期|时间|地区|城市|省份|渠道|来源|品类|类型|分类|部门|产品/.test(text)) dimensions.push(text);
      else if (/数|率|额|比|量|值|占比|增速|环比|同比|DAU|MAU|GMV|UV|PV/.test(text)) metrics.push(text);
    });
  }
  
  // 去重
  dimensions = [...new Set(dimensions)];
  metrics = [...new Set(metrics)];
  
  charts.push({
    图表名: title,
    类型: chartType,
    维度: dimensions.length > 0 ? dimensions : ['(待确认)'],
    指标: metrics.length > 0 ? metrics : ['(待确认)'],
    尺寸: `${Math.round(rect.w)}x${Math.round(rect.h)}`
  });
});

// 如果没找到图表卡片，直接找 canvas/svg 容器的父级
if (charts.length === 0) {
  document.querySelectorAll('canvas, svg').forEach(el => {
    const rect = el.getBoundingClientRect();
    if (rect.width < 100) return;
    const parent = el.closest('div') || el.parentElement;
    const title = parent?.querySelector('h1,h2,h3,h4')?.textContent?.trim() 
      || parent?.getAttribute('title') 
      || `图表 ${charts.length + 1}`;
    const type = el.tagName === 'CANVAS' ? '图表(canvas)' : '图表(svg)';
    charts.push({
      图表名: title,
      类型: type,
      维度: ['(待确认)'],
      指标: ['(待确认)'],
      尺寸: `${Math.round(rect.w)}x${Math.round(rect.h)}`
    });
  });
}

console.log(JSON.stringify(charts, null, 2));
JSEOF

agent-browser eval "$(cat $TMPDIR/extract_charts.js)" 2>&1 | grep -A999 '^\[' > "$TMPDIR/charts.json" 2>/dev/null || echo '[]' > "$TMPDIR/charts.json"

echo "  ✅ 图表提取完成"

# 4. 关闭浏览器
agent-browser close 2>/dev/null || true

# 5. 生成 Skill 文件
echo ""
echo "[4/4] 生成 SKILL.md..."

# 美化输出展示
echo ""
echo "========================================"
echo " 📋 扫描结果"
echo "========================================"

echo ""
echo "🎛️ 筛选条件:"
python3 -c "
import json
with open('$TMPDIR/filters.json') as f:
    data = json.load(f)
if data:
    for i, flt in enumerate(data, 1):
        name = flt.get('名称', '?')
        ftype = flt.get('类型', '?')
        opts = flt.get('可选值', [])
        if opts:
            opt_str = ', '.join(opts[:8])
            if len(opts) > 8: opt_str += '...'
            print(f'  {i}. [{ftype}] {name} = {opt_str}')
        else:
            print(f'  {i}. [{ftype}] {name}')
else:
    print('  (未自动识别到筛选条件，请手动补充)')
" 2>/dev/null

echo ""
echo "📈 图表清单:"
python3 -c "
import json
with open('$TMPDIR/charts.json') as f:
    data = json.load(f)
if data:
    for i, c in enumerate(data, 1):
        name = c.get('图表名', '?')
        ctype = c.get('类型', '?')
        dims = ', '.join(c.get('维度', []))
        mets = ', '.join(c.get('指标', []))
        print(f'  {i}. [{ctype}] {name}')
        print(f'     维度: {dims}')
        print(f'     指标: {mets}')
else:
    print('  (未识别到图表，请手动补充)')
" 2>/dev/null

# 提取参数名用于 skill 描述
PARAMS_DESC=""
python3 -c "
import json
with open('$TMPDIR/filters.json') as f:
    data = json.load(f)
if data:
    for flt in data:
        name = flt.get('名称', '参数')
        ftype = flt.get('类型', 'string')
        opts = flt.get('可选值', [])
        if opts:
            print(f'- **{name}** (可选): 筛选条件，可选值: {json.dumps(opts[:10], ensure_ascii=False)}')
        else:
            print(f'- **{name}** (可选): 筛选条件')
else:
    print('（请补充筛选参数说明）')
" 2>/dev/null > "$TMPDIR/params_desc.txt"

CHARTS_DESC=""
python3 -c "
import json
with open('$TMPDIR/charts.json') as f:
    data = json.load(f)
if data:
    for c in data:
        name = c.get('图表名', '?')
        dims = ', '.join(c.get('维度', []))
        mets = ', '.join(c.get('指标', []))
        print(f'- **{name}**: 维度=[{dims}], 指标=[{mets}]')
else:
    print('- （请补充图表信息）')
" 2>/dev/null > "$TMPDIR/charts_desc.txt"

# 生成 SKILL.md
# 生成分析型 SKILL.md —— 服务"取数+分析"目的
##
# 从扫描结果提取维度和指标汇总（去重合并）
python3 -c "
import json

with open('$TMPDIR/charts.json') as f:
    charts = json.load(f)

with open('$TMPDIR/filters.json') as f:
    filters = json.load(f)

all_dims = set()
all_metrics = set()
chart_list = []

for c in charts:
    name = c.get('图表名', '?')
    dims = c.get('维度', [])
    mets = c.get('指标', [])
    ctype = c.get('类型', '?')
    for d in dims:
        if d != '(待确认)': all_dims.add(d)
    for m in mets:
        if m != '(待确认)': all_metrics.add(m)
    chart_list.append({
        'name': name,
        'type': ctype,
        'dimensions': [d for d in dims if d != '(待确认)'],
        'metrics': [m for m in mets if m != '(待确认)']
    })

# 参数列表
param_list = []
for f in filters:
    name = f.get('名称', '参数')
    ftype = f.get('类型', 'string')
    opts = f.get('可选值', [])
    param_list.append({
        'name': name,
        'type': ftype,
        'options': opts[:10]
    })

output = {
    'dimensions': sorted(all_dims) if all_dims else ['(待确认)'],
    'metrics': sorted(all_metrics) if all_metrics else ['(待确认)'],
    'charts': chart_list,
    'params': param_list
}

with open('$TMPDIR/skill_data.json', 'w') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(json.dumps(output, ensure_ascii=False, indent=2))
" 2>/dev/null > "$TMPDIR/skill_data_pretty.txt"

# 从 skill_data.json 读取数据生成 Markdown
python3 -c "
import json

with open('$TMPDIR/skill_data.json') as f:
    data = json.load(f)

dims = data.get('dimensions', [])
mets = data.get('metrics', [])
charts = data.get('charts', [])
params = data.get('params', [])

# 参数部分
param_lines = []
for p in params:
    name = p.get('name', '参数')
    opts = p.get('options', [])
    if opts:
        opts_str = ', '.join(str(o) for o in opts)
        param_lines.append(f'- **{name}** (可选): 可选值 {opts_str}')
    else:
        param_lines.append(f'- **{name}** (可选)')

# 分析能力描述（基于维度和指标自动生成）
analysis_capabilities = []
if any('日期' in d or '时间' in d for d in dims):
    analysis_capabilities.append('- 📈 **趋势分析**: 基于时间维度的变化趋势')
if any('地区' in d or '省份' in d or '城市' in d for d in dims):
    analysis_capabilities.append('- 🗺️ **地域分析**: 按地区维度的分布与对比')
if any('渠道' in d or '来源' in d for d in dims):
    analysis_capabilities.append('- 🔗 **渠道分析**: 不同渠道/来源的效果对比')
if any('品类' in d or '分类' in d or '类型' in d for d in dims):
    analysis_capabilities.append('- 🏷️ **分类分析**: 按品类/分类维度的结构分析')
analysis_capabilities.append('- 📊 **对比分析**: 支持多维度交叉对比')
analysis_capabilities.append('- 🎯 **异常发现**: 识别数据中的异常波动')

print('---')
print('name: $SKILL_NAME')
print('description: 查询并分析业务数据，支持多维度筛选和指标分析。')
print('read_when:')
print('  - 需要查询业务数据')
print('  - 需要分析数据趋势、对比、分布')
print('metadata:')
print('  emoji: 📊')
print('  dashboard_url: $URL')
print('  scan_time: $(date '+%Y-%m-%d %H:%M:%S')')
print('---')
print()
print(f'# $SKILL_NAME')
print()
print('## 📋 可查询的数据')
print()
print('### 维度')
for d in dims:
    print(f'- {d}')
print()
print('### 指标')
for m in mets:
    print(f'- {m}')
print()
print('### 筛选条件')
for line in param_lines:
    print(line)
print()
print('## 🔍 能做的分析')
for cap in analysis_capabilities:
    print(cap)
print()
print('## 📊 包含的图表')
for c in charts:
    name = c.get('name', '?')
    ctype = c.get('type', '?')
    cdims = c.get('dimensions', [])
    cmets = c.get('metrics', [])
    dim_str = ', '.join(cdims) if cdims else '(待确认)'
    met_str = ', '.join(cmets) if cmets else '(待确认)'
    print(f'- **[{ctype}] {name}**')
    print(f'  - 维度: {dim_str}')
    print(f'  - 指标: {met_str}')
print()
print('## 💬 提问示例')
sample_questions = []
if any('日期' in d for d in dims):
    if mets:
        sample_questions.append(f'- \"{mets[0]}最近7天的趋势怎么样？\"')
        if len(mets) > 1:
            sample_questions.append(f'- \"{mets[0]}和{mets[1]}的对比趋势\"')
if any('地区' in d for d in dims):
    if mets:
        sample_questions.append(f'- \"各地区的{mets[0]}排名\"')
if any('渠道' in d for d in dims):
    if mets:
        sample_questions.append(f'- \"哪个渠道的{mets[0]}最高？\"')
sample_questions.append('- \"有哪些异常波动需要关注？\"')
for q in sample_questions:
    print(q)
print()
print('## ⚙️ 数据查询')
print()
print('数据来自底表，SQL 逻辑请补充：')
print()
print('\`\`\`sql')
print('-- TODO: 补充实际的查询 SQL')
print('-- SELECT <维度>, <指标>')
print('-- FROM <底表>')
print('-- WHERE <筛选条件>')
print('\`\`\`')
" 2>/dev/null > "$OUTPUT_DIR/SKILL.md"

echo ""
echo "========================================"
echo " ✅ 扫描完成！"
echo ""
echo " Skill 文件: $OUTPUT_DIR/SKILL.md"
echo ""
echo " 下一步:"
echo "  1. 检查 SKILL.md 中的维度和指标是否正确"
echo "  2. 补充 SQL 查询逻辑"
echo "  3. 把 skills/$SKILL_NAME 放入 OpenClaw skills 目录"
echo "========================================"

echo ""
echo "========================================"
echo " ✅ 扫描完成！"
echo ""
echo " Skill 文件: $OUTPUT_DIR/SKILL.md"
echo ""
echo " 下一步:"
echo "  1. 检查 SKILL.md 中的参数和图表信息"
echo "  2. 补充 scripts/query.py 的 SQL 查询逻辑"
echo "  3. 把 skills/$SKILL_NAME 放入 OpenClaw skills 目录即可使用"
echo "========================================"
