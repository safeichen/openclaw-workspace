#!/usr/bin/env node

/**
 * 邮件监控测试脚本
 */

const { checkNewEmails, generateNotification } = require('./email-monitor.js');

async function test() {
  console.log('🧪 开始测试邮件监控功能...');
  console.log('='.repeat(50));
  
  try {
    console.log('1. 检查新邮件...');
    const newEmails = await checkNewEmails();
    
    console.log(`2. 检查结果: ${newEmails.length} 封新邮件`);
    
    if (newEmails.length > 0) {
      console.log('3. 邮件详情:');
      newEmails.forEach((email, index) => {
        console.log(`\n   邮件 ${index + 1}:`);
        console.log(`   主题: ${email.subject}`);
        console.log(`   发件人: ${email.from}`);
        console.log(`   时间: ${email.date}`);
        console.log(`   摘要: ${email.snippet}`);
        console.log(`   UID: ${email.uid}`);
      });
      
      console.log('\n4. 生成通知消息:');
      const notification = generateNotification(newEmails);
      console.log(notification);
      
      console.log('\n5. 缓存状态:');
      const fs = require('fs');
      const path = require('path');
      
      const cacheFile = path.join(__dirname, 'email-monitor-cache.json');
      const notifiedFile = path.join(__dirname, 'email-notified.json');
      
      if (fs.existsSync(cacheFile)) {
        const cache = JSON.parse(fs.readFileSync(cacheFile, 'utf8'));
        console.log(`   最后检查时间: ${cache.lastCheck}`);
        console.log(`   最后UID: ${cache.lastUid}`);
      }
      
      if (fs.existsSync(notifiedFile)) {
        const notified = JSON.parse(fs.readFileSync(notifiedFile, 'utf8'));
        console.log(`   已通知邮件数量: ${notified.notifiedIds.length}`);
      }
    } else {
      console.log('3. 没有新邮件，检查缓存...');
      
      const fs = require('fs');
      const path = require('path');
      
      const cacheFile = path.join(__dirname, 'email-monitor-cache.json');
      if (fs.existsSync(cacheFile)) {
        const cache = JSON.parse(fs.readFileSync(cacheFile, 'utf8'));
        console.log(`   最后检查时间: ${cache.lastCheck}`);
        console.log(`   最后UID: ${cache.lastUid}`);
      }
    }
    
    console.log('\n='.repeat(50));
    console.log('✅ 测试完成！');
    
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    console.error('错误详情:', error.stack);
  }
}

// 运行测试
if (require.main === module) {
  test();
}

module.exports = test;