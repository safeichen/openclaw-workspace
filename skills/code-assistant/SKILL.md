---
name: code-assistant
description: 编程助手技能。提供代码编写、调试、优化、解释和学习功能。支持多种编程语言和开发工具。
---

# Code Assistant Skill

编程助手技能，提供全面的代码开发支持。

## 功能特性

### 1. 代码编写
- 多种语言支持：Python, JavaScript, TypeScript, Java, C++, Go, Rust等
- 代码片段生成
- 函数和类模板
- 算法实现
- 数据结构代码

### 2. 代码调试
- 错误分析和修复
- 性能优化建议
- 代码审查
- 测试用例生成

### 3. 代码解释
- 代码功能解释
- 算法原理说明
- 复杂逻辑解析
- 技术文档生成

### 4. 学习资源
- 编程概念讲解
- 最佳实践指南
- 框架使用示例
- 工具链配置

### 5. 开发工具
- Git操作指导
- 构建工具配置
- 部署脚本编写
- 环境配置帮助

## 支持的语言

### 主要语言
- **Python** - 数据分析、机器学习、Web开发
- **JavaScript/TypeScript** - 前端开发、Node.js后端
- **Java** - 企业应用、Android开发
- **C++** - 系统编程、游戏开发
- **Go** - 并发编程、微服务
- **Rust** - 系统编程、安全关键应用

### 脚本语言
- **Bash/Shell** - 系统管理、自动化脚本
- **PowerShell** - Windows自动化
- **SQL** - 数据库查询和管理

### Web技术
- **HTML/CSS** - 网页开发
- **React/Vue** - 前端框架
- **Express/Django/Flask** - 后端框架

## 快速开始

### 基本使用
```bash
# 在OpenClaw中调用编程助手
# 例如："写一个Python函数计算斐波那契数列"
# 或："解释这段JavaScript代码"
```

### 代码示例请求
你可以请求：
- "写一个Python爬虫获取网页内容"
- "创建一个React组件显示用户列表"
- "写一个Go的HTTP服务器"
- "优化这段Java代码的性能"

## 实用工具

### 代码片段库
```python
# Python示例：文件操作
def read_file_safely(filepath):
    """安全读取文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"文件不存在: {filepath}")
        return None
    except Exception as e:
        print(f"读取文件错误: {e}")
        return None
```

```javascript
// JavaScript示例：异步处理
async function fetchData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP错误: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('获取数据失败:', error);
        return null;
    }
}
```

### 调试助手
```bash
# 常见调试命令
# Python调试
python -m pdb script.py
# 或使用ipdb
import ipdb; ipdb.set_trace()

# JavaScript调试
node --inspect script.js
# 浏览器开发者工具 F12
```

## 学习路径

### Python学习路径
1. 基础语法和数据类型
2. 函数和模块
3. 面向对象编程
4. 文件操作和异常处理
5. 常用库：requests, pandas, numpy
6. Web框架：Flask, Django
7. 数据科学：matplotlib, scikit-learn

### JavaScript学习路径
1. 基础语法和DOM操作
2. 异步编程（Promise, async/await）
3. ES6+新特性
4. Node.js基础
5. 前端框架（React/Vue）
6. 构建工具（Webpack, Vite）

## 最佳实践

### 代码规范
```python
# PEP 8 Python代码规范
# - 使用4空格缩进
# - 行长度不超过79字符
# - 函数和类之间空两行
# - 使用有意义的变量名
```

```javascript
// JavaScript最佳实践
// - 使用const和let，避免var
// - 使用===而不是==
// - 函数和变量使用驼峰命名
// - 添加JSDoc注释
```

### 版本控制
```bash
# Git工作流
git checkout -b feature/new-feature
# 开发代码...
git add .
git commit -m "添加新功能"
git push origin feature/new-feature
# 创建Pull Request
```

## 故障排除

### 常见问题
1. **导入错误** - 检查模块安装和路径
2. **语法错误** - 使用linter检查代码
3. **运行时错误** - 添加异常处理和日志
4. **性能问题** - 使用性能分析工具

### 调试技巧
1. 打印关键变量值
2. 使用断点调试
3. 查看错误堆栈
4. 简化问题复现

## 集成开发环境

### VS Code配置
```json
// .vscode/settings.json
{
    "python.pythonPath": "python3",
    "editor.formatOnSave": true,
    "files.autoSave": "afterDelay"
}
```

### 常用扩展
- Python
- JavaScript/TypeScript
- GitLens
- Prettier
- ESLint

## 项目模板

### Python项目结构
```
my_project/
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── requirements.txt
├── README.md
└── .gitignore
```

### JavaScript项目结构
```
my_app/
├── src/
│   ├── index.js
│   ├── components/
│   └── utils/
├── public/
│   └── index.html
├── package.json
├── webpack.config.js
└── README.md
```

## 资源推荐

### 学习网站
- MDN Web Docs - Web技术文档
- Python官方文档
- freeCodeCamp - 免费编程课程
- LeetCode - 算法练习

### 工具推荐
- Git - 版本控制
- Docker - 容器化
- Postman - API测试
- Jupyter Notebook - 数据科学

---

**注意**: 此技能提供编程指导和代码示例，实际代码执行需要在相应的开发环境中进行。