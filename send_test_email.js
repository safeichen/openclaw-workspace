const nodemailer = require('nodemailer');
require('dotenv').config({ path: '/root/.openclaw/workspace/skills/imap-smtp-email/.env' });

async function sendTestEmail() {
    console.log('开始发送测试邮件...');
    
    // 创建SMTP传输器
    const transporter = nodemailer.createTransport({
        host: process.env.SMTP_HOST || 'smtp.qq.com',
        port: parseInt(process.env.SMTP_PORT) || 587,
        secure: process.env.SMTP_SECURE === 'true',
        auth: {
            user: process.env.SMTP_USER,
            pass: process.env.SMTP_PASS
        },
        tls: {
            rejectUnauthorized: process.env.SMTP_REJECT_UNAUTHORIZED === 'true'
        }
    });

    // 邮件内容
    const mailOptions = {
        from: process.env.SMTP_FROM || process.env.SMTP_USER,
        to: '573890754@qq.com',
        subject: 'OpenClaw测试邮件',
        text: `这是一封来自OpenClaw的测试邮件。

发送时间: ${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}
发件人: ${process.env.SMTP_USER}
收件人: 573890754@qq.com

OpenClaw系统状态:
- 系统时间: ${new Date().toISOString()}
- 测试目的: 验证邮件发送功能

祝你使用愉快！

OpenClaw助手`,
        html: `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>OpenClaw测试邮件</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #4CAF50; color: white; padding: 10px; text-align: center; border-radius: 5px; }
        .content { background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin-top: 20px; }
        .footer { margin-top: 20px; text-align: center; color: #666; font-size: 12px; }
        .info { background-color: #e8f5e9; padding: 10px; border-left: 4px solid #4CAF50; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📧 OpenClaw测试邮件</h1>
        </div>
        
        <div class="content">
            <p>这是一封来自OpenClaw的测试邮件。</p>
            
            <div class="info">
                <p><strong>发送时间:</strong> ${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}</p>
                <p><strong>发件人:</strong> ${process.env.SMTP_USER}</p>
                <p><strong>收件人:</strong> 573890754@qq.com</p>
            </div>
            
            <h3>OpenClaw系统状态:</h3>
            <ul>
                <li>系统时间: ${new Date().toISOString()}</li>
                <li>测试目的: 验证邮件发送功能</li>
                <li>状态: ✅ 邮件发送测试中</li>
            </ul>
            
            <p>祝你使用愉快！</p>
            <p><strong>OpenClaw助手</strong></p>
        </div>
        
        <div class="footer">
            <p>此邮件为自动发送的测试邮件，请勿回复。</p>
            <p>OpenClaw - 个人AI助手系统</p>
        </div>
    </div>
</body>
</html>`
    };

    try {
        console.log('正在连接SMTP服务器...');
        console.log('服务器:', process.env.SMTP_HOST);
        console.log('端口:', process.env.SMTP_PORT);
        console.log('发件人:', process.env.SMTP_USER);
        
        // 验证连接
        await transporter.verify();
        console.log('✅ SMTP服务器连接成功');
        
        // 发送邮件
        console.log('正在发送邮件...');
        const info = await transporter.sendMail(mailOptions);
        
        console.log('✅ 邮件发送成功！');
        console.log('邮件ID:', info.messageId);
        console.log('响应:', info.response);
        
        return {
            success: true,
            messageId: info.messageId,
            response: info.response
        };
        
    } catch (error) {
        console.error('❌ 邮件发送失败:');
        console.error('错误信息:', error.message);
        
        if (error.code) {
            console.error('错误代码:', error.code);
        }
        
        if (error.command) {
            console.error('SMTP命令:', error.command);
        }
        
        return {
            success: false,
            error: error.message,
            code: error.code
        };
    }
}

// 执行发送
sendTestEmail().then(result => {
    if (result.success) {
        console.log('\n🎉 测试邮件已成功发送到 573890754@qq.com');
        console.log('请检查收件箱（包括垃圾邮件文件夹）');
        process.exit(0);
    } else {
        console.log('\n❌ 邮件发送失败');
        process.exit(1);
    }
}).catch(error => {
    console.error('未预期的错误:', error);
    process.exit(1);
});