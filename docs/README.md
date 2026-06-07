# Cursor + mitmproxy 抓包操作文档

## 📁 文件列表

| 文件 | 说明 |
|------|------|
| `capture_cursor_prompt.py` | 抓包脚本（三平台通用） |
| `cursor-mitm-mac.md` | macOS 操作指南 |
| `cursor-mitm-win.md` | Windows 操作指南 |

## ⚡ 一句话速览

1. 安装 mitmproxy
2. 保存脚本 `capture_cursor_prompt.py`
3. 运行 `mitmweb -s capture_cursor_prompt.py -p 8888`
4. 安装 HTTPS 证书（最关键一步！）
5. Cursor 设置里填 Proxy：`http://127.0.0.1:8888`
6. 正常使用 Cursor，prompt 自动保存到 `cursor_prompts/` 目录
