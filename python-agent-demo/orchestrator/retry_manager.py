"""
重试管理器
"""

import asyncio
import time
from typing import Dict, Any, Optional, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum
import random


class RetryStrategy(Enum):
    """重试策略"""
    FIXED = "fixed"          # 固定间隔
    EXPONENTIAL = "exponential"  # 指数退避
    RANDOM = "random"        # 随机间隔
    LINEAR = "linear"        # 线性增加


@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3
    base_delay: float = 1.0  # 基础延迟（秒）
    max_delay: float = 30.0  # 最大延迟（秒）
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    jitter: bool = True      # 是否添加抖动


class RetryManager:
    """重试管理器"""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.retry_stats: Dict[str, Any] = {}
    
    async def execute_with_retry(
        self,
        task_func: Callable[..., Awaitable[Any]],
        task_name: str = "unknown",
        *args,
        **kwargs
    ) -> Any:
        """带重试的执行"""
        retry_count = 0
        last_error = None
        
        # 初始化统计
        task_key = f"{task_name}_{int(time.time())}"
        self.retry_stats[task_key] = {
            "task_name": task_name,
            "start_time": time.time(),
            "retries": [],
            "success": False
        }
        
        while retry_count <= self.config.max_retries:
            try:
                start_time = time.time()
                result = await task_func(*args, **kwargs)
                end_time = time.time()
                
                # 更新统计
                self.retry_stats[task_key]["success"] = True
                self.retry_stats[task_key]["end_time"] = end_time
                self.retry_stats[task_key]["execution_time"] = end_time - start_time
                self.retry_stats[task_key]["final_result"] = result
                
                return result
                
            except Exception as e:
                last_error = e
                retry_count += 1
                
                # 记录重试
                retry_info = {
                    "retry_number": retry_count,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "timestamp": time.time()
                }
                self.retry_stats[task_key]["retries"].append(retry_info)
                
                if retry_count > self.config.max_retries:
                    break
                
                # 计算等待时间
                wait_time = self._calculate_wait_time(retry_count)
                
                # 添加抖动（如果启用）
                if self.config.jitter:
                    wait_time = self._add_jitter(wait_time)
                
                # 记录等待时间
                retry_info["wait_time"] = wait_time
                
                # 等待
                await asyncio.sleep(wait_time)
        
        # 所有重试都失败
        self.retry_stats[task_key]["end_time"] = time.time()
        self.retry_stats[task_key]["final_error"] = str(last_error)
        
        raise last_error
    
    def _calculate_wait_time(self, retry_count: int) -> float:
        """计算等待时间"""
        base = self.config.base_delay
        max_delay = self.config.max_delay
        
        if self.config.strategy == RetryStrategy.FIXED:
            wait_time = base
        
        elif self.config.strategy == RetryStrategy.EXPONENTIAL:
            wait_time = base * (2 ** (retry_count - 1))
        
        elif self.config.strategy == RetryStrategy.LINEAR:
            wait_time = base * retry_count
        
        elif self.config.strategy == RetryStrategy.RANDOM:
            wait_time = random.uniform(base, base * retry_count)
        
        else:
            wait_time = base
        
        # 限制最大等待时间
        return min(wait_time, max_delay)
    
    def _add_jitter(self, wait_time: float) -> float:
        """添加抖动"""
        # 添加 ±20% 的随机抖动
        jitter_factor = random.uniform(0.8, 1.2)
        return wait_time * jitter_factor
    
    def should_retry(self, error: Exception) -> bool:
        """判断是否应该重试"""
        # 可重试的错误类型
        retryable_errors = [
            "TimeoutError",
            "ConnectionError",
            "NetworkError",
            "ServiceUnavailable",
            "RateLimitExceeded",
            "TemporaryFailure"
        ]
        
        error_type = type(error).__name__
        
        # 检查错误消息中的关键词
        error_msg = str(error).lower()
        retryable_keywords = [
            "timeout", "connection", "network", "temporary",
            "busy", "overload", "rate limit", "quota",
            "retry", "try again", "service unavailable"
        ]
        
        if any(keyword in error_msg for keyword in retryable_keywords):
            return True
        
        return error_type in retryable_errors
    
    def get_retry_stats(self, task_key: Optional[str] = None) -> Dict[str, Any]:
        """获取重试统计"""
        if task_key:
            return self.retry_stats.get(task_key, {})
        return self.retry_stats
    
    def reset_stats(self, task_key: Optional[str] = None):
        """重置统计"""
        if task_key:
            if task_key in self.retry_stats:
                del self.retry_stats[task_key]
        else:
            self.retry_stats.clear()
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        if not self.retry_stats:
            return 0.0
        
        successful = sum(1 for stats in self.retry_stats.values() 
                        if stats.get("success", False))
        
        return successful / len(self.retry_stats)
    
    def get_average_retries(self) -> float:
        """获取平均重试次数"""
        if not self.retry_stats:
            return 0.0
        
        total_retries = sum(len(stats.get("retries", [])) 
                           for stats in self.retry_stats.values())
        
        return total_retries / len(self.retry_stats)
    
    def create_circuit_breaker(self, failure_threshold: int = 5, 
                              reset_timeout: float = 60.0):
        """创建熔断器"""
        return CircuitBreaker(self, failure_threshold, reset_timeout)


class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, retry_manager: RetryManager, 
                 failure_threshold: int = 5, 
                 reset_timeout: float = 60.0):
        self.retry_manager = retry_manager
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def execute(self, task_func: Callable[..., Awaitable[Any]], 
                     *args, **kwargs) -> Any:
        """通过熔断器执行"""
        current_time = time.time()
        
        # 检查熔断器状态
        if self.state == "OPEN":
            # 检查是否应该尝试恢复
            if current_time - self.last_failure_time > self.reset_timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. Last failure: {self.last_failure_time}"
                )
        
        try:
            # 执行任务
            result = await task_func(*args, **kwargs)
            
            # 成功执行，重置熔断器
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            # 执行失败
            self.failure_count += 1
            self.last_failure_time = current_time
            
            # 检查是否应该打开熔断器
            if (self.failure_count >= self.failure_threshold and 
                self.state != "OPEN"):
                self.state = "OPEN"
            
            raise
    
    def get_state(self) -> str:
        """获取熔断器状态"""
        return self.state
    
    def reset(self):
        """重置熔断器"""
        self.state = "CLOSED"
        self.failure_count = 0
        self.last_failure_time = 0


class CircuitBreakerOpenError(Exception):
    """熔断器打开错误"""
    pass