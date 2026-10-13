#!/bin/bash
# 早餐点单系统 启动/管理脚本
DIR="/root/.openclaw/workspace/breakfast-order"
PID_FILE="$DIR/server.pid"
LOG="$DIR/server.log"
PORT=8092

running() { [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; }

case "$1" in
  start)
    if running; then echo "已在运行 (PID $(cat "$PID_FILE"))"; exit 0; fi
    cd "$DIR"
    setsid /usr/bin/python3 "$DIR/server.py" >> "$LOG" 2>&1 < /dev/null &
    echo $! > "$PID_FILE"
    sleep 2
    if running; then echo "已启动 PID $(cat "$PID_FILE")，端口 $PORT";
    else echo "启动失败，查看 $LOG"; tail -5 "$LOG"; exit 1; fi
    ;;
  stop)
    [ -f "$PID_FILE" ] && kill "$(cat "$PID_FILE")" 2>/dev/null
    rm -f "$PID_FILE"; echo "已停止";;
  restart)
    "$0" stop; sleep 2; "$0" start;;
  status)
    if running; then echo "运行中 PID $(cat "$PID_FILE")  http://43.159.52.61:$PORT";
    else echo "未运行"; fi;;
  *)
    echo "用法: $0 {start|stop|restart|status}";;
esac
