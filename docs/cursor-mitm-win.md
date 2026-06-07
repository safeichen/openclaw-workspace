# Windows 端 — mitmproxy + Cursor 抓包指南

## 1. 安装 mitmproxy

**方式一（推荐）：下载 exe 安装包**
- 访问 https://mitmproxy.org/downloads/
- 下载 `mitmproxy-X.X.X-windows-installer.exe`
- 双击安装，一路 Next

**方式二：pip 安装**
```bash
pip install mitmproxy
```

## 2. 准备脚本和目录

```bash
# 在 D 盘创建目录
mkdir D:\cursor_debug
mkdir D:\cursor_debug\cursor_prompts
```

把 `capture_cursor_prompt.py` 保存到 `D:\cursor_debug\` 下。

> ⚠️ **新建文件注意**：建文本文档粘贴后，记得把后缀 `.txt` 改成 `.py`

## 3. 安装 HTTPS 证书（必须！）

**方法一（推荐）：用浏览器安装**
1. 先启动一次 mitmweb：
   ```bash
   cd /d D:\cursor_debug
   mitmweb -p 8888
   ```
2. 浏览器访问 **http://mitm.it**
3. 下载 Windows 版证书
4. 双击下载的 `.p12` 或 `.cer` 文件
5. 选择 **"本地计算机"** → 下一步
6. 选择 **"将所有证书放入下列存储"**
7. 浏览 → **"受信任的根证书颁发机构"** → 确定 → 完成

**方法二：命令行安装**
```powershell
certutil -addstore Root %USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.cer
```

## 4. 启动抓包

```cmd
cd /d D:\cursor_debug
mitmweb -s capture_cursor_prompt.py -p 8888
```

浏览器会自动打开 http://127.0.0.1:8081 （mitmweb 界面）

> 如果没自动打开，手动访问这个地址就行

## 5. 配置 Cursor

**Cursor → File → Preferences → Settings**
搜索 `proxy`，找到 **Http: Proxy**，填入：
```
http://127.0.0.1:8888
```

或者用命令行启动：
```cmd
set HTTPS_PROXY=http://127.0.0.1:8888
set HTTP_PROXY=http://127.0.0.1:8888
"C:\Users\你的用户名\AppData\Local\Programs\Cursor\Cursor.exe"
```

## 6. 开始使用

在 Cursor 里正常写代码、问问题。抓到的内容保存到：

```
D:\cursor_debug\cursor_prompts\20260607_153000_api2_cursor_sh_.txt
```

每个文件内容示例：
```
⏰ 2026-06-07 15:30:00
🌐 https://api2.cursor.sh/xxx
🧠 模型: claude-sonnet-4-20250514

============================================================
【SYSTEM PROMPT - 系统提示词】
============================================================
You are Cursor, an expert software engineer...

============================================================
【USER MESSAGES - 用户消息】
============================================================

--- 用户消息 #1 ---
帮我写一个 Python 脚本...
```

## 7. 关闭

用完后去 Cursor 设置清空 Proxy，关掉 mitmweb 窗口。

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 证书装完还是 HTTPS 报错 | 重启 Cursor + 重启 mitmweb |
| 抓不到请求 | 检查 Cursor 的 Proxy 是否已保存成功 |
| 端口被占用 | `mitmweb -p 8899` 换个端口 |
| PowerShell 报执行策略 | 用 cmd 代替，或 `Set-ExecutionPolicy Unrestricted` |
| 不知道 Cursor 装在哪 | 一般路径：`C:\Users\你的用户名\AppData\Local\Programs\Cursor\Cursor.exe` |
| 不想每次打这么长命令 | 建个 `start.bat`：`cd /d D:\cursor_debug && mitmweb -s capture_cursor_prompt.py -p 8888` |
