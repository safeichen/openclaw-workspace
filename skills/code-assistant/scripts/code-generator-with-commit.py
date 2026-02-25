#!/usr/bin/env python3
"""
编程代码生成器 with 自动提交
自动提交生成的代码到 git@github.com:safeichen/toos.git
"""

import os
import sys
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

class CodeGeneratorWithCommit:
    """带自动提交的代码生成器"""
    
    # 配置
    TARGET_REPO = "git@github.com:safeichen/toos.git"
    CODE_DIR = "/root/.openclaw/workspace/generated-code"
    BRANCH = "main"
    COMMIT_PREFIX = "代码生成: "
    
    def __init__(self):
        self.setup_directories()
    
    def setup_directories(self):
        """设置目录"""
        os.makedirs(self.CODE_DIR, exist_ok=True)
        
        # 初始化Git仓库（如果还没有）
        git_dir = os.path.join(self.CODE_DIR, ".git")
        if not os.path.exists(git_dir):
            self.run_command(["git", "init"], cwd=self.CODE_DIR)
            
            # 添加.gitignore
            gitignore_content = """# 编译输出
__pycache__/
*.pyc
*.pyo
*.pyd

# 依赖
node_modules/
vendor/
dist/
build/

# 环境文件
.env
.env.local

# 日志
*.log

# 系统文件
.DS_Store
Thumbs.db
"""
            gitignore_path = os.path.join(self.CODE_DIR, ".gitignore")
            with open(gitignore_path, "w") as f:
                f.write(gitignore_content)
            
            # 添加远程仓库
            self.run_command(["git", "remote", "add", "origin", self.TARGET_REPO], 
                           cwd=self.CODE_DIR)
    
    def run_command(self, cmd, cwd=None):
        """运行命令"""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"命令执行失败: {' '.join(cmd)}")
            print(f"错误: {e.stderr}")
            return None
    
    def generate_python_code(self, description, code_content):
        """生成Python代码并自动提交"""
        # 创建临时文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{timestamp}.py"
        filepath = os.path.join(self.CODE_DIR, filename)
        
        # 添加文件头注释
        header = f'''"""
{description}
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
生成工具: OpenClaw编程助手
"""
'''
        full_content = header + "\n" + code_content
        
        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)
        
        print(f"✅ 代码已生成: {filename}")
        
        # 自动提交
        return self.auto_commit(filename, description)
    
    def generate_javascript_code(self, description, code_content):
        """生成JavaScript代码并自动提交"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{timestamp}.js"
        filepath = os.path.join(self.CODE_DIR, filename)
        
        # 添加文件头注释
        header = f'''/*
{description}
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
生成工具: OpenClaw编程助手
*/
'''
        full_content = header + "\n" + code_content
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)
        
        print(f"✅ 代码已生成: {filename}")
        return self.auto_commit(filename, description)
    
    def generate_bash_script(self, description, code_content):
        """生成Bash脚本并自动提交"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{timestamp}.sh"
        filepath = os.path.join(self.CODE_DIR, filename)
        
        # 添加shebang和注释
        header = f'''#!/bin/bash
# {description}
# 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# 生成工具: OpenClaw编程助手

'''
        full_content = header + code_content
        
        # 添加执行权限
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)
        os.chmod(filepath, 0o755)
        
        print(f"✅ 脚本已生成: {filename}")
        return self.auto_commit(filename, description)
    
    def auto_commit(self, filename, description):
        """自动提交到Git仓库"""
        print(f"🤖 自动提交到: {self.TARGET_REPO}")
        
        # 切换到代码目录
        original_cwd = os.getcwd()
        os.chdir(self.CODE_DIR)
        
        try:
            # 添加文件
            add_result = self.run_command(["git", "add", filename])
            if add_result is None:
                return False
            
            # 提交
            commit_msg = f"{self.COMMIT_PREFIX}{description}"
            commit_result = self.run_command(["git", "commit", "-m", commit_msg])
            
            if commit_result is None:
                print("⚠️  提交失败（可能没有更改）")
                return False
            
            # 推送到远程
            print(f"📤 推送到 {self.BRANCH} 分支...")
            push_result = self.run_command(["git", "push", "origin", self.BRANCH])
            
            if push_result is None:
                print("⚠️  推送失败，尝试先拉取...")
                # 尝试先拉取再推送
                pull_result = self.run_command(["git", "pull", "--rebase", "origin", self.BRANCH])
                if pull_result is not None:
                    push_result = self.run_command(["git", "push", "origin", self.BRANCH])
            
            if push_result is not None:
                print(f"🎉 代码已提交并推送到: {self.TARGET_REPO}")
                print(f"   文件: {filename}")
                print(f"   提交: {commit_msg}")
                print(f"   分支: {self.BRANCH}")
                return True
            else:
                print("❌ 推送失败")
                return False
                
        finally:
            os.chdir(original_cwd)
    
    def quick_generate(self, language, description, code_content):
        """快速生成代码"""
        if language.lower() in ["python", "py"]:
            return self.generate_python_code(description, code_content)
        elif language.lower() in ["javascript", "js"]:
            return self.generate_javascript_code(description, code_content)
        elif language.lower() in ["bash", "shell", "sh"]:
            return self.generate_bash_script(description, code_content)
        else:
            print(f"❌ 不支持的语言: {language}")
            return False
    
    def interactive_mode(self):
        """交互式模式"""
        print("💻 编程代码生成器 (带自动提交)")
        print("=" * 50)
        
        while True:
            print("\n📋 选项:")
            print("1. 生成Python代码")
            print("2. 生成JavaScript代码")
            print("3. 生成Bash脚本")
            print("4. 查看配置")
            print("5. 退出")
            
            choice = input("\n请选择 (1-5): ").strip()
            
            if choice == "1":
                desc = input("代码描述: ").strip() or "Python代码"
                print("输入Python代码 (输入空行结束):")
                lines = []
                while True:
                    line = input("> ")
                    if line == "":
                        break
                    lines.append(line)
                
                if lines:
                    code = "\n".join(lines)
                    self.generate_python_code(desc, code)
            
            elif choice == "2":
                desc = input("代码描述: ").strip() or "JavaScript代码"
                print("输入JavaScript代码 (输入空行结束):")
                lines = []
                while True:
                    line = input("> ")
                    if line == "":
                        break
                    lines.append(line)
                
                if lines:
                    code = "\n".join(lines)
                    self.generate_javascript_code(desc, code)
            
            elif choice == "3":
                desc = input("脚本描述: ").strip() or "Bash脚本"
                print("输入Bash脚本代码 (输入空行结束):")
                lines = []
                while True:
                    line = input("> ")
                    if line == "":
                        break
                    lines.append(line)
                
                if lines:
                    code = "\n".join(lines)
                    self.generate_bash_script(desc, code)
            
            elif choice == "4":
                print("\n⚙️  当前配置:")
                print(f"  目标仓库: {self.TARGET_REPO}")
                print(f"  代码目录: {self.CODE_DIR}")
                print(f"  分支: {self.BRANCH}")
                print(f"  提交前缀: {self.COMMIT_PREFIX}")
                
                # 显示最近提交
                print(f"\n📁 代码目录文件数: {len(os.listdir(self.CODE_DIR)) - 1}")  # 减去.git目录
            
            elif choice == "5":
                print("👋 退出")
                break
            
            else:
                print("❌ 无效选择")

def main():
    """主函数"""
    if len(sys.argv) < 4:
        # 交互式模式
        generator = CodeGeneratorWithCommit()
        generator.interactive_mode()
    else:
        # 命令行模式: python script.py <语言> <描述> <代码文件>
        language = sys.argv[1]
        description = sys.argv[2]
        code_file = sys.argv[3]
        
        if not os.path.exists(code_file):
            print(f"❌ 代码文件不存在: {code_file}")
            sys.exit(1)
        
        with open(code_file, "r", encoding="utf-8") as f:
            code_content = f.read()
        
        generator = CodeGeneratorWithCommit()
        success = generator.quick_generate(language, description, code_content)
        
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()