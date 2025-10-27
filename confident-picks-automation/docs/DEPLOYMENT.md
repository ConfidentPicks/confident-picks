# Deployment Guide

This guide provides step-by-step instructions for deploying the Confident Picks automation system to Vercel.

## 📋 Prerequisites

Before deploying, ensure you have:

- [ ] Node.js 18+ installed
- [ ] Vercel account created
- [ ] Firebase project with service account
- [ ] OpenAI API key
- [ ] DraftKings API access (if needed)
- [ ] Slack webhook URL (optional)

## 🚀 Initial Deployment

### Step 1: Prepare the Project

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd confident-picks-automation
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Verify project structure**
   ```bash
   ls -la
   # Should show: api/, lib/, config/, docs/, package.json, vercel.json
   ```

### Step 2: Set Up Firebase

1. **Create Firebase Project**
   - Go to [Firebase Console](https://console.firebase.google.com)
   - Click "Create a project"
   - Follow the setup wizard

2. **Enable Firestore**
   - In Firebase Console, go to "Firestore Database"
   - Click "Create database"
   - Choose "Start in test mode" (we'll secure it later)

3. **Create Service Account**
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Download the JSON file
   - Keep this file secure - you'll need it for environment variables

### Step 3: Configure Environment Variables

1. **Create environment file**
   ```bash
   cp .env.example .env.local
   ```

2. **Edit environment variables**
   ```bash
   nano .env.local
   ```

3. **Required variables:**
   ```bash
   # Firebase Configuration
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_PRIVATE_KEY_ID=your-private-key-id
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
   FIREBASE_CLIENT_ID=your-client-id

   # OpenAI Configuration
   OPENAI_API_KEY=sk-your-openai-api-key

   # Optional: Slack Notifications
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url

   # Environment
   NODE_ENV=production
   ```

### Step 4: Deploy to Vercel

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy the project**
   ```bash
   vercel --prod
   ```

4. **Set environment variables in Vercel**
   ```bash
   vercel env add FIREBASE_PROJECT_ID
   vercel env add FIREBASE_PRIVATE_KEY_ID
   vercel env add FIREBASE_PRIVATE_KEY
   vercel env add FIREBASE_CLIENT_EMAIL
   vercel env add FIREBASE_CLIENT_ID
   vercel env add OPENAI_API_KEY
   vercel env add SLACK_WEBHOOK_URL
   vercel env add NODE_ENV
   ```

5. **Redeploy with environment variables**
   ```bash
   vercel --prod
   ```

## ⚙️ Configuration

### Step 5: Configure Sports

1. **Edit sport configuration**
   ```bash
   nano config/sports.js
   ```

2. **Enable desired sports**
   ```javascript
   export const NFL_CONFIG = {
     enabled: true,  // Set to true to enable NFL
     confidence_threshold: 0.70,
     markets: ['spread', 'totals', 'props'],
     auto_approve: true,
     max_picks_per_day: 50
   };
   ```

3. **Adjust thresholds**
   ```bash
   nano config/thresholds.js
   ```

### Step 6: Set Up Cron Jobs

1. **Verify cron configuration**
   ```bash
   cat vercel.json
   ```

2. **Test cron endpoints**
   ```bash
   # Test health check
   curl -X GET https://your-app.vercel.app/api/health-check

   # Test data collection (manual trigger)
   curl -X POST https://your-app.vercel.app/api/collect-data
   ```

3. **Monitor cron execution**
   ```bash
   vercel logs --follow
   ```

## 🔒 Security Configuration

### Step 7: Secure Firebase

1. **Set up Firestore Security Rules**
   ```javascript
   // In Firebase Console > Firestore > Rules
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       // Allow read/write for service account
       match /{document=**} {
         allow read, write: if request.auth != null;
       }
     }
   }
   ```

2. **Configure Firebase Authentication**
   - Go to Firebase Console > Authentication
   - Enable authentication methods as needed
   - Set up user management

### Step 8: API Security

1. **Secure environment variables**
   ```bash
   # Never commit .env files
   echo ".env*" >> .gitignore
   ```

2. **Use Vercel environment variables**
   ```bash
   # All sensitive data should be in Vercel
   vercel env ls
   ```

3. **Implement rate limiting**
   - Vercel automatically provides rate limiting
   - Monitor usage in Vercel dashboard

## 📊 Monitoring Setup

### Step 9: Configure Monitoring

1. **Set up Slack notifications**
   ```bash
   # Create Slack webhook
   # Go to https://api.slack.com/messaging/webhooks
   # Create new webhook
   # Add URL to environment variables
   ```

2. **Test health monitoring**
   ```bash
   # Trigger health check
   curl -X GET https://your-app.vercel.app/api/health-check
   ```

3. **Monitor system metrics**
   - Check Vercel dashboard for function metrics
   - Monitor Firebase usage
   - Track OpenAI API usage

### Step 10: Test the System

1. **Run health check**
   ```bash
   curl -X GET https://your-app.vercel.app/api/health-check
   ```

2. **Test data collection**
   ```bash
   curl -X POST https://your-app.vercel.app/api/collect-data
   ```

3. **Test pick generation**
   ```bash
   curl -X POST https://your-app.vercel.app/api/generate-picks
   ```

4. **Verify data in Firebase**
   - Check Firebase Console
   - Verify data is being stored
   - Check pick generation

## 🔄 Updates and Maintenance

### Updating the System

1. **Pull latest changes**
   ```bash
   git pull origin main
   ```

2. **Update dependencies**
   ```bash
   npm update
   ```

3. **Redeploy**
   ```bash
   vercel --prod
   ```

### Environment Variable Updates

1. **Update environment variables**
   ```bash
   vercel env add VARIABLE_NAME
   ```

2. **Remove old variables**
   ```bash
   vercel env rm VARIABLE_NAME
   ```

3. **Redeploy after changes**
   ```bash
   vercel --prod
   ```

### Database Maintenance

1. **Backup data**
   ```bash
   # Export Firestore data
   firebase firestore:export gs://your-bucket/backup-$(date +%Y%m%d)
   ```

2. **Clean up old data**
   ```javascript
   // Create cleanup function
   const cleanupOldData = async () => {
     const db = getFirestore();
     const cutoffDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000); // 30 days ago
     
     const oldLogs = await db.collection('automation_logs')
       .where('timestamp', '<', cutoffDate)
       .get();
     
     const batch = db.batch();
     oldLogs.docs.forEach(doc => batch.delete(doc.ref));
     await batch.commit();
   };
   ```

## 🚨 Troubleshooting Deployment

### Common Deployment Issues

1. **Environment Variable Errors**
   ```bash
   # Check if variables are set
   vercel env ls
   
   # Verify variable values
   vercel env pull .env.local
   cat .env.local
   ```

2. **Firebase Connection Issues**
   ```bash
   # Test Firebase connection
   curl -X GET https://your-app.vercel.app/api/health-check
   ```

3. **Function Timeout Issues**
   ```bash
   # Check function logs
   vercel logs --filter="function-name"
   ```

### Debugging Steps

1. **Check deployment status**
   ```bash
   vercel ls
   ```

2. **View function logs**
   ```bash
   vercel logs --follow
   ```

3. **Test endpoints locally**
   ```bash
   vercel dev
   ```

4. **Verify configuration**
   ```bash
   # Check vercel.json
   cat vercel.json
   
   # Check package.json
   cat package.json
   ```

## 📈 Performance Optimization

### Optimizing for Production

1. **Enable Vercel Analytics**
   ```bash
   vercel analytics
   ```

2. **Configure caching**
   ```json
   // In vercel.json
   {
     "headers": [
       {
         "source": "/api/(.*)",
         "headers": [
           {
             "key": "Cache-Control",
             "value": "s-maxage=300"
           }
         ]
       }
     ]
   }
   ```

3. **Monitor performance**
   - Check Vercel dashboard for metrics
   - Monitor function execution times
   - Track memory usage

### Scaling Considerations

1. **Function limits**
   - Vercel Pro: 60s timeout, 1GB memory
   - Vercel Enterprise: Custom limits

2. **Database scaling**
   - Firestore scales automatically
   - Monitor read/write quotas
   - Consider data partitioning

3. **API rate limits**
   - Monitor OpenAI usage
   - Track DraftKings API calls
   - Implement proper backoff strategies

## 🔐 Security Best Practices

### Production Security

1. **Environment Variables**
   - Never commit sensitive data
   - Use Vercel environment variables
   - Rotate keys regularly

2. **API Security**
   - Implement proper authentication
   - Use HTTPS for all communications
   - Monitor for suspicious activity

3. **Data Protection**
   - Encrypt sensitive data
   - Implement access controls
   - Regular security audits

### Monitoring Security

1. **Log monitoring**
   - Monitor for failed authentication attempts
   - Track unusual API usage patterns
   - Alert on security events

2. **Access control**
   - Limit admin access
   - Use strong passwords
   - Enable two-factor authentication

## 📞 Support and Maintenance

### Regular Maintenance Tasks

1. **Weekly**
   - Check system health
   - Review error logs
   - Monitor performance metrics

2. **Monthly**
   - Update dependencies
   - Review security settings
   - Backup data

3. **Quarterly**
   - Security audit
   - Performance review
   - Cost optimization

### Getting Help

1. **Documentation**
   - Check API documentation
   - Review troubleshooting guide
   - Search existing issues

2. **Community**
   - Vercel community forum
   - Firebase community
   - GitHub issues

3. **Professional Support**
   - Vercel support (Pro/Enterprise)
   - Firebase support
   - OpenAI support

## 📝 Deployment Checklist

### Pre-Deployment

- [ ] All environment variables configured
- [ ] Firebase project set up
- [ ] Service account created
- [ ] OpenAI API key obtained
- [ ] Dependencies installed
- [ ] Configuration files updated

### Deployment

- [ ] Vercel CLI installed and authenticated
- [ ] Project deployed to Vercel
- [ ] Environment variables set in Vercel
- [ ] Cron jobs configured
- [ ] Health check endpoint working

### Post-Deployment

- [ ] System health check passed
- [ ] Data collection working
- [ ] Pick generation functional
- [ ] Monitoring configured
- [ ] Alerts set up
- [ ] Documentation updated

### Production Readiness

- [ ] Security rules configured
- [ ] Performance optimized
- [ ] Monitoring active
- [ ] Backup procedures in place
- [ ] Support contacts established
- [ ] Maintenance schedule created




