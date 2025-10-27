# 📧 Email System Setup Guide

## Step 1: Create SendGrid Account

1. Go to: https://signup.sendgrid.com/
2. Sign up with your email
3. Verify your email address
4. Complete the "Tell us about yourself" form:
   - **Role:** Developer
   - **Company:** Confident Picks
   - **Website:** confident-picks.com
   - **Use Case:** Transactional emails
5. Skip the "Send Your First Email" tutorial

## Step 2: Get API Key

1. In SendGrid dashboard, go to **Settings** → **API Keys**
2. Click **Create API Key**
3. Name: `confident-picks-production`
4. Permission Level: **Full Access**
5. Click **Create & View**
6. **COPY THE KEY** (starts with `SG.`)
7. Save it securely (you won't see it again!)

## Step 3: Verify Domain (Optional but Recommended)

1. Go to **Settings** → **Sender Authentication**
2. Click **Authenticate Your Domain**
3. Select your DNS host (e.g., Squarespace, GoDaddy)
4. Follow instructions to add DNS records
5. Wait for verification (can take up to 48 hours)

**For now, you can use:** `noreply@confident-picks.com` (will show "via sendgrid.net" until domain is verified)

## Step 4: Configure Environment Variable

### Option A: Windows (PowerShell)
```powershell
$env:SENDGRID_API_KEY="YOUR_API_KEY_HERE"
```

### Option B: Windows (Command Prompt)
```cmd
set SENDGRID_API_KEY=YOUR_API_KEY_HERE
```

### Option C: Add to `.env` file (Recommended)
Create a file named `.env` in your project root:
```
SENDGRID_API_KEY=YOUR_API_KEY_HERE
```

## Step 5: Test Email

Run the test script:
```bash
node test_email.js your-email@example.com
```

You should receive a test email within seconds!

## Step 6: Update Email Templates

Edit `email_templates.js` to customize:
- FROM_EMAIL (use your verified domain)
- FROM_NAME
- Email content and styling

## Troubleshooting

### Email not received?
1. Check spam/junk folder
2. Verify API key is correct
3. Check SendGrid Activity Feed (Settings → Activity)
4. Ensure "from" email matches verified domain

### "403 Forbidden" error?
- API key doesn't have Full Access permission
- Create a new key with Full Access

### "401 Unauthorized" error?
- API key is incorrect or expired
- Check environment variable is set correctly

## Free Tier Limits

SendGrid Free Plan:
- ✅ 100 emails per day
- ✅ All features included
- ✅ No credit card required

For production (if you exceed 100/day):
- **Essentials Plan:** $19.95/month for 50,000 emails
- **Pro Plan:** $89.95/month for 100,000 emails

## Email Types We'll Send

1. **Email Verification** - When user signs up
2. **Welcome Email** - After email is verified
3. **Password Reset** - When user requests password reset
4. **Subscription Confirmation** - When user upgrades
5. **Payment Receipt** - After each payment

## Next Steps

Once email is working:
1. ✅ Integrate with Firebase Authentication
2. ✅ Add password reset flow
3. ✅ Add email verification flow
4. ✅ Connect to Stripe webhooks for receipts

---

**Questions?** Check SendGrid docs: https://docs.sendgrid.com/

