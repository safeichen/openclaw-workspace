"""
问候技能
"""

import asyncio
from typing import Dict, Any
from datetime import datetime
from .base import BaseSkill, SkillResult


class GreetingSkill(BaseSkill):
    """问候技能"""
    
    def __init__(self):
        super().__init__(
            name="greeting",
            description="向用户发送问候消息"
        )
        self.languages = {
            "zh-CN": {
                "morning": "早上好！🌞 新的一天开始啦！",
                "afternoon": "下午好！☕️ 休息一下喝杯茶吧！",
                "evening": "晚上好！🌙 今天过得怎么样？",
                "night": "晚安！🌠 做个好梦！",
                "default": "你好！👋 很高兴见到你！"
            },
            "en-US": {
                "morning": "Good morning! 🌞 A new day begins!",
                "afternoon": "Good afternoon! ☕️ Time for a tea break!",
                "evening": "Good evening! 🌙 How was your day?",
                "night": "Good night! 🌠 Sweet dreams!",
                "default": "Hello! 👋 Nice to meet you!"
            }
        }
    
    async def execute(self, **kwargs) -> SkillResult:
        """执行问候"""
        start_time = datetime.now()
        
        try:
            # 获取参数
            language = kwargs.get("language", "zh-CN")
            name = kwargs.get("name", "朋友")
            formal = kwargs.get("formal", False)
            
            # 验证语言支持
            if language not in self.languages:
                language = "zh-CN"
            
            # 获取当前时间
            current_hour = datetime.now().hour
            
            # 选择问候语
            if 5 <= current_hour < 12:
                time_key = "morning"
            elif 12 <= current_hour < 18:
                time_key = "afternoon"
            elif 18 <= current_hour < 22:
                time_key = "evening"
            else:
                time_key = "night"
            
            greeting = self.languages[language][time_key]
            
            # 添加姓名
            if name:
                if language == "zh-CN":
                    greeting = f"{name}，{greeting}"
                else:
                    greeting = f"{name}, {greeting}"
            
            # 正式问候
            if formal:
                if language == "zh-CN":
                    greeting = f"尊敬的{name}，{greeting.split('！')[0]}！"
                else:
                    greeting = f"Dear {name}, {greeting}"
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return SkillResult(
                success=True,
                data={
                    "greeting": greeting,
                    "language": language,
                    "time_of_day": time_key,
                    "formal": formal
                },
                execution_time=execution_time,
                metadata={
                    "skill": self.name,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return SkillResult(
                success=False,
                error=f"问候失败: {str(e)}",
                execution_time=execution_time
            )
    
    def validate_input(self, **kwargs) -> bool:
        """验证输入"""
        language = kwargs.get("language", "zh-CN")
        return language in self.languages