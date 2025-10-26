# 🎯 Stripe Setup - Quick Action Guide

## ✅ What's Done

- [x] Live Stripe keys installed in `index.html`
- [x] Production mode enabled
- [x] Sandbox labels removed
- [x] Real checkout flow implemented
- [x] Webhook function deployed to Firebase
- [x] Changes pushed to GitHub (live on confident-picks.com)

---

## 🚨 What You Need to Do NOW (15 minutes)

### 1️⃣ Create Live Mode Price (5 min)

1. Go to: https://dashboard.stripe.com/products
2. **Toggle to LIVE MODE** (top-right corner)
3. Click **"+ Add product"**
4. Fill in:
   - Name: `Confident Picks Premium`
   - Price: `$15.00 USD`
   - Billing: `Recurring - Monthly`
5. Click **"Save product"**
6. **Copy the Price ID** (looks like `price_1ABC...`)

### 2️⃣ Update Price ID in Code (2 min)

1. Open `index.html`
2. Find line **7332**
3. Replace the price ID:
   ```javascript
   priceId: 'YOUR_NEW_LIVE_PRICE_ID_HERE',
   ```
4. Save, commit, and push:
   ```bash
   git add index.html
   git commit -m "Update to live Stripe price ID"
   git push origin master
   ```

### 3️⃣ Register Webhook in Stripe (5 min)

1. Go to: https://dashboard.stripe.com/webhooks
2. **Make sure you're in LIVE MODE**
3. Click **"+ Add endpoint"**
4. Enter:
   ```
   Endpoint URL: https://us-central1-confident-picks-app-8-25.cloudfunctions.net/stripeWebhook
   ```
5. Select events:
   - ✅ `checkout.session.completed`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`
6. Click **"Add endpoint"**
7. **Copy the signing secret** (starts with `whsec_...`) - save it somewhere safe

### 4️⃣ Test the Webhook (3 min)

1. In Stripe Dashboard, click on your new webhook endpoint
2. Click **"Send test webhook"**
3. Select: `checkout.session.completed`
4. Click **"Send test webhook"**
5. Should see `200 OK` response

---

## 🧪 Test Before Going Live

### Use Stripe Test Mode First:

1. **Switch to TEST MODE** in Stripe Dashboard
2. Create a **test price** (same as live)
3. Temporarily update `index.html` with **test price ID**
4. Test payment with test card: `4242 4242 4242 4242`
5. Verify subscription activates in Firestore
6. **Switch back to LIVE MODE** when ready

---

## 📋 Complete Checklist

- [ ] Live price created in Stripe
- [ ] Price ID updated in `index.html` and pushed to GitHub
- [ ] Webhook registered in Stripe Dashboard
- [ ] Webhook tested with test event (200 OK response)
- [ ] Test payment completed successfully (optional but recommended)
- [ ] Subscription activated in Firestore (check after test payment)

---

## 🆘 Need Help?

### If webhook isn't working:
```bash
# Check Firebase logs
firebase functions:log --only stripeWebhook --project confident-picks-app-8-25
```

### If payment doesn't activate subscription:
1. Check Stripe Dashboard > Webhooks > Recent deliveries
2. Look for errors in Firebase Functions logs
3. Verify user ID is being passed correctly

---

## 📞 Quick Links

- **Stripe Dashboard:** https://dashboard.stripe.com
- **Stripe Webhooks:** https://dashboard.stripe.com/webhooks
- **Firebase Console:** https://console.firebase.google.com/project/confident-picks-app-8-25/functions
- **Your Site:** https://confident-picks.com

---

## ✅ You're Almost There!

Just complete the 4 steps above and your payment system will be fully live! 🚀

**Estimated time:** 15 minutes  
**Difficulty:** Easy (just following steps)  
**Risk:** Low (can test in test mode first)

