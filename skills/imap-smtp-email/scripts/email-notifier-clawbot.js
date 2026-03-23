#!/usr/bin/env node

/**
 * 邮件通知推送脚本 - ClawBot版本
 * 检查新邮件并通过ClawBot推送通知
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
              hasNewMail: true,
              notification: notification,
              rawOutput: output
            });
          } else {
            resolve({
              hasNewMail: true,
              notification: output.trim(),
              rawOutput: output
            });
          }
        } else {
          // 其他错误
          reject(new Error(`邮件监控脚本执行失败: ${error.message}\n${stderr}`));
        }
      } else {
        // 没有新邮件
        resolve({
          hasNewMail: false,
          notification: '',
          rawOutput: stdout.toString()
        });
      }
    });
  });
}

// 通过ClawBot发送消息
async function sendClawBotNotification(message) {
  try {
    console.log('📧 新邮件通知（通过ClawBot发送）：');
    console.log('');
    console.log(message);
    console.log('');
    console.log('📅 检查时间:', new Date().toLocaleString('zh-CN'));
    
    // 输出特殊格式，让主会话能够捕获并发送到ClawBot
    console.log('[[CLAWBOT_EMAIL_NOTIFICATION_START]]');
    console.log('📧 新邮件通知');
    console.log('');
    console.log(message);
    console.log('');
    console.log('📅 检查时间: ' + new Date().toLocaleString('zh-CN'));
    console.log('[[CLAWBOT_EMAIL_NOTIFICATION_END]]');
    
    return true;
  } catch (error) {
    console.error('发送ClawBot通知失败:', error.message);
    return false;
  }
}

// 主函数
async function main() {
  try {
    console.log('开始检查邮件通知...');
    console.log('时间:', new Date().toLocaleString('zh-CN'));
    
    const result = await runEmailMonitor();
    
    if (result.hasNewMail) {
      console.log('检测到新邮件，准备发送通知...');
      
      // 发送ClawBot通知
      await sendClawBotNotification(result.notification);
      
      console.log('新邮件通知已发送到ClawBot');
    } else {
      console.log('没有新邮件，无需发送通知');
    }
    
    // 更新最后检查时间
    updateLastCheckTime();
    
    console.log('邮件通知检查完成');
  } catch (error) {
    console.error('邮件通知脚本执行失败:', error.message);
    process.exit(1);
  }
}

// 更新最后检查时间
function updateLastCheckTime() {
  const cacheFile = path.join(__dirname, 'last-email-check.json');
  const data = {
    lastCheck: new Date().toISOString(),
    timestamp: Date.now()
  };
  
  try {
    fs.writeFileSync(cacheFile, JSON.stringify(data, null, 2));
  } catch (err) {
    console.error('更新检查时间失败:', err.message);
  }
}

// 运行主函数
if (require.main === module) {
  main();
}

module.exports = { main, runEmailMonitor, sendClawBotNotification };