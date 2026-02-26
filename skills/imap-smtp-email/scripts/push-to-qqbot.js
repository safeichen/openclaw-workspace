#!/usr/bin/env node

/**
 * 邮件推送脚本 - 将新邮件通知推送到QQ Bot
 * 这个脚本会被cron任务调用，当检测到新邮件时输出特定格式
 */

const { exec } = require('child_process');
const path = require('path');

// 邮件监控脚本路径
const MONITOR_SCRIPT = path.join(__dirname, 'email-monitor.js');

// 运行邮件监控
async function checkAndPush() {
  return new Promise((resolve, reject) => {
    // 直接运行监控脚本
    exec(`node "${MONITOR_SCRIPT}"`, (error, stdout, stderr) => {
      if (error) {
        // 退出码1表示有新邮件
        if (error.code === 1) {
          const output = stdout.toString();
          
          // 提取通知内容
          const startMarker = '=== 新邮件通知 ===';
          const endMarker = '=== 通知结束 ===';
          
          const startIndex = output.indexOf(startMarker);
          const endIndex = output.indexOf(endMarker);
          
          let notification = '';
          if (startIndex !== -1 && endIndex !== -1) {
            notification = output.substring(
              startIndex + startMarker.length,
              endIndex
            ).trim();
          } else {
            notification = output.trim();
          }
          
          // 输出QQ Bot推送格式
          // 使用特殊标记让主会话识别并处理
          console.log('[[QQ_BOT_PUSH_START]]');
          console.log('📧 新邮件通知');
          console.log('');
          console.log(notification);
          console.log('');
          console.log('📅 检查时间: ' + new Date().toLocaleString('zh-CN'));
          console.log('[[QQ_BOT_PUSH_END]]');
          
          resolve({ hasNew: true, notification: notification });
        } else {
          reject(new Error(`监控脚本执行失败: ${error.message}\n${stderr}`));
        }
      } else {
        // 没有新邮件
        console.log('[[NO_NEW_EMAIL]]');
        resolve({ hasNew: false });
      }
    });
  });
}

// 主函数
async function main() {
  try {
    const result = await checkAndPush();
    
    // 记录日志
    const fs = require('fs');
    const logDir = path.join(__dirname, 'logs');
    const logFile = path.join(logDir, 'push-log.json');
    
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }
    
    let logs = [];
    if (fs.existsSync(logFile)) {
      try {
        logs = JSON.parse(fs.readFileSync(logFile, 'utf8'));
      } catch (err) {
        logs = [];
      }
    }
    
    logs.push({
      timestamp: new Date().toISOString(),
      hasNew: result.hasNew,
      notification: result.notification ? result.notification.substring(0, 200) + '...' : null
    });
    
    // 只保留最近100条日志
    if (logs.length > 100) {
      logs = logs.slice(-100);
    }
    
    fs.writeFileSync(logFile, JSON.stringify(logs, null, 2));
    
  } catch (error) {
    console.error('❌ 推送脚本执行失败:', error.message);
    process.exit(1);
  }
}

// 如果直接运行此脚本
if (require.main === module) {
  main();
}

module.exports = { checkAndPush };