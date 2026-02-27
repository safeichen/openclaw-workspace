#!/usr/bin/env python3
"""
AI资讯网站后端服务器 - 简化版本
"""

import os
import json
import time
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import subprocess
import threading

# 配置
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

PORT = 8080
HOST = '0.0.0.0'

# 模拟数据存储
news_cache = {
    'last_update': datetime.now().isoformat(),
    'news': [],
    'trends': {},
    'stats': {}
}

# 模拟资讯数据
def get_mock_news(category='all'):
    mock_news = [
        {
            'id': '1',
            'title': 'OpenAI发布新一代多模态模型，实现文本图像视频统一理解',
            'excerpt': 'OpenAI最新研究突破，推出能够同时处理文本、图像和视频的统一模型架构，在多项基准测试中刷新记录。',
            'category': 'research',
            'source': 'OpenAI Blog',
            'date': (datetime.now() - timedelta(hours=2)).isoformat(),
            'url': 'https://openai.com/blog'
        },
        {
            'id': '2',
            'title': '谷歌DeepMind推出AlphaFold 3，蛋白质结构预测准确率再提升',
            'excerpt': 'AlphaFold 3在蛋白质结构预测方面取得重大进展，准确率相比上一代提升15%，有望加速药物研发进程。',
            'category': 'research',
            'source': 'Nature',
            'date': (datetime.now() - timedelta(hours=5)).isoformat(),
            'url': 'https://www.nature.com'
        },
        {
            'id': '3',
            'title': '微软将Copilot全面集成Office套件，AI办公时代来临',
            'excerpt': '微软宣布将Copilot AI助手深度集成到所有Office应用中，大幅提升办公效率和创造力。',
            'category': 'industry',
            'source': 'Microsoft News',
            'date': (datetime.now() - timedelta(hours=8)).isoformat(),
            'url': 'https://news.microsoft.com'
        },
        {
            'id': '4',
            'title': 'AI芯片初创公司获5亿美元融资，专注边缘计算场景',
            'excerpt': '专注于边缘AI计算的芯片公司完成新一轮融资，计划推出面向物联网设备的专用AI处理器。',
            'category': 'startup',
            'source': 'TechCrunch',
            'date': (datetime.now() - timedelta(days=1)).isoformat(),
            'url': 'https://techcrunch.com'
        },
        {
            'id': '5',
            'title': '欧盟通过AI法案，建立全球最严格AI监管框架',
            'excerpt': '欧洲议会正式通过AI法案，对高风险AI系统实施严格监管，为全球AI治理提供参考。',
            'category': 'ethics',
            'source': 'EU Parliament',
            'date': (datetime.now() - timedelta(days=2)).isoformat(),
            'url': 'https://www.europarl.europa.eu'
        },
        {
            'id': '6',
            'title': 'GitHub Copilot企业版发布，支持私有代码库训练',
            'excerpt': 'GitHub推出Copilot企业版本，支持在私有代码库上进行定制化训练，提升代码生成准确性。',
            'category': 'tools',
            'source': 'GitHub Blog',
            'date': (datetime.now() - timedelta(days=3)).isoformat(),
            'url': 'https://github.blog'
        }
    ]
    
    if category != 'all':
        return [news for news in mock_news if news['category'] == category]
    return mock_news

def update_news_cache():
    """更新资讯缓存"""
    while True:
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 更新AI资讯缓存...")
            
            # 尝试使用OpenClaw获取真实数据
            try:
                result = subprocess.run(
                    ['openclaw', 'news', '--brief', '--json'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    # 解析OpenClaw输出
                    news_data = []
                    lines = result.stdout.strip().split('\n')
                    for i, line in enumerate(lines[:10]):  # 限制10条
                        if line.strip():
                            news_data.append({
                                'id': f'ocl-{i}',
                                'title': line[:100] + '...' if len(line) > 100 else line,
                                'excerpt': '来自OpenClaw news-summary技能的实时AI资讯',
                                'category': 'research',
                                'source': 'OpenClaw News',
                                'date': datetime.now().isoformat(),
                                'url': '#'
                            })
                    
                    if news_data:
                        news_cache['news'] = news_data
                    else:
                        news_cache['news'] = get_mock_news('all')
                else:
                    news_cache['news'] = get_mock_news('all')
                    
            except Exception as e:
                print(f"OpenClaw调用失败，使用模拟数据: {e}")
                news_cache['news'] = get_mock_news('all')
            
            # 更新统计信息
            news_cache['last_update'] = datetime.now().isoformat()
            news_cache['stats'] = {
                'total_news': len(news_cache['news']),
                'source_count': len(set(n['source'] for n in news_cache['news'])),
                'update_frequency': '5分钟'
            }
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 缓存更新完成: {len(news_cache['news'])} 条资讯")
            
        except Exception as e:
            print(f"更新缓存失败: {e}")
        
        # 每5分钟更新一次
        time.sleep(300)

# API路由
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/ai-news', methods=['GET'])
def get_ai_news():
    category = request.args.get('category', 'all')
    news_data = get_mock_news(category)
    
    return jsonify({
        'success': True,
        'news': news_data,
        'total': len(news_data),
        'last_update': news_cache['last_update']
    })

@app.route('/api/system/status', methods=['GET'])
def system_status():
    return jsonify({
        'success': True,
        'online': True,
        'server': 'AI资讯聚合站',
        'version': '1.0.0',
        'ip_address': '43.159.52.61',
        'port': PORT,
        'uptime': '1天',
        'last_news_update': news_cache['last_update'],
        'total_news': len(news_cache['news']),
        'update_frequency': '5分钟'
    })

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({
        'success': True,
        'message': 'AI资讯API运行正常',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('.', path)
    except:
        return jsonify({'error': '文件未找到'}), 404

def main():
    # 启动后台更新线程
    update_thread = threading.Thread(target=update_news_cache, daemon=True)
    update_thread.start()
    
    print("="*60)
    print("🤖 AI资讯聚合站 - 后端服务器")
    print("="*60)
    print(f"主页面: http://43.159.52.61:{PORT}")
    print(f"API状态: http://43.159.52.61:{PORT}/api/system/status")
    print(f"测试API: http://43.159.52.61:{PORT}/api/test")
    print("\n后台任务: 每5分钟自动更新AI资讯")
    print("="*60)
    
    # 立即执行一次初始更新
    update_news_cache()
    
    app.run(host=HOST, port=PORT, debug=False, threaded=True)

if __name__ == '__main__':
    main()