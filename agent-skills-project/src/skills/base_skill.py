"""
基础技能类
所有技能都继承自这个基类
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
from loguru import logger


class SkillInput(BaseModel):
    """技能输入模型"""
    task: str = Field(..., description="任务描述")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="技能参数")
    context: Optional[Dict[str, Any]] = Field(default=None, description="执行上下文")


class SkillOutput(BaseModel):
    """技能输出模型"""
    success: bool = Field(..., description="执行是否成功")
    result: Any = Field(..., description="执行结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class BaseSkill(ABC):
    """基础技能抽象类"""
    
    def __init__(self, name: str, description: str, max_retries: int = 3):
        """
        初始化技能
        
        Args:
            name: 技能名称
            description: 技能描述
            max_retries: 最大重试次数
        """
        self.name = name
        self.description = description
        self.max_retries = max_retries
        self.retry_count = 0
        
    @abstractmethod
    async def execute(self, input_data: SkillInput) -> SkillOutput:
        """
        执行技能
        
        Args:
            input_data: 技能输入
            
        Returns:
            SkillOutput: 技能输出
        """
        pass
    
    def validate_input(self, input_data: SkillInput) -> bool:
        """
        验证输入数据
        
        Args:
            input_data: 技能输入
            
        Returns:
            bool: 输入是否有效
        """
        if not input_data.task:
            logger.error(f"技能 {self.name}: 任务描述不能为空")
            return False
        return True
    
    def can_handle(self, task: str) -> bool:
        """
        判断技能是否能处理指定任务
        
        Args:
            task: 任务描述
            
        Returns:
            bool: 是否能处理
        """
        # 基础实现：检查任务描述是否包含技能关键词
        task_lower = task.lower()
        name_lower = self.name.lower()
        return name_lower in task_lower or any(
            keyword in task_lower for keyword in self.get_keywords()
        )
    
    def get_keywords(self) -> List[str]:
        """
        获取技能关键词
        
        Returns:
            List[str]: 关键词列表
        """
        # 默认返回技能名称的小写形式
        return [self.name.lower()]
    
    def reset_retry(self):
        """重置重试计数"""
        self.retry_count = 0
        
    def should_retry(self) -> bool:
        """
        判断是否应该重试
        
        Returns:
            bool: 是否应该重试
        """
        return self.retry_count < self.max_retries
    
    def increment_retry(self):
        """增加重试计数"""
        self.retry_count += 1
        
    def __str__(self):
        return f"Skill(name={self.name}, description={self.description})"
    
    def __repr__(self):
        return self.__str__()