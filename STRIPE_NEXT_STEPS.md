# 🚨 STRIPE LIVE MODE - IMMEDIATE NEXT STEPS

## ⚠️ CRITICAL: Do These NOW Before Accepting Real Payments

---

## 1️⃣ Create Live Mode Price (5 minutes)

**Why:** The current price ID is from test mode and won't work with live keys.

### Steps:
1. Open: https://dashboard.stripe.com/products
2. **Verify you're in LIVE MODE** (toggle in top-right corner)
3. Click **"+ Add product"**
4. Fill in:
   ```
   Name: Confident Picks Premium
   Description: Unlimited access to all premium sports picks
   Price: $15.00 USD
   Billing: Recurring - Monthly
   ```
5. Click **"Save product"**
6. Copy the **Price ID** (looks like `price_1ABC...`)

### Update the Code:
1. Open `index.html`
2. Find line **7332**
3. Replace:
   ```javascript
   priceId: 'price_1SF51I1G2mT1SwALThzOjtiQ',
   ```
   With:
   ```javascript
   priceId: 'price_YOUR_NEW_LIVE_PRICE_ID',
   ```
4. Commit and push:
   ```bash
   git add index.html
   git commit -m "Update to live Stripe price ID"
   git push origin master
   ```

---

## 2️⃣ Set Up Webhook Endpoint (30 minutes)

**Why:** Without webhooks, subscriptions won't activate automatically after payment.

### Option A: Firebase Cloud Function (Recommended)

#### Step 1: Install Firebase CLI
```bash
npm install -g firebase-tools
firebase login
```

#### Step 2: Initialize Functions
```bash
cd C:\Users\durel\Documents\confident-picks-restored
firebase init functions
# Choose JavaScript
# Install dependencies: Yes
```

#### Step 3: Create Webhook Function

Create `functions/index.js`:
```javascript
const functions = require('firebase-functions');
const admin = require('firebase-admin');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

admin.initializeApp();

exports.stripeWebhook = functions.https.onRequest(async (req, res) => {
  const sig = req.headers['stripe-signature'];
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
  
  let event;
  try {
    event = stripe.webhooks.constructEvent(req.body, sig, webhookSecret);
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }
  
  console.log('Webhook event received:', event.type);
  
  // Handle checkout.session.completed
  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;
    const userId = session.client_reference_id;
    
    if (!userId) {
      console.error('No client_reference_id found in session');
      return res.status(400).send('Missing user ID');
    }
    
    try {
      // Update user subscription in Firestore
      await admin.firestore().collection('users').doc(userId).update({
        subscription: {
          status: 'active',
          tier: 'premium',
          stripeCustomerId: session.customer,
          stripeSubscriptionId: session.subscription,
          stripePriceId: session.line_items?.data[0]?.price?.id || session.display_items?.[0]?.plan?.id,
          startedAt: admin.firestore.FieldValue.serverTimestamp(),
          updatedAt: admin.firestore.FieldValue.serverTimestamp()
        }
      });
      
      console.log(`✅ Subscription activated for user ${userId}`);
    } catch (error) {
      console.error('Error updating user subscription:', error);
      return res.status(500).send('Error updating subscription');
    }
  }
  
  // Handle subscription.deleted (cancellation)
  if (event.type === 'customer.subscription.deleted') {
    const subscription = event.data.object;
    const customerId = subscription.customer;
    
    try {
      // Find user by Stripe customer ID
      const usersSnapshot = await admin.firestore()
        .collection('users')
        .where('subscription.stripeCustomerId', '==', customerId)
        .limit(1)
        .get();
      
      if (!usersSnapshot.empty) {
        const userDoc = usersSnapshot.docs[0];
        await userDoc.ref.update({
          'subscription.status': 'canceled',
          'subscription.tier': 'free',
          'subscription.updatedAt': admin.firestore.FieldValue.serverTimestamp()
        });
        
        console.log(`✅ Subscription canceled for customer ${customerId}`);
      }
    } catch (error) {
      console.error('Error canceling subscription:', error);
      return res.status(500).send('Error canceling subscription');
    }
  }
  
  res.json({ received: true });
});
```

#### Step 4: Set Environment Variables
```bash
firebase functions:config:set stripe.secret_key="YOUR_STRIPE_SECRET_KEY"
firebase functions:config:set stripe.webhook_secret="YOUR_WEBHOOK_SECRET_FROM_STRIPE"
```

