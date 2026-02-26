#!/bin/bash

# 检查80端口服务器状态

echo "🔍 检查80端口OpenClaw测试服务器状态"
echo "=========================================="
echo "服务器IP: 43.159.52.61"
echo "端口: 80 (HTTP标准端口)"
echo "测试时间: $(date)"
echo "=========================================="
echo ""

# 检查本地服务器进程
echo "1. 检查服务器进程..."
if pgrep -f "python.*server.py" > /dev/null; then
    echo "   ✅ Python服务器进程运行中"
    pgrep -f "python.*server.py" | while read pid; do
        echo "     进程ID: $pid, 命令: $(ps -p $pid -o cmd=)"
    done
else
    echo "   ❌ Python服务器进程未运行"
fi

# 检查端口监听
echo "2. 检查80端口监听状态..."
if netstat -tlnp 2>/dev/null | grep -q ":80 "; then
    echo "   ✅ 80端口正在监听"
    netstat -tlnp 2>/dev/null | grep ":80 " | while read line; do
        echo "     监听状态: $line"
    done
else
    echo "   ❌ 80端口未监听"
fi

# 测试本地HTTP连接
echo "3. 测试本地HTTP连接..."
LOCAL_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/status 2>/dev/null)
if [ "$LOCAL_STATUS" = "200" ]; then
    echo "   ✅ 本地HTTP连接成功 (状态码: $LOCAL_STATUS)"
    
    # 获取服务器信息
    SERVER_INFO=$(curl -s http://localhost/api/status)
    if echo "$SERVER_INFO" | grep -q "online"; then
        echo "   📊 服务器状态: online"
        echo "   🕐 服务器时间: $(echo "$SERVER_INFO" | grep -o '"time": "[^"]*"' | cut -d'"' -f4)"
    fi
else
    echo "   ❌ 本地HTTP连接失败 (状态码: ${LOCAL_STATUS:-无响应})"
fi

# 测试外部访问（如果可能）
echo "4. 测试外部网络访问..."
EXTERNAL_STATUS=$(timeout 5 curl -s -o /dev/null -w "%{http_code}" http://43.159.52.61/api/status 2>/dev/null || echo "timeout")
if [ "$EXTERNAL_STATUS" = "200" ]; then
    echo "   ✅ 外部HTTP连接成功 (状态码: $EXTERNAL_STATUS)"
    echo "   🌐 测试页面已可通过互联网访问!"
elif [ "$EXTERNAL_STATUS" = "timeout" ]; then
    echo "   ⚠️  外部连接超时"
    echo "     可能原因: 云服务器安全组未开放80端口"
else
    echo "   ❌ 外部HTTP连接失败 (状态码: $EXTERNAL_STATUS)"
fi

# 显示系统信息
echo "5. 显示系统信息..."
if [ "$LOCAL_STATUS" = "200" ]; then
    SYSTEM_INFO=$(curl -s http://localhost/api/system)
    if echo "$SYSTEM_INFO" | grep -q "hostname"; then
        HOSTNAME=$(echo "$SYSTEM_INFO" | grep -o '"hostname": "[^"]*"' | cut -d'"' -f4)
        echo "   🖥️  主机名: $HOSTNAME"
        
        # 显示服务状态
        echo "   📡 服务状态:"
        echo "$SYSTEM_INFO" | grep -o '"name": "[^"]*".*"status": "[^"]*"' | while read line; do
            NAME=$(echo "$line" | grep -o '"name": "[^"]*"' | cut -d'"' -f4)
            STATUS=$(echo "$line" | grep -o '"status": "[^"]*"' | cut -d'"' -f4)
            
            if [ "$STATUS" = "running" ]; then
                echo "      ✅ $NAME: $STATUS"
            else
                echo "      ❌ $NAME: $STATUS"
            fi
        done
    fi
fi

echo ""
echo "=========================================="
echo "📋 访问信息:"
echo "主页面: http://43.159.52.61"
echo "API状态: http://43.159.52.61/api/status"
echo "系统信息: http://43.159.52.61/api/system"
echo "邮件状态: http://43.159.52.61/api/email-status"
echo ""
echo "🔧 管理命令:"
echo "停止服务器: pkill -f 'python.*server.py'"
echo "重启服务器: cd /root/.openclaw/workspace/test-webpage && python3 server.py"
echo ""
echo "⚠️  注意: 80端口需要云服务器安全组开放规则"
echo "=========================================="