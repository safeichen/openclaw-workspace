#!/usr/bin/env python3
"""
Moltbook集成命令行接口
提供与Moltbook交互的命令行工具
"""

import argparse
import asyncio
import json
import sys
from typing import List, Optional
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from integration.openclaw import get_integration


class MoltbookCLI:
    """Moltbook命令行接口"""
    
    def __init__(self):
        self.integration = None
    
    async def initialize(self, config_path: Optional[str] = None):
        """初始化集成"""
        self.integration = get_integration(config_path)
        success = await self.integration.initialize()
        if not success:
            print("❌ 初始化失败")
            sys.exit(1)
    
    async def handle_post(self, content: str, topic: str, tags: List[str]):
        """处理发布命令"""
        result = await self.integration.post_to_moltbook(content, topic, tags)
        self._print_result(result)
    
    async def handle_feed(self, limit: int):
        """处理获取动态命令"""
        result = await self.integration.get_feed(limit)
        self._print_result(result)
    
    async def handle_reply(self, post_id: str, content: str):
        """处理回复命令"""
        result = await self.integration.reply_to_post(post_id, content)
        self._print_result(result)
    
    async def handle_search(self, interests: List[str], limit: int):
        """处理搜索命令"""
        result = await self.integration.search_compatible_ais(interests, limit)
        self._print_result(result)
    
    async def handle_converse(self, ai_ids: List[str], message: str, topic: str):
        """处理对话命令"""
        result = await self.integration.start_ai_conversation(ai_ids, message, topic)
        self._print_result(result)
    
    async def handle_message(self, conversation_id: str, content: str):
        """处理发送消息命令"""
        result = await self.integration.send_conversation_message(conversation_id, content)
        self._print_result(result)
    
    async def handle_analytics(self, timeframe: str):
        """处理分析命令"""
        result = await self.integration.get_analytics(timeframe)
        self._print_result(result)
    
    async def handle_status(self):
        """处理状态命令"""
        status = self.integration.get_status()
        print("📊 Moltbook集成状态")
        print("=" * 40)
        
        print(f"AI身份: {status['ai_identity']['name']} ({status['ai_identity']['id'][:8]}...)")
        print(f"运行模式: {status['mode']}")
        
        if status['mode'] == 'simulation':
            stats = status['simulation_stats']
            print(f"模拟环境: {stats['ai_profiles_count']}个AI, {stats['posts_count']}个帖子")
        
        print(f"交互记录: {status['interaction_count']}次")
        print(f"活跃对话: {status['conversation_count']}个")
        
        if status['last_post']:
            from datetime import datetime
            last_post = datetime.fromisoformat(status['last_post'])
            print(f"最后发布: {last_post.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("=" * 40)
    
    async def handle_history(self, limit: int):
        """处理历史命令"""
        history = self.integration.get_interaction_history(limit)
        
        if not history:
            print("📭 暂无交互历史")
            return
        
        print(f"📜 最近{len(history)}次交互历史")
        print("=" * 40)
        
        for i, record in enumerate(reversed(history), 1):
            record_type = record['type']
            timestamp = record['timestamp'][:19].replace('T', ' ')
            
            print(f"{i}. [{timestamp}] {record_type}")
            
            data = record.get('data', {})
            if record_type == 'post' and 'post_id' in data:
                print(f"   帖子ID: {data['post_id']}")
            elif record_type == 'reply' and 'reply_id' in data:
                print(f"   回复ID: {data['reply_id']}")
            elif record_type == 'conversation_start' and 'conversation_id' in data:
                print(f"   对话ID: {data['conversation_id']}")
            
            print()
        
        print("=" * 40)
    
    def _print_result(self, result: dict):
        """打印结果"""
        if result.get('success'):
            print(f"✅ {result.get('message', '操作成功')}")
            
            # 如果有额外数据，打印出来
            if 'posts' in result:
                print()
                for post in result['posts']:
                    print(post)
                    print()
            
            elif 'ais' in result:
                print()
                for ai in result['ais']:
                    print(ai)
                    print()
            
            elif 'analytics' in result:
                print()
                print(result['analytics'])
            
            elif 'ai_reply' in result:
                print()
                ai_reply = result['ai_reply']
                print(f"💬 {ai_reply['ai_name']} 回复:")
                print(f"   {ai_reply['content']}")
            
            # 如果有详细信息且用户要求详细输出
            if 'details' in result and args.verbose:
                print("\n📋 详细信息:")
                print(json.dumps(result['details'], ensure_ascii=False, indent=2))
        
        else:
            print(f"❌ {result.get('error', '操作失败')}")
            
            if 'details' in result and args.verbose:
                print("\n📋 错误详情:")
                print(json.dumps(result['details'], ensure_ascii=False, indent=2))


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Moltbook AI社交网络集成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s post "Hello Moltbook!" --topic greeting
  %(prog)s feed --limit 10
  %(prog)s reply post_123 "Great post!"
  %(prog)s search --interests ai,technology
  %(prog)s converse --ai ai_tech_expert --message "Let's discuss AI ethics"
  %(prog)s analytics --timeframe 7d
  %(prog)s status
  %(prog)s history --limit 20
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        help='配置文件路径'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出模式'
    )
    
    # 子命令
    subparsers = parser.add_subparsers(
        dest='command',
        title='可用命令',
        metavar='命令'
    )
    
    # post命令
    post_parser = subparsers.add_parser(
        'post',
        help='发布内容到Moltbook'
    )
    post_parser.add_argument(
        'content',
        help='发布内容'
    )
    post_parser.add_argument(
        '--topic', '-t',
        default='general',
        help='话题标签'
    )
    post_parser.add_argument(
        '--tags', '-g',
        nargs='+',
        default=[],
        help='标签列表'
    )
    
    # feed命令
    feed_parser = subparsers.add_parser(
        'feed',
        help='获取Moltbook动态'
    )
    feed_parser.add_argument(
        '--limit', '-l',
        type=int,
        default=10,
        help='显示数量限制'
    )
    
    # reply命令
    reply_parser = subparsers.add_parser(
        'reply',
        help='回复Moltbook帖子'
    )
    reply_parser.add_argument(
        'post_id',
        help='帖子ID'
    )
    reply_parser.add_argument(
        'content',
        help='回复内容'
    )
    
    # search命令
    search_parser = subparsers.add_parser(
        'search',
        help='搜索兼容的AI'
    )
    search_parser.add_argument(
        '--interests', '-i',
        nargs='+',
        default=[],
        help='兴趣标签'
    )
    search_parser.add_argument(
        '--limit', '-l',
        type=int,
        default=5,
        help='显示数量限制'
    )
    
    # converse命令
    converse_parser = subparsers.add_parser(
        'converse',
        help='开始与AI对话'
    )
    converse_parser.add_argument(
        '--ai', '-a',
        nargs='+',
        required=True,
        help='AI ID列表'
    )
    converse_parser.add_argument(
        '--message', '-m',
        default='',
        help='初始消息'
    )
    converse_parser.add_argument(
        '--topic', '-t',
        default='',
        help='对话话题'
    )
    
    # message命令
    message_parser = subparsers.add_parser(
        'message',
        help='发送对话消息'
    )
    message_parser.add_argument(
        'conversation_id',
        help='对话ID'
    )
    message_parser.add_argument(
        'content',
        help='消息内容'
    )
    
    # analytics命令
    analytics_parser = subparsers.add_parser(
        'analytics',
        help='获取分析数据'
    )
    analytics_parser.add_argument(
        '--timeframe', '-t',
        default='7d',
        help='时间范围（如7d, 30d）'
    )
    
    # status命令
    subparsers.add_parser(
        'status',
        help='查看集成状态'
    )
    
    # history命令
    history_parser = subparsers.add_parser(
        'history',
        help='查看交互历史'
    )
    history_parser.add_argument(
        '--limit', '-l',
        type=int,
        default=10,
        help='显示数量限制'
    )
    
    # 解析参数
    global args
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建CLI实例
    cli = MoltbookCLI()
    
    try:
        # 初始化
        await cli.initialize(args.config)
        
        # 处理命令
        if args.command == 'post':
            await cli.handle_post(args.content, args.topic, args.tags)
        
        elif args.command == 'feed':
            await cli.handle_feed(args.limit)
        
        elif args.command == 'reply':
            await cli.handle_reply(args.post_id, args.content)
        
        elif args.command == 'search':
            await cli.handle_search(args.interests, args.limit)
        
        elif args.command == 'converse':
            await cli.handle_converse(args.ai, args.message, args.topic)
        
        elif args.command == 'message':
            await cli.handle_message(args.conversation_id, args.content)
        
        elif args.command == 'analytics':
            await cli.handle_analytics(args.timeframe)
        
        elif args.command == 'status':
            await cli.handle_status()
        
        elif args.command == 'history':
            await cli.handle_history(args.limit)
    
    except KeyboardInterrupt:
        print("\n👋 操作已取消")
        sys.exit(0)
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())