**Note:** Replace `YOUR_STRIPE_SECRET_KEY` with your actual Stripe secret key (starts with `sk_live_...`)

#### Step 5: Deploy
```bash
firebase deploy --only functions
```

Copy the function URL (e.g., `https://us-central1-confident-picks-app-8-25.cloudfunctions.net/stripeWebhook`)

---

### Step 6: Register Webhook in Stripe

1. Go to: https://dashboard.stripe.com/webhooks
2. Click **"+ Add endpoint"**
3. **Endpoint URL:** Paste your Firebase Function URL
4. **Events to send:**
   - ✅ `checkout.session.completed`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`
5. Click **"Add endpoint"**
6. Copy the **Signing secret** (starts with `whsec_...`)
7. Update Firebase config:
   ```bash
   firebase functions:config:set stripe.webhook_secret="whsec_YOUR_SIGNING_SECRET"
   firebase deploy --only functions
   ```

---

## 3️⃣ Test Payment Flow (15 minutes)

### Use Stripe Test Mode First

1. **Switch back to test mode temporarily:**
   - In Stripe Dashboard, toggle to **TEST MODE**
   - Create a test price (same as live)
   - Update `index.html` with test price ID
   - Push changes

2. **Test with test card:**
   - Go to: https://confident-picks.com
   - Sign up for free account
   - Click "Upgrade"
   - Use test card: `4242 4242 4242 4242`
   - Expiry: Any future date
   - CVC: Any 3 digits

3. **Verify:**
   - ✅ Redirected to Stripe checkout
   - ✅ Payment completes successfully
   - ✅ Redirected back to confident-picks.com
   - ✅ Webhook received (check Firebase logs)
   - ✅ User subscription updated in Firestore
   - ✅ User sees all premium picks

4. **Switch back to live mode:**
   - Update `index.html` with live price ID
   - Push changes

---

## 4️⃣ Add Success/Cancel Handlers (10 minutes)

Users are redirected to these URLs after checkout:
- Success: `https://confident-picks.com/?session_id=...&success=true`
- Cancel: `https://confident-picks.com/?canceled=true`

### Add to `index.html` (in the `<script>` section):

```javascript
// Handle Stripe checkout redirect
window.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  
  // Handle successful payment
  if (urlParams.get('success') === 'true') {
    const sessionId = urlParams.get('session_id');
    
    // Show success message
    alert(
      '🎉 Payment Successful!\n\n' +
      'Welcome to Confident Picks Premium!\n\n' +
      'You now have unlimited access to all picks.\n' +
      'Your subscription will renew monthly at $15.'
    );
    
    // Clean up URL
    window.history.replaceState({}, document.title, '/');
    
    // Refresh auth state
    if (window.auth?.currentUser) {
      location.hash = '#account';
      route();
    }
  }
  
  // Handle canceled payment
  if (urlParams.get('canceled') === 'true') {
    alert(
      'Payment Canceled\n\n' +
      'Your payment was canceled.\n' +
      'You can try again anytime from the Account page.'
    );
    
    // Clean up URL
    window.history.replaceState({}, document.title, '/');
  }
});
```

---

## ✅ Final Checklist

Before accepting real payments:

- [ ] Live price created in Stripe
- [ ] Price ID updated in `index.html`
- [ ] Webhook function deployed
- [ ] Webhook registered in Stripe
- [ ] Webhook signing secret configured
- [ ] Test payment completed successfully
- [ ] Subscription activated in Firestore
- [ ] Success/cancel handlers added
- [ ] All changes pushed to GitHub

---

## 🆘 Troubleshooting

### Payment doesn't redirect to Stripe
- Check browser console for errors
- Verify Stripe publishable key is correct
- Verify price ID is correct and in live mode

### Webhook not receiving events
- Check Firebase Functions logs
- Verify webhook URL is correct
- Verify webhook signing secret is set
- Test webhook in Stripe Dashboard

### Subscription not activating
- Check Firestore for user document
- Verify `client_reference_id` is being passed
- Check Firebase Functions logs for errors

---

## 📞 Need Help?

- **Stripe Support:** https://support.stripe.com
- **Firebase Support:** https://firebase.google.com/support
- **Stripe Webhook Testing:** https://dashboard.stripe.com/webhooks (click endpoint > "Send test webhook")

---

**Current Status:** Live keys deployed, webhook setup needed  
**Estimated Time to Complete:** 1 hour  
**Risk Level:** 🟡 Medium (payments won't activate without webhook)

