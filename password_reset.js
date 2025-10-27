/**
 * Password Reset System for Confident Picks
 * Handles password reset requests and token validation
 */

const crypto = require('crypto');
const { sendPasswordResetEmail } = require('./send_email');

// In-memory storage for reset tokens (in production, use Firebase/database)
// Format: { email: { token: 'xxx', expires: timestamp, used: false } }
const resetTokens = new Map();

// Token expiration time (1 hour)
const TOKEN_EXPIRY = 60 * 60 * 1000; // 1 hour in milliseconds

/**
 * Generate a secure random token
 */
function generateToken() {
    return crypto.randomBytes(32).toString('hex');
}

/**
 * Request password reset - generates token and sends email
 * @param {string} email - User's email address
 * @param {string} userName - User's display name
 * @returns {Promise<object>} - Result object
 */
async function requestPasswordReset(email, userName) {
    try {
        // Generate secure token
        const token = generateToken();
        const expires = Date.now() + TOKEN_EXPIRY;
        
        // Store token
        resetTokens.set(email, {
            token: token,
            expires: expires,
            used: false,
            createdAt: Date.now()
        });
        
        // Create reset link
        const resetLink = `https://confident-picks.com/reset-password.html?token=${token}&email=${encodeURIComponent(email)}`;
        
        // Send email
        await sendPasswordResetEmail(email, userName, resetLink);
        
        console.log(`✅ Password reset email sent to ${email}`);
        console.log(`🔑 Token: ${token} (expires in 1 hour)`);
        
        return {
            success: true,
            message: 'Password reset email sent',
            expiresIn: '1 hour'
        };
        
    } catch (error) {
        console.error('❌ Error sending password reset email:', error);
        throw error;
    }
}

/**
 * Validate reset token
 * @param {string} email - User's email address
 * @param {string} token - Reset token
 * @returns {object} - Validation result
 */
function validateResetToken(email, token) {
    const storedToken = resetTokens.get(email);
    
    if (!storedToken) {
        return {
            valid: false,
            error: 'No reset request found for this email'
        };
    }
    
    if (storedToken.token !== token) {
        return {
            valid: false,
            error: 'Invalid reset token'
        };
    }
    
    if (storedToken.used) {
        return {
            valid: false,
            error: 'This reset link has already been used'
        };
    }
    
    if (Date.now() > storedToken.expires) {
        return {
            valid: false,
            error: 'This reset link has expired. Please request a new one.'
        };
    }
    
    return {
        valid: true,
        message: 'Token is valid'
    };
}

/**
 * Mark token as used
 * @param {string} email - User's email address
 */
function markTokenAsUsed(email) {
    const storedToken = resetTokens.get(email);
    if (storedToken) {
        storedToken.used = true;
        resetTokens.set(email, storedToken);
    }
}

/**
 * Clean up expired tokens (run periodically)
 */
function cleanupExpiredTokens() {
    const now = Date.now();
    let cleaned = 0;
    
    for (const [email, tokenData] of resetTokens.entries()) {
        if (now > tokenData.expires || tokenData.used) {
            resetTokens.delete(email);
            cleaned++;
        }
    }
    
    if (cleaned > 0) {
        console.log(`🧹 Cleaned up ${cleaned} expired/used reset tokens`);
    }
}

// Cleanup function available for manual/scheduled use
// In production, run this as a scheduled task (e.g., cron job)
// setInterval(cleanupExpiredTokens, 15 * 60 * 1000);

/**
 * Test function - request password reset
 */
async function testPasswordReset(email, userName) {
    console.log('🧪 Testing password reset flow...');
    console.log(`📧 Email: ${email}`);
    console.log(`👤 Name: ${userName}`);
    console.log('');
    
    try {
        const result = await requestPasswordReset(email, userName);
        console.log('✅ Test successful!');
        console.log('Result:', result);
        console.log('');
        console.log('📬 Check your email for the reset link');
        console.log('');
        
        // Show stored token for testing
        const storedToken = resetTokens.get(email);
        if (storedToken) {
            console.log('🔑 Token Details:');
            console.log(`   Token: ${storedToken.token}`);
            console.log(`   Expires: ${new Date(storedToken.expires).toLocaleString()}`);
            console.log(`   Used: ${storedToken.used}`);
        }
        
        return result;
    } catch (error) {
        console.error('❌ Test failed:', error.message);
        throw error;
    }
}

module.exports = {
    requestPasswordReset,
    validateResetToken,
    markTokenAsUsed,
    cleanupExpiredTokens,
    testPasswordReset
};

