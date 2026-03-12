"""
重试处理器
处理技能执行失败时的重试逻辑
"""

import asyncio
import time
from typing import Callable, Any, Optional, Dict
from functools import wraps
from loguru import logger


class RetryHandler:
    """重试处理器"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 30.0,
        backoff_factor: float = 2.0,
        retry_exceptions: tuple = (Exception,)
    ):
        """
        初始化重试处理器
        
        Args:
            max_retries: 最大重试次数
            initial_delay: 初始延迟（秒）
            max_delay: 最大延迟（秒）
            backoff_factor: 退避因子
            retry_exceptions: 需要重试的异常类型
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.retry_exceptions = retry_exceptions
        
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        执行函数并支持重试
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            Any: 函数执行结果
            
        Raises:
            Exception: 重试次数用尽后抛出最后一个异常
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"重试尝试 {attempt}/{self.max_retries}")
                
                # 执行函数
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # 如果成功，返回结果
                if attempt > 0:
                    logger.success(f"重试成功 (尝试 {attempt})")
                return result
                
            except self.retry_exceptions as e:
                last_exception = e
                
                # 检查是否还有重试次数
                if attempt < self.max_retries:
                    # 计算延迟时间
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"执行失败 (尝试 {attempt + 1}/{self.max_retries + 1}): "
                        f"{type(e).__name__}: {str(e)}. "
                        f"{delay:.1f}秒后重试..."
                    )
                    
                    # 等待延迟
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"重试次数用尽: {type(e).__name__}: {str(e)}")
        
        # 重试次数用尽，抛出最后一个异常
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """
        计算重试延迟
        
        Args:
            attempt: 当前尝试次数
            
        Returns:
            float: 延迟时间（秒）
        """
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        return min(delay, self.max_delay)
    
    def create_retry_decorator(self) -> Callable:
        """
        创建重试装饰器
        
        Returns:
            Callable: 重试装饰器
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self.execute_with_retry(func, *args, **kwargs)
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # 对于同步函数，我们需要在事件循环中运行
                async def async_func():
                    return await self.execute_with_retry(func, *args, **kwargs)
                
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                return loop.run_until_complete(async_func())
            
            # 根据函数类型返回相应的包装器
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    async def execute_with_custom_retry(
        self,
        func: Callable,
        retry_condition: Callable[[Exception], bool],
        *args,
        **kwargs
    ) -> Any:
        """
        执行函数并使用自定义重试条件
        
        Args:
            func: 要执行的函数
            retry_condition: 重试条件函数，接收异常并返回是否重试
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            Any: 函数执行结果
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"自定义重试尝试 {attempt}/{self.max_retries}")
                
                # 执行函数
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # 如果成功，返回结果
                if attempt > 0:
                    logger.success(f"自定义重试成功 (尝试 {attempt})")
                return result
                
            except Exception as e:
                last_exception = e
                
                # 检查是否满足重试条件
                if attempt < self.max_retries and retry_condition(e):
                    # 计算延迟时间
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"执行失败 (尝试 {attempt + 1}/{self.max_retries + 1}): "
                        f"{type(e).__name__}: {str(e)}. "
                        f"{delay:.1f}秒后重试..."
                    )
                    
                    # 等待延迟
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"重试条件不满足或次数用尽: {type(e).__name__}: {str(e)}")
                    raise
        
        # 重试次数用尽，抛出最后一个异常
        raise last_exception


# 全局重试处理器实例
default_retry_handler = RetryHandler()


def retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
    retry_exceptions: tuple = (Exception,)
):
    """
    重试装饰器工厂函数
    
    Args:
        max_retries: 最大重试次数
        initial_delay: 初始延迟（秒）
        max_delay: 最大延迟（秒）
        backoff_factor: 退避因子
        retry_exceptions: 需要重试的异常类型
        
    Returns:
        Callable: 重试装饰器
    """
    retry_handler = RetryHandler(
        max_retries=max_retries,
        initial_delay=initial_delay,
        max_delay=max_delay,
        backoff_factor=backoff_factor,
        retry_exceptions=retry_exceptions
    )
    
    return retry_handler.create_retry_decorator()