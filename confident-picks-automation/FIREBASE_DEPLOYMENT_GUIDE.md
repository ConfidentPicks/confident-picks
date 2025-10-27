# Firebase Functions Deployment Guide

## Quick Start (5 minutes)

### Step 1: Install Firebase CLI
```bash
# Use the full path since Node.js isn't in PATH
& "C:\Program Files\nodejs\npm.cmd" install -g firebase-tools
```

### Step 2: Login to Firebase
```bash
firebase login
```

### Step 3: Initialize Functions (if needed)
```bash
firebase init functions
# Select: Use existing project
# Select: confident-picks-app
# Select: JavaScript
# Select: No to ESLint
# Select: No to install dependencies now
```

### Step 4: Install Dependencies
```bash
cd functions
npm install
cd ..
```

### Step 5: Deploy Functions
```bash
firebase deploy --only functions
```

## Environment Variables

After deployment, set these in Firebase Console:

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select project: `confident-picks-app`
3. Go to Functions → Configuration
4. Add environment variables:
   - `openai.api_key` = your OpenAI API key
   - `draftkings.api_key` = your DraftKings API key (when ready)

## Test Endpoints

After deployment, test these URLs:
- `https://us-central1-confident-picks-app.cloudfunctions.net/healthCheck`
- `https://us-central1-confident-picks-app.cloudfunctions.net/test`
- `https://us-central1-confident-picks-app.cloudfunctions.net/collectData`
- `https://us-central1-confident-picks-app.cloudfunctions.net/generatePicks`
- `https://us-central1-confident-picks-app.cloudfunctions.net/scoreGames`

## Expected Results

✅ **Health Check**: Returns system status  
✅ **Test**: Returns "Firebase Functions test endpoint working!"  
✅ **Other endpoints**: Return "ready" messages (implementation pending)  

## Next Steps

1. Test all endpoints
2. Configure environment variables
3. Implement DraftKings API integration
4. Implement OpenAI pick generation
5. Test full automation workflow

## Troubleshooting

- **Login issues**: Run `firebase login --reauth`
- **Permission issues**: Make sure you're logged in with the right Google account
- **Deploy failures**: Check Firebase Console for error logs
- **Function not found**: Wait 2-3 minutes after deployment




