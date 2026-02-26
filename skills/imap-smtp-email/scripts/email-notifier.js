#!/usr/bin/env node

/**
 * 邮件通知推送脚本
 * 检查新邮件并通过QQ Bot推送通知
 */

const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

// 邮件监控脚本路径
const MONITOR_SCRIPT = path.join(__dirname, 'email-monitor.js');

// 运行邮件监控
async function runEmailMonitor() {
  return new Promise((resolve, reject) => {
    exec(`node "${MONITOR_SCRIPT}"`, (error, stdout, stderr) => {
      if (error) {
        // 退出码1表示有新邮件（这是我们设计的）
        if (error.code === 1) {
          // 从stdout中提取通知内容
          const output = stdout.toString();
          const startMarker = '=== 新邮件通知 ===';
          const endMarker = '=== 通知结束 ===';
          
          const startIndex = output.indexOf(startMarker);
          const endIndex = output.indexOf(endMarker);
          
          if (startIndex !== -1 && endIndex !== -1) {
            const notification = output.substring(
              startIndex + startMarker.length,
              endIndex
            ).trim();
            
            resolve({
              hasNew: true,
              notification: notification,
              rawOutput: output
            });
          } else {
            // 如果没有找到标记，使用整个输出
            resolve({
              hasNew: true,
              notification: output.trim(),
              rawOutput: output
            });
          }
        } else {
          reject(new Error(`监控脚本执行失败: ${error.message}\n${stderr}`));
        }
      } else {
        // 退出码0表示没有新邮件
        resolve({
          hasNew: false,
          notification: null,
          rawOutput: stdout.toString()
        });
      }
    });
  });
}

// 通过QQ Bot发送消息
async function sendQQNotification(message) {
  return new Promise((resolve, reject) => {
    // 这里使用OpenClaw的message工具发送消息
    // 由于我们无法直接调用OpenClaw工具，我们将输出到控制台
    // 主会话会捕获这个输出并处理
    
    console.log('📧 新邮件通知（通过QQ Bot发送）：');
    console.log(message);
    console.log('--- 通知内容结束 ---');
    
    // 在实际部署中，这里应该调用OpenClaw的message工具
    // 例如：使用exec调用openclaw命令行工具
    
    resolve(true);
  });
}

// 主函数
async function main() {
  try {
    console.log('🚀 启动邮件通知检查...');
    console.log(`监控脚本: ${MONITOR_SCRIPT}`);
    console.log(`当前时间: ${new Date().toLocaleString('zh-CN')}`);
    console.log('=' .repeat(50));
    
    const result = await runEmailMonitor();
    
    if (result.hasNew) {
      console.log('✅ 检测到新邮件！');
      console.log('=' .repeat(50));
      
      // 发送QQ通知
      await sendQQNotification(result.notification);
      
      console.log('=' .repeat(50));
      console.log('✅ 通知已发送！');
      
      // 记录日志
      logNotification(result);
      
    } else {
      console.log('ℹ️ 没有新邮件');
    }
    
    console.log('=' .repeat(50));
    console.log('✅ 邮件通知检查完成');
    
  } catch (error) {
    console.error('❌ 邮件通知检查失败:', error.message);
    process.exit(1);
  }
}

// 记录通知日志
function logNotification(result) {
  const logDir = path.join(__dirname, 'logs');
  const logFile = path.join(logDir, 'notifications.log');
  
  // 创建日志目录
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }
  
  const logEntry = {
    timestamp: new Date().toISOString(),
    hasNew: result.hasNew,
    notification: result.notification,
    rawOutput: result.rawOutput.substring(0, 500) // 只记录前500字符
  };
  
  // 读取现有日志
  let logs = [];
  if (fs.existsSync(logFile)) {
    try {
      const content = fs.readFileSync(logFile, 'utf8');
      logs = JSON.parse(content);
    } catch (err) {
      logs = [];
    }
  }
  
  // 添加新日志（只保留最近50条）
  logs.push(logEntry);
  if (logs.length > 50) {
    logs = logs.slice(-50);
  }
  
  // 保存日志
  fs.writeFileSync(logFile, JSON.stringify(logs, null, 2));
  
  // 同时写入文本日志
  const textLogFile = path.join(logDir, 'notifications-text.log');
  const textEntry = `[${new Date().toLocaleString('zh-CN')}] 新邮件通知\n${result.notification}\n${'='.repeat(80)}\n`;
  fs.appendFileSync(textLogFile, textEntry);
}

// 如果直接运行此脚本
if (require.main === module) {
  main().catch(error => {
    console.error('脚本执行失败:', error);
    process.exit(1);
  });
}

module.exports = { main, runEmailMonitor, sendQQNotification };