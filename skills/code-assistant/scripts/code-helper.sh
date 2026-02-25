#!/bin/bash
# 编程助手工具脚本

echo "💻 编程助手工具"
echo "=============="

show_menu() {
    echo ""
    echo "📋 编程工具菜单"
    echo "--------------"
    echo "1. 代码片段生成"
    echo "2. 代码审查"
    echo "3. 算法实现"
    echo "4. 项目模板"
    echo "5. 学习资源"
    echo "6. 调试助手"
    echo "7. 退出"
    echo ""
}

code_snippets() {
    echo "📝 代码片段生成"
    echo "---------------"
    
    echo "选择编程语言:"
    echo "1. Python"
    echo "2. JavaScript"
    echo "3. Bash/Shell"
    echo "4. SQL"
    echo "5. HTML/CSS"
    echo ""
    
    read -p "选择语言 (1-5): " lang_choice
    
    case $lang_choice in
        1)
            echo "Python代码片段:"
            echo "----------------"
            echo "1. 文件读取"
            echo "2. HTTP请求"
            echo "3. 数据处理"
            echo "4. 类定义"
            echo ""
            read -p "选择片段类型: " py_choice
            
            case $py_choice in
                1)
                    cat << 'EOF'
# Python文件安全读取
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
EOF
                    ;;
                2)
                    cat << 'EOF'
# Python HTTP请求（使用requests库）
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
EOF
                    ;;
                3)
                    cat << 'EOF'
# Python数据处理（使用pandas）
import pandas as pd

def process_csv(filepath):
    """处理CSV文件"""
    try:
        # 读取CSV
        df = pd.read_csv(filepath)
        
        # 基本统计
        print(f"数据形状: {df.shape}")
        print(f"列名: {list(df.columns)}")
        print("\n前5行数据:")
        print(df.head())
        
        # 处理缺失值
        if df.isnull().sum().sum() > 0:
            print(f"\n发现缺失值，填充中...")
            df = df.fillna(method='ffill')
        
        return df
    except Exception as e:
        print(f"处理CSV失败: {e}")
        return None

# 使用示例
data = process_csv("data.csv")
EOF
                    ;;
                4)
                    cat << 'EOF'
# Python类定义示例
class Person:
    """人员类示例"""
    
    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.created_at = datetime.now()
    
    def greet(self):
        """问候方法"""
        return f"你好，我是{self.name}，今年{self.age}岁"
    
    def is_adult(self):
        """判断是否成年"""
        return self.age >= 18
    
    def __str__(self):
        return f"Person(name={self.name}, age={self.age})"
    
    def __repr__(self):
        return self.__str__()

# 使用示例
person = Person("张三", 25)
print(person.greet())
print(f"是否成年: {person.is_adult()}")
print(person)  # 调用__str__
EOF
                    ;;
            esac
            ;;
        2)
            echo "JavaScript代码片段:"
            echo "-------------------"
            echo "1. 异步函数"
            echo "2. DOM操作"
            echo "3. 事件处理"
            echo "4. API调用"
            echo ""
            read -p "选择片段类型: " js_choice
            
            case $js_choice in
                1)
                    cat << 'EOF'
// JavaScript异步函数
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

// 或在async函数中使用
async function main() {
    const data = await fetchData('https://api.example.com/data');
    if (data) {
        console.log('数据:', data);
    }
}
EOF
                    ;;
                2)
                    cat << 'EOF'
// JavaScript DOM操作
class DOMHelper {
    /**
     * 创建元素
     * @param {string} tag - 标签名
     * @param {object} attributes - 属性对象
     * @param {string|HTMLElement} content - 内容
     * @returns {HTMLElement}
     */
    static createElement(tag, attributes = {}, content = '') {
        const element = document.createElement(tag);
        
        // 设置属性
        Object.entries(attributes).forEach(([key, value]) => {
            element.setAttribute(key, value);
        });
        
        // 设置内容
        if (typeof content === 'string') {
            element.textContent = content;
        } else if (content instanceof HTMLElement) {
            element.appendChild(content);
        }
        
        return element;
    }
    
