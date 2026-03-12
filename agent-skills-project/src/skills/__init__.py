"""
技能模块
"""

from .base_skill import BaseSkill, SkillInput, SkillOutput
from .calculator_skill import CalculatorSkill
from .web_search_skill import WebSearchSkill
from .file_processor_skill import FileProcessorSkill

__all__ = [
    "BaseSkill",
    "SkillInput",
    "SkillOutput",
    "CalculatorSkill",
    "WebSearchSkill",
    "FileProcessorSkill",
]