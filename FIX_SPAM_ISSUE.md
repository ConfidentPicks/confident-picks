# 📧 Fix Emails Going to Spam

## Why Emails Go to Spam

Your emails are going to spam because:
1. Sending from Gmail (`durellmars@gmail.com`) instead of your domain
2. Domain not verified with SendGrid
3. No SPF/DKIM records set up

---

## Solution: Verify Your Domain

### Step 1: Authenticate Your Domain in SendGrid

1. Go to SendGrid: https://app.sendgrid.com/
2. Click **Settings** → **Sender Authentication**
3. Click **Authenticate Your Domain**
4. Select your DNS provider (Squarespace, GoDaddy, etc.)
5. Enter: `confident-picks.com`
6. Click **Next**

### Step 2: Add DNS Records

SendGrid will give you DNS records to add. You'll need to add these to your domain:

**Example records (yours will be different):**
```
Type: CNAME
Host: s1._domainkey
Value: s1.domainkey.u12345678.wl123.sendgrid.net

Type: CNAME
Host: s2._domainkey
Value: s2.domainkey.u12345678.wl123.sendgrid.net

Type: CNAME
Host: em1234
Value: u12345678.wl123.sendgrid.net
```

### Step 3: Add Records to Your Domain

**If using Squarespace:**
1. Go to your domain settings
2. Click **DNS Settings**
3. Add each CNAME record
4. Save changes

**If using GoDaddy/Namecheap:**
1. Go to DNS Management
2. Add CNAME records
3. Save

### Step 4: Verify in SendGrid

1. Back in SendGrid, click **Verify**
2. Wait 24-48 hours for DNS propagation
3. Once verified, you'll see a green checkmark ✅

### Step 5: Update Email Address

Once verified, update the sender email:

**In `send_email.js` and `email_templates.js`:**
```javascript
const FROM_EMAIL = 'noreply@confident-picks.com'; // Change from Gmail
```

---

## Quick Fix (Temporary)

**For now, to avoid spam:**

1. **Whitelist the sender** in Gmail:
   - Open the spam email
   - Click "Not Spam"
   - Add `durellmars@gmail.com` to contacts

2. **Create a filter:**
   - Gmail Settings → Filters
   - From: `durellmars@gmail.com`
   - Subject contains: `Confident Picks`
   - Action: Never send to Spam

---

## Benefits of Domain Verification

Once your domain is verified:
- ✅ Emails go to inbox (not spam)
- ✅ Professional sender: `noreply@confident-picks.com`
- ✅ Higher deliverability rate
- ✅ Better trust from email providers
- ✅ No "via sendgrid.net" label

---

## Timeline

- **DNS Setup:** 10 minutes
- **DNS Propagation:** 24-48 hours
- **Verification:** Instant after propagation

---

## Need Help?

SendGrid has great guides:
- https://docs.sendgrid.com/ui/account-and-settings/how-to-set-up-domain-authentication
- Live chat support available in SendGrid dashboard

---

**For now:** The password reset will work once GitHub Pages deploys (2-3 minutes). The spam issue is cosmetic and can be fixed later with domain verification.

