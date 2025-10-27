#!/usr/bin/env node
/**
 * Test Password Reset Flow
 * Usage: node test_password_reset.js your-email@example.com "Your Name"
 */

const { testPasswordReset } = require('./password_reset');

// Get email and name from command line
const email = process.argv[2];
const userName = process.argv[3] || 'User';

if (!email) {
    console.error('❌ Error: Please provide an email address');
    console.log('Usage: node test_password_reset.js your-email@example.com "Your Name"');
    process.exit(1);
}

// Validate email format
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailRegex.test(email)) {
    console.error('❌ Error: Invalid email format');
    process.exit(1);
}

console.log('🔑 Testing Password Reset Flow');
console.log('================================');
console.log('');

testPasswordReset(email, userName)
    .then(() => {
        console.log('');
        console.log('✅ Password reset test completed!');
        console.log('');
        console.log('What to do next:');
        console.log('1. Check your email for the reset link');
        console.log('2. Click the link to open reset-password.html');
        console.log('3. Enter a new password');
        console.log('4. Verify the password is updated in Firebase');
    })
    .catch((error) => {
        console.log('');
        console.error('❌ Test failed:', error.message);
        process.exit(1);
    });

