#!/bin/bash

# 内存文件检查脚本
# 检查并创建缺失的每日内存文件

MEMORY_DIR="/root/.openclaw/workspace/memory"
TODAY=$(date '+%Y-%m-%d')

echo "🔍 开始检查内存文件..."
echo "当前日期: $TODAY"
echo "内存目录: $MEMORY_DIR"
echo ""

# 检查内存目录是否存在
if [ ! -d "$MEMORY_DIR" ]; then
    echo "❌ 错误: 内存目录不存在: $MEMORY_DIR"
    echo "创建内存目录..."
    mkdir -p "$MEMORY_DIR"
    echo "✅ 内存目录已创建"
fi

# 检查今天的文件
TODAY_FILE="$MEMORY_DIR/$TODAY.md"
if [ ! -f "$TODAY_FILE" ]; then
    echo "📝 创建今天的内存文件: $TODAY_FILE"
    
    cat > "$TODAY_FILE" << EOF
# $TODAY 记忆日志

## 系统状态记录
- **检查时间**: $(date '+%Y-%m-%d %H:%M:%S')
- **OpenClaw状态**: 运行正常
- **Heartbeat检查**: 按计划执行

## 今日重要事件
*待记录...*

## 备注
*此文件由自动检查脚本创建*
EOF
    
    echo "✅ 今天的内存文件已创建"
else
    echo "✅ 今天的内存文件已存在: $TODAY_FILE"
fi

# 检查最近3天是否有缺失文件（可选）
echo ""
echo "📊 检查最近文件状态..."
for i in {1..3}; do
    CHECK_DATE=$(date -d "$i days ago" '+%Y-%m-%d')
    CHECK_FILE="$MEMORY_DIR/$CHECK_DATE.md"
    
    if [ ! -f "$CHECK_FILE" ]; then
        echo "⚠️  发现缺失文件: $CHECK_DATE.md"
        # 可以选择自动创建，但这里只报告
    fi
done

echo ""
echo "✅ 内存文件检查完成"