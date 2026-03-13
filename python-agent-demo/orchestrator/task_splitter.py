"""
任务拆分器
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TaskComplexity(Enum):
    """任务复杂度"""
    SIMPLE = "simple"      # 简单任务，无需拆分
    MODERATE = "moderate"  # 中等任务，可拆分为2-3个子任务
    COMPLEX = "complex"    # 复杂任务，可拆分为多个子任务


@dataclass
class Subtask:
    """子任务"""
    id: str
    name: str
    skill: str
    parameters: Dict[str, Any]
    dependencies: List[str]  # 依赖的子任务ID
    priority: int = 1


class TaskSplitter:
    """任务拆分器"""
    
    def __init__(self, max_depth: int = 5):
        self.max_depth = max_depth
        
        # 任务模式识别规则
        self.patterns = {
            "sequential": [
                "然后", "接着", "之后", "下一步",
                "then", "next", "after", "followed by"
            ],
            "parallel": [
                "同时", "并行", "一起",
                "simultaneously", "in parallel", "concurrently"
            ],
            "conditional": [
                "如果", "假如", "当", "要是",
                "if", "when", "in case", "provided that"
            ],
            "iterative": [
                "每个", "所有", "循环", "重复",
                "each", "every", "for each", "loop"
            ]
        }
    
    def analyze_complexity(self, task_description: str) -> TaskComplexity:
        """分析任务复杂度"""
        # 基于关键词的简单分析
        complexity_keywords = {
            TaskComplexity.SIMPLE: ["简单", "基本", "快速", "直接"],
            TaskComplexity.COMPLEX: ["复杂", "困难", "多个", "系列", "流程"]
        }
        
        task_lower = task_description.lower()
        
        # 检查复杂关键词
        for keyword in complexity_keywords.get(TaskComplexity.COMPLEX, []):
            if keyword in task_lower:
                return TaskComplexity.COMPLEX
        
        # 检查长度和结构
        words = task_description.split()
        if len(words) > 20:
            return TaskComplexity.COMPLEX
        elif len(words) > 10:
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.SIMPLE
    
    def split_task(self, task_description: str, skill: str, 
                  parameters: Dict[str, Any], depth: int = 0) -> List[Subtask]:
        """拆分任务"""
        if depth >= self.max_depth:
            return [Subtask(
                id=f"task_{depth}",
                name=task_description[:50] + ("..." if len(task_description) > 50 else ""),
                skill=skill,
                parameters=parameters,
                dependencies=[]
            )]
        
        complexity = self.analyze_complexity(task_description)
        
        if complexity == TaskComplexity.SIMPLE:
            # 简单任务不拆分
            return [Subtask(
                id=f"task_{depth}_0",
                name=task_description[:50] + ("..." if len(task_description) > 50 else ""),
                skill=skill,
                parameters=parameters,
                dependencies=[]
            )]
        
        elif complexity == TaskComplexity.MODERATE:
            # 中等任务拆分为2-3个子任务
            subtasks = []
            
            # 基于任务描述的关键部分拆分
            parts = self._split_by_patterns(task_description)
            
            for i, part in enumerate(parts[:3]):  # 最多3个子任务
                subtask = Subtask(
                    id=f"task_{depth}_{i}",
                    name=part[:50] + ("..." if len(part) > 50 else ""),
                    skill=skill,
                    parameters={**parameters, "subtask": part},
                    dependencies=[f"task_{depth}_{j}" for j in range(i)] if i > 0 else []
                )
                subtasks.append(subtask)
            
            return subtasks
        
        else:  # COMPLEX
            # 复杂任务递归拆分
            subtasks = []
            
            # 识别主要步骤
            steps = self._extract_steps(task_description)
            
            for i, step in enumerate(steps):
                step_subtasks = self.split_task(
                    step, skill, parameters, depth + 1
                )
                
                # 为子任务添加依赖关系
                for j, subtask in enumerate(step_subtasks):
                    # 修改ID以包含步骤信息
                    subtask.id = f"task_{depth}_{i}_{j}"
                    
                    # 添加跨步骤依赖
                    if i > 0:
                        # 当前步骤的第一个子任务依赖前一个步骤的最后一个子任务
                        if j == 0:
                            prev_last_id = f"task_{depth}_{i-1}_{len(step_subtasks)-1}"
                            subtask.dependencies.append(prev_last_id)
                    
                    subtasks.append(subtask)
            
            return subtasks
    
    def _split_by_patterns(self, text: str) -> List[str]:
        """基于模式拆分文本"""
        parts = []
        current = []
        
        sentences = text.replace('。', '.').replace('！', '!').replace('？', '?').split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # 检查是否是序列模式
            is_sequence = any(pattern in sentence for pattern in self.patterns["sequential"])
            
            if is_sequence and current:
                parts.append(' '.join(current))
                current = [sentence]
            else:
                current.append(sentence)
        
        if current:
            parts.append(' '.join(current))
        
        return parts if len(parts) > 1 else [text]
    
    def _extract_steps(self, text: str) -> List[str]:
        """提取步骤"""
        steps = []
        
        # 基于数字或字母编号的步骤
        import re
        
        # 匹配 "1. xxx" 或 "第一步" 等模式
        step_patterns = [
            r'(\d+)\.\s*(.+?)(?=\d+\.|$)',  # 1. xxx
            r'第(\d+)步[:：]\s*(.+)',        # 第1步: xxx
            r'[①②③④⑤⑥⑦⑧⑨⑩]\s*(.+)',      # ① xxx
        ]
        
        for pattern in step_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        steps.append(match[1].strip())
                    else:
                        steps.append(match.strip())
                break
        
        # 如果没有找到编号步骤，按句子拆分
        if not steps:
            sentences = re.split(r'[。！？;；]', text)
            steps = [s.strip() for s in sentences if s.strip()]
        
        return steps[:self.max_depth]  # 限制步骤数量
    
    def create_execution_plan(self, subtasks: List[Subtask]) -> Dict[str, Any]:
        """创建执行计划"""
        # 构建依赖图
        dependency_graph = {}
        for subtask in subtasks:
            dependency_graph[subtask.id] = {
                "task": subtask,
                "dependencies": subtask.dependencies,
                "dependents": []
            }
        
        # 添加依赖关系
        for subtask_id, info in dependency_graph.items():
            for dep_id in info["dependencies"]:
                if dep_id in dependency_graph:
                    dependency_graph[dep_id]["dependents"].append(subtask_id)
        
        # 拓扑排序
        execution_order = []
        visited = set()
        
        def dfs(node_id: str):
            if node_id in visited:
                return
            visited.add(node_id)
            
            for dep_id in dependency_graph[node_id]["dependencies"]:
                if dep_id in dependency_graph:
                    dfs(dep_id)
            
            execution_order.append(node_id)
        
        for subtask_id in dependency_graph:
            if subtask_id not in visited:
                dfs(subtask_id)
        
        # 分组并行任务
        parallel_groups = []
        current_group = []
        
        for task_id in execution_order:
            task_info = dependency_graph[task_id]
            
            # 如果没有依赖或依赖已在前一组，可以并行
            can_parallel = all(
                dep_id not in current_group 
                for dep_id in task_info["dependencies"]
            )
            
            if can_parallel:
                current_group.append(task_id)
            else:
                if current_group:
                    parallel_groups.append(current_group)
                current_group = [task_id]
        
        if current_group:
            parallel_groups.append(current_group)
        
        return {
            "execution_order": execution_order,
            "parallel_groups": parallel_groups,
            "dependency_graph": dependency_graph,
            "total_tasks": len(subtasks),
            "max_parallel": max(len(group) for group in parallel_groups) if parallel_groups else 0
        }