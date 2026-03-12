"""
示例脚本 - 演示 Agent Skills 项目功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.skill_manager import SkillManager
from src.skills.calculator_skill import CalculatorSkill
from src.skills.web_search_skill import WebSearchSkill
from src.skills.file_processor_skill import FileProcessorSkill


async def demo_calculator_skill():
    """演示计算器技能"""
    print("=" * 60)
    print("演示: 计算器技能")
    print("=" * 60)
    
    skill = CalculatorSkill()
    
    test_cases = [
        "计算 2 + 3 * 4",
        "算一下 10 / 2 + 5",
        "求 (3 + 5) * 2 的结果",
    ]
    
    for task in test_cases:
        print(f"\n任务: {task}")
        
        # 检查技能是否能处理
        if skill.can_handle(task):
            print(f"  ✓ 技能 '{skill.name}' 可以处理此任务")
            
            # 执行技能
            from src.skills.base_skill import SkillInput
            input_data = SkillInput(task=task)
            output = await skill.execute(input_data)
            
            if output.success:
                print(f"  ✓ 执行成功!")
                print(f"  结果: {output.result}")
            else:
                print(f"  ✗ 执行失败: {output.error}")
        else:
            print(f"  ✗ 技能 '{skill.name}' 无法处理此任务")
    
    print("\n" + "=" * 60)


async def demo_web_search_skill():
    """演示网络搜索技能"""
    print("\n" + "=" * 60)
    print("演示: 网络搜索技能")
    print("=" * 60)
    
    skill = WebSearchSkill()
    
    test_cases = [
        "搜索 Python 教程",
        "查找天气信息",
        "查询最新新闻",
    ]
    
    for task in test_cases:
        print(f"\n任务: {task}")
        
        # 检查技能是否能处理
        if skill.can_handle(task):
            print(f"  ✓ 技能 '{skill.name}' 可以处理此任务")
            
            # 执行技能
            from src.skills.base_skill import SkillInput
            input_data = SkillInput(task=task)
            output = await skill.execute(input_data)
            
            if output.success:
                print(f"  ✓ 执行成功!")
                results = output.result
                print(f"  找到 {len(results)} 条结果:")
                for i, result in enumerate(results[:3], 1):  # 只显示前3条
                    print(f"    {i}. {result['title']}")
                    print(f"       链接: {result['url']}")
                    print(f"       摘要: {result['snippet'][:60]}...")
            else:
                print(f"  ✗ 执行失败: {output.error}")
        else:
            print(f"  ✗ 技能 '{skill.name}' 无法处理此任务")
    
    print("\n" + "=" * 60)


async def demo_skill_manager():
    """演示技能管理器"""
    print("\n" + "=" * 60)
    print("演示: 技能管理器")
    print("=" * 60)
    
    # 初始化技能管理器
    manager = SkillManager()
    
    # 注册技能
    manager.register_skill(CalculatorSkill())
    manager.register_skill(WebSearchSkill())
    manager.register_skill(FileProcessorSkill())
    
    print(f"已注册 {len(manager)} 个技能:")
    for skill_name in manager.get_skill_names():
        skill_info = manager.get_skill_info(skill_name)
        print(f"  - {skill_name}: {skill_info['description']}")
    
    # 测试任务分发
    test_tasks = [
        "帮我计算一下 15 + 27",
        "搜索人工智能相关资料",
        "处理文件 data.json",
        "这个任务没有合适的技能",
    ]
    
    print("\n任务分发测试:")
    for task in test_tasks:
        print(f"\n任务: '{task}'")
        
        # 查找适合的技能
        suitable_skills = manager.find_skills_for_task(task)
        
        if suitable_skills:
            print(f"  找到 {len(suitable_skills)} 个适合的技能:")
            for skill in suitable_skills:
                print(f"    - {skill.name} ({skill.description})")
        else:
            print("  没有找到适合的技能")
    
    print("\n" + "=" * 60)


async def main():
    """主函数"""
    print("Agent Skills 项目演示")
    print("=" * 60)
    
    # 演示各个功能
    await demo_calculator_skill()
    await demo_web_search_skill()
    await demo_skill_manager()
    
    print("\n演示完成! 🎉")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())