const nodemailer = require('nodemailer');

const sendEmail = async (options) => {
    // If no mail credentials, log to console (Development Mode)
    if (!process.env.MAIL_USERNAME || process.env.MAIL_USERNAME === 'replace_me') {
        console.log('---------------------------------------------------');
        console.log('EMAIL SIMULATION (No credentials provided)');
        console.log(`To: ${options.email}`);
        console.log(`Subject: ${options.subject}`);
        console.log(`Message: ${options.message}`);
        console.log('---------------------------------------------------');
        return;
    }

    const transporter = nodemailer.createTransport({
        host: process.env.MAIL_SERVER || 'smtp.gmail.com',
        port: process.env.MAIL_PORT || 587,
        secure: false, // true for 465, false for other ports
        auth: {
            user: process.env.MAIL_USERNAME,
            pass: process.env.MAIL_PASSWORD
        }
    });

    const message = {
        from: `${process.env.FROM_NAME || 'CRM App'} <${process.env.FROM_EMAIL || process.env.MAIL_USERNAME}>`,
        to: options.email,
        subject: options.subject,
        text: options.message,
        html: options.html
    };

    try {
        const info = await transporter.sendMail(message);
        console.log('Message sent: %s', info.messageId);
    } catch (error) {
        console.error('Error sending email:', error);
        // Don't throw error to avoid breaking the flow, just log it. 
        // In production you might want to handle this differently.
    }
};

module.exports = sendEmail;
