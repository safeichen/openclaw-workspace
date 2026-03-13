"""
状态管理模块
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class TaskResult(BaseModel):
    """任务结果"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskState(BaseModel):
    """任务状态"""
    task_id: str
    name: str
    skill: str
    status: TaskStatus = TaskStatus.PENDING
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[TaskResult] = None
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    parent_task_id: Optional[str] = None
    child_tasks: List[str] = Field(default_factory=list)
    
    def start(self):
        """开始任务"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
    
    def complete(self, success: bool, data: Any = None, error: str = None):
        """完成任务"""
        self.status = TaskStatus.SUCCESS if success else TaskStatus.FAILED
        self.completed_at = datetime.now()
        
        execution_time = 0.0
        if self.started_at and self.completed_at:
            execution_time = (self.completed_at - self.started_at).total_seconds()
        
        self.result = TaskResult(
            success=success,
            data=data,
            error=error,
            execution_time=execution_time
        )
    
    def retry(self):
        """重试任务"""
        if self.retry_count < self.max_retries:
            self.status = TaskStatus.RETRYING
            self.retry_count += 1
            self.started_at = None
            self.completed_at = None
            self.result = None
            return True
        return False
    
    def cancel(self):
        """取消任务"""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()


class AgentState(BaseModel):
    """代理状态"""
    agent_id: str
    current_tasks: Dict[str, TaskState] = Field(default_factory=dict)
    completed_tasks: Dict[str, TaskState] = Field(default_factory=dict)
    failed_tasks: Dict[str, TaskState] = Field(default_factory=dict)
    task_history: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    
    def add_task(self, task: TaskState):
        """添加任务"""
        self.current_tasks[task.task_id] = task
        self.task_history.append(task.task_id)
    
    def update_task(self, task_id: str, **kwargs):
        """更新任务"""
        if task_id in self.current_tasks:
            task = self.current_tasks[task_id]
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
    
    def complete_task(self, task_id: str, success: bool, data: Any = None, error: str = None):
        """完成任务"""
        if task_id in self.current_tasks:
            task = self.current_tasks[task_id]
            task.complete(success, data, error)
            
            # 移动到相应的完成列表
            del self.current_tasks[task_id]
            if success:
                self.completed_tasks[task_id] = task
            else:
                self.failed_tasks[task_id] = task
    
    def get_task(self, task_id: str) -> Optional[TaskState]:
        """获取任务"""
        if task_id in self.current_tasks:
            return self.current_tasks[task_id]
        elif task_id in self.completed_tasks:
            return self.completed_tasks[task_id]
        elif task_id in self.failed_tasks:
            return self.failed_tasks[task_id]
        return None
    
    def get_running_tasks(self) -> List[TaskState]:
        """获取运行中的任务"""
        return [task for task in self.current_tasks.values() 
                if task.status == TaskStatus.RUNNING]
    
    def get_pending_tasks(self) -> List[TaskState]:
        """获取等待中的任务"""
        return [task for task in self.current_tasks.values() 
                if task.status == TaskStatus.PENDING]
    
    def update_metrics(self, **kwargs):
        """更新指标"""
        self.metrics.update(kwargs)