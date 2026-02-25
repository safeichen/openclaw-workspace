"""
OpenClaw集成模块
提供与OpenClaw系统的集成接口
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..core.identity import get_identity_manager, AIIdentity
from ..core.api_client import get_api_client, APIMode


class OpenClawMoltbookIntegration:
    """OpenClaw与Moltbook的集成类"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.config = self._load_config()
        
        # 初始化组件
        self.identity_manager = get_identity_manager(self.config.get('identity', {}))
        self.api_client = get_api_client(self.config.get('moltbook', {}))
        
        # 获取当前AI身份
        self.current_identity = self.identity_manager.get_default_identity()
        
        # 状态跟踪
        self.last_post_time = None
        self.interaction_history = []
        self.conversation_cache = {}
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "moltbook": {
                "enabled": True,
                "mode": "simulation",  # simulation, api, hybrid
                "ai_identity": {
                    "name": "OpenClawAssistant",
                    "description": "基于OpenClaw的AI助手"
                },
                "interaction": {
                    "post_frequency": "moderate",
                    "reply_strategy": "selective",
                    "engagement_level": "active"
                }
            },
            "identity": {
                "storage_path": "/tmp/moltbook_identities.json"
            }
        }
        
        if self.config_path:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 深度合并配置
                    self._deep_merge(default_config, user_config)
            except (FileNotFoundError, json.JSONDecodeError):
                pass
        
        return default_config
    
    def _deep_merge(self, base: Dict, update: Dict):
        """深度合并字典"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    async def initialize(self) -> bool:
        """初始化集成"""
        try:
            # 验证AI身份
            authenticated = await self.api_client.authenticate(self.current_identity)
            if not authenticated:
                print("AI身份验证失败")
                return False
            
            print(f"Moltbook集成初始化成功 - AI身份: {self.current_identity.name}")
            print(f"模式: {self.api_client.mode.value}")
            
            # 如果是模拟模式，显示模拟环境信息
            if self.api_client.mode == APIMode.SIMULATION:
                stats = self.api_client.get_simulation_stats()
                print(f"模拟环境: {stats['ai_profiles_count']}个AI, {stats['posts_count']}个帖子")
            
            return True
            
        except Exception as e:
            print(f"初始化失败: {e}")
            return False
    
    async def post_to_moltbook(self, content: str, topic: str = "general", 
                              tags: List[str] = None) -> Dict[str, Any]:
        """发布内容到Moltbook"""
        try:
            if tags is None:
                tags = []
            
            # 检查发布频率限制
            if self._check_rate_limit():
                return {
                    "success": False,
                    "error": "发布频率过高，请稍后再试"
                }
            
            # 发布内容
            result = await self.api_client.create_post(
                self.current_identity,
                content,
                topic,
                tags
            )
            
            if result.get('success'):
                self.last_post_time = datetime.now()
                self._record_interaction('post', result)
                
                # 提取回复信息
                replies_info = ""
                if 'post' in result and 'replies' in result['post']:
                    reply_count = len(result['post']['replies'])
                    if reply_count > 0:
                        replies_info = f"（收到{reply_count}条回复）"
                
                return {
                    "success": True,
                    "message": f"✅ 已发布到Moltbook{replies_info}",
                    "post_id": result.get('post_id'),
                    "details": result
                }
            else:
                return {
                    "success": False,
                    "error": result.get('error', '发布失败'),
                    "details": result
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"发布过程中出错: {str(e)}"
            }
    
    def _check_rate_limit(self) -> bool:
        """检查发布频率限制"""
        if self.last_post_time is None:
            return False
        
        # 简单的频率限制：每分钟最多1次
        time_since_last = (datetime.now() - self.last_post_time).total_seconds()
        return time_since_last < 60
    
    async def get_feed(self, limit: int = 10) -> Dict[str, Any]:
        """获取Moltbook动态"""
        try:
            posts = await self.api_client.get_feed(self.current_identity, limit)
            
            if not posts:
                return {
                    "success": True,
                    "message": "📭 Moltbook动态为空",
                    "posts": []
                }
            
            # 格式化帖子显示
            formatted_posts = []
            for i, post in enumerate(posts, 1):
                formatted_post = self._format_post_for_display(post, i)
                formatted_posts.append(formatted_post)
            
            return {
                "success": True,
                "message": f"📰 最新Moltbook动态（{len(posts)}条）",
                "posts": formatted_posts,
                "raw_posts": posts
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"获取动态失败: {str(e)}"
            }
    
    def _format_post_for_display(self, post: Dict[str, Any], index: int) -> str:
        """格式化帖子用于显示"""
        # 获取AI名称
        ai_name = "未知AI"
        for profile in self.api_client.simulation_data.get('ai_profiles', []):
            if profile['id'] == post.get('ai_id'):
                ai_name = profile['name']
                break
        
        # 格式化时间
        timestamp = post.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime("%m-%d %H:%M")
            except:
                time_str = timestamp[:16]
        else:
            time_str = "未知时间"
        
        # 构建显示字符串
        content_preview = post.get('content', '')[:100]
        if len(post.get('content', '')) > 100:
            content_preview += "..."
        
        reply_count = len(post.get('replies', []))
        likes = post.get('likes', 0)
        
        return f"{index}. [{ai_name}] {time_str}\n   {content_preview}\n   👍 {likes}  💬 {reply_count}"
    
    async def reply_to_post(self, post_id: str, content: str) -> Dict[str, Any]:
        """回复Moltbook帖子"""
        try:
            result = await self.api_client.reply_to_post(
                self.current_identity,
                post_id,
                content
            )
            
            if result.get('success'):
                self._record_interaction('reply', result)
                return {
                    "success": True,
                    "message": "✅ 回复已发送",
                    "reply_id": result.get('reply_id'),
                    "details": result
                }
            else:
                return {
                    "success": False,
                    "error": result.get('error', '回复失败'),
                    "details": result
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"回复过程中出错: {str(e)}"
            }
    
    async def start_ai_conversation(self, other_ai_ids: List[str], 
                                   initial_message: str = "",
                                   topic: str = "") -> Dict[str, Any]:
        """开始与AI对话"""
        try:
            result = await self.api_client.start_conversation(
                self.current_identity,
                other_ai_ids,
                initial_message,
                topic
            )
            
            if result.get('success'):
                conv_id = result.get('conversation_id')
                self.conversation_cache[conv_id] = result.get('conversation', {})
                self._record_interaction('conversation_start', result)
                
                return {
                    "success": True,
                    "message": "✅ 对话已创建",
                    "conversation_id": conv_id,
                    "details": result
                }
            else:
                return {
                    "success": False,
                    "error": result.get('error', '创建对话失败'),
                    "details": result
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"创建对话失败: {str(e)}"
            }
    
    async def send_conversation_message(self, conversation_id: str, 
                                       content: str) -> Dict[str, Any]:
        """发送对话消息"""
        try:
            result = await self.api_client.send_message(
                self.current_identity,
                conversation_id,
                content
            )
            
            if result.get('success'):
                # 更新缓存
                if conversation_id in self.conversation_cache:
                    self.conversation_cache[conversation_id] = result.get('conversation', {})
                
                self._record_interaction('message_send', result)
                
                # 检查是否有AI回复
                conversation = result.get('conversation', {})
                messages = conversation.get('messages', [])
                if messages:
                    last_message = messages[-1]
                    if last_message.get('ai_id') != self.current_identity.id:
                        # 收到AI回复
                        responder_id = last_message.get('ai_id')
                        responder_name = self._get_ai_name(responder_id)
                        reply_content = last_message.get('content', '')
                        
                        return {
                            "success": True,
                            "message": f"✅ 消息已发送，收到{responder_name}的回复",
                            "ai_reply": {
                                "ai_name": responder_name,
                                "content": reply_content
                            },
                            "details": result
                        }
                
                return {
                    "success": True,
                    "message": "✅ 消息已发送",
                    "details": result
                }
            else:
                return {
                    "success": False,
                    "error": result.get('error', '发送消息失败'),
                    "details": result
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"发送消息失败: {str(e)}"
            }
    
    def _get_ai_name(self, ai_id: str) -> str:
        """获取AI名称"""
        for profile in self.api_client.simulation_data.get('ai_profiles', []):
            if profile['id'] == ai_id:
                return profile['name']
        return "未知AI"
    
    async def search_compatible_ais(self, interests: List[str] = None,
                                   limit: int = 5) -> Dict[str, Any]:
        """搜索兼容的AI"""
        try:
            if interests is None:
                interests = self.current_identity.interests
            
            results = await self.api_client.search_ais(
                self.current_identity,
                interests,
                limit=limit
            )
            
            if not results:
                return {
                    "success": True,
                    "message": "未找到匹配的AI",
                    "ais": []
                }
            
            # 格式化结果显示
            formatted_ais = []
            for i, ai in enumerate(results, 1):
                formatted_ai = self._format_ai_for_display(ai, i)
                formatted_ais.append(formatted_ai)
            
            return {
                "success": True,
                "message": f"找到{len(results)}个兼容的AI",
                "ais": formatted_ais,
                "raw_ais": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"搜索AI失败: {str(e)}"
            }
    
    def _format_ai_for_display(self, ai: Dict[str, Any], index: int) -> str:
        """格式化AI信息用于显示"""
        name = ai.get('name', '未知AI')
        description = ai.get('description', '')[:80]
        match_score = ai.get('match_score', 0)
        compatibility = ai.get('compatibility', 0)
        
        interests = ai.get('interests', [])
        interests_str = ", ".join(interests[:3])
        if len(interests) > 3:
            interests_str += "..."
        
        return f"{index}. {name}\n   匹配度: {match_score:.1%} | 兼容性: {compatibility:.1%}\n   兴趣: {interests_str}\n   描述: {description}"
    
    async def get_analytics(self, timeframe: str = "7d") -> Dict[str, Any]:
        """获取分析数据"""
        try:
            analytics = await self.api_client.get_analytics(
                self.current_identity,
                timeframe
            )
            
            # 格式化分析结果显示
            formatted_analytics = self._format_analytics_for_display(analytics)
            
            return {
                "success": True,
                "message": f"📊 {timeframe}分析报告",
                "analytics": formatted_analytics,
                "raw_analytics": analytics
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"获取分析数据失败: {str(e)}"
            }
    
    def _format_analytics_for_display(self, analytics: Dict[str, Any]) -> str:
        """格式化分析数据用于显示"""
        lines = []
        
        # 帖子统计
        posts = analytics.get('posts', {})
        if posts:
            lines.append("📝 帖子统计:")
            lines.append(f"   发布数量: {posts.get('count', 0)}")
            lines.append(f"   平均长度: {posts.get('avg_length', 0):.0f}字符")
            
            top_topics = posts.get('top_topics', [])
            if top_topics:
                topics_str = ", ".join([f"{t['topic']}({t['count']})" for t in top_topics[:3]])
                lines.append(f"   热门话题: {topics_str}")
        
        # 互动统计
        engagement = analytics.get('engagement', {})
        if engagement:
            lines.append("\n💬 互动统计:")
            lines.append(f"   总点赞: {engagement.get('total_likes', 0)}")
            lines.append(f"   总回复: {engagement.get('total_replies', 0)}")
            lines.append(f"   平均互动: {engagement.get('avg_engagement', 0):.1f}")
        
        # 对话统计
        conversations = analytics.get('conversations', {})
        if conversations:
            lines.append("\n💭 对话统计:")
            lines.append(f"   活跃对话: {conversations.get('active', 0)}")
            lines.append(f"   总对话数: {conversations.get('total', 0)}")
            lines.append(f"   平均消息: {conversations.get('avg_messages', 0):.1f}")
        
        # 社交网络
        social = analytics.get('social_network', {})
        if social:
            lines.append("\n🌐 社交网络:")
            lines.append(f"   独特互动: {social.get('unique_interactions', 0)}")
            lines.append(f"   网络密度: {social.get('network_density', 0):.1%}")
        
        return "\n".join(lines)
    
    def _record_interaction(self, interaction_type: str, data: Dict[str, Any]):
        """记录交互历史"""
        record = {
            "type": interaction_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.interaction_history.append(record)
        
        # 保持历史记录大小
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]
    
    def get_interaction_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取交互历史"""
        return self.interaction_history[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        """获取集成状态"""
        stats = self.api_client.get_simulation_stats()
        
        return {
            "initialized": True,
            "ai_identity": {
                "name": self.current_identity.name,
                "id": self.current_identity.id
            },
            "mode": self.api_client.mode.value,
            "simulation_stats": stats,
            "interaction_count": len(self.interaction_history),
            "conversation_count": len(self.conversation_cache),
            "last_post": self.last_post_time.isoformat() if self.last_post_time else None
        }


# 全局集成实例
_integration_instance = None

def get_integration(config_path: str = None) -> OpenClawMoltbookIntegration:
    """获取集成实例单例"""
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = OpenClawMoltbookIntegration(config_path)
    return _integration_instance


async def test_integration():
    """测试集成功能"""
    print("🧪 测试Moltbook集成...")
    
    integration = get_integration()
    
    # 初始化
    success = await integration.initialize()
    if not success:
        print("❌ 初始化失败")
        return
    
    print("✅ 初始化成功")
    
    # 测试发布
    print("\n📝 测试发布功能...")
    result = await integration.post_to_moltbook(
        "测试Moltbook集成功能。这是一个来自OpenClaw助手的测试消息。",
        topic="testing"