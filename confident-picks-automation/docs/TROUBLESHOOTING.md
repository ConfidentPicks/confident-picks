# Troubleshooting Guide

This guide covers common issues and solutions for the Confident Picks automation system.

## 🚨 Critical Issues

### System Not Running

**Symptoms:**
- No picks generated for extended periods
- Health check showing critical status
- All endpoints returning errors

**Diagnosis:**
1. Check Vercel deployment status
2. Verify environment variables
3. Review Firebase connection
4. Check cron job execution

**Solutions:**
```bash
# Check Vercel deployment
vercel logs

# Verify environment variables
vercel env ls

# Test Firebase connection
curl -X GET https://your-app.vercel.app/api/health-check
```

### Firebase Connection Issues

**Symptoms:**
- "Firebase initialization failed" errors
- "Permission denied" errors
- Data not being stored

**Common Causes:**
1. Invalid service account credentials
2. Incorrect project ID
3. Missing permissions
4. Network connectivity issues

**Solutions:**

1. **Verify Service Account**
   ```bash
   # Check if service account file is valid
   cat firebase-service-account.json | jq .
   ```

2. **Test Firebase Connection**
   ```javascript
   // Test script
   const admin = require('firebase-admin');
   const serviceAccount = require('./firebase-service-account.json');
   
   admin.initializeApp({
     credential: admin.credential.cert(serviceAccount)
   });
   
   const db = admin.firestore();
   db.collection('test').doc('test').set({ test: true })
     .then(() => console.log('Firebase working'))
     .catch(err => console.error('Firebase error:', err));
   ```

3. **Check Permissions**
   - Ensure service account has Firestore read/write permissions
   - Verify project ID matches your Firebase project
   - Check if billing is enabled (required for some operations)

### OpenAI API Issues

**Symptoms:**
- "OpenAI API error" messages
- Pick generation failing
- Rate limit exceeded errors

**Common Causes:**
1. Invalid API key
2. Rate limit exceeded
3. Insufficient credits
4. Model access issues

**Solutions:**

