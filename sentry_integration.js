/**
 * Sentry Error Monitoring Integration
 * Catches and reports all JavaScript errors in production
 */

// Sentry Configuration
const SENTRY_DSN = 'YOUR_SENTRY_DSN_HERE'; // Replace with actual DSN
const ENVIRONMENT = 'production'; // or 'development', 'staging'

/**
 * Initialize Sentry
 * Add this to the <head> of index.html
 */
function initializeSentry() {
    // Load Sentry SDK
    const script = document.createElement('script');
    script.src = 'https://browser.sentry-cdn.com/7.80.0/bundle.min.js';
    script.integrity = 'sha384-example'; // Will be provided by Sentry
    script.crossOrigin = 'anonymous';
    
    script.onload = function() {
        if (typeof Sentry !== 'undefined') {
            Sentry.init({
                dsn: SENTRY_DSN,
                environment: ENVIRONMENT,
                
                // Performance Monitoring
                integrations: [
                    new Sentry.BrowserTracing(),
                    new Sentry.Replay({
                        maskAllText: true,
                        blockAllMedia: true,
                    }),
                ],
                
                // Set tracesSampleRate to 1.0 to capture 100% of transactions
                // We recommend adjusting this value in production
                tracesSampleRate: 1.0,
                
                // Capture Replay for 10% of all sessions,
                // plus 100% of sessions with an error
                replaysSessionSampleRate: 0.1,
                replaysOnErrorSampleRate: 1.0,
                
                // Filter out sensitive data
                beforeSend(event, hint) {
                    // Don't send events in development
                    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                        return null;
                    }
                    
                    // Filter out sensitive data from error messages
                    if (event.message) {
                        event.message = event.message.replace(/password=\w+/gi, 'password=***');
                        event.message = event.message.replace(/token=\w+/gi, 'token=***');
                        event.message = event.message.replace(/api[_-]?key=\w+/gi, 'apikey=***');
                    }
                    
                    return event;
                },
                
                // Ignore certain errors
                ignoreErrors: [
                    // Browser extensions
                    'top.GLOBALS',
                    'originalCreateNotification',
                    'canvas.contentDocument',
                    'MyApp_RemoveAllHighlights',
                    'atomicFindClose',
                    // Network errors
                    'NetworkError',
                    'Network request failed',
                    // Random plugins/extensions
                    'Can\'t find variable: ZiteReader',
                    'jigsaw is not defined',
                    'ComboSearch is not defined',
                    // Facebook blocked
                    'fb_xd_fragment',
                    // ISP injected ads
                    'bmi_SafeAddOnload',
                    'EBCallBackMessageReceived',
                ],
            });
            
            console.log('✅ Sentry initialized');
            
            // Set user context when user signs in
            if (window.auth && window.auth.currentUser) {
                Sentry.setUser({
                    id: window.auth.currentUser.uid,
                    email: window.auth.currentUser.email,
                });
            }
        }
    };
    
    document.head.appendChild(script);
}

/**
 * Manually capture an error
 */
function captureError(error, context = {}) {
    if (typeof Sentry !== 'undefined') {
        Sentry.captureException(error, {
            extra: context
        });
    } else {
        console.error('Sentry not loaded:', error);
    }
}

/**
 * Capture a message (not an error)
 */
function captureMessage(message, level = 'info') {
    if (typeof Sentry !== 'undefined') {
        Sentry.captureMessage(message, level);
    }
}

/**
 * Set user context
 */
function setUser(userId, email) {
    if (typeof Sentry !== 'undefined') {
        Sentry.setUser({
            id: userId,
            email: email,
        });
    }
}

/**
 * Clear user context (on logout)
 */
function clearUser() {
    if (typeof Sentry !== 'undefined') {
        Sentry.setUser(null);
    }
}

/**
 * Add breadcrumb (track user actions)
 */
function addBreadcrumb(message, category = 'user-action', data = {}) {
    if (typeof Sentry !== 'undefined') {
        Sentry.addBreadcrumb({
            message: message,
            category: category,
            level: 'info',
            data: data,
        });
    }
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeSentry,
        captureError,
        captureMessage,
        setUser,
        clearUser,
        addBreadcrumb,
    };
}

