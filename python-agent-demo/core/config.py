"""
配置管理模块
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class SkillConfig(BaseModel):
    """技能配置"""
    enabled: bool = True
    parameters: Dict[str, Any] = Field(default_factory=dict)


class OrchestratorConfig(BaseModel):
    """编排器配置"""
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 30.0
    enable_task_splitting: bool = True
    max_task_depth: int = 5


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "logs/agent.log"
    max_size: int = 10_485_760  # 10MB
    backup_count: int = 5


class PerformanceConfig(BaseModel):
    """性能配置"""
    max_concurrent_tasks: int = 5
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5分钟


class AgentConfig(BaseModel):
    """代理配置"""
    name: str = "PythonAgent"
    version: str = "1.0.0"
    description: str = "Python智能代理"
    
    skills: Dict[str, SkillConfig] = Field(default_factory=dict)
    orchestrator: OrchestratorConfig = Field(default_factory=OrchestratorConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)


class Config:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self._config: Optional[AgentConfig] = None
        
    def load(self) -> AgentConfig:
        """加载配置"""
        if self._config is not None:
            return self._config
            
        if self.config_path and Path(self.config_path).exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
        else:
            config_data = {}
            
        # 合并默认配置
        self._config = AgentConfig(**config_data.get('agent', {}))
        return self._config
    
    def get_skill_config(self, skill_name: str) -> SkillConfig:
        """获取技能配置"""
        config = self.load()
        return config.skills.get(skill_name, SkillConfig())
    
    def update_skill_config(self, skill_name: str, **kwargs):
        """更新技能配置"""
        config = self.load()
        if skill_name not in config.skills:
            config.skills[skill_name] = SkillConfig()
        
        for key, value in kwargs.items():
            if hasattr(config.skills[skill_name], key):
                setattr(config.skills[skill_name], key, value)
            else:
                config.skills[skill_name].parameters[key] = value
    
    def save(self, path: Optional[str] = None):
        """保存配置"""
        save_path = path or self.config_path
        if not save_path:
            raise ValueError("未指定配置保存路径")
            
        config_dict = {"agent": self._config.dict()}
        with open(save_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, allow_unicode=True, default_flow_style=False)