#!/bin/bash
# AI资讯网站80端口启动脚本

echo "启动AI资讯网站（80端口）..."
echo "当前目录: $(pwd)"

# 检查是否以root运行
if [ "$EUID" -ne 0 ]; then 
    echo "错误：80端口需要root权限"
    echo "请使用: sudo $0"
    exit 1
fi

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到python3"
    exit 1
fi

# 检查Flask
if ! python3 -c "import flask" 2>/dev/null; then
    echo "安装Flask..."
    pip3 install flask flask-cors
fi

# 停止可能已经在运行的服务器
echo "停止现有服务..."
pkill -f "python3.*server.py" 2>/dev/null || true
sleep 2

# 启动服务器
echo "启动服务器在 http://0.0.0.0:80 ..."
cd "$(dirname "$0")"
nohup python3 server.py > server-80.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > server-80.pid

echo "服务器已启动，PID: $SERVER_PID"
echo "日志文件: server-80.log"
echo "访问地址: http://$(hostname -I | awk '{print $1}'):80"
echo "本地访问: http://localhost:80"
echo ""
echo "检查服务状态:"
sleep 2
netstat -tlnp | grep :80 || echo "端口80未监听，请检查日志"