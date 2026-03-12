"""
技能管理器
管理所有可用技能，负责技能的注册、发现和调度
"""

from typing import Dict, List, Optional, Type, Any
from loguru import logger
from ..skills.base_skill import BaseSkill, SkillInput, SkillOutput


class SkillManager:
    """技能管理器"""
    
    def __init__(self):
        """初始化技能管理器"""
        self._skills: Dict[str, BaseSkill] = {}
        self._skill_classes: Dict[str, Type[BaseSkill]] = {}
        
    def register_skill(self, skill: BaseSkill):
        """
        注册技能实例
        
        Args:
            skill: 技能实例
        """
        if skill.name in self._skills:
            logger.warning(f"技能 '{skill.name}' 已存在，将被覆盖")
        
        self._skills[skill.name] = skill
        logger.info(f"注册技能: {skill.name} - {skill.description}")
    
    def register_skill_class(self, skill_class: Type[BaseSkill], **kwargs):
        """
        注册技能类
        
        Args:
            skill_class: 技能类
            **kwargs: 传递给技能构造函数的参数
        """
        skill_name = skill_class.__name__.lower().replace('skill', '')
        
        try:
            skill_instance = skill_class(**kwargs)
            self.register_skill(skill_instance)
            self._skill_classes[skill_name] = skill_class
        except Exception as e:
            logger.error(f"注册技能类失败 {skill_class.__name__}: {str(e)}")
    
    def get_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """
        获取技能实例
        
        Args:
            skill_name: 技能名称
            
        Returns:
            Optional[BaseSkill]: 技能实例，如果不存在则返回None
        """
        return self._skills.get(skill_name)
    
    def get_all_skills(self) -> List[BaseSkill]:
        """
        获取所有技能实例
        
        Returns:
            List[BaseSkill]: 所有技能实例
        """
        return list(self._skills.values())
    
    def get_skill_names(self) -> List[str]:
        """
        获取所有技能名称
        
        Returns:
            List[str]: 技能名称列表
        """
        return list(self._skills.keys())
    
    def find_skills_for_task(self, task: str) -> List[BaseSkill]:
        """
        查找适合处理任务的技能
        
        Args:
            task: 任务描述
            
        Returns:
            List[BaseSkill]: 适合的技能列表
        """
        suitable_skills = []
        
        for skill in self._skills.values():
            if skill.can_handle(task):
                suitable_skills.append(skill)
        
        # 按技能名称排序，确保一致性
        suitable_skills.sort(key=lambda s: s.name)
        
        logger.debug(f"为任务 '{task}' 找到 {len(suitable_skills)} 个适合的技能")
        return suitable_skills
    
    async def execute_skill(self, skill_name: str, input_data: SkillInput) -> SkillOutput:
        """
        执行指定技能
        
        Args:
            skill_name: 技能名称
            input_data: 技能输入
            
        Returns:
            SkillOutput: 技能输出
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return SkillOutput(
                success=False,
                result=None,
                error=f"技能 '{skill_name}' 不存在",
                metadata={"skill_name": skill_name}
            )
        
        # 验证输入
        if not skill.validate_input(input_data):
            return SkillOutput(
                success=False,
                result=None,
                error="输入验证失败",
                metadata={"skill_name": skill_name, "task": input_data.task}
            )
        
        # 执行技能
        try:
            logger.info(f"执行技能: {skill_name} - {input_data.task}")
            output = await skill.execute(input_data)
            return output
        except Exception as e:
            logger.error(f"技能执行异常 {skill_name}: {str(e)}")
            return SkillOutput(
                success=False,
                result=None,
                error=f"技能执行异常: {str(e)}",
                metadata={
                    "skill_name": skill_name,
                    "task": input_data.task,
                    "error_type": type(e).__name__
                }
            )
    
    def create_skill_input(self, task: str, **kwargs) -> SkillInput:
        """
        创建技能输入
        
        Args:
            task: 任务描述
            **kwargs: 其他参数
            
        Returns:
            SkillInput: 技能输入
        """
        return SkillInput(task=task, **kwargs)
    
    def get_skill_info(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """
        获取技能信息
        
        Args:
            skill_name: 技能名称
            
        Returns:
            Optional[Dict]: 技能信息
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return None
        
        return {
            "name": skill.name,
            "description": skill.description,
            "max_retries": skill.max_retries,
            "keywords": skill.get_keywords()
        }
    
    def get_all_skills_info(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有技能信息
        
        Returns:
            Dict[str, Dict]: 所有技能信息
        """
        return {
            skill_name: self.get_skill_info(skill_name)
            for skill_name in self.get_skill_names()
        }
    
    def clear_skills(self):
        """清空所有技能"""
        self._skills.clear()
        self._skill_classes.clear()
        logger.info("已清空所有技能")
    
    def __len__(self) -> int:
        """获取技能数量"""
        return len(self._skills)
    
    def __contains__(self, skill_name: str) -> bool:
        """检查技能是否存在"""
        return skill_name in self._skills
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"SkillManager(skills={len(self)})"
    
    def __repr__(self) -> str:
        """表示"""
        return self.__str__()