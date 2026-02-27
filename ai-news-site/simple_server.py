#!/usr/bin/env python3
"""
简单的AI资讯网站服务器
提供静态文件和模拟API
"""

import http.server
import socketserver
import json
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import threading

PORT = 8083

# 模拟数据
mock_news = [
    {
        'id': '1',
        'title': 'OpenAI发布新一代多模态模型',
        'excerpt': 'OpenAI最新研究突破，推出能够同时处理文本、图像和视频的统一模型架构。',
        'category': 'research',
        'source': 'OpenAI Blog',
        'date': datetime.now().isoformat(),
        'url': 'https://openai.com/blog'
    },
    {
        'id': '2',
        'title': '谷歌DeepMind推出AlphaFold 3',
        'excerpt': 'AlphaFold 3在蛋白质结构预测方面取得重大进展，准确率相比上一代提升15%。',
        'category': 'research',
        'source': 'Nature',
        'date': datetime.now().isoformat(),
        'url': 'https://www.nature.com'
    },
    {
        'id': '3',
        'title': '微软将Copilot全面集成Office套件',
        'excerpt': '微软宣布将Copilot AI助手深度集成到所有Office应用中，大幅提升办公效率。',
        'category': 'industry',
        'source': 'Microsoft News',
        'date': datetime.now().isoformat(),
        'url': 'https://news.microsoft.com'
    }
]

class AIRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # API路由
        if parsed_path.path == '/api/test':
            self.send_api_response({
                'success': True,
                'message': 'AI资讯API运行正常',
                'timestamp': datetime.now().isoformat()
            })
        
        elif parsed_path.path == '/api/system/status':
            self.send_api_response({
                'success': True,
                'online': True,
                'server': 'AI资讯聚合站',
                'version': '1.0.0',
                'ip_address': '43.159.52.61',
                'port': PORT,
                'total_news': len(mock_news),
                'update_frequency': '实时'
            })
        
        elif parsed_path.path == '/api/ai-news':
            query_params = parse_qs(parsed_path.query)
            category = query_params.get('category', ['all'])[0]
            
            if category == 'all':
                news_data = mock_news
            else:
                news_data = [n for n in mock_news if n['category'] == category]
            
            self.send_api_response({
                'success': True,
                'news': news_data,
                'total': len(news_data),
                'last_update': datetime.now().isoformat()
            })
        
        else:
            # 静态文件服务
            super().do_GET()
    
    def send_api_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps(data, ensure_ascii=False)
        self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        # 简化日志输出
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.address_string()} - {format % args}")

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("="*60)
    print("🤖 AI资讯聚合站 - 轻量级服务器")
    print("="*60)
    print(f"主页面: http://43.159.52.61:{PORT}")
    print(f"API状态: http://43.159.52.61:{PORT}/api/system/status")
    print(f"测试API: http://43.159.52.61:{PORT}/api/test")
    print(f"AI资讯: http://43.159.52.61:{PORT}/api/ai-news")
    print("="*60)
    print("服务器启动中...")
    
    with socketserver.TCPServer(("", PORT), AIRequestHandler) as httpd:
        print(f"服务器已在端口 {PORT} 启动")
        print(f"按 Ctrl+C 停止服务器")
        httpd.serve_forever()

if __name__ == '__main__':
    import os
    main()