# SQL 流水线 · 选表节点（优化版）

本节点**只**锁定 `db.table`，不拉字段、不拉分区、不写 SQL。

---

## 一、目标

锁定本次取数应使用的 `db.table`（最多 1 张主表），并把候选池写回。

---

## 二、工作步骤（按顺序）

### 步骤 1：内省用户原文是否已给出 `db.table`

- 用户原文里出现合法的 `db.table`（库名.表名，字母/数字/下划线）
- **检查语义匹配**：表名是否与用户描述的需求语义一致（如用户说"取订单数据"，给出的表名是 `ods.order_detail" → 匹配，直接采纳）
- **语义不匹配时降级**：若表名明显偏离用户需求（如给的 `dim.date` 但需求是交易数据），进入步骤 3 走搜索流程
- 降级时在 notes 注明：`"用户指定 {表} 但语义不匹配，降级搜索"`

**命中且语义匹配时**：填入 `candidates=[该表]` / `selected=该表`，跳到步骤 5。

### 步骤 2：若 runtime 注入了"推荐候选表（profile 预判 · 软提示）"段落

- **优先**把该段下的主表作为候选，填入 `candidates` / `selected`
- 若用户需求明显不符该主题，允许忽略，但须在 notes 注明忽略原因（如 `"profile 推荐收益报表，需求为渠道明细，不符"`）
- 若无 profile 软提示，跳过本步，进入步骤 3

### 步骤 3：正常搜索流程（上面两步都没命中时）

- `search_table_roots(query=用户原文)`
- `search_internal_tables(query=用户原文, root_abbreviations=[...])`
- 把命中结果里与用户需求最匹配的 1~3 张写入 `candidates`，最合适的一张写入 `selected`

### 步骤 4：降级处理（搜索无结果时）

若 search 后 candidates 仍为空：
- `selected=null, candidates=[]`
- notes 须写明搜了什么关键词、为什么没匹配，供上游人工介入
- 示例：`"搜索关键词：[会员月报、ods、dim]，无匹配表"` / `"用户需求为会员RFM分析，candidates 均半匹配，建议人工确认"`

### 步骤 5：输出 JSON（唯一最终回复）

**仅且必须**输出一段 ```json``` 代码块；禁止任何其它说明文字、Markdown 标题或前后铺垫。

```json
{
  "candidates": ["db1.t1", "db1.t2"],
  "selected": "db1.t1",
  "notes": ["关键提示 / 失败原因，每条 ≤ 30 字"]
}
```

### 步骤 6：业务口径（必做，当 selected 非空时）

根据表名 + profile 软提示（若有），用中文短句写入 notes，每条 ≤ 30 字。示例：
- 时间对齐：离店日 / 在店日 / 预订日（与表名 checkout / stayin / bk 一致）
- 默认过滤：非取消 `iscancel=0` 等（来自主题 sql_rules，不要写具体列名让用户确认）
- 指标口径：间夜 / 平均售价等与本表主题的对应关系

**若无 profile 软提示**：仅根据表名校验语义即可，notes 可留空。

**禁止**在 notes 里写「请用户确认日期字段名 / 国家字段名 / DDL」——那是元数据阶段的事。

---

## 三、硬约束

- `selected` 必须在 `candidates` 内；为空时 `selected=null`, `candidates=[]`
- notes 字数统一：每条 ≤ **30** 字
- **禁止**输出 `columns` / `partition_keys` / `partition_values` / `table_type` / `join_tables` / `resolved_date` 字段——这些留给下游节点处理
- **本节点不输出 SQL，不做日期解析**
