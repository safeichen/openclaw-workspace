"""
计算器技能
"""

import asyncio
import re
from typing import Dict, Any
from datetime import datetime
from .base import BaseSkill, SkillResult


class CalculatorSkill(BaseSkill):
    """计算器技能"""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="执行数学计算"
        )
        self.operations = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b if b != 0 else float('inf'),
            "^": lambda a, b: a ** b,
            "%": lambda a, b: a % b,
        }
    
    async def execute(self, **kwargs) -> SkillResult:
        """执行计算"""
        start_time = datetime.now()
        
        try:
            # 获取参数
            expression = kwargs.get("expression", "")
            precision = kwargs.get("precision", 6)
            
            if not expression:
                return SkillResult(
                    success=False,
                    error="未提供计算表达式",
                    execution_time=(datetime.now() - start_time).total_seconds()
                )
            
            # 清理表达式
            expression = expression.strip()
            
            # 方法1: 直接计算简单表达式
            result = self._calculate_simple(expression, precision)
            
            # 方法2: 如果方法1失败，尝试解析复杂表达式
            if result is None:
                result = self._calculate_complex(expression, precision)
            
            if result is None:
                raise ValueError(f"无法计算表达式: {expression}")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return SkillResult(
                success=True,
                data={
                    "expression": expression,
                    "result": result,
                    "precision": precision,
                    "formatted": f"{result:.{precision}f}" if isinstance(result, float) else str(result)
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
                error=f"计算失败: {str(e)}",
                execution_time=execution_time
            )
    
    def _calculate_simple(self, expression: str, precision: int) -> Any:
        """计算简单表达式"""
        try:
            # 安全地评估表达式
            # 注意：在生产环境中应该使用更安全的评估方法
            result = eval(expression, {"__builtins__": {}}, {})
            
            # 处理浮点数精度
            if isinstance(result, float):
                result = round(result, precision)
            
            return result
        except:
            return None
    
    def _calculate_complex(self, expression: str, precision: int) -> Any:
        """计算复杂表达式"""
        try:
            # 解析表达式
            tokens = self._tokenize(expression)
            if not tokens:
                return None
            
            # 转换为RPN并计算
            rpn = self._shunting_yard(tokens)
            result = self._evaluate_rpn(rpn)
            
            if isinstance(result, float):
                result = round(result, precision)
            
            return result
        except:
            return None
    
    def _tokenize(self, expression: str) -> list:
        """分词"""
        # 简单的分词逻辑
        tokens = []
        current = ""
        
        for char in expression:
            if char.isdigit() or char == '.':
                current += char
            elif char in self.operations or char in "()":
                if current:
                    tokens.append(current)
                    current = ""
                tokens.append(char)
            elif char.isspace():
                if current:
                    tokens.append(current)
                    current = ""
            else:
                return []  # 非法字符
        
        if current:
            tokens.append(current)
        
        return tokens
    
    def _shunting_yard(self, tokens: list) -> list:
        """调度场算法转换为RPN"""
        precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
        output = []
        stack = []
        
        for token in tokens:
            if token.replace('.', '').isdigit():  # 数字
                output.append(float(token) if '.' in token else int(token))
            elif token in self.operations:  # 操作符
                while (stack and stack[-1] in self.operations and
                       precedence.get(stack[-1], 0) >= precedence.get(token, 0)):
                    output.append(stack.pop())
                stack.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()  # 弹出 '('
        
        while stack:
            output.append(stack.pop())
        
        return output
    
    def _evaluate_rpn(self, rpn: list) -> Any:
        """计算RPN表达式"""
        stack = []
        
        for token in rpn:
            if isinstance(token, (int, float)):
                stack.append(token)
            elif token in self.operations:
                if len(stack) < 2:
                    raise ValueError("无效的表达式")
                b = stack.pop()
                a = stack.pop()
                result = self.operations[token](a, b)
                stack.append(result)
        
        if len(stack) != 1:
            raise ValueError("无效的表达式")
        
        return stack[0]
    
    def validate_input(self, **kwargs) -> bool:
        """验证输入"""
        expression = kwargs.get("expression", "")
        if not expression:
            return False
        
        # 简单的安全检查
        dangerous_patterns = [
            "import", "__", "eval", "exec", "compile",
            "open", "file", "os.", "sys.", "subprocess"
        ]
        
        for pattern in dangerous_patterns:
            if pattern in expression.lower():
                return False
        
        return True