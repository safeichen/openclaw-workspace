#!/bin/bash

# AI资讯网站启动脚本

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVER_PY="$SCRIPT_DIR/server.py"
LOG_FILE="$SCRIPT_DIR/server.log"
PID_FILE="$SCRIPT_DIR/server.pid"
PORT=8083

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 显示横幅
show_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                 AI资讯聚合站 - 启动脚本                  ║"
    echo "║                 AI News Aggregator                       ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 检查Python依赖
check_dependencies() {
    log_info "检查Python依赖..."
    
    # 检查Python3
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    log_info "Python3 版本: $(python3 --version)"
    
    # 检查pip
    if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
        log_error "pip3 未安装，请先安装pip: python3 -m ensurepip --upgrade"
        exit 1
    fi
    
    # 检查Flask
    if ! python3 -c "import flask" 2>/dev/null; then
        log_warning "Flask 未安装，正在安装..."
        pip3 install flask flask-cors || {
            log_error "安装Flask失败"
            exit 1
        }
    fi
    
    log_success "Python依赖检查通过"
}

# 检查端口
check_port() {
    log_info "检查端口 $PORT..."
    
    if netstat -tlnp 2>/dev/null | grep -q ":$PORT "; then
        log_warning "端口 $PORT 已被占用"
        return 1
    fi
    
    log_success "端口 $PORT 可用"
    return 0
}

# 启动服务器
start_server() {
    log_info "启动AI资讯网站服务器..."
    
    # 检查依赖
    check_dependencies
    
    # 检查端口
    if ! check_port; then
        log_warning "端口 $PORT 被占用，尝试使用端口 8084"
        PORT=8084
        if ! check_port; then
            log_error "端口 8084 也被占用，无法启动服务器"
            exit 1
        fi
    fi
    
    # 切换到脚本目录
    cd "$SCRIPT_DIR"
    
    # 创建数据目录
    mkdir -p data
    
    # 启动服务器（后台运行）
    log_info "启动Python服务器..."
    nohup python3 "simple_server.py" >> "$LOG_FILE" 2>&1 &
    SERVER_PID=$!
    
    # 保存PID
    echo $SERVER_PID > "$PID_FILE"
    
    # 等待服务器启动
    sleep 3
    
    # 检查是否启动成功
    if ps -p $SERVER_PID > /dev/null; then
        log_success "服务器启动成功！PID: $SERVER_PID"
        
        # 测试API连接
        sleep 2
        test_api_connection
        
        # 显示服务器信息
        show_server_info
        
    else
        log_error "服务器启动失败"
        echo "查看日志: tail -f $LOG_FILE"
        exit 1
    fi
}

# 测试API连接
test_api_connection() {
    log_info "测试API连接..."
    
    local max_retries=10
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/api/test 2>/dev/null | grep -q "200"; then
            log_success "API连接测试成功"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        sleep 1
    done
    
    log_warning "API连接测试超时，服务器可能仍在启动中"
    return 1
}

# 显示服务器信息
show_server_info() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                   服务器信息                            ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}🌐 访问地址:${NC}"
    echo "  主页面: http://43.159.52.61:$PORT"
    echo "  API状态: http://43.159.52.61:$PORT/api/system/status"
    echo ""
    echo -e "${GREEN}🔧 技术信息:${NC}"
    echo "  服务器IP: 43.159.52.61"
    echo "  端口: $PORT"
    echo "  PID: $SERVER_PID"
    echo "  日志文件: $LOG_FILE"
    echo "  数据目录: $SCRIPT_DIR/data/"
    echo ""
    echo -e "${GREEN}📊 功能特性:${NC}"
    echo "  • 实时AI资讯聚合"
    echo "  • 自动分类和趋势分析"
    echo "  • RESTful API接口"
    echo "  • 每5分钟自动更新"
    echo "  • 响应式Web界面"
    echo ""
    echo -e "${GREEN}🔗 API端点:${NC}"
    echo "  GET /api/ai-news          # 获取AI资讯"
    echo "  GET /api/ai-news/search   # 搜索AI资讯"
    echo "  GET /api/ai-trends        # 获取趋势数据"
    echo "  GET /api/system/status    # 系统状态"
    echo "  GET /api/system/stats     # 系统统计"
    echo ""
    echo -e "${GREEN}🛠️ 管理命令:${NC}"
    echo "  查看状态: $0 status"
    echo "  查看日志: $0 logs"
    echo "  停止服务: $0 stop"
    echo "  重启服务: $0 restart"
    echo ""
    echo -e "${CYAN}🚀 AI资讯聚合站已准备就绪！${NC}"
}

