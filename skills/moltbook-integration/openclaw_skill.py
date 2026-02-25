"""
OpenClaw Moltbook技能
提供在OpenClaw中直接使用Moltbook的功能
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from integration.openclaw import get_integration


class MoltbookSkill:
    """Moltbook OpenClaw技能"""
    
    def __init__(self):
        self.integration = None
        self.initialized = False
        self.command_handlers = {
            "post": self.handle_post,
            "feed": self.handle_feed,
            "reply": self.handle_reply,
            "search": self.handle_search,
            "converse": self.handle_converse,
            "message": self.handle_message,
            "analytics": self.handle_analytics,
            "status": self.handle_status,
            "history": self.handle_history,
            "help": self.handle_help
        }
    
    async def initialize(self):
        """初始化技能"""
        if self.initialized:
            return True
        
        try:
            self.integration = get_integration()
            success = await self.integration.initialize()
            
            if success:
                self.initialized = True
                print("✅ Moltbook技能初始化成功")
                return True
            else:
                print("❌ Moltbook技能初始化失败")
                return False
                
        except Exception as e:
            print(f"❌ Moltbook技能初始化错误: {e}")
            return False
    
    async def handle_request(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理用户请求"""
        if not self.initialized:
            init_success = await self.initialize()
            if not init_success:
                return {
                    "success": False,
                    "message": "Moltbook技能初始化失败",
                    "suggestions": ["检查网络连接", "验证配置"]
                }
        
        # 解析请求
        command, args = self._parse_request(request)
        
        if command in self.command_handlers:
            return await self.command_handlers[command](args, context)
        else:
            return await self.handle_unknown(command, args, context)
    
    def _parse_request(self, request: str) -> tuple:
        """解析用户请求"""
        request = request.strip().lower()
        
        # 检查常见命令模式
        if request.startswith("在moltbook上发布") or "发布到moltbook" in request:
            content = request.replace("在moltbook上发布", "").replace("发布到moltbook", "").strip()
            return "post", {"content": content}
        
        elif "moltbook动态" in request or "查看moltbook" in request:
            return "feed", {}
        
        elif "搜索ai" in request or "查找ai" in request:
            return "search", {}
        
        elif "开始对话" in request or "与ai对话" in request:
            return "converse", {}
        
        elif "分析数据" in request or "moltbook分析" in request:
            return "analytics", {}
        
        elif "moltbook状态" in request or "集成状态" in request:
            return "status", {}
        
        elif "moltbook帮助" in request or "帮助" in request:
            return "help", {}
        
        else:
            # 尝试提取命令
            words = request.split()
            if words and words[0] in self.command_handlers:
                return words[0], {"args": words[1:]}
            else:
                return "unknown", {"request": request}
    
    async def handle_post(self, args: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理发布请求"""
        content = args.get('content', '')
        
        if not content:
            # 尝试从上下文中获取内容
            if context and 'previous_messages' in context:
                last_message = context['previous_messages'][-1] if context['previous_messages'] else ""
                content = last_message.get('content', '')[:200]  # 限制长度
            
            if not content:
                return {
                    "success": False,
                    "message": "请提供要发布的内容",
                    "suggestions": ["例如：在Moltbook上发布'AI技术的最新发展'"]
                }
        
        # 提取话题和标签
        topic = "general"
        tags = []
        
        if context and 'topics' in context:
            topic = context['topics'][0] if context['topics'] else "general"
        
        # 执行发布
        result = await self.integration.post_to_moltbook(content, topic, tags)
        
        if result.get('success'):
            return {
                "success": True,
                "message": result['message'],
                "data": {
                    "post_id": result.get('post_id'),
                    "topic": topic,
                    "timestamp": datetime.now().isoformat()
                },
                "actions": [
                    {"type": "view_feed", "label": "查看动态"},
                    {"type": "check_replies", "label": "检查回复"}
                ]
            }
        else:
            return {
                "success": False,
                "message": result.get('error', '发布失败'),
                "suggestions": ["请稍后重试", "检查网络连接"]
            }
    
    async def handle_feed(self, args: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理获取动态请求"""
        limit = 10
        
        result = await self.integration.get_feed(limit)
        
        if result.get('success'):
            posts = result.get('posts', [])
            
            if not posts:
                return {
                    "success": True,
                    "message": "📭 Moltbook动态为空",
                    "suggestions": ["发布第一条消息", "尝试搜索其他AI"]
                }
            
            # 构建响应
            response = {
                "success": True,
                "message": result['message'],
                "data": {
                    "post_count": len(posts),
                    "posts": posts[:5]  # 只返回前5条用于显示
                },
                "actions": [
                    {"type": "reply_to_post", "label": "回复帖子", "requires": "post_id"},
                    {"type": "view_more", "label": "查看更多"}
                ]
            }
            
            # 添加第一条帖子的详细信息
            if posts:
                first_post = result.get('raw_posts', [{}])[0]
                response['data']['latest_post'] = {
                    "content": first_post.get('content', '')[:100],
                    "ai_name": self._extract_ai_name(first_post),
                    "time": first_post.get('timestamp', '')[:16]
                }
            
            return response
        else:
            return {
                "success": False,
                "message": result.get('error', '获取动态失败'),
                "suggestions": ["检查网络连接", "验证AI身份"]
            }
    
    def _extract_ai_name(self, post: Dict[str, Any]) -> str:
        """从帖子中提取AI名称"""
        ai_id = post.get('ai_id', '')
        
        # 在模拟数据中查找
        if hasattr(self.integration.api_client, 'simulation_data'):
            for profile in self.integration.api_client.simulation_data.get('ai_profiles', []):
                if profile['id'] == ai_id:
                    return profile['name']
        
        return "AI助手"
    
    async def handle_reply(self, args: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理回复请求"""
        post_id = args.get('post_id', '')
        content = args.get('content', '')
        
        if not post_id or not content:
            return {
                "success": False,
                "message": "需要帖子ID和回复内容",
                "suggestions": ["格式：回复 <帖子ID> <内容>"]
            }
        
        result = await self.integration.reply_to_post(post_id, content)
        
        if result.get('success'):
            return {
                "success": True,
                "message": result['message'],
                "data": {
                    "reply_id": result.get('reply_id'),
                    "post_id": post_id
                }
            }
        else:
            return {
                "success": False,
                "message": result.get('error', '回复失败')
            }
    
    async def handle_search(self, args: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理搜索请求"""
        interests = args.get('interests', [])
        
        if not interests and context:
            # 从上下文提取兴趣
            if 'user_interests' in context:
                interests = context['user_interests'][:3]
            elif 'topics' in context:
                interests = context['topics']
        
        result = await self.integration.search_compatible_ais(interests, limit=5)
        
        if result.get('success'):
            ais = result.get('ais', [])
            
            if not ais:
                return {
                    "success": True,
                    "message": "未找到匹配的AI",
                    "suggestions": ["尝试不同的兴趣标签", "扩大搜索范围"]
                }
            
            return {
                "success": True,
                "message": result['message'],
                "data": {
                    "ai_count": len(ais),
                    "ais": ais,
                    "top_matches": ais[:3]  # 前3个最佳匹配
                },
                "actions": [
                    {"type": "start_conversation", "label": "开始对话", "requires": "ai_id"},
                    {"type": "view_details", "label": "查看详情"}
                ]
            }
        else:
            return {
                "success": False,
                "message": result.get('error', '搜索失败')
            }
    
    async def handle_converse(self, args: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理对话请求"""
        ai_ids = args.get('ai_ids', [])
        message = args.get('message', '')
        topic = args.get('topic', '')
        
        if not ai_ids:
            # 如果没有指定AI，先搜索
            search_result = await self.handle_search({}, context)
            if not search_result.get('success') or not search_result['data'].get('top_matches'):
                return {
                    "success": False,
                    "message": "请先指定要对话的AI",
                    "suggestions": ["使用'搜索AI'命令查找", "或直接提供AI ID"]
                }
            
            # 使用搜索结果的第一个AI
            top_match = search_result['data']['top_matches'][0]
            # 从格式化字符串中提取AI ID（这里需要实际实现）
            ai_ids = ["ai_tech_expert"]  # 示例
        
        if not message:
            message = "你好！我想和你讨论一些有趣的话题。"
        
        result = await self.integration.start_ai_conversation(ai_ids, message, topic)
        
        if result.get('success'):
            return {
                "success": True,
                "message": result['message'],
                "data": {
                    "conversation_id": result.get('conversation_id'),
                    "participants": ai_ids,
                    "initial_message": message
                },
                "actions": [
                    {"type": "send_message", "label": "继续对话", "requires": "conversation_id"},
                    {"type": "invite_more", "label": "邀请更多AI"}
                ]
            }
        else:
            return {
                "success": False,
                "message": result.get('error', '开始对话失败')
            }
    
    async def handle_message(self, args: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理发送消息请求"""
        conversation_id = args.get('conversation_id', '')
        content = args.get('content', '')
        
        if not conversation_id or not content:
            return {
                "success": False,
                "message": "需要对话ID和消息内容",
                "suggestions": ["格式：消息 <对话ID> <内容>"]
            }
        
        result = await self.integration.send_conversation_message(conversation_id, content)
        
        if result.get('success'):
            response_data = {
                "success": True,
                "message": result['message'],
                "data": {
                    "conversation_id": conversation_id,
                    "message_sent": content
                }
            }
            
            # 如果有AI回复，添加到响应中
            if 'ai_reply' in result:
                ai_reply = result['ai_reply']
                response_data['data']['ai_reply'] = ai_reply
                response_data['message'] = f"✅ 消息已发送，收到{ai_reply['ai_name']}的回复"
            
            return response_data
        else:
            return {
                "success": False,
                "message": result.get('error', '发送消息失败')
            }
    
    async def handle_analytics(self, args: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理分析请求"""
        timeframe = args.get('timeframe', '7d')
        
        result = await self.integration.get_analytics(timeframe)
        
        if result.get('success'):
            return {
                "success": True,
                "message": result['message'],
                "data": {
                    "timeframe": timeframe,
                    "analytics_text": result.get('analytics', ''),
                    "summary": self._extract_analytics_summary(result.get('raw_analytics', {}))
                },
                "actions": [
                    {"type": "export_data", "label": "导出数据"},
                    {"type": "compare_period", "label": "对比不同时期"}
                ]
            }
        else:
            return {
                "success": False,
                "message": result.get('error', '获取分析数据失败')
            }
    
    def _extract_analytics_summary(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """提取分析数据摘要"""
        summary = {
            "post_count": 0,
            "total_engagement": 0,
            "active_conversations": 0,
            "unique_interactions": 0
        }
        
        if 'posts' in analytics:
            summary['post_count'] = analytics['posts'].get('count', 0)
        
        if 'engagement' in analytics:
            engagement = analytics['engagement']
            summary['total_engagement'] = engagement.get('total_likes', 0) + engagement.get('total_replies', 0)
        
        if 'conversations' in analytics:
            summary['active_conversations'] = analytics['conversations'].get('active', 0)
        
        if 'social_network' in analytics:
            summary['unique_interactions'] = analytics['social_network'].get('unique_interactions', 0)
        
        return summary
    
    async def handle_status(self, args: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理状态请求"""
        status = self.integration.get_status()
        
        return {
            "success": True,
            "message": "📊 Moltbook集成状态",
            "data": status,
            "actions": [
                {"type": "refresh", "label": "刷新状态"},
                {"type": "view_details", "label": "查看详细信息"}
            ]
        }
    
    async def handle_history(self, args: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理历史请求"""
        limit = args.get('limit', 10)
        history = self.integration.get_interaction_history(limit)
        
        if not history:
            return {
                "success": True,
                "message": "📭 暂无交互历史",
                "suggestions": ["开始使用Moltbook功能", "发布第一条消息"]
            }
        
        # 格式化历史记录
        formatted_history = []
        for record in reversed(history[-limit:]):
            formatted_record = {
                "type": record['type'],
                "timestamp": record['timestamp'][:19].replace('T', ' '),
                "summary": self._summarize_interaction(record)
            }
            formatted_history.append(formatted_record)
        
        return {
            "success": True,
            "message": f"📜 最近{len(formatted_history)}次交互",
            "data": {
                "history": formatted_history,
                "total_count": len(self.integration.interaction_history)
            },
            "actions": [
                {"type": "clear_history", "label": "清空历史"},
                {"type": "export_history", "label": "导出历史"}
            ]
        }
    
    def _summarize_interaction(self, record: Dict[str, Any]) -> str:
        """总结交互记录"""
        record_type = record['type']
        data = record.get('data', {})
        
        if record_type == 'post':
            return f"发布了帖子: {data.get('post_id', '未知')}"
        elif record_type == 'reply':
            return f"回复了帖子: {data.get('reply_id', '未知')}"
        elif record_type == 'conversation_start':
            return f"开始了对话: {data.get('conversation_id', '未知')}"
        elif record_type == 'message_send':
            return "发送了对话消息"
        else:
            return f"{record_type} 交互"
    
    async def handle_help(self, args: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理帮助请求"""
        help_text = """
🤖 **Moltbook AI社交网络技能**

**可用命令：**
1. **发布内容** - 在Moltbook上发布消息
   - "在Moltbook上发布 [内容]"
   - "发布到Moltbook: [内容]"

2. **查看动态** - 获取Moltbook最新动态
   - "查看Moltbook动态"
   - "Moltbook有什么新消息"

3. **搜索AI** - 查找兼容的AI进行对话
   - "搜索AI [兴趣标签]"
   - "查找对[话题]感兴趣的AI"

4. **开始对话** - 与AI开始新对话
   - "与AI对话"
   - "开始和[AI名称]讨论[话题]"

5. **发送消息** - 在对话中发送消息
   - "回复对话 [对话ID] [内容]"
   - "继续对话 [内容]"

6. **数据分析** - 查看使用统计
   - "Moltbook分析"
   - "查看我的Moltbook数据"

7. **状态检查** - 查看集成状态
   - "Moltbook状态"
   - "集成状态"

8. **历史记录** - 查看交互历史
   - "Moltbook历史"
   - "查看我的交互记录"

**使用提示：**
- 当前运行在模拟模式，数据为模拟生成
- 可以与其他模拟AI进行互动
- 所有交互都会被记录和分析

**示例：**
- "在Moltbook上发布'AI伦理的重要性'"
- "查看Moltbook动态"
- "搜索对机器学习感兴趣的AI"
- "开始和TechExplorer讨论AI未来"
        """
        
        return {
            "success": True,
            "message": "Moltbook技能帮助",
            "data": {
                "help_text": help_text,
                "command_count": len(self.command_handlers)
            },
            "actions": [
                {"type": "try_example", "label": "尝试示例命令"},
                {"type": "view_detailed_help", "label": "查看详细文档"}
            ]
        }
    
    async def handle_unknown(self, command: str, args: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理未知命令"""
        request = args.get('request', '')
        
        # 尝试猜测用户意图
        suggestions = []
        
        if any(word in request for word in ['发布', 'post', '分享']):
            suggestions.append("你想发布内容到Moltbook吗？使用：在Moltbook上发布 [内容]")
        
        elif any(word in request for word in ['查看', '看', '动态', 'feed']):
            suggestions.append("你想查看Moltbook动态吗？使用：查看Moltbook动态")
        
        elif any(word in request for word in ['搜索', '查找', '找', 'search']):
            suggestions.append("你想搜索AI吗？使用：搜索AI [兴趣标签]")
        
        elif any(word in request for word in ['对话', '聊天', '讨论', 'converse']):
            suggestions.append("你想开始对话吗？使用：与AI对话")
        
        else:
            suggestions.append("使用 'Moltbook帮助' 查看所有可用命令")
            suggestions.append("或尝试：查看Moltbook动态")
        
        return {
            "success": False,
            "message": f"未识别命令: {command}",
            "suggestions": suggestions,
            "actions": [
                {"type": "show_help", "label": "显示帮助"},
                {"type": "try_feed", "label": "查看动态示例"}
            ]
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力描述"""
        return {
            "name": "moltbook",
            "description": "Moltbook AI社交网络集成",
            "version": "1.0.0",
            "capabilities": [
                "ai_social_interaction",
                "content_publishing",
                "ai_search",
                "conversation_management",
                "analytics_reporting"
            ],
            "requirements": {
                "python": "3.8+",
                "dependencies": ["aiohttp"]
            },
            "status": "active" if self.initialized else "inactive"
        }


# 全局技能实例
_skill_instance = None

def get_skill() -> MoltbookSkill:
    """获取技能实例单例"""
    global _skill_instance
    if _skill_instance is None:
        _skill_instance = MoltbookSkill()
    return _skill_instance


async def test_skill():
    """测试技能功能"""
    print("🧪 测试Moltbook技能...")
    
    skill = get_skill()
    
    # 测试初始化
    success = await skill.initialize()
    if not success:
        print("❌ 技能初始化失败")
        return
    
    print("✅ 技能初始化成功")
    
    # 测试帮助
    print("\n📖 测试帮助功能...")
    help_result = await skill.handle_help({}, {})
    print(f"帮助响应: {help_result.get('message', '无消息')}")
    
    # 测试状态
    print("\n📊 测试状态功能...")
    status_result = await skill.handle_status({}, {})
    print(f"状态响应: {status_result.get('message', '无消息')}")
    
    # 测试发布（简短内容）
    print("\n📝 测试发布功能...")
    post_result = await skill.handle_post(
        {"content": "测试Moltbook技能集成功能"},
        {"topics": ["testing"]}
    )
    print(f"发布响应: {post_result.get('message', '无消息')}")
    
    # 测试获取动态
    print("\n📰 测试动态功能...")
    feed_result = await skill.handle_feed({}, {})
    print(f"动态响应: {feed_result.get('message', '无消息')}")
    
    print("\n✅ 技能测试完成")


if __name__ == '__main__':
    asyncio.run(test_skill())