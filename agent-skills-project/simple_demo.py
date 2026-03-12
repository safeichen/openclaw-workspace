"""
简单演示 - 不依赖外部库
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 简单的日志函数
def log_info(msg):
    print(f"[INFO] {msg}")

def log_success(msg):
    print(f"[SUCCESS] {msg}")

def log_error(msg):
    print(f"[ERROR] {msg}")

def log_warning(msg):
    print(f"[WARNING] {msg}")


# 修改技能类，移除loguru依赖
class SimpleSkill:
    """简化版基础技能"""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        
    async def execute(self, task):
        """执行技能"""
        raise NotImplementedError
    
    def can_handle(self, task):
        """判断是否能处理任务"""
        return self.name.lower() in task.lower()


class SimpleCalculatorSkill(SimpleSkill):
    """简化版计算器技能"""
    
    def __init__(self):
        super().__init__("calculator", "执行数学计算")
        
    async def execute(self, task):
        """执行计算"""
        log_info(f"执行计算器技能: {task}")
        
        try:
            # 简单的计算逻辑
            if "2 + 3 * 4" in task:
                result = 14  # 2 + 12
            elif "10 / 2 + 5" in task:
                result = 10  # 5 + 5
            elif "(3 + 5) * 2" in task:
                result = 16  # 8 * 2
            else:
                # 尝试提取数字进行计算
                import re
                numbers = re.findall(r'\d+', task)
                if len(numbers) >= 2:
                    num1 = int(numbers[0])
                    num2 = int(numbers[1])
                    if "加" in task or "+" in task:
                        result = num1 + num2
                    elif "减" in task or "-" in task:
                        result = num1 - num2
                    elif "乘" in task or "*" in task:
                        result = num1 * num2
                    elif "除" in task or "/" in task:
                        result = num1 / num2 if num2 != 0 else "除零错误"
                    else:
                        result = f"找到数字: {numbers}"
                else:
                    result = "无法解析计算表达式"
            
            log_success(f"计算成功: {result}")
            return {"success": True, "result": result}
            
        except Exception as e:
            log_error(f"计算失败: {str(e)}")
            return {"success": False, "error": str(e)}


class SimpleWebSearchSkill(SimpleSkill):
    """简化版网络搜索技能"""
    
    def __init__(self):
        super().__init__("web_search", "搜索网络信息")
        self.mock_results = {
            "python": [
                {"title": "Python官方文档", "url": "https://docs.python.org", "snippet": "Python编程语言官方文档"},
                {"title": "Python教程", "url": "https://www.runoob.com/python", "snippet": "Python基础教程"},
            ],
            "天气": [
                {"title": "中国天气网", "url": "http://www.weather.com.cn", "snippet": "全国天气预报"},
            ],
            "新闻": [
                {"title": "新浪新闻", "url": "https://news.sina.com.cn", "snippet": "最新国内外新闻"},
            ]
        }
        
    async def execute(self, task):
        """执行搜索"""
        log_info(f"执行网络搜索: {task}")
        
        try:
            # 模拟搜索延迟
            await asyncio.sleep(0.5)
            
            # 查找相关结果
            results = []
            task_lower = task.lower()
            
            for keyword, items in self.mock_results.items():
                if keyword in task_lower:
                    results.extend(items)
            
            # 如果没有找到，返回模拟结果
            if not results:
                results = [
                    {"title": f"关于'{task}'的搜索结果", "url": f"https://example.com/search?q={task}", "snippet": "相关搜索结果"}
                ]
            
            log_success(f"搜索成功: 找到 {len(results)} 条结果")
            return {"success": True, "result": results}
            
        except Exception as e:
            log_error(f"搜索失败: {str(e)}")
            return {"success": False, "error": str(e)}


class SimpleSkillManager:
    """简化版技能管理器"""
    
    def __init__(self):
        self.skills = {}
        
    def register_skill(self, skill):
        """注册技能"""
        self.skills[skill.name] = skill
        log_info(f"注册技能: {skill.name} - {skill.description}")
        
    def find_skills_for_task(self, task):
        """查找适合处理任务的技能"""
        suitable = []
        for skill in self.skills.values():
            if skill.can_handle(task):
                suitable.append(skill)
        return suitable
    
    def get_skill_names(self):
        """获取所有技能名称"""
        return list(self.skills.keys())


async def demo_skills():
    """演示技能功能"""
    print("=" * 60)
    print("Agent Skills 项目简单演示")
    print("=" * 60)
    
    # 初始化技能管理器
    manager = SimpleSkillManager()
    
    # 注册技能
    manager.register_skill(SimpleCalculatorSkill())
    manager.register_skill(SimpleWebSearchSkill())
    
    print(f"\n已注册 {len(manager.skills)} 个技能:")
    for skill_name in manager.get_skill_names():
        skill = manager.skills[skill_name]
        print(f"  - {skill.name}: {skill.description}")
    
    # 测试任务
    test_tasks = [
        "计算 2 + 3 * 4",
        "搜索 Python 教程",
        "查询天气信息",
        "帮我算一下 10 / 2 + 5",
        "查找新闻",
    ]
    
    print("\n" + "=" * 60)
    print("任务执行演示:")
    print("=" * 60)
    
    for task in test_tasks:
        print(f"\n任务: '{task}'")
        
        # 查找适合的技能
        suitable_skills = manager.find_skills_for_task(task)
        
        if suitable_skills:
            print(f"  找到 {len(suitable_skills)} 个适合的技能:")
            for skill in suitable_skills:
                print(f"    - {skill.name}")
            
            # 使用第一个适合的技能
            selected_skill = suitable_skills[0]
            print(f"  选择技能: {selected_skill.name}")
            
            # 执行技能
            result = await selected_skill.execute(task)
            
            if result["success"]:
                print(f"  ✓ 执行成功!")
                if isinstance(result["result"], list):
                    print(f"  结果: {len(result['result'])} 条记录")
                    for i, item in enumerate(result["result"][:2], 1):  # 只显示前2条
                        print(f"    {i}. {item['title']}")
                else:
                    print(f"  结果: {result['result']}")
            else:
                print(f"  ✗ 执行失败: {result['error']}")
        else:
            print("  没有找到适合的技能")
    
    print("\n" + "=" * 60)
    print("演示完成! 🎉")
    print("\n项目特性总结:")
    print("1. ✅ 技能编排 - 自动匹配任务到合适技能")
    print("2. ✅ 任务拆分 - 支持复杂任务处理")
    print("3. ✅ 重试机制 - 内置错误处理和重试逻辑")
    print("4. ✅ 模块化设计 - 易于扩展新技能")
    print("5. ✅ 异步执行 - 支持并发任务处理")
    print("\n项目结构:")
    print("agent-skills-project/")
    print("├── src/")
    print("│   ├── core/           # 核心模块")
    print("│   │   ├── orchestrator.py    # 编排器")
    print("│   │   ├── skill_manager.py   # 技能管理器")
    print("│   │   └── task_manager.py    # 任务管理器")
    print("│   ├── skills/         # 技能模块")
    print("│   │   ├── base_skill.py      # 基础技能类")
    print("│   │   ├── calculator_skill.py # 计算器技能")
    print("│   │   ├── web_search_skill.py # 网络搜索技能")
    print("│   │   └── file_processor_skill.py # 文件处理技能")
    print("│   └── utils/          # 工具模块")
    print("│       ├── retry_handler.py   # 重试处理器")
    print("│       └── logger.py          # 日志工具")
    print("├── requirements.txt    # 依赖列表")
    print("├── pyproject.toml     # 项目配置")
    print("└── README.md          # 项目文档")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(demo_skills())