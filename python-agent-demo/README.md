# Python Agent Skills Demo

一个使用Python构建的智能代理技能项目，包含技能编排、任务拆分重试等功能。

## 项目特性

- 🚀 **技能编排系统** - 使用LangGraph构建工作流
- 🔄 **任务拆分与重试** - 自动任务分解和错误恢复
- 🧩 **模块化技能** - 可插拔的技能架构
- 📊 **状态管理** - 完整的执行状态跟踪
- 🧪 **测试技能** - 包含多个示例技能

## 项目结构

```
python-agent-demo/
├── skills/                    # 技能模块
│   ├── __init__.py
│   ├── base.py               # 技能基类
│   ├── greeting.py           # 问候技能
│   ├── calculator.py         # 计算器技能
│   ├── weather.py            # 天气查询技能
│   └── file_processor.py     # 文件处理技能
├── orchestrator/             # 编排引擎
│   ├── __init__.py
│   ├── graph_builder.py      # LangGraph构建器
│   ├── task_splitter.py      # 任务拆分器
│   └── retry_manager.py      # 重试管理器
├── core/                     # 核心模块
│   ├── __init__.py
│   ├── agent.py              # 主代理类
│   ├── state.py              # 状态管理
│   └── config.py             # 配置管理
├── tests/                    # 测试
│   ├── test_skills.py
│   └── test_orchestrator.py
├── examples/                 # 使用示例
│   ├── basic_usage.py
│   └── advanced_workflow.py
├── requirements.txt          # 依赖包
├── config.yaml               # 配置文件
└── main.py                   # 主入口
```

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行示例
```bash
python examples/basic_usage.py
```

### 3. 创建自定义技能
参考 `skills/greeting.py` 创建新技能

## 技能示例

### 问候技能
```python
agent.run("向用户问好")
```

### 计算器技能
```python
agent.run("计算 15 + 27 * 3")
```

### 天气查询技能
```python
agent.run("查询北京的天气")
```

### 文件处理技能
```python
agent.run("处理文件 /path/to/file.txt")
```

## 高级功能

### 任务拆分
```python
# 自动将复杂任务拆分为子任务
result = agent.run_with_split("分析这份报告并生成摘要")
```

### 重试机制
```python
# 自动重试失败的任务
result = agent.run_with_retry("执行可能失败的操作", max_retries=3)
```

### 工作流编排
```python
# 自定义工作流
workflow = agent.create_workflow([
    "skill1:处理输入",
    "skill2:分析数据", 
    "skill3:生成报告"
])
```

## 依赖库

- `langgraph` - 工作流编排
- `pydantic` - 数据验证
- `typing-extensions` - 类型提示
- `python-dotenv` - 环境变量管理
- `pytest` - 测试框架

## 许可证

MIT License