# 停止服务器
stop_server() {
    if [ -f "$PID_FILE" ]; then
        SERVER_PID=$(cat "$PID_FILE")
        
        if ps -p $SERVER_PID > /dev/null; then
            log_info "正在停止服务器 (PID: $SERVER_PID)..."
            kill $SERVER_PID
            sleep 2
            
            if ps -p $SERVER_PID > /dev/null; then
                log_warning "正常停止失败，强制停止..."
                kill -9 $SERVER_PID
            fi
            
            rm -f "$PID_FILE"
            log_success "服务器已停止"
        else
            log_warning "服务器未运行 (PID: $SERVER_PID)"
            rm -f "$PID_FILE"
        fi
    else
        log_warning "PID文件不存在，服务器可能未运行"
    fi
}

# 重启服务器
restart_server() {
    log_info "重启服务器..."
    stop_server
    sleep 3
    start_server
}

# 查看服务器状态
status_server() {
    if [ -f "$PID_FILE" ]; then
        SERVER_PID=$(cat "$PID_FILE")
        
        if ps -p $SERVER_PID > /dev/null; then
            log_success "服务器正在运行"
            echo "  PID: $SERVER_PID"
            echo "  端口: $PORT"
            echo "  启动时间: $(ps -o lstart= -p $SERVER_PID)"
            echo "  内存使用: $(ps -o rss= -p $SERVER_PID | awk '{printf "%.1f MB", $1/1024}')"
            echo "  CPU使用: $(ps -o %cpu= -p $SERVER_PID)%"
            
            # 检查端口监听
            if netstat -tlnp 2>/dev/null | grep -q ":$PORT "; then
                echo "  端口状态: 监听中"
            else
                echo "  端口状态: 未监听"
            fi
            
            # 测试API连接
            echo -n "  API状态: "
            if curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/api/test 2>/dev/null | grep -q "200"; then
                echo -e "${GREEN}正常${NC}"
            else
                echo -e "${RED}异常${NC}"
            fi
            
            # 显示资讯统计
            echo -n "  资讯数量: "
            local news_count=$(curl -s http://localhost:$PORT/api/system/status 2>/dev/null | grep -o '"total_news":[0-9]*' | cut -d: -f2)
            if [ -n "$news_count" ]; then
                echo "$news_count 条"
            else
                echo "未知"
            fi
            
        else
            log_error "服务器未运行 (PID文件存在但进程不存在)"
            rm -f "$PID_FILE"
        fi
    else
        log_warning "服务器未运行"
    fi
}

# 查看日志
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        log_info "显示服务器日志 (最后50行):"
        echo "══════════════════════════════════════════════════════════"
        tail -n 50 "$LOG_FILE"
        echo "══════════════════════════════════════════════════════════"
        echo "完整日志: $LOG_FILE"
        echo "实时日志: tail -f $LOG_FILE"
    else
        log_warning "日志文件不存在: $LOG_FILE"
    fi
}

# 显示帮助
show_help() {
    show_banner
    echo "使用方法: $0 {start|stop|restart|status|logs|help}"
    echo ""
    echo "命令:"
    echo "  start    启动AI资讯网站服务器"
    echo "  stop     停止服务器"
    echo "  restart  重启服务器"
    echo "  status   查看服务器状态"
    echo "  logs     查看服务器日志"
    echo "  help     显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start    # 启动服务器"
    echo "  $0 status   # 查看状态"
    echo "  $0 logs     # 查看日志"
    echo "  $0 stop     # 停止服务器"
    echo ""
    echo "环境要求:"
    echo "  • Python 3.6+"
    echo "  • Flask 和 Flask-CORS"
    echo "  • 端口 $PORT 可用"
    echo ""
    echo "部署完成后访问: http://43.159.52.61:$PORT"
}

# 主逻辑
case "$1" in
    start)
        show_banner
        start_server
        ;;
    stop)
        show_banner
        stop_server
        ;;
    restart)
        show_banner
        restart_server
        ;;
    status)
        show_banner
        status_server
        ;;
    logs)
        show_banner
        show_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "未知命令: $1"
        echo ""
        show_help
        exit 1
        ;;
esac