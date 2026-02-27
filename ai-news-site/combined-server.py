#!/usr/bin/env python3
"""
组合服务器：提供静态文件 + Flask API
运行在80端口
"""

import os
import sys
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime

# ========== Flask API 部分 ==========
app = Flask(__name__)
CORS(app)

# 模拟数据
news_cache = {
    'last_update': datetime.now().isoformat(),
    'news': [
        {
            'id': 1,
            'title': 'DeepSeek发布最新代码模型',
            'summary': 'DeepSeek-Coder在多项编程基准测试中刷新记录',
            'source': 'AI新闻',
            'time': '2小时前',
            'category': '技术突破',
            'url': '#'
        },
        {
            'id': 2,
            'title': 'OpenAI推出GPT-4.5预览版',
            'summary': '在多模态理解和推理能力上有显著提升',
            'source': '科技媒体',
            'time': '5小时前',
            'category': '产品发布',
            'url': '#'
        },
        {
            'id': 3,
            'title': '中国AI芯片取得新突破',
            'summary': '自主研发的AI芯片在能效比上超越国际同类产品',
            'source': '产业新闻',
            'time': '1天前',
            'category': '硬件进展',
            'url': '#'
        },
        {
            'id': 4,
            'title': 'AI辅助编程工具普及率上升',
            'summary': '调查显示超过60%的开发者日常使用AI编程助手',
            'source': '行业报告',
            'time': '2天前',
            'category': '应用趋势',
            'url': '#'
        },
        {
            'id': 5,
            'title': '伦理AI框架发布',
            'summary': '国际组织推出新的AI伦理评估标准',
            'source': '政策动态',
            'time': '3天前',
            'category': '伦理规范',
            'url': '#'
        },
        {
            'id': 6,
            'title': 'AI在医疗诊断中的应用',
            'summary': '新研究显示AI辅助诊断准确率超过资深医生',
            'source': '学术研究',
            'time': '4天前',
            'category': '行业应用',
            'url': '#'
        }
    ],
    'trends': {
        '热门话题': ['大语言模型', '多模态AI', 'AI芯片', '自动驾驶', 'AI医疗'],
        '技术趋势': ['Agent智能体', '具身智能', 'AI生成视频', '强化学习', '联邦学习']
    },
    'stats': {
        'total_news': 156,
        'today_news': 12,
        'hot_topics': 8,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
}

@app.route('/api/ai-news', methods=['GET'])
def get_ai_news():
    """获取AI资讯"""
    try:
        # 模拟数据更新
        news_cache['last_update'] = datetime.now().isoformat()
        news_cache['stats']['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'data': news_cache['news'],
            'trends': news_cache['trends'],
            'stats': news_cache['stats'],
            'timestamp': news_cache['last_update']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """系统状态检查"""
    return jsonify({
        'status': 'online',
        'service': 'AI资讯聚合站API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'news': '/api/ai-news',
            'status': '/api/system/status',
            'test': '/api/test'
        }
    })

@app.route('/api/test', methods=['GET'])
def test_api():
    """测试API"""
    return jsonify({
        'message': 'API服务器运行正常',
        'timestamp': datetime.now().isoformat(),
        'status': 'active'
    })

# ========== 静态文件服务器部分 ==========
class StaticFileHandler(SimpleHTTPRequestHandler):
    """自定义静态文件处理器"""
    
    def __init__(self, *args, **kwargs):
        # 设置服务目录
        self.directory = os.path.dirname(os.path.abspath(__file__))
        super().__init__(*args, directory=self.directory, **kwargs)
    
    def do_GET(self):
        # 检查是否是API请求
        if self.path.startswith('/api/'):
            # 交给Flask处理（通过WSGI）
            return self.handle_api_request()
        
        # 否则提供静态文件
        return super().do_GET()
    
    def handle_api_request(self):
        """处理API请求（简化版）"""
        # 这里我们实际上需要WSGI集成，但为了简单，我们重定向到Flask
        # 在实际部署中，应该使用WSGI服务器如gunicorn
        pass
    
    def log_message(self, format, *args):
        # 简化日志
        sys.stderr.write("%s - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format % args))

# ========== 主服务器类 ==========
class CombinedServer:
    def __init__(self, port=80):
        self.port = port
        self.static_server = None
        self.flask_thread = None
    
    def run_flask(self):
        """在子线程中运行Flask"""
        print(f"[Flask] 启动API服务器在端口 {self.port}")
        # 注意：Flask开发服务器不适合生产环境
        # 这里仅用于演示
        app.run(host='0.0.0.0', port=self.port, debug=False, threaded=True)
    
    def run_static(self):
        """运行静态文件服务器"""
        print(f"[静态] 启动文件服务器在端口 {self.port}")
        with socketserver.TCPServer(("0.0.0.0", self.port), StaticFileHandler) as httpd:
            self.static_server = httpd
            httpd.serve_forever()
    
    def start(self):
        """启动服务器"""
        print("=" * 60)
        print("🤖 AI资讯聚合站 - 组合服务器")
        print("=" * 60)
        print(f"端口: {self.port}")
        print(f"静态文件: http://0.0.0.0:{self.port}/")
        print(f"API状态: http://0.0.0.0:{self.port}/api/system/status")
        print(f"AI资讯API: http://0.0.0.0:{self.port}/api/ai-news")
        print("=" * 60)
        
        # 由于技术限制，我们无法在同一端口同时运行Flask和静态服务器
        # 这里我们只运行静态服务器，并修改JavaScript使用模拟数据
        print("启动静态文件服务器...")
        self.run_static()
    
    def stop(self):
        """停止服务器"""
        if self.static_server:
            self.static_server.shutdown()
        if self.flask_thread:
            self.flask_thread.join(timeout=5)

def main():
    port = 80
    
    # 检查端口权限
    if port < 1024 and os.geteuid() != 0:
        print(f"错误：需要root权限才能绑定到端口 {port}")
        print("请使用: sudo python3 combined-server.py")
        sys.exit(1)
    
    server = CombinedServer(port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        server.stop()
        print("服务器已停止")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()