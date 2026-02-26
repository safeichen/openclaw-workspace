#!/bin/bash

# OpenClaw测试Web服务器启动脚本

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVER_PY="$SCRIPT_DIR/server.py"
LOG_FILE="$SCRIPT_DIR/server.log"
PID_FILE="$SCRIPT_DIR/server.pid"
PORT=80

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# 检查Python3
check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    log_info "Python3 已安装: $(python3 --version)"
}

# 检查端口是否被占用
check_port() {
    if netstat -tlnp 2>/dev/null | grep -q ":$PORT "; then
        log_warning "端口 $PORT 已被占用"
        return 1
    fi
    return 0
}

# 启动服务器
start_server() {
    log_info "正在启动OpenClaw测试服务器..."
    
    # 检查Python
    check_python
    
    # 检查端口
    if ! check_port; then
        log_error "无法启动服务器，端口 $PORT 已被占用"
        echo "请执行: $0 stop 停止现有服务器"
        echo "或修改 server.py 中的 PORT 变量"
        exit 1
    fi
    
    # 切换到脚本目录
    cd "$SCRIPT_DIR"
    
    # 启动服务器（后台运行）
    nohup python3 "$SERVER_PY" >> "$LOG_FILE" 2>&1 &
    SERVER_PID=$!
    
    # 保存PID
    echo $SERVER_PID > "$PID_FILE"
    
    # 等待服务器启动
    sleep 2
    
    # 检查是否启动成功
    if ps -p $SERVER_PID > /dev/null; then
        log_success "服务器启动成功！PID: $SERVER_PID"
        log_success "访问地址: http://43.159.52.61:$PORT"
        log_success "日志文件: $LOG_FILE"
        
        # 显示服务器信息
        echo ""
        echo "📊 服务器信息:"
        echo "  IP地址: 43.159.52.61"
        echo "  端口: $PORT"
        echo "  PID: $SERVER_PID"
        echo "  日志: $LOG_FILE"
        echo ""
        echo "🌐 测试连接:"
        echo "  curl http://43.159.52.61:$PORT"
        echo "  curl http://43.159.52.61:$PORT/api/status"
        echo ""
        echo "📋 管理命令:"
        echo "  查看状态: $0 status"
        echo "  查看日志: $0 logs"
        echo "  停止服务: $0 stop"
        echo "  重启服务: $0 restart"
        
    else
        log_error "服务器启动失败"
        echo "查看日志: tail -f $LOG_FILE"
        exit 1
    fi
}

# 停止服务器
stop_server() {
    if [ -f "$PID_FILE" ]; then
        SERVER_PID=$(cat "$PID_FILE")
        
        if ps -p $SERVER_PID > /dev/null; then
            log_info "正在停止服务器 (PID: $SERVER_PID)..."
            kill $SERVER_PID
            sleep 1
            
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
    log_info "正在重启服务器..."
    stop_server
    sleep 2
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
            echo "  内存使用: $(ps -o rss= -p $SERVER_PID | awk '{print $1/1024 " MB"}')"
            
            # 检查端口监听
            if netstat -tlnp 2>/dev/null | grep -q ":$PORT "; then
                echo "  端口状态: 监听中"
            else
                echo "  端口状态: 未监听"
            fi
            
            # 测试连接
            echo -n "  连接测试: "
            if curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/api/status 2>/dev/null | grep -q "200"; then
                echo "成功"
            else
                echo "失败"
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
        echo "=========================================="
        tail -n 50 "$LOG_FILE"
        echo "=========================================="
        echo "完整日志: $LOG_FILE"
        echo "实时日志: tail -f $LOG_FILE"
    else
        log_warning "日志文件不存在: $LOG_FILE"
    fi
}

# 显示帮助
show_help() {
    echo "OpenClaw测试Web服务器管理脚本"
    echo ""
    echo "使用方法: $0 {start|stop|restart|status|logs|help}"
    echo ""
    echo "命令:"
    echo "  start   启动服务器"
    echo "  stop    停止服务器"
    echo "  restart 重启服务器"
    echo "  status  查看服务器状态"
    echo "  logs    查看服务器日志"
    echo "  help    显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start    # 启动服务器"
    echo "  $0 status   # 查看状态"
    echo "  $0 logs     # 查看日志"
    echo "  $0 stop     # 停止服务器"
}

# 主逻辑
case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        status_server
        ;;
    logs)
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