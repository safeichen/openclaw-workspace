#!/bin/bash

# AI Daily Insights 部署脚本
# 将网站部署到GitHub Pages

set -e

# 配置
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOY_DIR="$PROJECT_ROOT/deploy"
GITHUB_USERNAME="your-username"
GITHUB_REPO="ai-daily-insights"
GITHUB_PAGES_URL="https://$GITHUB_USERNAME.github.io/$GITHUB_REPO"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# 检查必要工具
check_requirements() {
    log "检查系统要求..."
    
    # 检查git
    if ! command -v git &> /dev/null; then
        error "Git未安装，请先安装Git"
        exit 1
    fi
    success "Git已安装"
    
    # 检查Node.js（可选）
    if command -v node &> /dev/null; then
        success "Node.js已安装"
    else
        warning "Node.js未安装，部分功能可能受限"
    fi
    
    # 检查GitHub CLI（可选）
    if command -v gh &> /dev/null; then
        success "GitHub CLI已安装"
    else
        warning "GitHub CLI未安装，建议安装以便更好的GitHub集成"
    fi
}

# 准备部署目录
prepare_deploy() {
    log "准备部署文件..."
    
    # 创建部署目录
    rm -rf "$DEPLOY_DIR"
    mkdir -p "$DEPLOY_DIR"
    
    # 复制网站文件
    cp -r "$PROJECT_ROOT"/* "$DEPLOY_DIR"/
    
    # 删除不需要的文件
    rm -rf "$DEPLOY_DIR"/scripts
    rm -rf "$DEPLOY_DIR"/.git
    rm -f "$DEPLOY_DIR"/README.md
    rm -f "$DEPLOY_DIR"/deploy.sh
    
    # 创建GitHub Pages需要的文件
    cat > "$DEPLOY_DIR/CNAME" << EOF
aidaily.insights
EOF
    
    cat > "$DEPLOY_DIR/.nojekyll" << EOF
# 告诉GitHub Pages不要使用Jekyll
EOF
    
    success "部署文件准备完成"
}

# 初始化Git仓库
init_git() {
    log "初始化Git仓库..."
    
    cd "$DEPLOY_DIR"
    
    # 初始化Git
    git init
    git checkout -b main
    
    # 配置Git
    git config user.name "AI Daily Insights Bot"
    git config user.email "bot@aidaily.insights"
    
    # 添加文件
    git add .
    git commit -m "Deploy AI Daily Insights website - $(date '+%Y-%m-%d %H:%M:%S')"
    
    success "Git仓库初始化完成"
}

# 部署到GitHub Pages
deploy_to_github() {
    log "部署到GitHub Pages..."
    
    cd "$DEPLOY_DIR"
    
    # 添加GitHub远程仓库
    git remote add origin "https://github.com/$GITHUB_USERNAME/$GITHUB_REPO.git"
    
    # 强制推送到GitHub
    git push -f origin main
    
    success "已推送到GitHub仓库"
    
    # 等待GitHub Pages构建
    log "等待GitHub Pages构建..."
    echo "网站将在几分钟内可用: $GITHUB_PAGES_URL"
}

# 部署到Vercel（替代方案）
deploy_to_vercel() {
    log "部署到Vercel..."
    
    if ! command -v vercel &> /dev/null; then
        warning "Vercel CLI未安装，跳过Vercel部署"
        echo "安装Vercel CLI: npm i -g vercel"
        return
    fi
    
    cd "$PROJECT_ROOT"
    
    # 部署到Vercel
    vercel --prod
    
    success "已部署到Vercel"
}

# 部署到Netlify（替代方案）
deploy_to_netlify() {
    log "部署到Netlify..."
    
    if ! command -v netlify &> /dev/null; then
        warning "Netlify CLI未安装，跳过Netlify部署"
        echo "安装Netlify CLI: npm i -g netlify-cli"
        return
    fi
    
    cd "$PROJECT_ROOT"
    
    # 部署到Netlify
    netlify deploy --prod
    
    success "已部署到Netlify"
}

# 生成部署报告
generate_report() {
    log "生成部署报告..."
    
    REPORT_FILE="$PROJECT_ROOT/deploy_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$REPORT_FILE" << EOF
# AI Daily Insights 部署报告

## 部署信息
- **部署时间**: $(date)
- **项目版本**: 1.0.0
- **部署目录**: $DEPLOY_DIR
- **文件数量**: $(find "$DEPLOY_DIR" -type f | wc -l)

## 网站结构
\`\`\`
$(tree "$DEPLOY_DIR" -I 'node_modules|.git' --dirsfirst)
\`\`\`

## 部署选项
1. **GitHub Pages**: $GITHUB_PAGES_URL
2. **Vercel**: 需要Vercel CLI
3. **Netlify**: 需要Netlify CLI

## 后续步骤
1. 访问网站确认部署成功
2. 设置自定义域名（可选）
3. 配置SSL证书
4. 设置网站分析

## 自动更新
网站配置了每日自动更新：
- 更新脚本: $PROJECT_ROOT/scripts/update-content.sh
- 更新时间: 每天上午9点（北京时间）
- 数据目录: $PROJECT_ROOT/data

## 联系方式
- 项目维护: AI Daily Insights Team
- 问题反馈: issues@aidaily.insights
EOF
    
    success "部署报告已生成: $REPORT_FILE"
}

# 显示部署选项
show_options() {
    echo ""
    echo "请选择部署方式:"
    echo "1) GitHub Pages (推荐)"
    echo "2) Vercel"
    echo "3) Netlify"
    echo "4) 所有方式"
    echo "5) 仅准备文件，不部署"
    echo ""
    
    read -p "请输入选项 (1-5): " choice
    echo ""
    
    case $choice in
        1)
            prepare_deploy
            init_git
            deploy_to_github
            ;;
        2)
            prepare_deploy
            deploy_to_vercel
            ;;
        3)
            prepare_deploy
            deploy_to_netlify
            ;;
        4)
            prepare_deploy
            init_git
            deploy_to_github
            deploy_to_vercel
            deploy_to_netlify
            ;;
        5)
            prepare_deploy
            success "部署文件已准备在: $DEPLOY_DIR"
            echo "你可以手动将这些文件上传到任何静态网站托管服务"
            ;;
        *)
            error "无效选项"
            exit 1
            ;;
    esac
}

# 主函数
main() {
    log "开始部署 AI Daily Insights 网站..."
    log "项目根目录: $PROJECT_ROOT"
    
    # 检查要求
    check_requirements
    
    # 显示部署选项
    show_options
    
    # 生成报告
    generate_report
    
    log "部署完成！"
    echo ""
    echo "🎉 网站部署成功！"
    echo ""
    echo "📊 部署摘要:"
    echo "  • 部署时间: $(date)"
    echo "  • 部署目录: $DEPLOY_DIR"
    echo "  • GitHub Pages: $GITHUB_PAGES_URL"
    echo ""
    echo "🔧 后续操作:"
    echo "  1. 访问网站确认部署成功"
    echo "  2. 设置自动更新定时任务"
    echo "  3. 配置网站分析"
    echo ""
    echo "📋 查看部署报告:"
    echo "  cat $PROJECT_ROOT/deploy_report_*.md"
    echo ""
}

# 错误处理
trap 'error "部署过程中出现错误"; exit 1' ERR

# 执行主函数
main

exit 0