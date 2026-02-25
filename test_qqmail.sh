#!/bin/bash
# QQ邮箱连接测试脚本

echo "🔧 QQ邮箱连接测试"
echo "================="

SKILL_DIR="/root/.openclaw/workspace/skills/imap-smtp-email"
ENV_FILE="$SKILL_DIR/.env"

# 检查配置文件
check_config() {
    echo "📋 检查配置文件..."
    
    if [ ! -f "$ENV_FILE" ]; then
        echo "❌ 配置文件不存在: $ENV_FILE"
        echo ""
        echo "请先创建配置文件:"
        echo "1. cd $SKILL_DIR"
        echo "2. cp .env.qqmail .env"
        echo "3. 编辑 .env 文件，填写你的QQ邮箱信息"
        return 1
    fi
    
    # 检查关键配置
    echo "✅ 配置文件存在"
    echo ""
    echo "当前配置摘要:"
    echo "--------------"
    
    if grep -q "你的QQ号" "$ENV_FILE"; then
        echo "⚠️  检测到示例配置，请修改为你的实际信息"
        echo ""
        grep -E "^(IMAP_USER|IMAP_HOST|SMTP_HOST)=" "$ENV_FILE"
        return 1
    fi
    
    # 显示配置（隐藏密码）
    grep -E "^(IMAP_HOST|IMAP_USER|IMAP_PORT|SMTP_HOST|SMTP_PORT)=" "$ENV_FILE" | while read line; do
        key=$(echo "$line" | cut -d= -f1)
        value=$(echo "$line" | cut -d= -f2)
        echo "  $key=$value"
    done
    
    # 检查是否使用了授权码（密码长度提示）
    pass_line=$(grep "^IMAP_PASS=" "$ENV_FILE")
    if [ -n "$pass_line" ]; then
        pass_value=$(echo "$pass_line" | cut -d= -f2)
        pass_length=${#pass_value}
        echo "  IMAP_PASS长度: $pass_length 字符"
        
        if [ "$pass_length" -lt 16 ]; then
            echo "⚠️  密码长度较短，QQ邮箱授权码应为16位"
        fi
    fi
    
    return 0
}

# 测试网络连接
test_network() {
    echo ""
    echo "🌐 测试网络连接..."
    
    # 测试QQ邮箱服务器
    servers=("imap.qq.com:993" "smtp.qq.com:587" "smtp.qq.com:465")
    
    for server in "${servers[@]}"; do
        host=$(echo "$server" | cut -d: -f1)
        port=$(echo "$server" | cut -d: -f2)
        
        echo -n "  测试 $host:$port ... "
        
        # 使用nc测试端口
        if timeout 5 nc -z "$host" "$port" 2>/dev/null; then
            echo "✅ 可连接"
        else
            echo "❌ 连接失败"
        fi
    done
}

# 测试IMAP连接
test_imap() {
    echo ""
    echo "📨 测试IMAP连接（接收邮件）..."
    
    cd "$SKILL_DIR"
    
    # 简单测试
    echo "尝试连接QQ邮箱IMAP服务器..."
    
    # 使用Node.js测试脚本
    if node -e "
const Imap = require('imap');
const dotenv = require('dotenv');
dotenv.config();

const config = {
  user: process.env.IMAP_USER,
  password: process.env.IMAP_PASS,
  host: process.env.IMAP_HOST,
  port: parseInt(process.env.IMAP_PORT),
  tls: process.env.IMAP_TLS === 'true',
  tlsOptions: { rejectUnauthorized: process.env.IMAP_REJECT_UNAUTHORIZED === 'true' }
};

console.log('配置:', { 
  host: config.host, 
  port: config.port, 
  user: config.user.substring(0, 3) + '...' 
});

const imap = new Imap(config);

imap.once('ready', () => {
  console.log('✅ IMAP连接成功');
  imap.end();
});

imap.once('error', (err) => {
  console.log('❌ IMAP连接失败:', err.message);
});

imap.connect();
" 2>&1; then
        echo ""
    else
        echo "❌ IMAP测试脚本执行失败"
    fi
}

# 测试SMTP连接
test_smtp() {
    echo ""
    echo "📤 测试SMTP连接（发送邮件）..."
    
    cd "$SKILL_DIR"
    
    echo "尝试连接QQ邮箱SMTP服务器..."
    
    # 使用Node.js测试脚本
    if node -e "
const nodemailer = require('nodemailer');
const dotenv = require('dotenv');
dotenv.config();

const config = {
  host: process.env.SMTP_HOST,
  port: parseInt(process.env.SMTP_PORT),
  secure: process.env.SMTP_SECURE === 'true',
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS
  },
  tls: {
    rejectUnauthorized: process.env.SMTP_REJECT_UNAUTHORIZED === 'true'
  }
};

console.log('配置:', { 
  host: config.host, 
  port: config.port, 
  user: config.auth.user.substring(0, 3) + '...',
  secure: config.secure 
});

const transporter = nodemailer.createTransport(config);

// 测试连接
transporter.verify(function(error, success) {
  if (error) {
    console.log('❌ SMTP连接失败:', error.message);
  } else {
    console.log('✅ SMTP连接成功');
  }
});
" 2>&1; then
        echo ""
    else
        echo "❌ SMTP测试脚本执行失败"
    fi
}

