"""
基础使用示例
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import Agent


async def main():
    """主函数"""
    print("=" * 60)
    print("Python Agent Skills Demo - 基础使用示例")
    print("=" * 60)
    
    # 创建代理
    print("\n1. 创建代理实例...")
    agent = Agent()
    
    # 获取代理状态
    print("\n2. 代理状态:")
    status = agent.get_status()
    print(f"   Agent ID: {status['agent_id']}")
    print(f"   名称: {status['name']}")
    print(f"   版本: {status['version']}")
    print(f"   已加载技能: {', '.join(status['skills'].keys())}")
    
    # 示例1: 问候技能
    print("\n3. 示例1: 使用问候技能")
    print("   " + "-" * 40)
    
    result = await agent.run("向用户问好", name="小明", language="zh-CN")
    
    if result["success"]:
        data = result["result"]["data"]
        print(f"   ✅ 问候结果: {data.get('greeting', 'N/A')}")
        print(f"     语言: {data.get('language', 'N/A')}")
        print(f"     时间: {data.get('time_of_day', 'N/A')}")
    else:
        print(f"   ❌ 问候失败: {result.get('error', '未知错误')}")
    
    # 示例2: 计算器技能
    print("\n4. 示例2: 使用计算器技能")
    print("   " + "-" * 40)
    
    expressions = [
        "15 + 27 * 3",
        "100 / 4",
        "2 ^ 10",  # 2的10次方
    ]
    
    for expr in expressions:
        result = await agent.run(f"计算 {expr}", expression=expr)
        
        if result["success"]:
            data = result["result"]["data"]
            print(f"   ✅ {expr} = {data.get('formatted', 'N/A')}")
        else:
            print(f"   ❌ 计算失败: {result.get('error', '未知错误')}")
    
    # 示例3: 天气查询技能
    print("\n5. 示例3: 使用天气查询技能")
    print("   " + "-" * 40)
    
    cities = ["北京", "上海", "广州"]
    
    for city in cities:
        result = await agent.run(f"查询{city}的天气", city=city, days=2)
        
        if result["success"]:
            data = result["result"]["data"]
            current = data.get("current", {})
            print(f"   ✅ {current.get('city', city)}: {current.get('weather', 'N/A')} "
                  f"{current.get('temperature', 'N/A')}°C "
                  f"{current.get('icon', '')}")
        else:
            print(f"   ❌ 天气查询失败: {result.get('error', '未知错误')}")
    
    # 示例4: 自动技能选择
    print("\n6. 示例4: 自动技能选择")
    print("   " + "-" * 40)
    
    tasks = [
        "今天天气怎么样？",
        "帮我计算一下 45 * 67 等于多少",
        "向李华问好",
        "这是一个复杂的任务，需要多个步骤完成"
    ]
    
    for task in tasks:
        result = await agent.run(task)
        
        if result["success"]:
            skill = result["result"].get("skill", "未知")
            summary = result["result"].get("summary", "完成")
            print(f"   ✅ '{task[:20]}...' -> 技能: {skill}, 结果: {summary}")
        else:
            print(f"   ❌ 任务失败: {result.get('error', '未知错误')}")
    
    # 最终状态
    print("\n7. 最终状态统计:")
    print("   " + "-" * 40)
    
    final_status = agent.get_status()
    metrics = final_status["metrics"]
    
    print(f"   总任务数: {metrics['total_tasks']}")
    print(f"   成功任务: {metrics['completed_tasks']}")
    print(f"   失败任务: {metrics['failed_tasks']}")
    print(f"   重试成功率: {metrics['retry_success_rate']:.2%}")
    print(f"   平均重试次数: {metrics['average_retries']:.2f}")
    
    print("\n" + "=" * 60)
    print("示例执行完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())