# AI Daily Insights - 每日AI资讯与论文网站

一个自动更新的AI资讯和论文推送网站，每天自动获取最新AI新闻和研究论文。

## 🌟 功能特性

### 核心功能
- **每日AI资讯** - 自动获取最新AI新闻、技术动态和行业趋势
- **论文推送** - 展示最新的AI研究论文，按领域分类
- **自动更新** - 每天自动更新内容，无需手动维护
- **响应式设计** - 适配桌面和移动设备
- **暗色模式** - 支持亮色/暗色主题切换

### 自动化特性
- **定时更新** - 每天上午9点自动更新内容
- **多数据源** - 从多个来源获取资讯和论文
- **智能分类** - 自动分类和标签化内容
- **趋势分析** - 识别热门话题和趋势

## 🚀 快速开始

### 1. 本地运行
```bash
# 克隆项目
git clone <repository-url>
cd ai-daily-website

# 安装依赖（如果需要）
npm install

# 启动本地服务器
python3 -m http.server 8000
# 或使用任何静态文件服务器

# 访问 http://localhost:8000
```

### 2. 设置自动更新
```bash
# 运行设置脚本
./scripts/setup-cron.sh

# 或手动设置cron任务
0 9 * * * /path/to/ai-daily-website/scripts/update-content.sh >> /path/to/logfile.log 2>&1
```

### 3. 部署到生产环境
```bash
# 运行部署脚本
./scripts/deploy.sh

# 选择部署方式：
# 1) GitHub Pages (推荐)
# 2) Vercel
# 3) Netlify
# 4) 所有方式
```

## 📁 项目结构

```
ai-daily-website/
├── index.html          # 首页
├── news.html          # 资讯页面
├── papers.html        # 论文页面
├── about.html         # 关于页面
├── css/
│   └── style.css      # 样式文件
├── js/
│   ├── main.js        # 主JavaScript文件
│   └── news.js        # 资讯页面JavaScript
├── data/
│   ├── news.json      # 资讯数据
│   ├── papers.json    # 论文数据
│   ├── stats.json     # 统计数据
│   └── metadata.json  # 元数据
├── scripts/
│   ├── update-content.sh  # 内容更新脚本
│   ├── setup-cron.sh      # 定时任务设置
│   └── deploy.sh          # 部署脚本
└── images/            # 图片资源
```

## 🔧 配置说明

### 数据源配置
编辑 `scripts/config.json` 配置数据源：

```json
{
  "news_sources": [
    "https://news.ycombinator.com/rss",
    "https://techcrunch.com/feed/",
    "https://openai.com/blog/rss/"
  ],
  "paper_sources": [
    "https://export.arxiv.org/api/query",
    "https://openreview.net/feed"
  ],
  "update_schedule": "0 9 * * *",
  "timezone": "Asia/Shanghai"
}
```

### 网站配置
编辑 `data/metadata.json` 配置网站信息：

```json
{
  "site_name": "AI Daily Insights",
  "description": "每日AI资讯与论文推送",
  "contact_email": "contact@aidaily.insights",
  "social_links": {
    "github": "https://github.com/your-username",
    "twitter": "https://twitter.com/your-handle"
  }
}
```

## 🤖 自动化更新系统

### 更新流程
1. **数据获取** - 从配置的数据源获取最新内容
2. **数据处理** - 清洗、分类、格式化数据
3. **数据存储** - 保存到JSON文件
4. **网站更新** - 更新网站显示的数据
5. **通知发送** - 发送更新通知（可选）

### 定时任务
- **每日更新**: 早上9点（北京时间）
- **实时监控**: 重要新闻实时推送
- **每周总结**: 周日生成一周热点

### 手动触发更新
```bash
# 手动运行更新脚本
./scripts/update-content.sh

# 查看更新日志
tail -f scripts/update.log
```

## 🌐 部署选项

### GitHub Pages (推荐)
- 免费托管
- 自动SSL证书
- 自定义域名支持
- 简单的部署流程

### Vercel
- 极速部署
- 自动HTTPS
- 全球CDN
- 服务器端渲染支持

### Netlify
- 持续部署
- 表单处理
- 身份验证
- 函数支持

### 自定义服务器
- 任何支持静态文件的Web服务器
- Nginx/Apache配置简单
- 需要手动配置SSL

## 📊 数据源集成

### 当前支持的数据源
- **arXiv API** - AI研究论文
- **Hacker News RSS** - 技术新闻
- **TechCrunch RSS** - 科技新闻
- **OpenAI Blog** - OpenAI官方博客
- **Google AI Blog** - Google AI研究

### 扩展数据源
要添加新的数据源：

1. 在 `scripts/update-content.sh` 中添加新的获取函数
2. 在 `config.json` 中添加数据源URL
3. 更新数据处理逻辑

## 🛠️ 开发指南

### 添加新页面
1. 创建HTML文件（如 `newpage.html`）
2. 添加CSS样式到 `css/style.css`
3. 添加JavaScript逻辑到 `js/` 目录
4. 更新导航栏链接

### 修改样式
- 主要样式在 `css/style.css`
- 使用CSS变量实现主题切换
- 响应式设计使用媒体查询

### 添加新功能
1. 在相应的JavaScript文件中添加函数
2. 更新HTML模板
3. 测试功能
4. 更新文档

## 🔍 SEO优化

### 已实现的SEO特性
- 语义化HTML标签
- 合理的标题结构
- 规范的URL
- 移动设备适配
- 页面加载优化

### 可进一步优化的方面
- 添加结构化数据
- 优化图片加载
- 实现预加载
- 添加sitemap

## 📈 网站分析

### 内置分析
- 页面访问统计
- 热门内容追踪
- 用户行为分析
- 性能监控

### 集成第三方分析
- Google Analytics
- Umami Analytics
- Plausible Analytics
- 自定义分析脚本

## 🤝 贡献指南

### 报告问题
1. 在GitHub Issues中创建新issue
2. 描述问题和复现步骤
3. 提供相关日志和截图

### 提交改进
1. Fork项目
2. 创建特性分支
3. 提交更改
4. 创建Pull Request

### 开发规范
- 使用语义化提交信息
- 保持代码风格一致
- 添加必要的注释
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- **项目主页**: https://aidaily.insights
- **问题反馈**: issues@aidaily.insights
- **功能建议**: features@aidaily.insights
- **合作联系**: partnership@aidaily.insights

## 🙏 致谢

感谢以下开源项目和服务的支持：
- [Font Awesome](https://fontawesome.com/) - 图标库
- [Google Fonts](https://fonts.google.com/) - 字体服务
- [arXiv](https://arxiv.org/) - 论文预印本库
- [Hacker News](https://news.ycombinator.com/) - 技术新闻社区

---

**AI Daily Insights** - 让AI学习更简单，让技术视野更开阔 🚀