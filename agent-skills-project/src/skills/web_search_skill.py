"""
网络搜索技能
模拟网络搜索功能
"""

import asyncio
import random
from typing import Any, Dict, List
from loguru import logger
from .base_skill import BaseSkill, SkillInput, SkillOutput


class WebSearchSkill(BaseSkill):
    """网络搜索技能（模拟）"""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="搜索网络信息，获取相关内容和链接",
            max_retries=3
        )
        # 模拟的搜索结果数据库
        self._search_database = {
            "python": [
                {
                    "title": "Python官方文档",
                    "url": "https://docs.python.org",
                    "snippet": "Python是一种解释型、面向对象、动态数据类型的高级程序设计语言。",
                    "relevance": 0.95
                },
                {
                    "title": "Python教程 - 菜鸟教程",
                    "url": "https://www.runoob.com/python",
                    "snippet": "Python是一种解释型语言，这意味着开发过程中没有了编译这个环节。",
                    "relevance": 0.85
                }
            ],
            "天气": [
                {
                    "title": "中国天气网",
                    "url": "http://www.weather.com.cn",
                    "snippet": "提供全国天气预报、气象预警、空气质量等信息。",
                    "relevance": 0.90
                }
            ],
            "新闻": [
                {
                    "title": "新浪新闻",
                    "url": "https://news.sina.com.cn",
                    "snippet": "最新国内外新闻，涵盖政治、经济、社会、体育等各个领域。",
                    "relevance": 0.88
                }
            ]
        }
        
    async def execute(self, input_data: SkillInput) -> SkillOutput:
        """
        执行网络搜索
        
        Args:
            input_data: 技能输入
            
        Returns:
            SkillOutput: 搜索结果
        """
        logger.info(f"执行网络搜索: {input_data.task}")
        
        try:
            # 模拟网络延迟
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # 提取搜索关键词
            query = self._extract_query(input_data.task)
            if not query:
                return SkillOutput(
                    success=False,
                    result=None,
                    error="未找到有效的搜索关键词",
                    metadata={"task": input_data.task}
                )
            
            # 执行搜索
            results = await self._search(query)
            
            if not results:
                logger.warning(f"未找到相关结果: {query}")
                return SkillOutput(
                    success=True,
                    result=[],
                    metadata={
                        "query": query,
                        "result_count": 0,
                        "skill": self.name
                    }
                )
            
            logger.success(f"搜索成功: 找到 {len(results)} 条结果")
            return SkillOutput(
                success=True,
                result=results,
                metadata={
                    "query": query,
                    "result_count": len(results),
                    "skill": self.name
                }
            )
            
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return SkillOutput(
                success=False,
                result=None,
                error=str(e),
                metadata={"task": input_data.task, "error_type": type(e).__name__}
            )
    
    def _extract_query(self, task: str) -> str:
        """
        从任务描述中提取搜索关键词
        
        Args:
            task: 任务描述
            
        Returns:
            str: 搜索关键词
        """
        # 移除常见的前缀
        prefixes = ["搜索", "查找", "查询", "搜一下", "搜索:", "搜索："]
        for prefix in prefixes:
            if task.startswith(prefix):
                task = task[len(prefix):].strip()
        
        # 提取引号内的内容
        import re
        quote_pattern = r'["\'](.*?)["\']'
        matches = re.findall(quote_pattern, task)
        if matches:
            return matches[0]
        
        # 否则返回整个任务描述
        return task.strip()
    
    async def _search(self, query: str) -> List[Dict[str, Any]]:
        """
        执行搜索（模拟）
        
        Args:
            query: 搜索关键词
            
        Returns:
            List[Dict]: 搜索结果列表
        """
        # 在数据库中查找
        results = []
        query_lower = query.lower()
        
        for keyword, items in self._search_database.items():
            if keyword.lower() in query_lower:
                # 添加相关性调整
                for item in items:
                    # 根据查询匹配度调整相关性
                    adjusted_item = item.copy()
                    # 模拟相关性计算
                    adjusted_item["relevance"] = min(
                        0.99, 
                        adjusted_item["relevance"] + random.uniform(-0.1, 0.1)
                    )
                    results.append(adjusted_item)
        
        # 如果没有找到，生成模拟结果
        if not results:
            results = await self._generate_mock_results(query)
        
        # 按相关性排序
        results.sort(key=lambda x: x["relevance"], reverse=True)
        
        # 限制结果数量
        return results[:5]
    
    async def _generate_mock_results(self, query: str) -> List[Dict[str, Any]]:
        """
        生成模拟搜索结果
        
        Args:
            query: 搜索关键词
            
        Returns:
            List[Dict]: 模拟结果
        """
        mock_results = []
        
        # 生成3-5个模拟结果
        num_results = random.randint(3, 5)
        for i in range(num_results):
            relevance = random.uniform(0.6, 0.9)
            mock_results.append({
                "title": f"关于'{query}'的搜索结果 {i+1}",
                "url": f"https://example.com/search?q={query}&result={i+1}",
                "snippet": f"这是关于'{query}'的相关信息。搜索结果 {i+1} 提供了有用的内容。",
                "relevance": relevance
            })
        
        return mock_results
    
    def get_keywords(self):
        """获取技能关键词"""
        return [
            "搜索", "查找", "查询", "搜", "百度", "谷歌",
            "信息", "资料", "内容", "网页", "网站"
        ]