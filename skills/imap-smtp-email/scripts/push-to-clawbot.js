#!/usr/bin/env node

/**
 * 邮件推送脚本 - 将新邮件通知推送到ClawBot
 * 这个脚本会被cron任务调用，当检测到新邮件时输出特定格式
 */

const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

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
          
          // 输出ClawBot推送格式
          // 使用特殊标记让主会话识别并处理
          console.log('[[CLAWBOT_PUSH_START]]');
          console.log('📧 新邮件通知');
          console.log('');
          console.log(notification);
          console.log('');
          console.log('📅 检查时间: ' + new Date().toLocaleString('zh-CN'));
          console.log('[[CLAWBOT_PUSH_END]]');
          
          // 更新最后检查时间
          updateLastCheckTime();
          
          resolve(true);
        } else {
          // 其他错误
          console.error('邮件监控脚本执行错误:', error.message);
          if (stderr) {
            console.error('错误详情:', stderr.toString());
          }
          reject(error);
        }
      } else {
        // 没有新邮件
        const output = stdout.toString();
        if (output.includes('没有新邮件')) {
          console.log('没有新邮件');
        } else {
          console.log('邮件检查完成，无新邮件');
        }
        
        // 更新最后检查时间
        updateLastCheckTime();
        
        resolve(false);
      }
    });
  });
}

// 更新最后检查时间
function updateLastCheckTime() {
  const cacheFile = path.join(__dirname, 'last-check-time.json');
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

// 主函数
async function main() {
  try {
    console.log('开始检查邮件并推送到ClawBot...');
    console.log('时间:', new Date().toLocaleString('zh-CN'));
    
    const hasNewMail = await checkAndPush();
    
    if (hasNewMail) {
      console.log('新邮件通知已准备推送到ClawBot');
    } else {
      console.log('没有新邮件，无需推送');
    }
    
    console.log('邮件检查完成');
  } catch (error) {
    console.error('邮件推送脚本执行失败:', error.message);
    process.exit(1);
  }
}

// 运行主函数
if (require.main === module) {
  main();
}

module.exports = { checkAndPush };