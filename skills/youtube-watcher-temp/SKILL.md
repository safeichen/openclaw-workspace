---
name: youtube-watcher-temp
description: 临时YouTube视频处理技能，支持获取视频信息、摘要和字幕。等待正式版安装。
---

# YouTube Watcher 临时版

由于ClawHub速率限制，这是临时YouTube处理技能。

## 当前功能

### 1. 基础处理
- YouTube链接解析
- 视频ID提取
- 基础信息展示

### 2. 可用工具
- `youtube-helper.sh` - 命令行工具
- 手动API调用指南
- Python代码示例

## 使用方法

### 命令行工具
```bash
# 获取视频所有信息
/root/.openclaw/workspace/youtube-helper.sh <YouTube链接>

# 只获取摘要
/root/.openclaw/workspace/youtube-helper.sh <YouTube链接> --summary

# 只获取字幕
/root/.openclaw/workspace/youtube-helper.sh <YouTube链接> --transcript

# 只获取信息
/root/.openclaw/workspace/youtube-helper.sh <YouTube链接> --info
```

### 在对话中使用
直接告诉我YouTube链接，我会：
1. 解析链接并提取视频ID
2. 提供处理选项
3. 给出获取完整信息的步骤

## 完整功能需要

### 1. YouTube Data API v3
- 申请地址: https://console.cloud.google.com/apis
- 启用YouTube Data API v3
- 创建API密钥

### 2. 第三方服务
- **summarize CLI**: `npm install -g @steipete/summarize`
- **youtube-transcript-api**: Python库
- **Apify YouTube scraper**: 需要API令牌

## 快速设置

### 方法A: 使用summarize（推荐）
```bash
# 安装
npm install -g @steipete/summarize

# 设置API密钥（Google Gemini）
export GEMINI_API_KEY=your_key_here

# 使用
summarize "https://youtu.be/VIDEO_ID" --youtube auto
```

### 方法B: Python方案
```bash
# 安装Python库
pip install youtube-transcript-api youtube-title

# 使用Python脚本
python3 -c "
from youtube_title import get_title
import json

video_id = 'VIDEO_ID'
title = get_title(video_id)
print(f'标题: {title}')
"
```

## 示例

### 处理YouTube链接
```
用户: 请处理 https://youtu.be/dQw4w9WgXcQ

助手: 
🎬 检测到YouTube链接
视频ID: dQw4w9WgXcQ

📊 可用操作:
1. 获取视频信息（需要API密钥）
2. 获取视频摘要（需要summarize CLI）
3. 获取字幕（需要Python库）

🔧 建议先安装summarize CLI:
npm install -g @steipete/summarize
export GEMINI_API_KEY=your_key
summarize \"https://youtu.be/dQw4w9WgXcQ\" --youtube auto
```

## 等待正式版

正式版 `youtube-watcher` 技能包含：
- ✅ 自动字幕提取
- ✅ 视频摘要生成
- ✅ 多语言支持
- ✅ 批量处理
- ✅ 缓存功能

**安装状态**: 等待ClawHub速率限制恢复后安装

## 临时解决方案

1. **立即使用**: 提供链接，我帮你分析
2. **手动处理**: 使用我创建的脚本
3. **等待安装**: 稍后重试 `clawhub install youtube-watcher`

## 帮助命令

```bash
# 查看帮助
/root/.openclaw/workspace/youtube-helper.sh

# 测试链接
/root/.openclaw/workspace/youtube-helper.sh https://youtu.be/dQw4w9WgXcQ --info
```

现在你可以提供YouTube链接，我会尽力帮你处理！