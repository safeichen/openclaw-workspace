"""
文件处理技能
读写和处理文件
"""

import os
import json
import tempfile
from typing import Any, Dict, List
from pathlib import Path
from loguru import logger
from .base_skill import BaseSkill, SkillInput, SkillOutput


class FileProcessorSkill(BaseSkill):
    """文件处理技能"""
    
    def __init__(self, base_dir: str = None):
        """
        初始化文件处理技能
        
        Args:
            base_dir: 基础目录，默认为临时目录
        """
        super().__init__(
            name="file_processor",
            description="读写和处理文件，支持文本、JSON等格式",
            max_retries=2
        )
        self.base_dir = base_dir or tempfile.gettempdir()
        self._ensure_base_dir()
        
    async def execute(self, input_data: SkillInput) -> SkillOutput:
        """
        执行文件处理
        
        Args:
            input_data: 技能输入
            
        Returns:
            SkillOutput: 处理结果
        """
        logger.info(f"执行文件处理: {input_data.task}")
        
        try:
            # 解析任务类型
            task_type = self._parse_task_type(input_data.task)
            
            if task_type == "read":
                result = await self._read_file(input_data)
            elif task_type == "write":
                result = await self._write_file(input_data)
            elif task_type == "list":
                result = await self._list_files(input_data)
            else:
                return SkillOutput(
                    success=False,
                    result=None,
                    error=f"不支持的文件操作类型: {task_type}",
                    metadata={"task": input_data.task}
                )
            
            return result
            
        except Exception as e:
            logger.error(f"文件处理失败: {str(e)}")
            return SkillOutput(
                success=False,
                result=None,
                error=str(e),
                metadata={"task": input_data.task, "error_type": type(e).__name__}
            )
    
    def _parse_task_type(self, task: str) -> str:
        """
        解析任务类型
        
        Args:
            task: 任务描述
            
        Returns:
            str: 任务类型 (read/write/list)
        """
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["读取", "打开", "查看", "read", "open"]):
            return "read"
        elif any(word in task_lower for word in ["写入", "保存", "创建", "write", "save", "create"]):
            return "write"
        elif any(word in task_lower for word in ["列表", "列出", "显示", "list", "show"]):
            return "list"
        else:
            # 默认尝试读取
            return "read"
    
    async def _read_file(self, input_data: SkillInput) -> SkillOutput:
        """
        读取文件
        
        Args:
            input_data: 技能输入
            
        Returns:
            SkillOutput: 读取结果
        """
        # 获取文件名
        filename = input_data.parameters.get("filename")
        if not filename:
            # 尝试从任务描述中提取文件名
            filename = self._extract_filename(input_data.task)
        
        if not filename:
            return SkillOutput(
                success=False,
                result=None,
                error="未指定文件名",
                metadata={"task": input_data.task}
            )
        
        # 构建完整路径
        filepath = self._get_full_path(filename)
        
        # 检查文件是否存在
        if not os.path.exists(filepath):
            return SkillOutput(
                success=False,
                result=None,
                error=f"文件不存在: {filename}",
                metadata={"filename": filename, "filepath": filepath}
            )
        
        # 读取文件
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试解析JSON
            try:
                parsed_content = json.loads(content)
                content_type = "json"
            except:
                parsed_content = content
                content_type = "text"
            
            logger.success(f"文件读取成功: {filename}")
            return SkillOutput(
                success=True,
                result={
                    "filename": filename,
                    "content": parsed_content,
                    "content_type": content_type,
                    "size": len(content)
                },
                metadata={
                    "filename": filename,
                    "filepath": filepath,
                    "content_type": content_type,
                    "skill": self.name
                }
            )
            
        except Exception as e:
            raise Exception(f"读取文件失败: {str(e)}")
    
    async def _write_file(self, input_data: SkillInput) -> SkillOutput:
        """
        写入文件
        
        Args:
            input_data: 技能输入
            
        Returns:
            SkillOutput: 写入结果
        """
        # 获取参数
        filename = input_data.parameters.get("filename")
        content = input_data.parameters.get("content")
        
        if not filename or content is None:
            return SkillOutput(
                success=False,
                result=None,
                error="需要指定文件名和内容",
                metadata={"task": input_data.task}
            )
        
        # 构建完整路径
        filepath = self._get_full_path(filename)
        
        # 写入文件
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 如果是字典，转换为JSON
            if isinstance(content, dict):
                content_str = json.dumps(content, ensure_ascii=False, indent=2)
            else:
                content_str = str(content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content_str)
            
            logger.success(f"文件写入成功: {filename}")
            return SkillOutput(
                success=True,
                result={
                    "filename": filename,
                    "filepath": filepath,
                    "size": len(content_str)
                },
                metadata={
                    "filename": filename,
                    "filepath": filepath,
                    "skill": self.name
                }
            )
            
        except Exception as e:
            raise Exception(f"写入文件失败: {str(e)}")
    
    async def _list_files(self, input_data: SkillInput) -> SkillOutput:
        """
        列出文件
        
        Args:
            input_data: 技能输入
            
        Returns:
            SkillOutput: 文件列表
        """
        # 获取目录路径
        directory = input_data.parameters.get("directory", ".")
        dirpath = self._get_full_path(directory)
        
        # 检查目录是否存在
        if not os.path.exists(dirpath):
            return SkillOutput(
                success=False,
                result=None,
                error=f"目录不存在: {directory}",
                metadata={"directory": directory, "dirpath": dirpath}
            )
        
        # 列出文件
        try:
            files = []
            for item in os.listdir(dirpath):
                item_path = os.path.join(dirpath, item)
                is_dir = os.path.isdir(item_path)
                size = os.path.getsize(item_path) if not is_dir else 0
                
                files.append({
                    "name": item,
                    "type": "directory" if is_dir else "file",
                    "size": size,
                    "path": item_path
                })
            
            logger.success(f"列出文件成功: {len(files)} 个项目")
            return SkillOutput(
                success=True,
                result=files,
                metadata={
                    "directory": directory,
                    "dirpath": dirpath,
                    "count": len(files),
                    "skill": self.name
                }
            )
            
        except Exception as e:
            raise Exception(f"列出文件失败: {str(e)}")
    
    def _extract_filename(self, task: str) -> str:
        """
        从任务描述中提取文件名
        
        Args:
            task: 任务描述
            
        Returns:
            str: 文件名
        """
        # 简单的提取逻辑
        import re
        
        # 匹配常见的文件扩展名
        patterns = [
            r'文件[：:]\s*([^\s]+\.(txt|json|csv|md|py))',
            r'([^\s]+\.(txt|json|csv|md|py))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, task)
            if match:
                return match.group(1)
        
        return ""
    
    def _get_full_path(self, path: str) -> str:
        """
        获取完整路径
        
        Args:
            path: 相对路径
            
        Returns:
            str: 完整路径
        """
        if os.path.isabs(path):
            return path
        return os.path.join(self.base_dir, path)
    
    def _ensure_base_dir(self):
        """确保基础目录存在"""
        os.makedirs(self.base_dir, exist_ok=True)
    
    def get_keywords(self):
        """获取技能关键词"""
        return [
            "文件", "读取", "写入", "保存", "打开",
            "文本", "json", "csv", "目录", "文件夹"
        ]