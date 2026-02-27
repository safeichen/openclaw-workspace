#!/usr/bin/env python3
"""
简单的HTTP服务器，用于在80端口提供AI资讯网站静态文件
"""

import http.server
import socketserver
import os
import sys

PORT = 80
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def log_message(self, format, *args):
        # 简化日志输出
        sys.stderr.write("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format % args))
    
    def end_headers(self):
        # 添加CORS头
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def main():
    # 切换到网站目录
    os.chdir(DIRECTORY)
    
    print(f"启动AI资讯网站HTTP服务器")
    print(f"目录: {DIRECTORY}")
    print(f"端口: {PORT}")
    print(f"访问地址: http://0.0.0.0:{PORT}")
    print(f"本地访问: http://localhost:{PORT}")
    print("按 Ctrl+C 停止服务器")
    
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
            httpd.serve_forever()
    except PermissionError:
        print(f"错误：需要root权限才能绑定到端口{PORT}")
        print("请使用: sudo python3 simple-http-server.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()