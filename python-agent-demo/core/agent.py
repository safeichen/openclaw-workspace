"""
主代理类
"""

import asyncio
import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .state import AgentState, TaskState, TaskStatus
from .config import Config
from skills import SKILL_REGISTRY, BaseSkill
from orchestrator import TaskSplitter, RetryManager


class Agent:
    """智能代理"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.agent_id = str(uuid.uuid4())
        self.config = Config(config_path)
        self.state = AgentState(agent_id=self.agent_id)
        
        # 初始化技能
        self.skills: Dict[str, BaseSkill] = {}
        self._init_skills()
        
        # 初始化编排器
        self.task_splitter = TaskSplitter()
        self.retry_manager = RetryManager()
        
        # 初始化日志
        self._init_logging()
        
        self.logger.info(f"Agent {self.agent_id} 初始化完成")
    
    def _init_logging(self):
        """初始化日志"""
        logging_config = self.config.load().logging
        
        self.logger = logging.getLogger(f"Agent.{self.agent_id}")
        self.logger.setLevel(getattr(logging, logging_config.level))
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, logging_config.level))
        console_formatter = logging.Formatter(logging_config.format)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器
        try:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                logging_config.file,
                maxBytes=logging_config.max_size,
                backupCount=logging_config.backup_count
            )
            file_handler.setLevel(getattr(logging, logging_config.level))
            file_formatter = logging.Formatter(logging_config.format)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            self.logger.warning(f"无法初始化文件日志: {e}")
    
    def _init_skills(self):
        """初始化技能"""
        agent_config = self.config.load()
        
        for skill_name, skill_class in SKILL_REGISTRY.items():
            skill_config = agent_config.skills.get(skill_name)
            
            if skill_config and skill_config.enabled:
                try:
                    skill = skill_class()
                    
                    # 应用配置
                    if skill_config.parameters:
                        skill.configure(**skill_config.parameters)
                    
                    self.skills[skill_name] = skill
                    self.logger.info(f"技能 '{skill_name}' 加载成功")
                    
                except Exception as e:
                    self.logger.error(f"技能 '{skill_name}' 加载失败: {e}")
    
    async def run(self, task_description: str, **kwargs) -> Dict[str, Any]:
        """运行任务"""
        task_id = str(uuid.uuid4())
        
        # 创建任务状态
        task = TaskState(
            task_id=task_id,
            name=task_description[:100],
            skill=kwargs.get("skill", "auto"),
            parameters=kwargs
        )
        
        self.state.add_task(task)
        self.logger.info(f"开始任务 {task_id}: {task_description}")
        
        try:
            # 开始任务
            task.start()
            
            # 执行任务
            result = await self._execute_task(task)
            
            # 完成任务
            self.state.complete_task(task_id, True, result)
            
            self.logger.info(f"任务 {task_id} 完成: {result.get('summary', '成功')}")
            
            return {
                "success": True,
                "task_id": task_id,
                "result": result,
                "execution_time": task.result.execution_time if task.result else 0
            }
            
        except Exception as e:
            # 任务失败
            self.state.complete_task(task_id, False, error=str(e))
            
            self.logger.error(f"任务 {task_id} 失败: {e}")
            
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e),
                "execution_time": task.result.execution_time if task.result else 0
            }
    
    async def _execute_task(self, task: TaskState) -> Dict[str, Any]:
        """执行单个任务"""
        # 自动选择技能
        skill_name = self._select_skill(task)
        
        if skill_name not in self.skills:
            raise ValueError(f"未找到技能: {skill_name}")
        
        skill = self.skills[skill_name]
        
        # 验证输入
        if not skill.validate_input(**task.parameters):
            raise ValueError(f"技能 '{skill_name}' 输入验证失败")
        
        # 使用重试管理器执行
        async def execute_skill():
            skill_result = await skill.execute(**task.parameters)
            
            if not skill_result.success:
                raise Exception(skill_result.error or "技能执行失败")
            
            return skill_result.data
        
        try:
            result = await self.retry_manager.execute_with_retry(
                execute_skill,
                task_name=f"{skill_name}_{task.task_id}",
            )
            
            return {
                "skill": skill_name,
                "data": result,
                "summary": self._generate_summary(skill_name, result)
            }
            
        except Exception as e:
            # 检查是否需要拆分任务
            if self.config.load().orchestrator.enable_task_splitting:
                return await self._handle_complex_task(task, skill_name, str(e))
            else:
                raise
    
    async def _handle_complex_task(self, task: TaskState, skill_name: str, 
                                  error: str) -> Dict[str, Any]:
        """处理复杂任务（拆分执行）"""
        self.logger.info(f"尝试拆分复杂任务: {task.name}")
        
        # 拆分任务
        subtasks = self.task_splitter.split_task(
            task.name, skill_name, task.parameters
        )
        
        if len(subtasks) <= 1:
            raise Exception(f"任务无法拆分: {error}")
        
        # 创建执行计划
        execution_plan = self.task_splitter.create_execution_plan(subtasks)
        
        self.logger.info(f"任务拆分为 {len(subtasks)} 个子任务")
        
        # 执行子任务
        results = {}
        task_results = {}
        
        for group in execution_plan["parallel_groups"]:
            # 并行执行组内任务
            group_tasks = []
            for task_id in group:
                subtask = next(s for s in subtasks if s.id == task_id)
                group_tasks.append(self._execute_subtask(subtask, results))
            
            # 等待组内所有任务完成
            group_results = await asyncio.gather(*group_tasks, return_exceptions=True)
            
            # 处理结果
            for i, task_id in enumerate(group):
                result = group_results[i]
                
                if isinstance(result, Exception):
                    self.logger.error(f"子任务 {task_id} 失败: {result}")
                    # 对于关键路径上的失败，可以在这里决定是否继续
                else:
                    results[task_id] = result
                    task_results[task_id] = result
        
        # 合并结果
        merged_result = self._merge_results(task_results)
        
        return {
            "skill": skill_name,
            "data": merged_result,
            "summary": f"任务已拆分为 {len(subtasks)} 个子任务执行",
            "subtasks": {
                "total": len(subtasks),
                "successful": len(task_results),
                "execution_plan": execution_plan
            }
        }
    
    async def _execute_subtask(self, subtask, context_results: Dict[str, Any]) -> Any:
        """执行子任务"""
        # 检查依赖是否满足
        for dep_id in subtask.dependencies:
            if dep_id not in context_results:
                raise Exception(f"依赖任务 {dep_id} 未完成")
        
        # 合并依赖结果到参数
        parameters = subtask.parameters.copy()
        for dep_id in subtask.dependencies:
            if dep_id in context_results:
                parameters[f"dep_{dep_id}"] = context_results[dep_id]
        
        # 执行子任务
        if subtask.skill in self.skills:
            skill = self.skills[subtask.skill]
            skill_result = await skill.execute(**parameters)
            
            if skill_result.success:
                return skill_result.data
            else:
                raise Exception(skill_result.error or "子任务执行失败")
        else:
            raise Exception(f"未找到技能: {subtask.skill}")
    
    def _select_skill(self, task: TaskState) -> str:
        """自动选择技能"""
        # 如果指定了技能，直接使用
        if task.skill != "auto" and task.skill in self.skills:
            return task.skill
        
        # 基于任务描述选择技能
        description = task.name.lower()
        
        if any(keyword in description for keyword in ["问候", "hello", "hi", "greet"]):
            return "greeting"
        elif any(keyword in description for keyword in ["计算", "calculate", "math", "算"]):
            return "calculator"
        elif any(keyword in description for keyword in ["天气", "weather", "气候"]):
            return "weather"
        elif any(keyword in description for keyword in ["文件", "file", "处理", "process"]):
            return "file_processor"
        else:
            # 默认使用第一个可用技能
            return next(iter(self.skills.keys())) if self.skills else "greeting"
    
    def _generate_summary(self, skill_name: str, result: Any) -> str:
        """生成结果摘要"""
        if skill_name == "greeting":
            return result.get("greeting", "问候完成")
        elif skill_name == "calculator":
            data = result.get("data", {})
            return f"计算结果: {data.get('formatted', 'N/A')}"
        elif skill_name == "weather":
            current = result.get("current", {})
            return f"{current.get('city', '未知城市')} 天气: {current.get('weather', '未知')} {current.get('temperature', 'N/A')}°C"
        else:
            return "任务执行完成"
    
    def _merge_results(self, task_results: Dict[str, Any]) -> Dict[str, Any]:
        """合并子任务结果"""
        merged = {
            "merged_from_subtasks": True,
            "total_subtasks": len(task_results),
            "subtask_results": task_results,
            "summary": f"合并了 {len(task_results)} 个子任务的结果"
        }
        
        # 尝试提取关键信息
        all_data = []
        for task_id, result in task_results.items():
            if isinstance(result, dict):
                all_data.append(result)
        
        if all_data:
            merged["combined_data"] = all_data
        
        return merged
    
    def get_status(self) -> Dict[str, Any]:
        """获取代理状态"""
        config = self.config.load()
        
        return {
            "agent_id": self.agent_id,
            "name": config.name,
            "version": config.version,
            "status": "running",
            "skills": {
                name: skill.get_info() 
                for name, skill in self.skills.items()
            },
            "metrics": {
                "total_tasks": len(self.state.task_history),
                "running_tasks": len(self.state.get_running_tasks()),
                "pending_tasks": len(self.state.get_pending_tasks()),
                "completed_tasks": len(self.state.completed_tasks),
                "failed_tasks": len(self.state.failed_tasks),
                "retry_success_rate": self.retry_manager.get_success_rate(),
                "average_retries": self.retry_manager.get_average_retries(),
            },
            "config": {
                "orchestrator": config.orchestrator.dict(),
                "performance": config.performance.dict(),
            }
        }
    
    async def run_with_retry(self, task_description: str, max_retries: int = 3, **kwargs) -> Dict[str, Any]:
        """带重试的运行"""
        original_max_retries = self.config.load().orchestrator.max_retries
        self.config.update_skill_config("orchestrator", max_retries=max_retries)
        
        try:
            return await self.run(task_description, **kwargs)
        finally:
            self.config.update_skill_config("orchestrator", max_retries=original_max_retries)
    
    async def run_with_split(self, task_description: str, **kwargs) -> Dict[str, Any]:
        """带任务拆分的运行"""
        # 强制启用任务拆分
        original_enable = self.config.load().orchestrator.enable_task_splitting
        self.config.update_skill_config("orchestrator", enable_task_splitting=True)
        
        try:
            return await self.run(task_description, **kwargs)
        finally:
            self.config.update_skill_config("orchestrator", enable_task_splitting=original_enable)
    
    def create_workflow(self, steps: List[str]) -> Dict[str, Any]:
        """创建工作流"""
        workflow_id = str(uuid.uuid4())
        
        workflow = {
            "workflow_id": workflow_id,
            "steps": steps,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        self.logger.info(f"创建工作流 {workflow_id}，包含 {len(steps)} 个步骤")
        
        return workflow
    
    async def execute_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """执行工作流"""
        workflow_id = workflow["workflow_id"]
        steps = workflow["steps"]
        
        self.logger.info(f"开始执行工作流 {workflow_id}")
        
        results = []
        workflow["status"] = "running"
        workflow["started_at"] = datetime.now().isoformat()
        
        for i, step in enumerate(steps):
            try:
                self.logger.info(f"执行工作流步骤 {i+1}/{len(steps)}: {step}")
                
                # 解析步骤（简单格式：skill:description）
                if ":" in step:
                    skill, description = step.split(":", 1)
                    result = await self.run(description.strip(), skill=skill.strip())
                else:
                    result = await self.run(step.strip())
                
                results.append({
                    "step": i + 1,
                    "description": step,
                    "result": result
                })
                
            except Exception as e:
                self.logger.error(f"工作流步骤 {i+1} 失败: {e}")
                results.append({
                    "step": i + 1,
                    "description": step,
                    "error": str(e),
                    "success": False
                })
                
                # 可以在这里决定是否继续执行后续步骤
                # break  # 如果失败则停止
        
        workflow["status"] = "completed"
        workflow["completed_at"] = datetime.now().isoformat()
        workflow["results"] = results
        
        success_count = sum(1 for r in results if r.get("success", True))
        
        self.logger.info(f"工作流 {workflow_id} 执行完成，成功率: {success_count}/{len(steps)}")
        
        return {
            "workflow_id": workflow_id,
            "success": success_count == len(steps),
            "total_steps": len(steps),
            "successful_steps": success_count,
            "results": results,
            "workflow": workflow
        }