    /**
     * 安全地添加事件监听器
     */
    static safeAddEventListener(element, event, handler) {
        if (element && typeof handler === 'function') {
            element.addEventListener(event, handler);
            return () => element.removeEventListener(event, handler);
        }
        return () => {};
    }
}

// 使用示例
const button = DOMHelper.createElement('button', 
    { class: 'btn', id: 'myBtn' }, 
    '点击我'
);

const removeListener = DOMHelper.safeAddEventListener(button, 'click', () => {
    console.log('按钮被点击了!');
});

document.body.appendChild(button);
EOF
                    ;;
            esac
            ;;
        3)
            echo "Bash/Shell脚本片段:"
            echo "-------------------"
            
            cat << 'EOF'
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

# 安全执行命令
safe_exec() {
    local cmd="$1"
    log_info "执行: $cmd"
    
    if eval "$cmd"; then
        log_success "执行成功"
        return 0
    else
        log_error "执行失败: $cmd"
        return 1
    fi
}

# 主函数
main() {
    log_info "脚本开始执行"
    
    # 检查依赖
    check_command "git" || exit 1
    check_command "curl" || exit 1
    
    # 执行任务
    safe_exec "git status"
    safe_exec "curl -s https://example.com | head -5"
    
    log_success "脚本执行完成"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
EOF
            ;;
    esac
}

code_review() {
    echo "🔍 代码审查指南"
    echo "---------------"
    
    echo "代码审查要点:"
    echo ""
    echo "1. 代码风格"
    echo "   - 命名规范（变量、函数、类）"
    echo "   - 缩进和空格一致性"
    echo "   - 注释是否清晰"
    echo ""
    echo "2. 代码质量"
    echo "   - 重复代码"
    echo "   - 过长函数/类"
    echo "   - 复杂度过高"
    echo ""
    echo "3. 安全性"
    echo "   - 输入验证"
    echo "   - 错误处理"
    echo "   - 资源管理（文件、网络）"
    echo ""
    echo "4. 性能"
    echo "   - 算法复杂度"
    echo "   - 内存使用"
    echo "   - 数据库查询优化"
    echo ""
    echo "5. 可测试性"
    echo "   - 单元测试覆盖"
    echo "   - 模块化设计"
    echo "   - 依赖注入"
    
    echo ""
    read -p "输入要审查的代码文件路径: " code_file
    
    if [ -f "$code_file" ]; then
        echo ""
        echo "📄 文件: $code_file"
        echo "大小: $(wc -l < "$code_file") 行"
        echo ""
        
        # 简单分析
        echo "初步分析:"
        echo "---------"
        
        # 检查文件类型
        file_ext="${code_file##*.}"
        case $file_ext in
            py)
                echo "语言: Python"
                echo "建议使用: pylint, black, mypy"
                ;;
            js|ts)
                echo "语言: JavaScript/TypeScript"
                echo "建议使用: ESLint, Prettier"
                ;;
            java)
                echo "语言: Java"
                echo "建议使用: Checkstyle, PMD"
                ;;
            *)
                echo "语言: $file_ext"
                ;;
        esac
        
        # 简单统计
        echo ""
        echo "代码统计:"
        echo "  - 总行数: $(wc -l < "$code_file")"
        echo "  - 空行数: $(grep -c '^$' "$code_file")"
        echo "  - 注释行: $(grep -c '^\s*#' "$code_file" 2>/dev/null || grep -c '^\s*//' "$code_file" 2>/dev/null || echo "0")"
        
        # 显示前10行
        echo ""
        echo "文件预览（前10行）:"
        echo "------------------"
        head -10 "$code_file"
    else
        echo "❌ 文件不存在: $code_file"
    fi
}

