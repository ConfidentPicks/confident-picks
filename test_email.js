#!/usr/bin/env node
/**
 * Test SendGrid Email Integration
 * Usage: node test_email.js your-email@example.com
 */

const { testEmail } = require('./send_email');

// Get email from command line argument
const testEmailAddress = process.argv[2];

if (!testEmailAddress) {
    console.error('❌ Error: Please provide an email address');
    console.log('Usage: node test_email.js your-email@example.com');
    process.exit(1);
}

// Validate email format
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailRegex.test(testEmailAddress)) {
    console.error('❌ Error: Invalid email format');
    process.exit(1);
}

console.log('📧 Testing SendGrid email integration...');
console.log(`📬 Sending test email to: ${testEmailAddress}`);
console.log('');

testEmail(testEmailAddress)
    .then((result) => {
        console.log('');
        console.log('✅ SUCCESS! Email sent successfully!');
        console.log(`📊 Status Code: ${result.statusCode}`);
        console.log('');
        console.log('📬 Check your inbox (and spam folder) for the test email.');
        console.log('');
        console.log('Next steps:');
        console.log('1. ✅ Email system is working!');
        console.log('2. Update email_templates.js with your branding');
        console.log('3. Integrate with Firebase Authentication');
        console.log('4. Set up password reset flow');
    })
    .catch((error) => {
        console.log('');
        console.error('❌ FAILED! Email could not be sent.');
        console.error('');
        console.error('Error details:', error.message);
        console.error('');
        console.log('Troubleshooting:');
        console.log('1. Check your SendGrid API key is correct');
        console.log('2. Ensure SENDGRID_API_KEY environment variable is set');
        console.log('3. Verify API key has Full Access permissions');
        console.log('4. Check SendGrid Activity Feed for more details');
        console.log('');
        console.log('Set API key:');
        console.log('  Windows (PowerShell): $env:SENDGRID_API_KEY="YOUR_KEY"');
        console.log('  Windows (CMD): set SENDGRID_API_KEY=YOUR_KEY');
        process.exit(1);
    });

