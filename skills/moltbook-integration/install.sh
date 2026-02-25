#!/bin/bash
# Moltbook集成技能安装脚本

set -e

echo "🚀 开始安装Moltbook集成技能..."

# 检查Python版本
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "📦 Python版本: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION 3.8" | awk '{print ($1 < $2)}') -eq 1 ]]; then
    echo "❌ 需要Python 3.8或更高版本"
    exit 1
fi

# 创建虚拟环境（可选）
if [ ! -d "venv" ]; then
    echo "🔧 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
fi

# 安装依赖
echo "📦 安装依赖包..."
pip install --upgrade pip
pip install aiohttp

# 创建必要的目录
echo "📁 创建目录结构..."
mkdir -p logs
mkdir -p data
mkdir -p cache

# 复制配置文件
if [ ! -f "config.yaml" ]; then
    echo "⚙️ 创建配置文件..."
    cp config.example.yaml config.yaml
    echo "✅ 配置文件已创建: config.yaml"
    echo "   请根据需要修改配置"
else
    echo "✅ 配置文件已存在"
fi

# 设置执行权限
echo "🔧 设置脚本权限..."
chmod +x cli.py

# 创建符号链接到PATH（可选）
if [ ! -f "/usr/local/bin/moltbook-cli" ]; then
    echo "🔗 创建命令行工具链接..."
    ln -sf "$(pwd)/cli.py" /usr/local/bin/moltbook-cli 2>/dev/null || true
    if [ -f "/usr/local/bin/moltbook-cli" ]; then
        echo "✅ 命令行工具已安装: moltbook-cli"
    fi
fi

# 测试安装
echo "🧪 测试安装..."
if python3 -c "import aiohttp" &>/dev/null; then
    echo "✅ 依赖检查通过"
else
    echo "❌ 依赖检查失败"
    exit 1
fi

# 运行简单测试
echo "🔍 运行基本测试..."
if python3 -c "
from integration.openclaw import get_integration
print('✅ 模块导入成功')
" 2>/dev/null; then
    echo "✅ 模块测试通过"
else
    echo "❌ 模块测试失败"
    exit 1
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "📋 下一步："
echo "1. 编辑 config.yaml 文件配置你的设置"
echo "2. 运行测试: python3 openclaw_skill.py"
echo "3. 使用命令行: python3 cli.py help"
echo "4. 或在OpenClaw中直接使用Moltbook技能"
echo ""
echo "💡 快速开始："
echo "  发布内容: python3 cli.py post '你好Moltbook!'"
echo "  查看动态: python3 cli.py feed"
echo "  搜索AI: python3 cli.py search --interests ai technology"
echo ""
echo "🔧 故障排除："
echo "  如果遇到权限问题: chmod +x *.py"
echo "  如果缺少依赖: pip install -r requirements.txt"
echo "  查看日志: tail -f logs/moltbook.log"