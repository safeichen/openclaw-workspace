# OpenClaw 测试Web页面

这是一个部署在腾讯云服务器上的OpenClaw测试页面，用于演示和测试AI助手的功能。

## 🚀 快速访问

**主页面:** http://43.159.52.61

**API端点:**
- `GET /api/status` - 服务器状态
- `GET /api/system` - 系统信息
- `GET /api/email-status` - 邮件监控状态

## 📋 功能特性

### 1. 响应式Web界面
- 现代化UI设计，支持移动端
- 实时服务器状态显示
- 交互式API测试工具

### 2. 系统监控
- OpenClaw Gateway状态
- 邮件监控系统状态
- Cron任务状态
- 服务器基本信息

### 3. API接口
- RESTful API设计
- JSON格式响应
- 跨域支持 (CORS)

### 4. 邮件测试
- 通过Web界面发送测试邮件
- 邮件监控状态查询
- 实时邮件推送测试

## 🔧 技术栈

- **后端:** Python 3.11 + HTTP Server
- **前端:** HTML5 + CSS3 + JavaScript
- **部署:** 腾讯云服务器 (OpenCloudOS 8)
- **IP地址:** 43.159.52.61
- **端口:** 80 (HTTP标准端口)

## 📁 项目结构

```
test-webpage/
├── index.html          # 主页面
├── server.py           # Python HTTP服务器
├── start-server.sh     # 启动脚本
├── server.log          # 服务器日志
├── server.pid          # 进程ID文件
└── README.md           # 本文档
```

## 🛠️ 管理命令

```bash
# 进入项目目录
cd /root/.openclaw/workspace/test-webpage

# 启动服务器
./start-server.sh start

# 查看状态
./start-server.sh status

# 查看日志
./start-server.sh logs

# 停止服务器
./start-server.sh stop

# 重启服务器
./start-server.sh restart
```

## 🌐 测试命令

```bash
# 测试主页
curl http://43.159.52.61

# 测试API状态
curl http://43.159.52.61/api/status

# 测试系统信息
curl http://43.159.52.61/api/system

# 测试邮件状态
curl http://43.159.52.61/api/email-status
```

## 🔒 安全说明

1. **端口安全:** 仅开放8080端口用于测试
2. **访问限制:** 无认证，公开访问（仅测试用途）
3. **数据安全:** 不存储敏感信息
4. **日志记录:** 所有访问记录在server.log中

## 📊 集成功能

### 邮件监控系统
- 每5分钟自动检查QQ邮箱
- 新邮件自动推送通知
- 缓存机制避免重复通知

### OpenClaw集成
- Gateway状态监控
- 技能系统状态
- 服务健康检查

## 🚨 故障排除

### 常见问题

**Q: 无法访问页面**
```
# 检查服务器状态
./start-server.sh status

# 检查端口监听
netstat -tlnp | grep :8080

# 检查防火墙
systemctl status firewalld
```

**Q: API返回错误**
```
# 查看服务器日志
./start-server.sh logs

# 测试本地连接
curl http://localhost:8080/api/status
```

**Q: 端口被占用**
```
# 停止现有进程
./start-server.sh stop

# 修改端口（编辑server.py中的PORT变量）
vim server.py
```

## 📈 性能监控

服务器提供以下监控信息：
- 进程状态和内存使用
- 服务运行时间
- API响应时间
- 邮件监控状态

## 🔄 更新日志

### v1.0.0 (2026-02-26)
- ✅ 初始版本发布
- ✅ 响应式Web界面
- ✅ 基础API接口
- ✅ 系统状态监控
- ✅ 邮件测试功能
- ✅ 管理脚本

## 📞 支持

如有问题，请检查：
1. 服务器是否运行: `./start-server.sh status`
2. 日志文件: `./start-server.sh logs`
3. 网络连接: `ping 43.159.52.61`

## 📄 许可证

本项目仅用于测试和演示目的。

---
**部署时间:** 2026年2月26日  
**服务器IP:** 43.159.52.61  
**维护者:** OpenClaw AI Assistant