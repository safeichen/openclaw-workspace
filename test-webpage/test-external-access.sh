#!/bin/bash

# 测试外部网络访问脚本

SERVER_IP="43.159.52.61"
PORT="80"
TEST_URL="http://${SERVER_IP}:${PORT}"

echo "🔍 测试OpenClaw测试页面外部访问"
echo "=========================================="
echo "服务器IP: $SERVER_IP"
echo "端口: $PORT"
echo "测试URL: $TEST_URL"
echo "测试时间: $(date)"
echo "=========================================="
echo ""

# 测试1: 基础连接
echo "1. 测试基础连接..."
if ping -c 2 $SERVER_IP > /dev/null 2>&1; then
    echo "   ✅ Ping测试成功"
else
    echo "   ❌ Ping测试失败"
fi

# 测试2: 端口扫描
echo "2. 测试端口访问..."
if timeout 5 bash -c "cat < /dev/null > /dev/tcp/${SERVER_IP}/${PORT}" 2>/dev/null; then
    echo "   ✅ 端口 $PORT 可访问"
else
    echo "   ❌ 端口 $PORT 不可访问"
fi

# 测试3: HTTP连接
echo "3. 测试HTTP连接..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "${TEST_URL}/" 2>/dev/null)
if [ "$HTTP_STATUS" = "200" ]; then
    echo "   ✅ HTTP连接成功 (状态码: $HTTP_STATUS)"
else
    echo "   ❌ HTTP连接失败 (状态码: ${HTTP_STATUS:-超时})"
fi

# 测试4: API状态
echo "4. 测试API状态..."
API_RESPONSE=$(curl -s --connect-timeout 10 "${TEST_URL}/api/status" 2>/dev/null)
if echo "$API_RESPONSE" | grep -q "online"; then
    echo "   ✅ API状态正常"
    echo "   📊 服务器信息:"
    echo "$API_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$API_RESPONSE"
else
    echo "   ❌ API状态异常"
    echo "   响应: $API_RESPONSE"
fi

# 测试5: 系统信息
echo "5. 测试系统信息API..."
SYS_RESPONSE=$(curl -s --connect-timeout 10 "${TEST_URL}/api/system" 2>/dev/null)
if echo "$SYS_RESPONSE" | grep -q "hostname"; then
    echo "   ✅ 系统信息API正常"
    
    # 提取关键信息
    HOSTNAME=$(echo "$SYS_RESPONSE" | grep -o '"hostname": "[^"]*"' | cut -d'"' -f4)
    SERVICES=$(echo "$SYS_RESPONSE" | grep -o '"services": \[.*\]' | head -1)
    
    echo "   🖥️  主机名: $HOSTNAME"
    echo "   📡 服务状态:"
    
    # 解析服务状态
    echo "$SYS_RESPONSE" | grep -o '"name": "[^"]*".*"status": "[^"]*"' | while read line; do
        NAME=$(echo "$line" | grep -o '"name": "[^"]*"' | cut -d'"' -f4)
        STATUS=$(echo "$line" | grep -o '"status": "[^"]*"' | cut -d'"' -f4)
        
        if [ "$STATUS" = "running" ]; then
            echo "     ✅ $NAME: $STATUS"
        else
            echo "     ❌ $NAME: $STATUS"
        fi
    done
else
    echo "   ❌ 系统信息API异常"
fi

echo ""
echo "=========================================="
echo "📋 访问指南:"
echo "1. 主页面: $TEST_URL"
echo "2. API状态: ${TEST_URL}/api/status"
echo "3. 系统信息: ${TEST_URL}/api/system"
echo "4. 邮件状态: ${TEST_URL}/api/email-status"
echo ""
echo "🔧 本地测试命令:"
echo "curl $TEST_URL"
echo "curl ${TEST_URL}/api/status"
echo "curl ${TEST_URL}/api/system"
echo "curl -X POST ${TEST_URL}/api/test-email"
echo ""
echo "✅ 测试完成!"