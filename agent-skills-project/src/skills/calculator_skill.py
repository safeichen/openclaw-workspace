"""
计算器技能
执行数学计算
"""

import re
import ast
from typing import Any, Dict
from loguru import logger
from .base_skill import BaseSkill, SkillInput, SkillOutput


class CalculatorSkill(BaseSkill):
    """计算器技能"""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="执行数学计算，支持加减乘除、幂运算等",
            max_retries=2
        )
        
    async def execute(self, input_data: SkillInput) -> SkillOutput:
        """
        执行计算
        
        Args:
            input_data: 技能输入
            
        Returns:
            SkillOutput: 计算结果
        """
        logger.info(f"执行计算器技能: {input_data.task}")
        
        try:
            # 提取数学表达式
            expression = self._extract_expression(input_data.task)
            if not expression:
                return SkillOutput(
                    success=False,
                    result=None,
                    error="未找到有效的数学表达式",
                    metadata={"task": input_data.task}
                )
            
            # 安全评估表达式
            result = self._safe_eval(expression)
            
            logger.success(f"计算成功: {expression} = {result}")
            return SkillOutput(
                success=True,
                result=result,
                metadata={
                    "expression": expression,
                    "task": input_data.task,
                    "skill": self.name
                }
            )
            
        except Exception as e:
            logger.error(f"计算失败: {str(e)}")
            return SkillOutput(
                success=False,
                result=None,
                error=str(e),
                metadata={"task": input_data.task, "error_type": type(e).__name__}
            )
    
    def _extract_expression(self, task: str) -> str:
        """
        从任务描述中提取数学表达式
        
        Args:
            task: 任务描述
            
        Returns:
            str: 数学表达式
        """
        # 移除常见的前缀
        prefixes = ["计算", "求", "计算一下", "算一下", "计算:", "计算："]
        for prefix in prefixes:
            if task.startswith(prefix):
                task = task[len(prefix):].strip()
        
        # 提取数学表达式部分
        # 匹配常见的数学表达式模式
        patterns = [
            r'[\d+\-*/^().\s]+=',  # 包含等号的表达式
            r'[\d+\-*/^().\s]+',   # 纯表达式
        ]
        
        for pattern in patterns:
            match = re.search(pattern, task)
            if match:
                expression = match.group().strip()
                # 清理表达式
                expression = expression.replace(' ', '')
                if expression.endswith('='):
                    expression = expression[:-1]
                return expression
        
        return task.strip()
    
    def _safe_eval(self, expression: str) -> Any:
        """
        安全评估数学表达式
        
        Args:
            expression: 数学表达式
            
        Returns:
            Any: 计算结果
            
        Raises:
            ValueError: 表达式无效
            ZeroDivisionError: 除零错误
        """
        # 定义安全的操作符
        safe_operators = {
            ast.Add: lambda a, b: a + b,
            ast.Sub: lambda a, b: a - b,
            ast.Mult: lambda a, b: a * b,
            ast.Div: lambda a, b: a / b,
            ast.Pow: lambda a, b: a ** b,
            ast.USub: lambda a: -a,
            ast.UAdd: lambda a: +a,
        }
        
        def _eval_node(node):
            if isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.BinOp):
                left = _eval_node(node.left)
                right = _eval_node(node.right)
                operator_type = type(node.op)
                if operator_type in safe_operators:
                    return safe_operators[operator_type](left, right)
                else:
                    raise ValueError(f"不支持的运算符: {operator_type}")
            elif isinstance(node, ast.UnaryOp):
                operand = _eval_node(node.operand)
                operator_type = type(node.op)
                if operator_type in safe_operators:
                    return safe_operators[operator_type](operand)
                else:
                    raise ValueError(f"不支持的运算符: {operator_type}")
            else:
                raise ValueError(f"不支持的表达式节点: {type(node)}")
        
        try:
            tree = ast.parse(expression, mode='eval')
            return _eval_node(tree.body)
        except ZeroDivisionError:
            raise ZeroDivisionError("除零错误")
        except Exception as e:
            raise ValueError(f"表达式无效: {str(e)}")
    
    def get_keywords(self):
        """获取技能关键词"""
        return [
            "计算", "算", "加", "减", "乘", "除", 
            "数学", "算式", "表达式", "等于", "结果"
        ]