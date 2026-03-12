"""
Agent Skills 项目主入口
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from core.skill_manager import SkillManager
from skills.calculator_skill import CalculatorSkill
from skills.web_search_skill import WebSearchSkill
from skills.file_processor_skill import FileProcessorSkill
from skills.base_skill import SkillInput


async def main():
    """主函数"""
    logger.info("启动 Agent Skills 项目...")
    
    # 初始化技能管理器
    skill_manager = SkillManager()
    
    # 注册技能
    logger.info("注册技能...")
    skill_manager.register_skill(CalculatorSkill())
    skill_manager.register_skill(WebSearchSkill())
    skill_manager.register_skill(FileProcessorSkill())
    
    # 显示技能信息
    logger.info(f"已注册 {len(skill_manager)} 个技能:")
    for skill_name in skill_manager.get_skill_names():
        skill_info = skill_manager.get_skill_info(skill_name)
        logger.info(f"  - {skill_name}: {skill_info['description']}")
    
    # 示例任务
    example_tasks = [
        "计算 2 + 3 * 4",
        "搜索 Python 教程",
        "读取文件 test.txt",
        "列出当前目录文件",
    ]
    
    logger.info("\n示例任务执行:")
    logger.info("=" * 50)
    
    for task in example_tasks:
        logger.info(f"\n任务: {task}")
        
        # 查找适合的技能
        suitable_skills = skill_manager.find_skills_for_task(task)
        
        if not suitable_skills:
            logger.warning("  没有找到适合的技能")
            continue
        
        logger.info(f"  找到 {len(suitable_skills)} 个适合的技能:")
        for skill in suitable_skills:
            logger.info(f"    - {skill.name}: {skill.description}")
        
        # 使用第一个适合的技能
        selected_skill = suitable_skills[0]
        logger.info(f"  选择技能: {selected_skill.name}")
        
        # 创建输入
        skill_input = skill_manager.create_skill_input(task)
        
        # 执行技能
        try:
            output = await skill_manager.execute_skill(selected_skill.name, skill_input)
            
            if output.success:
                logger.success(f"  执行成功!")
                logger.info(f"  结果: {output.result}")
                if output.metadata:
                    logger.debug(f"  元数据: {output.metadata}")
            else:
                logger.error(f"  执行失败: {output.error}")
                
        except Exception as e:
            logger.error(f"  技能执行异常: {str(e)}")
    
    logger.info("\n" + "=" * 50)
    logger.info("示例执行完成!")
    
    # 显示所有技能信息
    logger.info("\n所有技能详细信息:")
    all_skills_info = skill_manager.get_all_skills_info()
    for skill_name, info in all_skills_info.items():
        logger.info(f"\n{skill_name}:")
        logger.info(f"  描述: {info['description']}")
        logger.info(f"  最大重试次数: {info['max_retries']}")
        logger.info(f"  关键词: {', '.join(info['keywords'])}")


if __name__ == "__main__":
    # 配置日志
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # 运行主函数
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序异常: {str(e)}")
        sys.exit(1)