#!/usr/bin/env node

/**
 * 邮件监控脚本 - 检查新邮件并推送通知
 * 支持缓存机制，避免重复通知
 */

const Imap = require('imap');
const { simpleParser } = require('mailparser');
const path = require('path');
const fs = require('fs');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

// 缓存文件路径
const CACHE_FILE = path.join(__dirname, 'email-monitor-cache.json');
const NOTIFIED_FILE = path.join(__dirname, 'email-notified.json');

// 默认配置
const DEFAULT_CONFIG = {
  user: process.env.IMAP_USER || process.env.SMTP_USER,
  password: process.env.IMAP_PASS || process.env.SMTP_PASS,
  host: process.env.IMAP_HOST || 'imap.qq.com',
  port: process.env.IMAP_PORT || 993,
  tls: true,
  tlsOptions: { 
    rejectUnauthorized: process.env.IMAP_REJECT_UNAUTHORIZED === 'true' || false 
  },
  authTimeout: 10000
};

// 加载缓存
function loadCache() {
  try {
    if (fs.existsSync(CACHE_FILE)) {
      return JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8'));
    }
  } catch (err) {
    console.error('加载缓存失败:', err.message);
  }
  return { lastCheck: null, lastUid: 0 };
}

// 保存缓存
function saveCache(cache) {
  try {
    fs.writeFileSync(CACHE_FILE, JSON.stringify(cache, null, 2));
  } catch (err) {
    console.error('保存缓存失败:', err.message);
  }
}

// 加载已通知的邮件ID
function loadNotified() {
  try {
    if (fs.existsSync(NOTIFIED_FILE)) {
      return JSON.parse(fs.readFileSync(NOTIFIED_FILE, 'utf8'));
    }
  } catch (err) {
    console.error('加载已通知列表失败:', err.message);
  }
  return { notifiedIds: [], notifiedTimes: {} };
}

// 保存已通知的邮件ID
function saveNotified(notified) {
  try {
    // 清理旧记录：只保留最近24小时内的通知记录
    const twentyFourHoursAgo = Date.now() - (24 * 60 * 60 * 1000);
    
    // 清理notifiedTimes中的旧记录
    Object.keys(notified.notifiedTimes).forEach(uid => {
      if (notified.notifiedTimes[uid] < twentyFourHoursAgo) {
        delete notified.notifiedTimes[uid];
      }
    });
    
    // 同步清理notifiedIds
    notified.notifiedIds = notified.notifiedIds.filter(uid => 
      notified.notifiedTimes[uid] && notified.notifiedTimes[uid] >= twentyFourHoursAgo
    );
    
    fs.writeFileSync(NOTIFIED_FILE, JSON.stringify(notified, null, 2));
  } catch (err) {
    console.error('保存已通知列表失败:', err.message);
  }
}

