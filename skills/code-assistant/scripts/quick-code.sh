#!/bin/bash
# 快速编程助手

echo "💻 OpenClaw 快速编程助手"
echo "========================"

echo ""
echo "📋 可用功能:"
echo "1. 生成Python代码片段"
echo "2. 生成JavaScript代码片段"
echo "3. 生成Bash脚本模板"
echo "4. 查看编程指南"
echo "5. 退出"
echo ""

read -p "请选择功能 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🐍 Python代码片段"
        echo "----------------"
        echo "1. 文件操作"
        echo "2. HTTP请求"
        echo "3. 数据处理"
        echo "4. 类定义"
        echo ""
        read -p "选择片段类型: " py_choice
        
        case $py_choice in
            1)
                echo ""
                echo "# Python文件安全读取"
                cat << 'PYTHONEOF'
def read_file_safely(filepath):
    """安全读取文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"文件不存在: {filepath}")
        return None
    except Exception as e:
        print(f"读取文件错误: {e}")
        return None

# 使用示例
content = read_file_safely("example.txt")
if content:
    print(f"文件内容: {content[:100]}...")
PYTHONEOF
                ;;
            2)
                echo ""
                echo "# Python HTTP请求"
                cat << 'PYTHONEOF'
import requests

def fetch_url(url, timeout=10):
    """获取URL内容"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # 检查HTTP错误
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

# 使用示例
html = fetch_url("https://example.com")
if html:
    print(f"获取到 {len(html)} 字符")
PYTHONEOF
                ;;
        esac
        ;;
    
    2)
        echo ""
        echo "📜 JavaScript代码片段"
        echo "-------------------"
        echo "1. 异步函数"
        echo "2. DOM操作"
        echo ""
        read -p "选择片段类型: " js_choice
        
        case $js_choice in
            1)
                echo ""
                echo "// JavaScript异步函数"
                cat << 'JSEOF'
async function fetchData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP错误: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('获取数据失败:', error);
        return null;
    }
}

// 使用示例
fetchData('https://api.example.com/data')
    .then(data => {
        if (data) {
            console.log('获取到数据:', data);
        }
    });
JSEOF
                ;;
        esac
        ;;
    
    3)
        echo ""
        echo "🐚 Bash脚本模板"
        cat << 'BASHEOF'
#!/bin/bash
# 安全的Bash脚本模板

set -euo pipefail  # 严格模式

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "命令未找到: $1"
        return 1
    fi
    return 0
}

# 主函数
main() {
    log_info "脚本开始执行"
    
    # 检查依赖
    check_command "git" || exit 1
    check_command "curl" || exit 1
    
    log_success "脚本执行完成"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
BASHEOF
        ;;
    
    4)
        echo ""
        echo "📚 编程指南"
        echo "----------"
        echo "查看完整指南: cat /root/.openclaw/workspace/CODING_GUIDE.md"
        echo ""
        echo "快速命令:"
        echo "  Python助手: python3 skills/code-assistant/scripts/python-helper.py"
        echo "  代码审查: 查看CODING_GUIDE.md中的最佳实践"
        echo "  项目模板: 查看CODING_GUIDE.md中的项目结构"
        ;;
    
    5)
        echo "👋 退出编程助手"
        exit 0
        ;;
    
    *)
        echo "❌ 无效选择"
        ;;
esac

echo ""
echo "💡 提示: 更多编程帮助请查看 CODING_GUIDE.md 文件"