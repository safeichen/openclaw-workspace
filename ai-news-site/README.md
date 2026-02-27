# 🤖 AI资讯聚合站

基于OpenClaw AI助手和news-summary技能构建的实时AI资讯聚合平台，自动从多个可信来源收集、分析和展示最新人工智能动态。

## 🚀 快速开始

### 访问地址
- **主页面:** http://43.159.52.61:8082
- **API状态:** http://43.159.52.61:8082/api/system/status
- **测试API:** http://43.159.52.61:8082/api/test

### 本地启动
```bash
# 进入项目目录
cd /root/.openclaw/workspace/ai-news-site

# 启动服务器
./start.sh start

# 查看状态
./start.sh status

# 查看日志
./start.sh logs

# 停止服务器
./start.sh stop
```

## 📋 功能特性

### 🎯 核心功能
1. **实时AI资讯聚合** - 自动从多个来源收集最新AI新闻
2. **智能分类系统** - 按研究、行业、创业、伦理等分类
3. **趋势分析** - 自动分析热门话题和研究机构
4. **响应式界面** - 现代化设计，支持移动端
5. **RESTful API** - 完整的API接口

### 🔧 技术架构
- **前端:** HTML5 + CSS3 + JavaScript (ES6+)
- **后端:** Python Flask + RESTful API
- **数据源:** OpenClaw news-summary技能 + 多源RSS
- **部署:** 腾讯云服务器 (43.159.52.61)

### 📊 数据流程
```
多源RSS → news-summary技能 → 数据清洗 → 分类分析 → 前端展示
    ↓          ↓           ↓          ↓          ↓
  资讯源      OpenClaw     Python    趋势分析    Web界面
```

## 🛠️ API接口

### 资讯相关
```bash
# 获取AI资讯
GET /api/ai-news
GET /api/ai-news?category=research
GET /api/ai-news?timeRange=week&sortBy=recent

# 搜索AI资讯
GET /api/ai-news/search?q=大语言模型

# 获取资讯详情
GET /api/ai-news/{id}/content
```

### 系统相关
```bash
# 系统状态
GET /api/system/status

# 系统统计
GET /api/system/stats

# 趋势数据
GET /api/ai-trends

# 测试接口
GET /api/test
```

### 使用示例
```bash
# 获取最新AI资讯
curl http://43.159.52.61:8082/api/ai-news

# 搜索特定主题
curl "http://43.159.52.61:8082/api/ai-news/search?q=GPT-5"

# 检查系统状态
curl http://43.159.52.61:8082/api/system/status
```

## 📁 项目结构

```
ai-news-site/
├── index.html              # 主页面
├── css/                    # 样式文件
│   └── style.css          # 主样式表
├── js/                     # JavaScript文件
│   ├── main.js            # 主逻辑
│   └── api.js             # API管理
├── images/                 # 图片资源
├── data/                   # 数据目录（自动生成）
│   ├── news_cache.json    # 资讯缓存
│   └── stats.json         # 统计信息
├── server.py              # Flask后端服务器
├── start.sh               # 启动脚本
├── server.log             # 服务器日志（自动生成）
├── server.pid             # 进程ID（自动生成）
└── README.md              # 本文档
```

## 🔧 部署指南

### 环境要求
- Python 3.6+
- Flask 2.0+
- Flask-CORS
- OpenClaw news-summary技能

### 安装步骤
```bash
# 1. 安装Python依赖
pip3 install flask flask-cors

# 2. 确保OpenClaw news-summary技能可用
openclaw news --brief

# 3. 启动服务器
cd /root/.openclaw/workspace/ai-news-site
./start.sh start

# 4. 验证部署
curl http://localhost:8082/api/test
```

### 配置说明
- **端口:** 8082 (可在server.py中修改)
- **主机:** 0.0.0.0 (监听所有接口)
- **更新频率:** 每5分钟自动更新
- **缓存:** 自动管理，支持离线访问

## 🚀 高级功能

### 1. 自定义资讯源
编辑`server.py`中的`CATEGORIES`字典，添加自定义分类和关键词：
```python
CATEGORIES = {
    'custom': ['自定义关键词1', '关键词2'],
    # ...
}
```

### 2. 修改更新频率
在`server.py`中调整后台更新间隔：
```python
# 每5分钟更新一次（300秒）
time.sleep(300)
```

### 3. 添加新API端点
在`server.py`中添加新的路由函数：
```python
@app.route('/api/custom', methods=['GET'])
def custom_endpoint():
    return jsonify({'message': '自定义端点'})
```

### 4. 集成其他OpenClaw技能
```python
# 集成weather技能
result = subprocess.run(['openclaw', 'weather'], capture_output=True, text=True)
```

## 📈 监控与维护

### 日志管理
```bash
# 查看实时日志
tail -f server.log

# 查看错误日志
grep -i error server.log

# 清理旧日志
truncate -s 0 server.log
```

### 性能监控
```bash
# 检查服务器状态
./start.sh status

# 查看进程资源使用
ps aux | grep server.py

# 监控API响应时间
time curl -s http://localhost:8082/api/test > /dev/null
```

### 数据备份
```bash
# 备份数据文件
cp data/news_cache.json data/news_cache_backup_$(date +%Y%m%d).json

# 恢复数据
cp data/news_cache_backup_20260226.json data/news_cache.json
```

## 🔒 安全建议

### 1. 防火墙配置
```bash
# 只允许特定IP访问
iptables -A INPUT -p tcp --dport 8082 -s 允许的IP -j ACCEPT
iptables -A INPUT -p tcp --dport 8082 -j DROP
```

### 2. 访问控制
- 在生产环境中添加认证中间件
- 限制API调用频率
- 记录访问日志

### 3. 数据安全
- 定期备份数据文件
- 监控异常访问模式
- 及时更新依赖包

## 🐛 故障排除

### 常见问题

**Q: 服务器无法启动**
```
# 检查端口占用
netstat -tlnp | grep :8082

# 检查Python依赖
python3 -c "import flask; import flask_cors"

# 查看详细错误
python3 server.py
```

**Q: 无法获取资讯数据**
```
# 测试news-summary技能
openclaw news --brief

# 检查网络连接
curl -v https://news.google.com/rss

# 查看服务器日志
tail -f server.log
```

**Q: API返回错误**
```
# 测试API连接
curl http://localhost:8082/api/test

# 检查Flask服务状态
ps aux | grep flask

# 重启服务
./start.sh restart
```

### 调试模式
```bash
# 以调试模式启动
python3 server.py

# 或修改server.py
DEBUG = True
```

## 📞 支持与贡献

### 获取帮助
1. 查看本文档
2. 检查服务器日志
3. 测试API接口状态
4. 联系维护者

### 贡献代码
1. Fork项目仓库
2. 创建功能分支
3. 提交Pull Request
4. 更新文档

### 报告问题
- 描述问题现象
- 提供复现步骤
- 附上相关日志
- 建议解决方案

## 📄 许可证

本项目基于MIT许可证开源，仅供学习和研究使用。

## 🎯 未来规划

### 短期目标
- [ ] 增加更多资讯源
- [ ] 优化移动端体验
- [ ] 添加用户收藏功能
- [ ] 实现邮件订阅

### 长期目标
- [ ] 多语言支持
- [ ] AI内容摘要生成
- [ ] 个性化推荐系统
- [ ] 社区贡献机制

---

**部署时间:** 2026年2月26日  
**服务器IP:** 43.159.52.61  
**维护者:** OpenClaw AI Assistant  
**版本:** 1.0.0  

🚀 让AI资讯触手可及！