#!/usr/bin/env python3
"""
OpenClaw测试Web服务器
提供静态文件服务和简单的API接口
"""

import http.server
import socketserver
import json
import os
import sys
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import subprocess
import threading

PORT = 80
WEB_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenClawHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """自定义HTTP请求处理器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        
        # API路由
        if parsed_path.path == '/api/status':
            self.handle_api_status()
        elif parsed_path.path == '/api/system':
            self.handle_api_system()
        elif parsed_path.path == '/api/email-status':
            self.handle_api_email_status()
        else:
            # 静态文件服务
            super().do_GET()
    
    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        self.send_error(404, "API endpoint not found")
    
    def handle_api_status(self):
        """处理状态API"""
        response = {
            "status": "online",
            "time": datetime.now().isoformat(),
            "server": "OpenClaw Test Server",
            "version": "1.0.0",
            "endpoints": [
                "/api/status",
                "/api/system", 
                "/api/email-status"
            ]
        }
        
        self.send_json_response(response)
    
    def handle_api_system(self):
        """处理系统信息API"""
        try:
            # 获取系统信息
            hostname = subprocess.check_output(['hostname']).decode().strip()
            
            # 检查服务状态
            services = []
            
            # 检查OpenClaw Gateway
            try:
                gateway_result = subprocess.run(['pgrep', '-f', 'openclaw-gate'], 
                                              capture_output=True, text=True)
                services.append({
                    "name": "OpenClaw Gateway",
                    "status": "running" if gateway_result.returncode == 0 else "stopped",
                    "pid": gateway_result.stdout.strip() if gateway_result.stdout else "N/A"
                })
            except:
                services.append({
                    "name": "OpenClaw Gateway",
                    "status": "unknown",
                    "pid": "N/A"
                })
            
            # 检查cron服务
            try:
                cron_result = subprocess.run(['pgrep', 'cron'], 
                                           capture_output=True, text=True)
                services.append({
                    "name": "Cron Service",
                    "status": "running" if cron_result.returncode == 0 else "stopped"
                })
            except:
                services.append({
                    "name": "Cron Service",
                    "status": "unknown"
                })
            
            # 检查邮件监控
            email_monitor_running = False
            try:
                with open('/root/.openclaw/workspace/skills/imap-smtp-email/scripts/email-monitor-cache.json', 'r') as f:
                    cache_data = json.load(f)
                    if 'lastCheck' in cache_data:
                        email_monitor_running = True
            except:
                pass
            
            services.append({
                "name": "邮件监控系统",
                "status": "running" if email_monitor_running else "stopped",
                "last_check": cache_data.get('lastCheck', 'N/A') if email_monitor_running else 'N/A'
            })
            
            response = {
                "hostname": hostname,
                "ip_address": "43.159.52.61",
                "port": PORT,
                "services": services,
                "timestamp": datetime.now().isoformat()
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            self.send_error(500, f"Error getting system info: {str(e)}")
    
    def handle_api_email_status(self):
        """处理邮件状态API"""
        try:
            cache_file = '/root/.openclaw/workspace/skills/imap-smtp-email/scripts/email-monitor-cache.json'
            notified_file = '/root/.openclaw/workspace/skills/imap-smtp-email/scripts/email-notified.json'
            
            cache_data = {}
            notified_data = {}
            
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
            
            if os.path.exists(notified_file):
                with open(notified_file, 'r') as f:
                    notified_data = json.load(f)
            
            response = {
                "email_monitor": {
                    "enabled": True,
                    "last_check": cache_data.get('lastCheck', 'Never'),
                    "check_interval": "5 minutes",
                    "notified_count": len(notified_data.get('notifiedIds', [])),
                    "cache_file": cache_file,
                    "status": "active" if cache_data.get('lastCheck') else "inactive"
                },
                "timestamp": datetime.now().isoformat()
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            self.send_error(500, f"Error getting email status: {str(e)}")
    

    
    def send_json_response(self, data, status=200):
        """发送JSON响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{timestamp} - {self.address_string()} - {format % args}")

def start_server():
    """启动HTTP服务器"""
    os.chdir(WEB_DIR)
    
    with socketserver.TCPServer(("", PORT), OpenClawHTTPRequestHandler) as httpd:
        print(f"🚀 OpenClaw测试服务器已启动")
        print(f"📡 访问地址: http://43.159.52.61:{PORT}")
        print(f"📁 服务目录: {WEB_DIR}")
        print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n可用API端点:")
        print(f"  GET  http://43.159.52.61:{PORT}/api/status")
        print(f"  GET  http://43.159.52.61:{PORT}/api/system")
        print(f"  GET  http://43.159.52.61:{PORT}/api/email-status")
        print("\n按 Ctrl+C 停止服务器")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服务器正在停止...")
            httpd.shutdown()
            print("✅ 服务器已停止")

if __name__ == "__main__":
    # 检查端口是否被占用
    try:
        start_server()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ 端口 {PORT} 已被占用")
            print("请尝试:")
            print(f"  1. 停止占用端口 {PORT} 的进程")
            print(f"  2. 修改 server.py 中的 PORT 变量")
            print(f"  3. 使用其他端口运行: python3 server.py --port 8081")
        else:
            print(f"❌ 启动服务器失败: {e}")
        sys.exit(1)