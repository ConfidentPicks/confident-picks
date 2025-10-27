/**
 * Utility functions for the automation system
 * Common helper functions used across the application
 */

import { THRESHOLDS, QUALITY_CONTROL } from '../config/thresholds.js';

/**
 * Sleep/delay function
 * @param {number} ms - Milliseconds to sleep
 */
export function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Retry function with exponential backoff
 * @param {Function} fn - Function to retry
 * @param {number} maxRetries - Maximum number of retries
 * @param {number} baseDelay - Base delay in milliseconds
 */
export async function retryWithBackoff(fn, maxRetries = THRESHOLDS.max_retry_attempts, baseDelay = THRESHOLDS.retry_delay_ms) {
  let lastError;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      if (attempt === maxRetries) {
        throw error;
      }
      
      const delay = baseDelay * Math.pow(2, attempt);
      console.log(`⚠️ Attempt ${attempt + 1} failed, retrying in ${delay}ms...`);
      await sleep(delay);
    }
  }
  
  throw lastError;
}

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} Is valid email
 */
export function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Format date for display
 * @param {Date} date - Date to format
 * @param {string} format - Format type ('short', 'long', 'iso')
 * @returns {string} Formatted date
 */
export function formatDate(date, format = 'short') {
  const d = new Date(date);
  
  switch (format) {
    case 'short':
      return d.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
      });
    case 'long':
      return d.toLocaleDateString('en-US', { 
        weekday: 'long',
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    case 'iso':
      return d.toISOString();
    case 'time':
      return d.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    default:
      return d.toString();
  }
}

/**
 * Format currency
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency code
 * @returns {string} Formatted currency
 */
export function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
}

/**
 * Calculate percentage
 * @param {number} value - Value
 * @param {number} total - Total
 * @param {number} decimals - Decimal places
 * @returns {number} Percentage
 */
export function calculatePercentage(value, total, decimals = 2) {
  if (total === 0) return 0;
  return Math.round((value / total) * 100 * Math.pow(10, decimals)) / Math.pow(10, decimals);
}

/**
 * Generate unique ID
 * @param {string} prefix - ID prefix
 * @returns {string} Unique ID
 */
export function generateId(prefix = '') {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substr(2, 5);
  return prefix ? `${prefix}_${timestamp}_${random}` : `${timestamp}_${random}`;
}

/**
 * Sanitize string for logging
 * @param {string} str - String to sanitize
 * @returns {string} Sanitized string
 */
export function sanitizeForLog(str) {
  if (typeof str !== 'string') return str;
  
  // Remove sensitive information
  return str
    .replace(/api[_-]?key[=:]\s*[^\s&]+/gi, 'api_key=***')
    .replace(/token[=:]\s*[^\s&]+/gi, 'token=***')
    .replace(/password[=:]\s*[^\s&]+/gi, 'password=***')
    .replace(/secret[=:]\s*[^\s&]+/gi, 'secret=***');
}

/**
 * Deep clone object
 * @param {Object} obj - Object to clone
 * @returns {Object} Cloned object
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof Array) return obj.map(item => deepClone(item));
  if (typeof obj === 'object') {
    const cloned = {};
    Object.keys(obj).forEach(key => {
      cloned[key] = deepClone(obj[key]);
    });
    return cloned;
  }
}

/**
 * Merge objects deeply
 * @param {Object} target - Target object
 * @param {Object} source - Source object
 * @returns {Object} Merged object
 */
export function deepMerge(target, source) {
  const result = deepClone(target);
  
  for (const key in source) {
    if (source.hasOwnProperty(key)) {
      if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
        result[key] = deepMerge(result[key] || {}, source[key]);
      } else {
        result[key] = source[key];
      }
    }
  }
  
  return result;
}

/**
 * Validate pick data structure
 * @param {Object} pick - Pick object to validate
 * @returns {Object} Validation result
 */
export function validatePick(pick) {
  const errors = [];
  const warnings = [];
  
  // Required fields
  if (!pick.gameId) errors.push('Missing gameId');
  if (!pick.prediction) errors.push('Missing prediction');
  if (!pick.confidence) errors.push('Missing confidence');
  if (!pick.sport) errors.push('Missing sport');
  
  // Confidence validation
  if (pick.confidence && (pick.confidence < 0 || pick.confidence > 100)) {
    errors.push('Confidence must be between 0 and 100');
  }
  
  // Market validation
  const validMarkets = ['spread', 'totals', 'moneyline', 'props', 'player_props', 'sgp'];
  if (pick.market && !validMarkets.includes(pick.market)) {
    warnings.push(`Unknown market type: ${pick.market}`);
  }
  
  // Reasoning validation
  if (!pick.reasoning || !pick.reasoning.primary) {
    warnings.push('Missing primary reasoning');
  }
  
  // Odds validation
  if (pick.odds && (typeof pick.odds !== 'number' || pick.odds === 0)) {
    warnings.push('Invalid odds value');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    warnings,
    score: Math.max(0, 100 - (errors.length * 20) - (warnings.length * 5))
  };
}

