#!/usr/bin/env python3
from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route('/')
def index():
    return "AI资讯网站测试服务器"

@app.route('/api/test')
def test():
    return jsonify({
        'success': True,
        'message': '服务器运行正常',
        'time': time.time()
    })

if __name__ == '__main__':
    print("启动测试服务器...")
    app.run(host='0.0.0.0', port=8082, debug=False)