1. **Verify API Key**
   ```bash
   # Test API key
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

2. **Check Rate Limits**
   ```bash
   # Check usage
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/usage
   ```

3. **Monitor Costs**
   - Check OpenAI dashboard for usage
   - Set up billing alerts
   - Review token usage patterns

### DraftKings API Issues

**Symptoms:**
- "DraftKings API error" messages
- Data collection failing
- No games data retrieved

**Common Causes:**
1. API endpoint changes
2. Rate limiting
3. Network connectivity
4. Authentication issues

**Solutions:**

1. **Test API Endpoints**
   ```bash
   # Test basic connectivity
   curl -H "User-Agent: Mozilla/5.0" \
        https://sportsbook.draftkings.com/api/v1/health
   ```

2. **Check Rate Limits**
   - Implement proper delays between requests
   - Use exponential backoff
   - Monitor request frequency

3. **Update API Endpoints**
   - Check DraftKings documentation for changes
   - Update GraphQL queries if needed
   - Verify request headers

## ⚠️ Warning Issues

### Data Freshness Problems

**Symptoms:**
- Health check showing "stale data" warnings
- Picks based on old information
- Data collection not running

**Diagnosis:**
1. Check cron job execution logs
2. Verify data collection endpoint
3. Review external API status

**Solutions:**

1. **Check Cron Jobs**
   ```bash
   # View Vercel cron logs
   vercel logs --follow
   ```

2. **Manual Data Collection**
   ```bash
   # Trigger manual data collection
   curl -X POST https://your-app.vercel.app/api/collect-data
   ```

3. **Verify External APIs**
   - Check DraftKings API status
   - Test weather API connectivity
   - Verify injury report sources

### Low Pick Generation

**Symptoms:**
- Fewer picks than expected
- High rejection rates
- Low confidence scores

**Common Causes:**
1. Insufficient data quality
2. High confidence thresholds
3. AI analysis issues
4. Market availability

**Solutions:**

1. **Adjust Confidence Thresholds**
   ```javascript
   // In config/thresholds.js
   export const THRESHOLDS = {
     auto_approve_confidence: 0.65, // Lower from 0.70
     manual_review_confidence: 0.55, // Lower from 0.60
     reject_confidence: 0.45 // Lower from 0.50
   };
   ```

2. **Improve Data Quality**
   - Add more data sources
   - Enhance data validation
   - Improve data preprocessing

3. **Review AI Prompts**
   - Analyze AI responses
   - Adjust prompt engineering
   - Test different models

### High Error Rates

**Symptoms:**
- Health check showing high error rates
- Frequent failure notifications
- System instability

**Diagnosis:**
1. Review error logs
2. Check system metrics
3. Analyze failure patterns

**Solutions:**

1. **Review Error Logs**
   ```bash
   # Check recent errors
   vercel logs --filter="error"
   ```

2. **Implement Retry Logic**
   ```javascript
   // Add retry with backoff
   const retryWithBackoff = async (fn, maxRetries = 3) => {
     for (let i = 0; i < maxRetries; i++) {
       try {
         return await fn();
       } catch (error) {
         if (i === maxRetries - 1) throw error;
         await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, i)));
       }
     }
   };
   ```

3. **Add Circuit Breakers**
   - Implement failure detection
   - Add automatic recovery
   - Monitor system health

## 🔧 Configuration Issues

### Environment Variables

**Symptoms:**
- "Environment variable not found" errors
- Authentication failures
- Missing configuration

**Solutions:**

1. **Verify Environment Variables**
   ```bash
   # List all environment variables
   vercel env ls
   
   # Check specific variable
   vercel env pull .env.local
   cat .env.local
   ```

2. **Set Missing Variables**
   ```bash
   # Set environment variable
   vercel env add OPENAI_API_KEY
   vercel env add FIREBASE_PROJECT_ID
   ```

3. **Validate Configuration**
   ```javascript
   // Configuration validation
   const requiredEnvVars = [
     'OPENAI_API_KEY',
     'FIREBASE_PROJECT_ID',
     'FIREBASE_PRIVATE_KEY',
     'FIREBASE_CLIENT_EMAIL'
   ];
   
   const missing = requiredEnvVars.filter(key => !process.env[key]);
   if (missing.length > 0) {
     throw new Error(`Missing environment variables: ${missing.join(', ')}`);
   }
   ```

### Sport Configuration

**Symptoms:**
- Sports not being processed
- Incorrect market types
- Wrong confidence thresholds

**Solutions:**

1. **Check Sport Configuration**
   ```javascript
   // In config/sports.js
   export const NFL_CONFIG = {
     enabled: true, // Ensure sport is enabled
     confidence_threshold: 0.70,
     markets: ['spread', 'totals', 'props'],
     auto_approve: true
   };
   ```

2. **Validate Market Types**
   - Check DraftKings API for available markets
   - Update market types in configuration
   - Test market data retrieval

3. **Adjust Thresholds**
   - Monitor pick generation rates
   - Adjust confidence thresholds
   - Review quality metrics

## 📊 Performance Issues

### Slow Response Times

**Symptoms:**
- API endpoints taking too long
- Timeout errors
- Poor user experience

**Solutions:**

1. **Optimize Database Queries**
   ```javascript
   // Use efficient queries
   const query = db.collection('picks')
     .where('sport', '==', 'NFL')
     .where('status', '==', 'live')
     .limit(50)
     .orderBy('createdAt', 'desc');
   ```

2. **Implement Caching**
   ```javascript
   // Add caching layer
   const cache = new Map();
   const getCachedData = (key, fetchFn) => {
     if (cache.has(key)) return cache.get(key);
     const data = await fetchFn();
     cache.set(key, data);
     return data;
   };
   ```

3. **Optimize API Calls**
   - Use bulk operations
   - Implement parallel processing
   - Reduce unnecessary requests

### High Memory Usage

**Symptoms:**
- Vercel function timeouts
- Memory limit exceeded
- Performance degradation

**Solutions:**

1. **Optimize Data Processing**
   ```javascript
   // Process data in chunks
   const processInChunks = async (data, chunkSize = 100) => {
     for (let i = 0; i < data.length; i += chunkSize) {
       const chunk = data.slice(i, i + chunkSize);
       await processChunk(chunk);
     }
   };
   ```

2. **Reduce Data Size**
   - Filter unnecessary data
   - Compress large objects
   - Use efficient data structures

3. **Monitor Memory Usage**
   ```javascript
   // Add memory monitoring
   const memoryUsage = process.memoryUsage();
   console.log('Memory usage:', memoryUsage);
   ```

## 🔍 Debugging

### Enable Debug Mode

```bash
# Set debug environment variable
vercel env add DEBUG true
```

### Log Analysis

1. **View Real-time Logs**
   ```bash
   vercel logs --follow
   ```

2. **Filter by Level**
   ```bash
   vercel logs --filter="error"
   vercel logs --filter="warn"
   ```

3. **Search Logs**
   ```bash
   vercel logs | grep "specific error message"
   ```

### Common Debug Commands

```bash
# Check deployment status
vercel ls