/**
 * Calculate standard deviation
 * @param {Array} values - Array of numbers
 * @returns {number} Standard deviation
 */
export function calculateStandardDeviation(values) {
  if (values.length === 0) return 0;
  
  const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
  const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
  
  return Math.sqrt(variance);
}

/**
 * Detect outliers using standard deviation
 * @param {Array} values - Array of numbers
 * @param {number} threshold - Standard deviation threshold
 * @returns {Array} Array of outlier indices
 */
export function detectOutliers(values, threshold = THRESHOLDS.outlier_std_dev) {
  if (values.length < 3) return [];
  
  const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
  const stdDev = calculateStandardDeviation(values);
  
  return values
    .map((value, index) => ({ value, index }))
    .filter(item => Math.abs(item.value - mean) > (threshold * stdDev))
    .map(item => item.index);
}

/**
 * Format confidence score for display
 * @param {number} confidence - Confidence score (0-100)
 * @returns {string} Formatted confidence
 */
export function formatConfidence(confidence) {
  if (confidence >= 90) return `${confidence}% (Excellent)`;
  if (confidence >= 80) return `${confidence}% (Strong)`;
  if (confidence >= 70) return `${confidence}% (Good)`;
  if (confidence >= 60) return `${confidence}% (Fair)`;
  return `${confidence}% (Weak)`;
}

/**
 * Get confidence color for UI
 * @param {number} confidence - Confidence score (0-100)
 * @returns {string} CSS color class
 */
export function getConfidenceColor(confidence) {
  if (confidence >= 80) return 'excellent';
  if (confidence >= 70) return 'strong';
  if (confidence >= 60) return 'good';
  if (confidence >= 50) return 'fair';
  return 'weak';
}

/**
 * Parse odds string to number
 * @param {string|number} odds - Odds value
 * @returns {number} Parsed odds
 */
export function parseOdds(odds) {
  if (typeof odds === 'number') return odds;
  if (typeof odds === 'string') {
    const cleaned = odds.replace(/[^\d.-]/g, '');
    const parsed = parseFloat(cleaned);
    return isNaN(parsed) ? -110 : parsed;
  }
  return -110;
}

/**
 * Convert odds to probability
 * @param {number} odds - American odds
 * @returns {number} Probability (0-1)
 */
export function oddsToProbability(odds) {
  if (odds > 0) {
    return 100 / (odds + 100);
  } else {
    return Math.abs(odds) / (Math.abs(odds) + 100);
  }
}

/**
 * Convert probability to odds
 * @param {number} probability - Probability (0-1)
 * @returns {number} American odds
 */
export function probabilityToOdds(probability) {
  if (probability >= 0.5) {
    return -((probability * 100) / (1 - probability));
  } else {
    return ((1 - probability) * 100) / probability;
  }
}

/**
 * Calculate expected value
 * @param {number} probability - Win probability (0-1)
 * @param {number} odds - American odds
 * @param {number} stake - Bet amount
 * @returns {number} Expected value
 */
export function calculateExpectedValue(probability, odds, stake = 100) {
  const winAmount = odds > 0 ? (odds / 100) * stake : (100 / Math.abs(odds)) * stake;
  const expectedValue = (probability * winAmount) - ((1 - probability) * stake);
  return expectedValue;
}

/**
 * Log with timestamp
 * @param {string} level - Log level
 * @param {string} message - Log message
 * @param {Object} data - Additional data
 */
export function logWithTimestamp(level, message, data = {}) {
  const timestamp = new Date().toISOString();
  const sanitizedData = sanitizeForLog(JSON.stringify(data));
  
  console.log(`[${timestamp}] ${level.toUpperCase()}: ${message}`, 
    sanitizedData !== '{}' ? sanitizedData : ''
  );
}

/**
 * Create error object with context
 * @param {string} message - Error message
 * @param {string} context - Error context
 * @param {Object} details - Additional details
 * @returns {Object} Error object
 */
export function createError(message, context, details = {}) {
  return {
    message,
    context,
    details,
    timestamp: new Date().toISOString(),
    id: generateId('error')
  };
}