algorithm_help() {
    echo "🧮 算法实现帮助"
    echo "---------------"
    
    echo "常见算法分类:"
    echo "1. 排序算法"
    echo "2. 搜索算法"
    echo "3. 图算法"
    echo "4. 动态规划"
    echo "5. 字符串算法"
    echo ""
    
    read -p "选择算法类别 (1-5): " algo_category
    
    case $algo_category in
        1)
            echo "排序算法:"
            echo "---------"
            echo "1. 快速排序 (平均 O(n log n))"
            echo "2. 归并排序 (稳定 O(n log n))"
            echo "3. 堆排序 (原地 O(n log n))"
            echo "4. 冒泡排序 (简单 O(n²))"
            echo ""
            read -p "选择排序算法: " sort_algo
            
            case $sort_algo in
                1)
                    cat << 'EOF'
# Python快速排序实现
def quick_sort(arr):
    """快速排序"""
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)

# 使用示例
numbers = [3, 6, 8, 10, 1, 2, 1]
sorted_numbers = quick_sort(numbers)
print(f"排序前: {numbers}")
print(f"排序后: {sorted_numbers}")
EOF
                    ;;
                2)
                    cat << 'EOF'
# Python归并排序实现
def merge_sort(arr):
    """归并排序"""
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    """合并两个有序数组"""
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# 使用示例
numbers = [3, 6, 8, 10, 1, 2, 1]
sorted_numbers = merge_sort(numbers)
print(f"排序前: {numbers}")
print(f"排序后: {sorted_numbers}")
EOF
                    ;;
            esac
            ;;
        2)
            echo "搜索算法:"
            echo "---------"
            echo "1. 二分查找 (有序数组)"
            echo "2. 广度优先搜索 (BFS)"
            echo "3. 深度优先搜索 (DFS)"
            echo ""
            read -p "选择搜索算法: " search_algo
            
            case $search_algo in
                1)
                    cat << 'EOF'
# Python二分查找实现
def binary_search(arr, target):
    """二分查找（数组必须已排序）"""
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if arr[mid] == target:
            return mid  # 找到目标，返回索引
        elif arr[mid] < target:
            left = mid + 1  # 在右半部分继续查找
        else:
            right = mid - 1  # 在左半部分继续查找
    
    return -1  # 未找到

# 使用示例
sorted_numbers = [1, 3, 5, 7, 9, 11, 13]
target = 7
result = binary_search(sorted_numbers, target)

if result != -1:
    print(f"找到目标 {target}，索引: {result}")
else:
    print(f"未找到目标 {target}")
EOF
                    ;;
            esac
            ;;
    esac
}

project_templates() {
    echo "📁 项目模板"
    echo "-----------"
    
    echo "选择项目类型:"
    echo "1. Python项目"
    echo "2. JavaScript项目"
    echo "3. Web应用"
    echo "4. 数据分析"
    echo ""
    
    read -p "选择项目类型 (1-4): " project_type
    
    case $project_type in
        1)
            echo "Python项目结构:"
            echo "----------------"
            cat << 'EOF'
my_python_project/
├── src/                    # 源代码
│   ├── __init__.py
│   ├── main.py            # 主程序
│   ├── utils.py           # 工具函数
│   └── models/            # 数据模型
│       └── __init__.py
├── tests/                 # 测试代码
│   ├── __init__.py
│   ├── test_main.py
│   └── test_utils.py
├── docs/                  # 文档
│   └── README.md
├── scripts/               # 脚本文件
│   └── setup.sh
├── requirements.txt       # Python依赖
├── requirements-dev.txt   # 开发依赖
├── .gitignore            # Git忽略文件
├── .env.example          # 环境变量示例
├── Dockerfile            # Docker配置
└── README.md             # 项目说明

# 创建命令
mkdir -p my_python_project/{src/models,tests,docs,scripts}
touch my_python_project/src/{__init__.py,main.py,utils.py}
touch my_python_project/src/models/__init__.py
touch my_python_project/tests/{__init__.py,test_main.py,test_utils.py}
touch my_python_project/{requirements.txt,requirements-dev.txt,.gitignore,.env.example,Dockerfile,README.md}
EOF
            ;;
        2)
            echo "JavaScript项目结构:"
            echo "--------------------"
            cat << 'EOF'
my_js_project/
├── src/                    # 源代码
│   ├── index.js           # 入口文件
│   ├── components/        # 组件
│   │   └── Button.js
│   ├── utils/             # 工具函数
