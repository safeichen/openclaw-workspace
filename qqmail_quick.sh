#!/bin/bash
# QQ邮箱快速使用脚本

echo "📧 QQ邮箱快速助手"
echo "================="

SKILL_DIR="/root/.openclaw/workspace/skills/imap-smtp-email"
cd "$SKILL_DIR"

while true; do
    echo ""
    echo "📋 功能菜单"
    echo "=========="
    echo "1. 查看邮件列表"
    echo "2. 查看未读邮件"
    echo "3. 搜索邮件"
    echo "4. 发送邮件"
    echo "5. 回复邮件"
    echo "6. 测试连接"
    echo "7. 退出"
    echo ""
    
    read -p "请选择 (1-7): " choice
    
    case $choice in
        1)
            echo "📨 查看最近邮件"
            read -p "显示数量 (默认5): " limit
            limit=${limit:-5}
            node scripts/imap.js check --limit "$limit"
            ;;
        2)
            echo "📬 查看未读邮件"
            read -p "显示数量 (默认10): " limit
            limit=${limit:-10}
            node scripts/imap.js check --unseen --limit "$limit"
            ;;
        3)
            echo "🔍 搜索邮件"
            echo "搜索选项:"
            echo "  a) 按发件人搜索"
            echo "  b) 按主题搜索"
            echo "  c) 搜索未读邮件"
            echo "  d) 搜索今天邮件"
            read -p "选择搜索类型 (a/b/c/d): " search_type
            
            case $search_type in
                a)
                    read -p "发件人邮箱: " from_email
                    node scripts/imap.js search --from "$from_email" --limit 10
                    ;;
                b)
                    read -p "主题关键词: " subject
                    node scripts/imap.js search --subject "$subject" --limit 10
                    ;;
                c)
                    node scripts/imap.js search --unseen --limit 10
                    ;;
                d)
                    node scripts/imap.js search --recent 1d --limit 10
                    ;;
                *)
                    echo "❌ 无效选择"
                    ;;
            esac
            ;;
        4)
            echo "📤 发送邮件"
            read -p "收件人: " to_email
            read -p "主题: " subject
            read -p "内容: " body
            
            if [ -n "$to_email" ] && [ -n "$subject" ] && [ -n "$body" ]; then
                node scripts/smtp.js send --to "$to_email" --subject "$subject" --body "$body"
            else
                echo "❌ 收件人、主题和内容都不能为空"
            fi
            ;;
        5)
            echo "↩️  回复邮件"
            echo "先查看邮件列表获取UID..."
            node scripts/imap.js check --limit 5
            
            read -p "输入要回复的邮件UID: " uid
            read -p "回复内容: " reply_body
            
            if [ -n "$uid" ] && [ -n "$reply_body" ]; then
                node reply_email.js "$uid" --body "$reply_body"
            else
                echo "❌ UID和回复内容不能为空"
            fi
            ;;
        6)
            echo "🔧 测试连接"
            echo "测试IMAP连接..."
            node scripts/imap.js check --limit 1
            
            echo ""
            echo "测试SMTP连接..."
            node scripts/smtp.js test
            ;;
        7)
            echo "👋 再见！"
            exit 0
            ;;
        *)
            echo "❌ 无效选择"
            ;;
    esac
    
    echo ""
    echo "----------------------------------------"
done