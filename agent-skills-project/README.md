# Agent Skills 项目

一个基于Python的智能体技能编排系统，支持任务拆分、重试机制和技能组合。

## 功能特性

- **技能编排**: 使用LangGraph构建技能执行流程
- **任务拆分**: 自动将复杂任务拆分为子任务
- **重试机制**: 智能重试失败的任务
- **技能管理**: 模块化的技能系统
- **状态管理**: 完整的执行状态跟踪

## 项目结构

```
agent-skills-project/
├── README.md
├── requirements.txt
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   ├── skill_manager.py
│   │   └── task_manager.py
│   ├── skills/
│   │   ├── __init__.py
│   │   ├── base_skill.py
│   │   ├── calculator_skill.py
│   │   ├── web_search_skill.py
│   │   ├── file_processor_skill.py
│   │   └── weather_skill.py
│   └── utils/
│       ├── __init__.py
│       ├── retry_handler.py
│       └── logger.py
└── tests/
    ├── __init__.py
    ├── test_skills.py
    └── test_orchestrator.py
```

## 快速开始

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 运行示例:
```bash
python -m src.main
```

## 核心概念

### 技能(Skill)
- 基础技能类: 所有技能都继承自BaseSkill
- 技能注册: 自动注册到技能管理器
- 技能执行: 统一的执行接口

### 编排器(Orchestrator)
- 基于LangGraph的状态机
- 任务拆分逻辑
- 并行执行控制

### 任务管理器(TaskManager)
- 任务队列管理
- 优先级调度
- 结果收集

## 示例技能

1. **计算器技能**: 执行数学计算
2. **网络搜索技能**: 搜索网络信息
3. **文件处理技能**: 读写和处理文件
4. **天气查询技能**: 获取天气信息

## 配置

在`config.yaml`中配置:
- 技能参数
- 重试策略
- 日志级别
- API密钥