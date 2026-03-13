"""
技能基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class SkillResult(BaseModel):
    """技能执行结果"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = {}


class BaseSkill(ABC):
    """技能基类"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.config = {}
    
    def configure(self, **kwargs):
        """配置技能"""
        self.config.update(kwargs)
    
    @abstractmethod
    async def execute(self, **kwargs) -> SkillResult:
        """执行技能（异步）"""
        pass
    
    def execute_sync(self, **kwargs) -> SkillResult:
        """执行技能（同步）"""
        import asyncio
        return asyncio.run(self.execute(**kwargs))
    
    def validate_input(self, **kwargs) -> bool:
        """验证输入参数"""
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """获取技能信息"""
        return {
            "name": self.name,
            "description": self.description,
            "config": self.config,
        }