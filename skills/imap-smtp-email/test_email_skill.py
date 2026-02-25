#!/usr/bin/env python3
"""
IMAP/SMTP邮件技能测试脚本
用于测试和演示邮件读取功能
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def test_skill_availability():
    """测试技能是否可用"""
    print("🧪 测试IMAP/SMTP邮件技能...")
    
    skill_dir = Path(__file__).parent
    scripts_dir = skill_dir / "scripts"
    
    # 检查必要的文件
    required_files = [
        "imap.js",
        "smtp.js",
        "../package.json"
    ]
    
    for file in required_files:
        file_path = skill_dir / file if file.startswith("..") else scripts_dir / file
        if not file_path.exists():
            print(f"❌ 缺少文件: {file}")
            return False
    
    print("✅ 技能文件完整")
    return True

def show_usage_guide():
    """显示使用指南"""
    print("\n📖 IMAP/SMTP邮件技能使用指南")
    print("=" * 50)
    
    print("\n1. 配置邮箱连接:")
    print("   cd /root/.openclaw/workspace/skills/imap-smtp-email")
    print("   cp .env.example .env")
    print("   # 编辑 .env 文件，填写你的邮箱信息")
    
    print("\n2. 常用命令:")
    print("   # 检查新邮件")
    print("   node scripts/imap.js check --limit 5")
    
    print("   # 搜索未读邮件")
    print("   node scripts/imap.js search --unseen --limit 10")
    
    print("   # 搜索特定发件人")
    print("   node scripts/imap.js search --from 'service@example.com'")
    
    print("   # 发送邮件")
    print("   node scripts/smtp.js send --to 'recipient@example.com' --subject '测试' --body '内容'")
    
    print("\n3. 邮箱服务器配置示例:")
    print("   QQ邮箱: imap.qq.com:993 / smtp.qq.com:587")
    print("   Gmail: imap.gmail.com:993 / smtp.gmail.com:587")
    print("   163邮箱: imap.163.com:993 / smtp.163.com:465")
    
    print("\n4. 重要提示:")
    print("   - QQ邮箱需要使用'授权码'，不是QQ密码")
    print("   - Gmail需要使用'应用专用密码'")
    print("   - 163邮箱也需要使用'授权码'")

def create_quick_config():
    """创建快速配置模板"""
    config_template = """# 邮箱配置模板
# 选择你的邮箱服务，取消对应行的注释

# === QQ邮箱配置 ===
IMAP_HOST=imap.qq.com
IMAP_PORT=993
IMAP_USER=你的QQ邮箱@qq.com
IMAP_PASS=你的授权码（16位字符）
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_SECURE=false

# === Gmail配置 ===
# IMAP_HOST=imap.gmail.com
# IMAP_PORT=993
# IMAP_USER=你的Gmail@gmail.com
# IMAP_PASS=你的应用专用密码
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_SECURE=false

# === 163邮箱配置 ===
# IMAP_HOST=imap.163.com
# IMAP_PORT=993
# IMAP_USER=你的邮箱@163.com
# IMAP_PASS=你的授权码
# SMTP_HOST=smtp.163.com
# SMTP_PORT=465
# SMTP_SECURE=true

# 通用配置
IMAP_TLS=true
IMAP_REJECT_UNAUTHORIZED=true
IMAP_MAILBOX=INBOX
SMTP_USER=${IMAP_USER}
SMTP_PASS=${IMAP_PASS}
SMTP_FROM=${IMAP_USER}
SMTP_REJECT_UNAUTHORIZED=true
"""
    
    config_path = Path(__file__).parent / ".env.quick"
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_template)
    
    print(f"✅ 快速配置模板已创建: {config_path}")
    print("   请复制为 .env 并填写你的邮箱信息")

def test_node_environment():
    """测试Node.js环境"""
    print("\n🔧 测试Node.js环境...")
    
    try:
        # 测试Node.js版本
        result = subprocess.run(["node", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js版本: {result.stdout.strip()}")
        else:
            print("❌ Node.js不可用")
            return False
        
        # 测试npm
        result = subprocess.run(["npm", "--version"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm版本: {result.stdout.strip()}")
        else:
            print("❌ npm不可用")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 环境测试失败: {e}")
        return False

def get_qqmail_auth_guide():
    """获取QQ邮箱授权码指南"""
    print("\n🔐 QQ邮箱授权码获取指南:")
    print("=" * 50)
    print("1. 登录QQ邮箱网页版 (mail.qq.com)")
    print("2. 点击右上角'设置' → '账户'")
    print("3. 找到'POP3/IMAP/SMTP服务'部分")
    print("4. 开启'IMAP/SMTP服务'")
    print("5. 点击'生成授权码'")
    print("6. 按照提示发送短信验证")
    print("7. 获取16位授权码（如: xxxxxxxxxxxxxxxx）")
    print("8. 在 .env 文件中使用这个授权码作为密码")
    print("\n⚠️ 注意: 使用授权码，不是QQ密码！")

def get_gmail_app_password_guide():
    """获取Gmail应用专用密码指南"""
    print("\n🔐 Gmail应用专用密码获取指南:")
    print("=" * 50)
    print("1. 确保已开启两步验证")
    print("2. 访问: https://myaccount.google.com/apppasswords")
    print("3. 选择应用为'邮件'")
    print("4. 选择设备为'其他'，输入名称如'OpenClaw'")
    print("5. 点击'生成'获取16位密码")
    print("6. 在 .env 文件中使用这个密码")

def main():
    """主函数"""
    print("📧 IMAP/SMTP邮件技能测试工具")
    print("=" * 50)
    
    # 测试技能可用性
    if not test_skill_availability():
        print("\n❌ 技能不可用，请检查安装")
        return
    
    # 测试环境
    if not test_node_environment():
        print("\n❌ 环境检查失败")
        return
    
    # 创建配置模板
    create_quick_config()
    
    # 显示使用指南
    show_usage_guide()
    
    # 询问用户需求
    print("\n🎯 你需要什么帮助？")
    print("1. 配置QQ邮箱")
    print("2. 配置Gmail")
    print("3. 配置其他邮箱")
    print("4. 直接测试连接")
    print("5. 退出")
    
    try:
        choice = input("\n请选择 (1-5): ").strip()
        
        if choice == "1":
            get_qqmail_auth_guide()
        elif choice == "2":
            get_gmail_app_password_guide()
        elif choice == "3":
            print("\n📧 其他邮箱配置:")
            print("- Outlook: outlook.office365.com:993")
            print("- 163邮箱: imap.163.com:993")
            print("- 126邮箱: imap.126.com:993")
            print("- Yahoo: imap.mail.yahoo.com:993")
            print("\n⚠️ 都需要在网页版邮箱中开启IMAP/SMTP服务")
        elif choice == "4":
            print("\n🔗 测试连接:")
            print("1. 确保已配置 .env 文件")
            print("2. 运行: node scripts/imap.js check --limit 1")
            print("3. 如果成功，会显示邮件信息")
            print("4. 如果失败，请检查配置和网络")
        elif choice == "5":
            print("👋 再见！")
            return
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n👋 操作已取消")
    
    print("\n💡 提示: 配置完成后，你可以:")
    print("1. 读取邮件: node scripts/imap.js check --limit 10")
    print("2. 搜索邮件: node scripts/imap.js search --unseen")
    print("3. 发送邮件: node scripts/smtp.js send --to ...")

if __name__ == "__main__":
    main()