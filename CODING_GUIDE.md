# 💻 OpenClaw 编程助手指南

## 📦 已安装的编程技能

### 1. code-assistant (自定义技能)
**位置**: `/root/.openclaw/workspace/skills/code-assistant/`
**功能**: 全面的编程开发支持工具

### 2. 可用工具脚本
- `code-helper.sh` - 交互式编程工具菜单
- `python-helper.py` - Python专用编程助手

## 🚀 快速开始

### 方法1: 使用交互式菜单
```bash
cd /root/.openclaw/workspace
./skills/code-assistant/scripts/code-helper.sh
```

### 方法2: 使用Python助手
```bash
cd /root/.openclaw/workspace
python3 skills/code-assistant/scripts/python-helper.py
```

### 方法3: 直接请求代码帮助
在OpenClaw对话中直接请求：
- "写一个Python函数处理CSV文件"
- "创建一个React组件"
- "解释这段JavaScript代码"
- "帮我调试这个错误"

## 🔧 主要功能

### 1. 代码片段生成
支持多种语言的常用代码片段：
- **Python**: 文件操作、HTTP请求、数据处理、类定义
- **JavaScript**: 异步函数、DOM操作、事件处理、API调用
- **Bash/Shell**: 安全脚本模板、错误处理、日志函数
- **SQL**: 查询优化、事务处理

### 2. 代码审查和分析
- 代码风格检查
- 复杂度分析
- 安全性评估
- 性能建议

### 3. 算法实现
- 排序算法（快速排序、归并排序等）
- 搜索算法（二分查找、BFS、DFS）
- 动态规划
- 图算法

### 4. 项目模板
- Python项目结构
- JavaScript项目结构
- Web应用模板
- 数据分析项目

## 🐍 Python开发支持

### Python助手工具
```bash
# 分析Python文件
python3 skills/code-assistant/scripts/python-helper.py analyze myfile.py

# 生成代码模板
python3 skills/code-assistant/scripts/python-helper.py template class

# 检查代码风格
python3 skills/code-assistant/scripts/python-helper.py check myfile.py

# 运行测试
python3 skills/code-assistant/scripts/python-helper.py test
```

### Python最佳实践
```python
# 1. 使用类型提示
def process_data(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """处理数据并返回DataFrame"""
    pass

# 2. 异常处理
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"操作失败: {e}")
    raise
except Exception as e:
    logger.exception("未知错误")
    raise

# 3. 使用上下文管理器
with open('file.txt', 'r') as f:
    content = f.read()

# 4. 文档字符串
def calculate_average(numbers: List[float]) -> float:
    """计算数字列表的平均值
    
    Args:
        numbers: 数字列表
        
    Returns:
        平均值
        
    Raises:
        ValueError: 如果列表为空
    """
    if not numbers:
        raise ValueError("数字列表不能为空")
    return sum(numbers) / len(numbers)
```

## 🌐 Web开发支持

### JavaScript/TypeScript
```javascript
// 现代JavaScript特性
const fetchUser = async (userId) => {
    try {
        const response = await fetch(`/api/users/${userId}`);
        if (!response.ok) throw new Error('请求失败');
        return await response.json();
    } catch (error) {
        console.error('获取用户失败:', error);
        return null;
    }
};

// TypeScript类型安全
interface User {
    id: number;
    name: string;
    email: string;
}

function greetUser(user: User): string {
    return `Hello, ${user.name}!`;
}
```

### React组件示例
```jsx
import React, { useState, useEffect } from 'react';

const UserList = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        fetchUsers();
    }, []);
    
    const fetchUsers = async () => {
        try {
            const response = await fetch('/api/users');
            const data = await response.json();
            setUsers(data);
        } catch (error) {
            console.error('获取用户列表失败:', error);
        } finally {
            setLoading(false);
        }
    };
    
    if (loading) return <div>加载中...</div>;
    
    return (
        <div className="user-list">
            <h2>用户列表</h2>
            <ul>
                {users.map(user => (
                    <li key={user.id}>
                        {user.name} - {user.email}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default UserList;
```

## 🗃️ 数据库支持

### SQL最佳实践
```sql
-- 使用参数化查询防止SQL注入
PREPARE getUser (int) AS
SELECT id, name, email 
FROM users 
WHERE id = $1;

EXECUTE getUser(123);

-- 创建索引优化查询
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_date ON orders(user_id, order_date);

-- 使用事务保证数据一致性
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

## 🐳 容器化和部署

### Dockerfile示例
```dockerfile
# Python应用Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# 运行应用
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:${PORT}"]
```

### Docker Compose配置
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      - db
    volumes:
      - ./app:/app

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 🧪 测试和调试

### 单元测试示例
```python
# test_calculator.py
import unittest
from calculator import add, subtract

class TestCalculator(unittest.TestCase):
    
    def test_add_positive_numbers(self):
        self.assertEqual(add(2, 3), 5)
    
    def test_add_negative_numbers(self):
        self.assertEqual(add(-2, -3), -5)
    
    def test_subtract_numbers(self):
        self.assertEqual(subtract(5, 3), 2)
    
    def test_subtract_negative_result(self):
        self.assertEqual(subtract(3, 5), -2)

if __name__ == '__main__':
    unittest.main()
```

### 调试技巧
```python
# 1. 使用print调试
print(f"变量值: {variable}")

# 2. 使用pdb调试器
import pdb; pdb.set_trace()

# 3. 使用logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("调试信息")

# 4. 使用断言
assert condition, "条件不满足时的错误信息"
```

## 📚 学习资源

### 在线学习平台
- **freeCodeCamp** - 免费编程课程
- **Codecademy** - 交互式编程学习
- **LeetCode** - 算法练习
- **HackerRank** - 编程挑战

### 文档资源
- **MDN Web Docs** - Web技术文档
- **Python官方文档**
- **React官方文档**
- **Docker官方文档**

### 工具推荐
- **VS Code** - 代码编辑器
- **Git** - 版本控制
- **Docker** - 容器化
- **Postman** - API测试

## 🚨 常见问题解决

### Python环境问题
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 冻结依赖
pip freeze > requirements.txt
```

### Node.js/npm问题
```bash
# 清理npm缓存
npm cache clean --force

# 重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 检查版本
node --version
npm --version
```

### Git问题
```bash
# 撤销最后一次提交（保留更改）
git reset --soft HEAD^

# 撤销最后一次提交（丢弃更改）
git reset --hard HEAD^

# 恢复误删的文件
git checkout -- filename
```

## 🎯 开始编程

### 第一步：选择项目类型
```bash
# 运行编程助手
cd /root/.openclaw/workspace
./skills/code-assistant/scripts/code-helper.sh
```

### 第二步：获取代码帮助
- "帮我写一个Python爬虫"
- "创建一个简单的Web API"
- "优化这段SQL查询"
- "解释这个算法"

### 第三步：测试和调试
- 运行单元测试
- 检查代码风格
- 性能分析
- 安全审查

## 🎉 开始编程之旅！

现在你可以：
1. 使用编程助手生成代码
2. 分析现有代码质量
3. 学习编程最佳实践
4. 构建完整的项目

**有任何编程问题，随时问我！** 🚀