// 检查新邮件
async function checkNewEmails() {
  return new Promise((resolve, reject) => {
    const imap = new Imap(DEFAULT_CONFIG);
    const cache = loadCache();
    const notified = loadNotified();
    const newEmails = [];
    
    imap.once('ready', () => {
      imap.openBox('INBOX', true, (err, box) => {
        if (err) {
          imap.end();
          reject(err);
          return;
        }
        
        // 搜索条件：只搜索自上次检查以来的未读邮件
        const searchCriteria = ['UNSEEN'];
        if (cache.lastCheck) {
          // 使用SINCE条件，只检查自上次检查以来的邮件
          searchCriteria.push(['SINCE', cache.lastCheck]);
        } else {
          // 如果是第一次运行，只检查最近1小时内的邮件，避免推送大量旧邮件
          const oneHourAgo = new Date();
          oneHourAgo.setHours(oneHourAgo.getHours() - 1);
          searchCriteria.push(['SINCE', oneHourAgo]);
        }
        
        imap.search(searchCriteria, (err, results) => {
          if (err) {
            imap.end();
            reject(err);
            return;
          }
          
          if (results.length === 0) {
            imap.end();
            cache.lastCheck = new Date();
            saveCache(cache);
            resolve([]);
            return;
          }
          
          // 过滤掉已经通知过的邮件
          const newResults = results.filter(uid => !notified.notifiedIds.includes(uid));
          
          if (newResults.length === 0) {
            imap.end();
            cache.lastCheck = new Date();
            saveCache(cache);
            resolve([]);
            return;
          }
          
          // 获取最新邮件的详细信息
          const f = imap.fetch(newResults, { 
            bodies: ['HEADER.FIELDS (FROM TO SUBJECT DATE)', 'TEXT'],
            struct: true 
          });
          
          f.on('message', (msg, seqno) => {
            let uid = newResults[seqno - 1];
            let headers = '';
            let text = '';
            
            msg.on('body', (stream, info) => {
              let buffer = '';
              stream.on('data', (chunk) => {
                buffer += chunk.toString('utf8');
              });
              
              stream.once('end', () => {
                if (info.which === 'TEXT') {
                  text = buffer;
                } else {
                  headers = buffer;
                }
              });
            });
            
            msg.once('attributes', (attrs) => {
              // 从属性中获取邮件UID
              if (attrs.uid) {
                uid = attrs.uid;
              }
            });
            
            msg.once('end', () => {
              // 解析邮件头
              const headerLines = headers.split('\r\n');
              const emailInfo = {
                uid: uid,
                from: '',
                to: '',
                subject: '',
                date: '',
                snippet: ''
              };
              
              for (const line of headerLines) {
                if (line.toLowerCase().startsWith('from:')) {
                  emailInfo.from = line.substring(5).trim();
                } else if (line.toLowerCase().startsWith('to:')) {
                  emailInfo.to = line.substring(3).trim();
                } else if (line.toLowerCase().startsWith('subject:')) {
                  emailInfo.subject = line.substring(8).trim();
                } else if (line.toLowerCase().startsWith('date:')) {
                  emailInfo.date = line.substring(5).trim();
                }
              }
              
              // 生成内容摘要（前200字符）
              emailInfo.snippet = text.substring(0, 200).replace(/\s+/g, ' ').trim();
              if (text.length > 200) {
                emailInfo.snippet += '...';
              }
              
              newEmails.push(emailInfo);
              notified.notifiedIds.push(uid);
              notified.notifiedTimes[uid] = Date.now();
            });
          });
          
          f.once('end', () => {
            imap.end();
            cache.lastCheck = new Date();
            cache.lastUid = Math.max(...newResults);
            saveCache(cache);
            saveNotified(notified);
            resolve(newEmails);
          });
        });
      });
    });
    
    imap.once('error', (err) => {
      console.error('IMAP错误:', err);
      reject(err);
    });
    
    imap.connect();
  });
}

// 生成推送消息
function generateNotification(emails) {
  if (emails.length === 0) {
    return null;
  }
  
  let message = `📧 您有 ${emails.length} 封新邮件：\n\n`;
  
  emails.forEach((email, index) => {
    message += `${index + 1}. **${email.subject}**\n`;
    message += `   发件人：${email.from}\n`;
    message += `   时间：${email.date}\n`;
    message += `   摘要：${email.snippet}\n\n`;
  });
  
  return message;
}

// 主函数
async function main() {
  try {
    console.log('开始检查新邮件...');
    const newEmails = await checkNewEmails();
    
    if (newEmails.length > 0) {
      console.log(`发现 ${newEmails.length} 封新邮件`);
      
      // 生成通知消息
      const notification = generateNotification(newEmails);
      
      // 输出到控制台（cron任务会捕获这个输出）
      console.log('=== 新邮件通知 ===');
      console.log(notification);
      console.log('=== 通知结束 ===');
      
      // 返回邮件信息供其他脚本使用
      return {
        hasNew: true,
        count: newEmails.length,
        emails: newEmails,
        notification: notification
      };
    } else {
      console.log('没有新邮件');
      return {
        hasNew: false,
        count: 0,
        emails: []
      };
    }
  } catch (error) {
    console.error('检查邮件失败:', error.message);
    return {
      hasNew: false,
      error: error.message
    };
  }
}

// 如果直接运行此脚本
if (require.main === module) {
  main().then(result => {
    if (result.hasNew) {
      // 退出码1表示有新邮件（cron任务可以检测这个）
      process.exit(1);
    } else {
      process.exit(0);
    }
  }).catch(err => {
    console.error('脚本执行失败:', err);
    process.exit(2);
  });
}

module.exports = { main, checkNewEmails, generateNotification };