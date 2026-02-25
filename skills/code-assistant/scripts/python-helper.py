#!/usr/bin/env python3
"""
Python编程助手工具
提供Python代码分析、生成和优化功能
"""

import sys
import os
import ast
import subprocess
from pathlib import Path
from typing import List, Dict, Any

class PythonCodeHelper:
    """Python代码助手类"""
    
    @staticmethod
    def analyze_file(filepath: str) -> Dict[str, Any]:
        """分析Python文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            tree = ast.parse(content)
            
            analysis = {
                'filepath': filepath,
                'lines': len(content.splitlines()),
                'functions': [],
                'classes': [],
                'imports': [],
                'issues': []
            }
            
            # 遍历AST
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis['functions'].append({
                        'name': node.name,
                        'lineno': node.lineno,
                        'args': len(node.args.args),
                        'docstring': ast.get_docstring(node)
                    })
                elif isinstance(node, ast.ClassDef):
                    analysis['classes'].append({
                        'name': node.name,
                        'lineno': node.lineno,
                        'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                        'docstring': ast.get_docstring(node)
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        analysis['imports'].append(f"{module}.{alias.name}")
            
            return analysis
            
        except Exception as e:
            return {'error': str(e), 'filepath': filepath}
    
    @staticmethod
    def generate_template(template_type: str, **kwargs) -> str:
        """生成代码模板"""
        templates = {
            'class': '''
class {class_name}:
    """{docstring}"""
    
    def __init__(self{init_args}):
        """初始化方法"""
        {init_body}
    
    def __str__(self):
        return "{class_name}()"
    
    def __repr__(self):
        return self.__str__()
''',
            'function': '''
def {function_name}({args}):
    """{docstring}
    
    Args:
        {arg_docs}
    
    Returns:
        {return_doc}
    """
    {body}
    return {return_value}
''',
            'cli': '''
#!/usr/bin/env python3
"""
{script_name} - {description}
"""

import argparse
import sys
from typing import List

def parse_args(args: List[str] = None):
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="{description}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='详细输出模式'
    )
    
    parser.add_argument(
        'input',
        help='输入文件或目录'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='输出文件（可选）'
    )
    
    return parser.parse_args(args)

def main():
    """主函数"""
    args = parse_args()
    
    try:
        # 主逻辑
        print(f"处理: {args.input}")
        
        if args.verbose:
            print("详细模式已启用")
        
        if args.output:
            print(f"输出到: {args.output}")
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
        }
        
        if template_type not in templates:
            return f"未知模板类型: {template_type}"
        
        return templates[template_type].format(**kwargs)
    
    @staticmethod
    def check_style(filepath: str) -> List[str]:
        """检查代码风格（使用pylint如果可用）"""
        issues = []
        
        # 简单的手动检查
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # 检查行长度
                if len(line.rstrip()) > 79:
                    issues.append(f"第{i}行: 行长度超过79字符 ({len(line.rstrip())}字符)")
                
                # 检查尾随空格
                if line.rstrip() != line.rstrip().rstrip():
                    issues.append(f"第{i}行: 有尾随空格")
                
                # 检查制表符
                if '\t' in line:
                    issues.append(f"第{i}行: 使用了制表符，建议使用4个空格")
            
            return issues
            
        except Exception as e:
            return [f"检查失败: {e}"]
    
    @staticmethod
    def run_tests(test_path: str = '.') -> Dict[str, Any]:
        """运行测试"""
        result = {
            'passed': 0,
            'failed': 0,
            'errors': [],
            'output': ''
        }
        
        try:
            # 尝试使用pytest
            cmd = ['python', '-m', 'pytest', test_path, '-v']
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            result['output'] = process.stdout
            
            # 简单解析pytest输出
            for line in process.stdout.splitlines():
                if 'PASSED' in line:
                    result['passed'] += 1
                elif 'FAILED' in line or 'ERROR' in line:
                    result['failed'] += 1
            
        except FileNotFoundError:
            # 回退到unittest
            try:
                cmd = ['python', '-m', 'unittest', 'discover', test_path, '-v']
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                result['output'] = process.stdout
            except Exception as e:
                result['errors'].append(f"测试运行失败: {e}")
        
        return result

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Python编程助手")
        print("==============")
        print("用法:")
        print("  python-helper.py analyze <文件路径>    # 分析Python文件")
        print("  python-helper.py template <类型>       # 生成代码模板")
        print("  python-helper.py check <文件路径>      # 检查代码风格")
        print("  python-helper.py test [测试路径]       # 运行测试")
        print()
        print("模板类型: class, function, cli")
        return
    
    command = sys.argv[1]
    helper = PythonCodeHelper()
    
    if command == 'analyze' and len(sys.argv) > 2:
        filepath = sys.argv[2]
        if os.path.exists(filepath):
            result = helper.analyze_file(filepath)
            print(f"文件分析: {filepath}")
            print(f"行数: {result.get('lines', 0)}")
            print()
            
            if result.get('functions'):
                print("函数列表:")
                for func in result['functions']:
                    print(f"  - {func['name']} (第{func['lineno']}行, {func['args']}个参数)")
                    if func['docstring']:
                        print(f"    文档: {func['docstring'][:50]}...")
            
            if result.get('classes'):
                print("\n类列表:")
                for cls in result['classes']:
                    print(f"  - {cls['name']} (第{cls['lineno']}行, {cls['methods']}个方法)")
                    if cls['docstring']:
                        print(f"    文档: {cls['docstring'][:50]}...")
            
            if result.get('imports'):
                print(f"\n导入模块 ({len(result['imports'])}个):")
                for imp in sorted(set(result['imports'])):
                    print(f"  - {imp}")
        
        else:
            print(f"文件不存在: {filepath}")
    
    elif command == 'template' and len(sys.argv) > 2:
        template_type = sys.argv[2]
        
        if template_type == 'class':
            class_name = input("类名: ") or "MyClass"
            docstring = input("类文档: ") or f"{class_name}类"
            init_args = input("初始化参数（逗号分隔）: ") or ""
            
            if init_args:
                init_args = ", " + init_args
            
            init_body_lines = []
            print("初始化属性（每行一个，空行结束）:")
            while True:
                line = input("  self.")
                if not line:
                    break
                init_body_lines.append(f"self.{line}")
            
            init_body = "\n        ".join(init_body_lines) if init_body_lines else "pass"
            
            template = helper.generate_template(
                'class',
                class_name=class_name,
                docstring=docstring,
                init_args=init_args,
                init_body=init_body
            )
            print("\n生成的类模板:")
            print(template)
        
        elif template_type == 'cli':
            script_name = input("脚本名称: ") or "my_script.py"
            description = input("脚本描述: ") or "Python命令行工具"
            
            template = helper.generate_template(
                'cli',
                script_name=script_name,
                description=description
            )
            print("\n生成的CLI模板:")
            print(template)
    
    elif command == 'check' and len(sys.argv) > 2:
        filepath = sys.argv[2]
        if os.path.exists(filepath):
            issues = helper.check_style(filepath)
            if issues:
                print(f"代码风格问题 ({len(issues)}个):")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print("代码风格良好！")
        else:
            print(f"文件不存在: {filepath}")
    
    elif command == 'test':
        test_path = sys.argv[2] if len(sys.argv) > 2 else '.'
        result = helper.run_tests(test_path)
        
        print(f"测试结果:")
        print(f"  通过: {result['passed']}")
        print(f"  失败: {result['failed']}")
        
        if result['errors']:
            print(f"  错误: {len(result['errors'])}")
            for error in result['errors']:
                print(f"    - {error}")
        
        if result['output']:
            print(f"\n输出:\n{result['output'][-500:]}")  # 显示最后500字符
    
    else:
        print(f"未知命令: {command}")

if __name__ == "__main__":
    main()