# 完整测试
full_test() {
    echo ""
    echo "🚀 开始完整测试..."
    echo "=================="
    
    if ! check_config; then
        return 1
    fi
    
    test_network
    test_imap
    test_smtp
    
    echo ""
    echo "📊 测试完成！"
    echo "如果看到'✅ 连接成功'，说明配置正确。"
    echo "如果看到'❌ 连接失败'，请检查："
    echo "1. 网络连接"
    echo "2. 授权码是否正确"
    echo "3. 是否开启了IMAP/SMTP服务"
}

# 快速修复建议
show_fixes() {
    echo ""
    echo "🔧 常见问题修复："
    echo "1. 授权码问题："
    echo "   - 确保使用16位授权码，不是QQ密码"
    echo "   - 重新生成授权码：QQ邮箱设置 → 账户 → 生成授权码"
    echo ""
    echo "2. 服务未开启："
    echo "   - 登录QQ邮箱网页版"
    echo "   - 设置 → 账户 → POP3/IMAP/SMTP服务"
    echo "   - 开启'IMAP/SMTP服务'"
    echo ""
    echo "3. 网络问题："
    echo "   - 测试: ping imap.qq.com"
    echo "   - 测试: telnet imap.qq.com 993"
    echo ""
    echo "4. 配置问题："
    echo "   - 检查 .env 文件格式"
    echo "   - 确保没有多余的空格"
    echo "   - 确保使用正确的QQ邮箱地址"
}

# 主菜单
main_menu() {
    while true; do
        echo ""
        echo "📋 QQ邮箱配置测试"
        echo "================="
        echo "1. 检查配置文件"
        echo "2. 测试网络连接"
        echo "3. 测试IMAP连接"
        echo "4. 测试SMTP连接"
        echo "5. 完整测试"
        echo "6. 查看修复建议"
        echo "7. 退出"
        echo ""
        
        read -p "请选择 (1-7): " choice
        
        case $choice in
            1) check_config ;;
            2) test_network ;;
            3) test_imap ;;
            4) test_smtp ;;
            5) full_test ;;
            6) show_fixes ;;
            7) echo "👋 再见！"; exit 0 ;;
            *) echo "❌ 无效选择" ;;
        esac
        
        echo ""
        echo "----------------------------------------"
    done
}

# 主程序
main() {
    echo "🔧 QQ邮箱配置助手"
    echo "================="
    echo "确保你已经："
    echo "1. 获取了QQ邮箱16位授权码"
    echo "2. 开启了IMAP/SMTP服务"
    echo "3. 创建了 .env 配置文件"
    echo ""
    
    main_menu
}

# 运行主程序
main "$@"