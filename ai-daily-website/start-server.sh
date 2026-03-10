#!/bin/bash

# AI Daily Insights 本地测试服务器
# 启动一个简单的HTTP服务器来测试网站

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=8080

echo "🚀 启动 AI Daily Insights 本地测试服务器..."
echo "项目目录: $PROJECT_ROOT"
echo "访问地址: http://localhost:$PORT"
echo ""
echo "📱 测试设备:"
echo "  • 电脑: http://localhost:$PORT"
echo "  • 手机: http://[你的IP地址]:$PORT"
echo ""
echo "📊 网站功能:"
echo "  • 首页: 左右分栏显示资讯和论文"
echo "  • 资讯页面: 完整的资讯列表"
echo "  • 论文页面: 完整的论文列表"
echo "  • 自动更新: 每天自动更新内容"
echo ""
echo "🔄 自动更新测试:"
echo "  运行: ./scripts/update-content.sh"
echo "  设置定时任务: ./scripts/setup-cron.sh"
echo ""

# 检查Python3是否可用
if command -v python3 &> /dev/null; then
    echo "使用 Python3 HTTP 服务器..."
    cd "$PROJECT_ROOT"
    python3 -m http.server "$PORT"
elif command -v python &> /dev/null; then
    echo "使用 Python HTTP 服务器..."
    cd "$PROJECT_ROOT"
    python -m SimpleHTTPServer "$PORT"
elif command -v php &> /dev/null; then
    echo "使用 PHP 内置服务器..."
    cd "$PROJECT_ROOT"
    php -S "localhost:$PORT"
elif command -v node &> /dev/null; then
    echo "使用 Node.js HTTP 服务器..."
    cat > "$PROJECT_ROOT/server.js" << 'EOF'
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8080;
const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

const server = http.createServer((req, res) => {
  let filePath = '.' + req.url;
  if (filePath === './') {
    filePath = './index.html';
  }

  const extname = path.extname(filePath);
  const contentType = MIME_TYPES[extname] || 'application/octet-stream';

  fs.readFile(filePath, (error, content) => {
    if (error) {
      if (error.code === 'ENOENT') {
        res.writeHead(404);
        res.end('File not found');
      } else {
        res.writeHead(500);
        res.end('Server error: ' + error.code);
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf-8');
    }
  });
});

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}/`);
});
EOF
    cd "$PROJECT_ROOT"
    node server.js
else
    echo "错误: 未找到可用的HTTP服务器"
    echo "请安装以下任一工具:"
    echo "  • Python3: python3 -m http.server"
    echo "  • PHP: php -S localhost:8080"
    echo "  • Node.js: npm install -g http-server"
    exit 1
fi