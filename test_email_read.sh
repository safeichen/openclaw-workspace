#!/bin/bash
# 邮件读取测试脚本

echo "📧 邮件读取测试"
echo "================"

SKILL_DIR="/root/.openclaw/workspace/skills/imap-smtp-email"
ENV_FILE="$SKILL_DIR/.env"

# 检查技能目录
if [ ! -d "$SKILL_DIR" ]; then
    echo "❌ 技能目录不存在: $SKILL_DIR"
    exit 1
fi

cd "$SKILL_DIR"

# 检查配置文件
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  配置文件不存在: $ENV_FILE"
    echo ""
    echo "请先创建配置文件:"
    echo "1. cp .env.example .env"
    echo "2. 编辑 .env 文件，填写你的邮箱信息"
    echo ""
    echo "QQ邮箱示例:"
    echo "  IMAP_HOST=imap.qq.com"
    echo "  IMAP_USER=你的QQ号@qq.com"
    echo "  IMAP_PASS=你的16位授权码"
    echo ""
    exit 1
fi

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    exit 1
fi

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install --quiet
fi

echo "✅ 环境检查通过"
echo ""

# 显示配置信息（隐藏密码）
echo "📋 当前配置:"
grep -E "^(IMAP_HOST|IMAP_USER|SMTP_HOST)=" "$ENV_FILE" | while read line; do
    key=$(echo "$line" | cut -d= -f1)
    value=$(echo "$line" | cut -d= -f2)
    echo "  $key=$value"
done
echo ""

# 测试菜单
while true; do
    echo "请选择测试项目:"
    echo "1. 测试IMAP连接"
    echo "2. 查看最近5封邮件"
    echo "3. 查看未读邮件"
    echo "4. 搜索测试"
    echo "5. 发送测试邮件"
    echo "6. 退出"
    echo ""
    read -p "选择 (1-6): " choice
    
    case $choice in
        1)
            echo "🔗 测试IMAP连接..."
            node scripts/imap.js check --limit 1
            ;;
        2)
            echo "📨 查看最近5封邮件..."
            node scripts/imap.js check --limit 5
            ;;
        3)
            echo "📬 查看未读邮件..."
            node scripts/imap.js check --unseen --limit 10
            ;;
        4)
            echo "🔍 搜索测试..."
            echo "可选搜索条件:"
            echo "  a) 搜索未读邮件"
            echo "  b) 搜索今天邮件"
            echo "  c) 自定义搜索"
            read -p "选择搜索类型 (a/b/c): " search_type
            
            case $search_type in
                a)
                    node scripts/imap.js search --unseen --limit 10
                    ;;
                b)
                    node scripts/imap.js search --recent 1d --limit 10
                    ;;
                c)
                    read -p "输入发件人邮箱 (留空跳过): " from_email
                    read -p "输入主题关键词 (留空跳过): " subject_keyword
                    
                    cmd="node scripts/imap.js search --limit 10"
                    if [ -n "$from_email" ]; then
                        cmd="$cmd --from \"$from_email\""
                    fi
                    if [ -n "$subject_keyword" ]; then
                        cmd="$cmd --subject \"$subject_keyword\""
                    fi
                    
                    eval $cmd
                    ;;
                *)
                    echo "❌ 无效选择"
                    ;;
            esac
            ;;
        5)
            echo "📤 发送测试邮件..."
            read -p "收件人邮箱: " to_email
            if [ -n "$to_email" ]; then
                node scripts/smtp.js send --to "$to_email" --subject "测试邮件 $(date '+%Y-%m-%d %H:%M:%S')" --body "这是一封来自OpenClaw邮件技能的测试邮件。"
            else
                echo "❌ 需要收件人邮箱"
            fi
            ;;
        6)
            echo "👋 退出"
            exit 0
            ;;
        *)
            echo "❌ 无效选择"
            ;;
    esac
    
    echo ""
    echo "----------------------------------------"
    echo ""
done