# View function logs
vercel logs --filter="function-name"

# Test endpoint locally
vercel dev

# Check environment variables
vercel env ls

# View deployment details
vercel inspect
```

## 🚀 Recovery Procedures

### System Recovery

1. **Restart Services**
   ```bash
   # Redeploy to restart all functions
   vercel --prod
   ```

2. **Clear Caches**
   ```bash
   # Clear Vercel cache
   vercel --force
   ```

3. **Reset Configuration**
   ```bash
   # Pull fresh environment variables
   vercel env pull .env.local
   ```

### Data Recovery

1. **Backup Data**
   ```bash
   # Export Firebase data
   firebase firestore:export gs://your-bucket/backup
   ```

2. **Restore Data**
   ```bash
   # Import Firebase data
   firebase firestore:import gs://your-bucket/backup
   ```

3. **Validate Data**
   ```javascript
   // Check data integrity
   const validateData = async () => {
     const db = getFirestore();
     const collections = ['live_picks', 'qa_picks', 'scoring'];
     
     for (const collection of collections) {
       const snapshot = await db.collection(collection).limit(1).get();
       console.log(`${collection}: ${snapshot.size} documents`);
     }
   };
   ```

## 📞 Support

### Getting Help

1. **Check Documentation**
   - Review API documentation
   - Check troubleshooting guide
   - Search existing issues

2. **Gather Information**
   - Collect error logs
   - Note reproduction steps
   - Include system information

3. **Contact Support**
   - Open GitHub issue
   - Contact development team
   - Check status pages

### Useful Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Firebase Documentation](https://firebase.google.com/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [DraftKings API Documentation](https://sportsbook.draftkings.com/api)

### Emergency Contacts

- **Critical Issues**: Contact development team immediately
- **API Issues**: Check service status pages
- **Billing Issues**: Contact respective service providers

## 📝 Prevention

### Best Practices

1. **Regular Monitoring**
   - Set up health check alerts
   - Monitor system metrics
   - Review error logs regularly

2. **Proactive Maintenance**
   - Update dependencies regularly
   - Test changes in staging
   - Implement proper error handling

3. **Documentation**
   - Keep documentation updated
   - Document configuration changes
   - Maintain runbooks

### Monitoring Setup

1. **Health Checks**
   - Configure Slack alerts
   - Set up monitoring dashboards
   - Implement automated recovery

2. **Performance Monitoring**
   - Track response times
   - Monitor error rates
   - Analyze usage patterns

3. **Cost Monitoring**
   - Set up billing alerts
   - Track API usage
   - Optimize resource usage




