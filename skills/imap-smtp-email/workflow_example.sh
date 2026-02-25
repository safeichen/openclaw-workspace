#!/bin/bash
# 邮件回复工作流程示例

echo "📧 邮件回复工作流程演示"
echo "========================"

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SKILL_DIR"

# 检查环境
check_environment() {
    echo "🔧 检查环境..."
    
    # 检查配置文件
    if [ ! -f ".env" ]; then
        echo "❌ 缺少 .env 配置文件"
        echo "请先运行: cp .env.example .env 并填写邮箱信息"
        exit 1
    fi
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js 未安装"
        exit 1
    fi
    
    echo "✅ 环境检查通过"
    echo ""
}

# 演示1: 查看和选择邮件
demo_view_and_select() {
    echo "1️⃣ 查看邮件列表"
    echo "---------------"
    
    echo "查看最近5封邮件:"
    node scripts/imap.js check --limit 5
    
    echo ""
    echo "查看未读邮件:"
    node scripts/imap.js check --unseen --limit 3
    
    echo ""
    read -p "请输入要回复的邮件UID (按Enter跳过): " mail_uid
    
    if [ -n "$mail_uid" ]; then
        echo ""
        echo "📨 邮件详情:"
        node scripts/imap.js fetch "$mail_uid" --simple
    fi
}

# 演示2: 简单回复
demo_simple_reply() {
    echo ""
    echo "2️⃣ 简单回复演示"
    echo "---------------"
    
    read -p "请输入测试邮件UID (或按Enter使用示例): " test_uid
    
    if [ -z "$test_uid" ]; then
        echo "使用示例回复..."
        # 这里可以创建一个测试邮件
        echo "📤 发送测试邮件给自己..."
        node scripts/smtp.js send --to "$(grep IMAP_USER .env | cut -d= -f2)" \
            --subject "测试回复功能 - $(date '+%Y-%m-%d %H:%M')" \
            --body "这是一封测试邮件，用于演示回复功能。"
        
        echo "等待5秒让邮件到达..."
        sleep 5
        
        # 获取最新邮件的UID
        test_uid=$(node scripts/imap.js check --limit 1 --json 2>/dev/null | grep -o '"uid":"[^"]*"' | head -1 | cut -d'"' -f4)
        
        if [ -z "$test_uid" ]; then
            echo "❌ 无法获取测试邮件UID"
            return
        fi
    fi
    
    echo ""
    echo "回复邮件 UID: $test_uid"
    echo "回复内容: '收到测试邮件，谢谢！'"
    echo ""
    
    read -p "是否发送回复？ (y/n): " confirm
    if [ "$confirm" = "y" ]; then
        node reply_email.js "$test_uid" --body "收到测试邮件，谢谢！"
    fi
}

# 演示3: 高级回复功能
demo_advanced_reply() {
    echo ""
    echo "3️⃣ 高级回复功能"
    echo "---------------"
    
    echo "a) 包含原邮件内容的回复"
    echo "   命令: node reply_email.js <UID> --body '回复内容' --include-original"
    echo ""
    
    echo "b) 带抄送的回复"
    echo "   命令: node reply_email.js <UID> --body '回复内容' --cc 'cc1@example.com,cc2@example.com'"
    echo ""
    
    echo "c) 使用回复模板"
    echo "   创建模板文件: echo '感谢来信！我们会尽快处理。' > template.txt"
    echo "   使用模板: node reply_email.js <UID> --body \"\$(cat template.txt)\""
    echo ""
    
    echo "d) 批量回复未读邮件"
    echo "   #!/bin/bash"
    echo "   for uid in \$(node scripts/imap.js check --unseen --json | grep -o '\"uid\":\"[^\"]*\"' | cut -d'\"' -f4); do"
    echo "     node reply_email.js \$uid --body '自动回复：已收到'"
    echo "   done"
}

# 演示4: 实际工作流程
demo_workflow() {
    echo ""
    echo "4️⃣ 实际工作流程示例"
    echo "-------------------"
    
    cat << 'EOF'
日常邮件处理流程：

1. 早上检查邮件
   node scripts/imap.js check --unseen --limit 20

2. 快速分类
   # 重要邮件立即回复
   node reply_email.js <重要邮件UID> --body "正在处理，稍后详细回复"

   # 普通邮件批量回复
   for uid in $(获取普通邮件UID列表); do
     node reply_email.js $uid --body "已收到，谢谢！"
   done

3. 下午跟进
   # 标记需要跟进的邮件
   node scripts/imap.js mark-unread <需要跟进UID>

4. 下班前总结
   # 检查未回复邮件
   node scripts/imap.js check --unseen
   
   # 发送当日总结
   node scripts/smtp.js send --to "summary@example.com" --subject "今日邮件处理总结" --body "今日共处理XX封邮件..."
EOF
}

# 演示5: 集成到OpenClaw
demo_openclaw_integration() {
    echo ""
    echo "5️⃣ 集成到OpenClaw"
    echo "-----------------"
    
    cat << 'EOF'
将邮件功能集成到OpenClaw技能：

1. 创建邮件技能包装器
   ```python
   # email_skill.py
   class EmailSkill:
       def check_emails(self, limit=10):
           # 调用node scripts/imap.js check
           pass
       
       def reply_to_email(self, uid, content):
           # 调用node reply_email.js
           pass
   ```

2. 在OpenClaw中调用
   ```bash
   # 用户可以说：
   # "查看我的未读邮件"
   # "回复邮件12345：谢谢你的分享"
   # "发送邮件给xxx：主题：问候"
   ```

3. 定时邮件检查
   ```bash
   # 在cron中设置
   0 */2 * * * cd /path/to/skill && node scripts/imap.js check --unseen --limit 5
   ```
EOF
}

# 主菜单
main_menu() {
    while true; do
        echo ""
        echo "📋 演示菜单"
        echo "=========="
        echo "1. 查看和选择邮件"
        echo "2. 简单回复演示"
        echo "3. 高级回复功能"
        echo "4. 实际工作流程"
        echo "5. OpenClaw集成"
        echo "6. 退出"
        echo ""
        
        read -p "请选择 (1-6): " choice
        
        case $choice in
            1) demo_view_and_select ;;
            2) demo_simple_reply ;;
            3) demo_advanced_reply ;;
            4) demo_workflow ;;
            5) demo_openclaw_integration ;;
            6) echo "👋 再见！"; exit 0 ;;
            *) echo "❌ 无效选择" ;;
        esac
        
        echo ""
        echo "----------------------------------------"
    done
}

# 主程序
main() {
    check_environment
    main_menu
}

# 运行主程序
main "$@"