#!/usr/bin/env python3
"""
QQ邮箱配置助手
交互式配置QQ邮箱连接
"""

import os
import sys
import getpass
from pathlib import Path

def print_header():
    """打印标题"""
    print("📧 QQ邮箱配置助手")
    print("=" * 50)
    print()

def get_qq_email():
    """获取QQ邮箱地址"""
    while True:
        email = input("请输入你的QQ邮箱地址 (如: 12345678@qq.com): ").strip()
        
        if not email:
            print("❌ 邮箱地址不能为空")
            continue
            
        if not email.endswith("@qq.com"):
            print("⚠️  这看起来不是QQ邮箱地址，请确认")
            confirm = input("确认使用这个邮箱吗？ (y/n): ").lower()
            if confirm != 'y':
                continue
        
        # 验证邮箱格式
        if '@' not in email or '.' not in email:
            print("❌ 邮箱格式不正确")
            continue
            
        return email

def get_auth_code():
    """获取授权码"""
    print("\n🔐 获取QQ邮箱授权码:")
    print("-" * 30)
    print("1. 登录QQ邮箱网页版 (mail.qq.com)")
    print("2. 设置 → 账户 → POP3/IMAP/SMTP服务")
    print("3. 开启'IMAP/SMTP服务'")
    print("4. 点击'生成授权码'")
    print("5. 按照提示发送短信验证")
    print("6. 获取16位授权码")
    print()
    
    while True:
        auth_code = getpass.getpass("请输入16位授权码 (输入不会显示): ").strip()
        
        if not auth_code:
            print("❌ 授权码不能为空")
            continue
            
        if len(auth_code) != 16:
            print(f"⚠️  授权码长度应为16位，当前为{len(auth_code)}位")
            confirm = input("确认使用这个授权码吗？ (y/n): ").lower()
            if confirm != 'y':
                continue
        
        # 确认授权码
        auth_code2 = getpass.getpass("请再次输入授权码确认: ").strip()
        
        if auth_code != auth_code2:
            print("❌ 两次输入的授权码不一致")
            continue
            
        return auth_code

def create_env_file(email, auth_code, skill_dir):
    """创建.env配置文件"""
    env_content = f"""# QQ邮箱配置
# 自动生成于 {import datetime; print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}

# IMAP配置（接收邮件）
IMAP_HOST=imap.qq.com
IMAP_PORT=993
IMAP_USER={email}
IMAP_PASS={auth_code}
IMAP_TLS=true
IMAP_REJECT_UNAUTHORIZED=true
IMAP_MAILBOX=INBOX

# SMTP配置（发送邮件）
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER={email}
SMTP_PASS={auth_code}
SMTP_FROM={email}
SMTP_REJECT_UNAUTHORIZED=true

# 连接超时设置
IMAP_TIMEOUT=30000
SMTP_TIMEOUT=30000
"""
    
    env_path = skill_dir / ".env"
    backup_path = skill_dir / ".env.backup"
    
    # 备份现有配置
    if env_path.exists():
        print(f"📦 备份现有配置文件: {backup_path}")
        env_path.rename(backup_path)
    
    # 写入新配置
    print(f"📝 创建配置文件: {env_path}")
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    # 设置权限
    env_path.chmod(0o600)
    print("✅ 配置文件已创建（权限设置为600）")
    
    return env_path

def show_config_summary(email, env_path):
    """显示配置摘要"""
    print("\n📋 配置摘要:")
    print("-" * 30)
    print(f"邮箱地址: {email}")
    print(f"配置文件: {env_path}")
    print(f"IMAP服务器: imap.qq.com:993")
    print(f"SMTP服务器: smtp.qq.com:587")
    print(f"使用授权码: 是 (16位)")
    print()

def show_next_steps(skill_dir):
    """显示下一步操作"""
    print("\n🎯 下一步操作:")
    print("=" * 30)
    
    print("1. 测试连接:")
    print(f"   cd {skill_dir}")
    print("   node scripts/imap.js check --limit 1")
    print()
    
    print("2. 或运行测试脚本:")
    print("   cd /root/.openclaw/workspace")
    print("   ./test_qqmail.sh")
    print()
    
    print("3. 开始使用:")
    print("   # 查看邮件")
    print("   node scripts/imap.js check --limit 10")
    print()
    print("   # 发送邮件")
    print("   node scripts/smtp.js send --to 'test@example.com' --subject '测试' --body '内容'")
    print()
    print("   # 回复邮件")
    print("   node reply_email.js <邮件UID> --body '回复内容'")
    print()

def check_skill_directory():
    """检查技能目录"""
    skill_dir = Path("/root/.openclaw/workspace/skills/imap-smtp-email")
    
    if not skill_dir.exists():
        print(f"❌ 技能目录不存在: {skill_dir}")
        print("请先安装 imap-smtp-email 技能")
        return None
    
    # 检查必要文件
    required_files = [
        "scripts/imap.js",
        "scripts/smtp.js",
        "package.json"
    ]
    
    for file in required_files:
        if not (skill_dir / file).exists():
            print(f"❌ 缺少文件: {file}")
            return None
    
    print(f"✅ 技能目录: {skill_dir}")
    return skill_dir

def main():
    """主函数"""
    print_header()
    
    # 检查技能目录
    skill_dir = check_skill_directory()
    if not skill_dir:
        sys.exit(1)
    
    # 获取配置信息
    print("📝 开始配置QQ邮箱...")
    print()
    
    email = get_qq_email()
    auth_code = get_auth_code()
    
    print(f"\n✅ 获取到信息:")
    print(f"   邮箱: {email}")
    print(f"   授权码: {'*' * 16}")
    
    # 确认配置
    print("\n⚠️  确认配置:")
    print(f"   邮箱: {email}")
    print(f"   授权码长度: {len(auth_code)} 位")
    print()
    
    confirm = input("是否创建配置文件？ (y/n): ").lower()
    if confirm != 'y':
        print("❌ 配置已取消")
        sys.exit(0)
    
    # 创建配置文件
    env_path = create_env_file(email, auth_code, skill_dir)
    
    # 显示摘要
    show_config_summary(email, env_path)
    
    # 显示下一步
    show_next_steps(skill_dir)
    
    # 询问是否测试
    print("\n🔧 是否现在测试连接？")
    test_now = input("运行测试脚本？ (y/n): ").lower()
    
    if test_now == 'y':
        test_script = Path("/root/.openclaw/workspace/test_qqmail.sh")
        if test_script.exists():
            print(f"\n🚀 运行测试脚本...")
            os.system(f"cd /root/.openclaw/workspace && ./test_qqmail.sh")
        else:
            print(f"❌ 测试脚本不存在: {test_script}")
            print("请手动测试连接")
