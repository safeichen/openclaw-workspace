"""
技能模块
"""

from .base import BaseSkill, SkillResult
from .greeting import GreetingSkill
from .calculator import CalculatorSkill
from .weather import WeatherSkill
from .file_processor import FileProcessorSkill

# 技能注册表
SKILL_REGISTRY = {
    "greeting": GreetingSkill,
    "calculator": CalculatorSkill,
    "weather": WeatherSkill,
    "file_processor": FileProcessorSkill,
}

__all__ = [
    "BaseSkill",
    "SkillResult",
    "GreetingSkill",
    "CalculatorSkill",
    "WeatherSkill",
    "FileProcessorSkill",
    "SKILL_REGISTRY",
]