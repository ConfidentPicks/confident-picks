# 🚀 Deploy Stripe Checkout Session Function

## What Changed

We've switched from the deprecated **client-only Stripe Checkout** to the modern **Stripe Checkout Sessions** approach, which uses a backend Firebase Function to create checkout sessions securely.

---

## 📋 Deployment Steps

### 1. Set Stripe Secret Key in Firebase Functions Config

Run this command in PowerShell (replace with your actual secret key):

```powershell
firebase functions:config:set stripe.secret_key="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"
```

### 2. Deploy the New Function

```powershell
cd functions
firebase deploy --only functions:createCheckoutSession
```

### 3. Verify Deployment

After deployment, you should see output like:
```
✔  functions[us-central1-createCheckoutSession]: Successful create operation.
Function URL (createCheckoutSession): https://us-central1-confident-picks-app-8-25.cloudfunctions.net/createCheckoutSession
```

---

## 🧪 Testing

1. **Hard refresh** your browser (Ctrl+Shift+R)
2. **Sign in with Google**
3. Click the **"Upgrade"** button
4. You should be redirected to the **real Stripe Checkout page**
5. Complete the test payment (use test card: `4242 4242 4242 4242`)

---

## 📝 What This Does

### Backend (Firebase Function)
- Creates a Stripe Checkout Session with your secret key
- Returns a secure checkout URL to the frontend
- Handles all sensitive operations server-side

### Frontend (index.html)
- Calls the Firebase Function with user details
- Redirects user to the Stripe-hosted checkout page
- No more client-only integration errors!

---

## ✅ Benefits

- ✅ **Secure**: Secret key never exposed to frontend
- ✅ **Modern**: Uses latest Stripe Checkout API
- ✅ **Compliant**: Follows Stripe best practices
- ✅ **Scalable**: Backend handles session creation

---

## 🔗 Files Modified

1. `functions/index.js` - Added `createCheckoutSession` function
2. `index.html` - Updated `redirectToCheckout` to call Firebase Function

---

**Ready to deploy? Run the commands above!** 🚀

