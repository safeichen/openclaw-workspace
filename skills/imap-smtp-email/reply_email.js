#!/usr/bin/env node
/**
 * 邮件回复工具
 * 用法: node reply_email.js <邮件UID> --body "回复内容" [选项]
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 解析命令行参数
const args = process.argv.slice(2);
let targetUid = null;
let replyBody = '';
let includeOriginal = false;
let addCc = [];
let addBcc = [];

for (let i = 0; i < args.length; i++) {
  const arg = args[i];
  
  if (arg === '--body' && args[i + 1]) {
    replyBody = args[i + 1];
    i++;
  } else if (arg === '--include-original') {
    includeOriginal = true;
  } else if (arg === '--cc' && args[i + 1]) {
    addCc = args[i + 1].split(',');
    i++;
  } else if (arg === '--bcc' && args[i + 1]) {
    addBcc = args[i + 1].split(',');
    i++;
  } else if (arg === '--help' || arg === '-h') {
    showHelp();
    process.exit(0);
  } else if (!targetUid && /^\d+$/.test(arg)) {
    targetUid = arg;
  }
}

if (!targetUid || !replyBody) {
  console.error('❌ 错误: 需要邮件UID和回复内容');
  console.error('用法: node reply_email.js <邮件UID> --body "回复内容"');
  console.error('示例: node reply_email.js 12345 --body "收到，谢谢！"');
  process.exit(1);
}

// 显示帮助
function showHelp() {
  console.log(`
📧 邮件回复工具

用法:
  node reply_email.js <邮件UID> --body "回复内容" [选项]

选项:
  --body <内容>          回复内容 (必需)
  --include-original     包含原邮件内容
  --cc <邮箱1,邮箱2>     抄送
  --bcc <邮箱1,邮箱2>    密送
  --help, -h            显示帮助

示例:
  # 简单回复
  node reply_email.js 12345 --body "收到，谢谢！"

  # 包含原邮件内容的回复
  node reply_email.js 12345 --body "我的回复如下：" --include-original

  # 带抄送的回复
  node reply_email.js 12345 --body "请查收" --cc "manager@example.com"
  `);
}

// 获取邮件信息
function getEmailInfo(uid) {
  try {
    console.log(`📨 获取邮件 ${uid} 的信息...`);
    
    // 使用imap.js获取邮件详情
    const result = execSync(`node scripts/imap.js fetch ${uid} --json`, {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    return JSON.parse(result);
  } catch (error) {
    console.error(`❌ 获取邮件信息失败: ${error.message}`);
    if (error.stderr) {
      console.error(error.stderr.toString());
    }
    process.exit(1);
  }
}

// 构建回复内容
function buildReplyContent(originalEmail, replyBody, includeOriginal) {
  let content = replyBody;
  
  if (includeOriginal && originalEmail) {
    content += '\n\n--- 原邮件内容 ---\n';
    content += `发件人: ${originalEmail.from}\n`;
    content += `时间: ${originalEmail.date}\n`;
    content += `主题: ${originalEmail.subject}\n`;
    content += `\n${originalEmail.text || originalEmail.body || ''}`;
  }
  
  return content;
}

// 构建回复主题
function buildReplySubject(originalSubject) {
  if (!originalSubject) return '回复';
  
  // 如果主题已经以 "Re:" 开头，不再重复添加
  if (originalSubject.toLowerCase().startsWith('re:')) {
    return originalSubject;
  }
  
  return `Re: ${originalSubject}`;
}

// 发送回复
function sendReply(emailInfo, replyBody, includeOriginal, cc, bcc) {
  const replyTo = emailInfo.from;
  const replySubject = buildReplySubject(emailInfo.subject);
  const replyContent = buildReplyContent(emailInfo, replyBody, includeOriginal);
  
  console.log(`📤 准备回复邮件给: ${replyTo}`);
  console.log(`主题: ${replySubject}`);
  console.log(`内容长度: ${replyContent.length} 字符`);
  
  if (cc.length > 0) {
    console.log(`抄送: ${cc.join(', ')}`);
  }
  
  if (bcc.length > 0) {
    console.log(`密送: ${bcc.join(', ')}`);
  }
  
  // 构建命令
  let command = `node scripts/smtp.js send --to "${replyTo}" --subject "${replySubject}" --body "${replyContent.replace(/"/g, '\\"')}"`;
  
  if (cc.length > 0) {
    command += ` --cc "${cc.join(',')}"`;
  }
  
  if (bcc.length > 0) {
    command += ` --bcc "${bcc.join(',')}"`;
  }
  
  try {
    console.log('\n🚀 发送回复...');
    const result = execSync(command, {
      encoding: 'utf-8',
      stdio: 'inherit'
    });
    
    console.log('\n✅ 回复已发送！');
    console.log(`📧 收件人: ${replyTo}`);
    console.log(`📝 主题: ${replySubject}`);
    
    // 可选：标记原邮件为已读
    console.log('\n📌 是否标记原邮件为已读？ (y/n)');
    const readline = require('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    rl.question('> ', (answer) => {
      if (answer.toLowerCase() === 'y') {
        try {
          execSync(`node scripts/imap.js mark-read ${targetUid}`, {
            encoding: 'utf-8',
            stdio: 'inherit'
          });
          console.log('✅ 原邮件已标记为已读');
        } catch (error) {
          console.log('⚠️  标记已读失败，但回复已发送');
        }
      }
      rl.close();
    });
    
  } catch (error) {
    console.error(`❌ 发送回复失败: ${error.message}`);
    if (error.stderr) {
      console.error(error.stderr.toString());
    }
    process.exit(1);
  }
}

// 主函数
async function main() {
  console.log('📧 邮件回复工具');
  console.log('=' .repeat(50));
  
  // 获取原邮件信息
  const emailInfo = getEmailInfo(targetUid);
  
  if (!emailInfo.from) {
    console.error('❌ 无法获取发件人信息');
    process.exit(1);
  }
  
  console.log(`📨 原邮件信息:`);
  console.log(`   发件人: ${emailInfo.from}`);
  console.log(`   主题: ${emailInfo.subject}`);
  console.log(`   时间: ${emailInfo.date}`);
  console.log(`   大小: ${emailInfo.size || '未知'} 字节`);
  
  // 发送回复
  sendReply(emailInfo, replyBody, includeOriginal, addCc, addBcc);
}

// 运行主函数
main().catch(error => {
  console.error('❌ 程序错误:', error);
  process.exit(1);
});