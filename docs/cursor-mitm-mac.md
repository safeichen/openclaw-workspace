# macOS 端 — mitmproxy + Cursor 抓包指南

## 1. 安装 mitmproxy

```bash
brew install mitmproxy
```

## 2. 准备脚本

创建目录并保存脚本：

```bash
mkdir -p ~/cursor_debug
```

把 `capture_cursor_prompt.py` 保存到 `~/cursor_debug/` 下。

## 3. 安装 HTTPS 证书（必须）

1. 启动 mitmweb（先随便跑一下）：
   ```bash
   cd ~/cursor_debug
   mitmweb -p 8888
   ```

2. 浏览器访问：**http://mitm.it**
3. 下载 macOS 证书
4. 双击证书文件 → 钥匙串访问打开
5. 找到证书 → 双击 → **信任** → 选择 **"始终信任"**

或者终端安装：
```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ~/.mitmproxy/mitmproxy-ca-cert.pem
```

## 4. 启动抓包

```bash
cd ~/cursor_debug
mitmweb -s capture_cursor_prompt.py -p 8888
```

浏览器会自动打开 http://127.0.0.1:8081 （mitmweb 界面）

## 5. 配置 Cursor

**Cursor → Settings → 搜索 `proxy`**
```
Http: Proxy → http://127.0.0.1:8888
```

或者命令行走代理启动：
```bash
HTTPS_PROXY=http://127.0.0.1:8888 open -a Cursor
```

## 6. 开始使用

在 Cursor 里正常写代码、问问题。每次对话的 system prompt 和用户消息会保存到：

```
~/cursor_debug/cursor_prompts/20260607_153000_api2_cursor_sh_.txt
```

## 7. 关闭

用完后在 Cursor 设置里清空 Proxy，关掉 mitmweb 窗口即可。

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 证书装完还是 HTTPS 报错 | 重启 Cursor，重启 mitmweb |
| 抓不到请求 | 确认 Cursor Proxy 设置已保存 |
| 端口被占用 | `mitmweb -p 8899` 换端口 |
| 不想每次输命令 | 做成 alias：`alias cursor-debug='cd ~/cursor_debug && mitmweb -s capture_cursor_prompt.py -p 8888'` |
