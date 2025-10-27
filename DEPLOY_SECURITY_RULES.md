# 🔐 Deploy Firebase Security Rules

## ✅ **What These Rules Do**

### **Users Collection:**
- ✅ Users can read their own data
- ✅ Users can create their own profile on signup
- ✅ Users can update their own data (favorites, settings, etc.)
- ❌ Users **CANNOT** modify their own `role` field (prevents self-promotion to admin)
- ❌ Users **CANNOT** modify their own `subscription` field (prevents free → paid upgrade)
- ✅ Only admins can modify `role` and `subscription` fields

### **Approved Models Collection:**
- ✅ Anyone can read models (needed for pick generation)
- ❌ Only admins can write/update models

### **Picks Collections:**
- ✅ Authenticated users can read picks
- ❌ Only admins can create/update/delete picks

### **Analytics & System:**
- ✅ Admins only (full access)

---

## 📋 **Deployment Steps**

### **Option 1: Firebase Console (Easiest)**

1. **Go to Firebase Console:**
   - Open: https://console.firebase.google.com/
   - Select your project: `confident-picks-app-8-25`

2. **Navigate to Firestore Rules:**
   - Click "Firestore Database" in left sidebar
   - Click "Rules" tab at the top

3. **Copy the Rules:**
   - Open the file: `firestore.rules` (I just created it)
   - Copy ALL the contents

4. **Paste & Publish:**
   - Paste into the Firebase Console editor
   - Click "Publish" button
   - Wait for confirmation message

5. **Done!** ✅

---

### **Option 2: Firebase CLI (Advanced)**

If you have Firebase CLI installed:

```bash
# Deploy rules from command line
firebase deploy --only firestore:rules
```

---

## 🧪 **Testing the Rules**

### **Test 1: Try to Modify Your Own Role (Should Fail)**

1. Open browser console (F12) on your app
2. Run this code:
```javascript
// Try to give yourself admin role (should fail)
const { doc, updateDoc } = await import('https://www.gstatic.com/firebasejs/10.0.0/firebase-firestore.js');
const userRef = doc(window.db, 'users', window.auth.currentUser.uid);
await updateDoc(userRef, { role: 'admin' });
```

**Expected Result:** Error message: `"Missing or insufficient permissions"`

---

### **Test 2: Try to Modify Your Own Subscription (Should Fail)**

```javascript
// Try to give yourself premium subscription (should fail)
const { doc, updateDoc } = await import('https://www.gstatic.com/firebasejs/10.0.0/firebase-firestore.js');
const userRef = doc(window.db, 'users', window.auth.currentUser.uid);
await updateDoc(userRef, { 
  subscription: { 
    status: 'active', 
    tier: 'premium' 
  } 
});
```

**Expected Result:** Error message: `"Missing or insufficient permissions"`

---

### **Test 3: Update Allowed Fields (Should Work)**

```javascript
// Update your display name (should work)
const { doc, updateDoc } = await import('https://www.gstatic.com/firebasejs/10.0.0/firebase-firestore.js');
const userRef = doc(window.db, 'users', window.auth.currentUser.uid);
await updateDoc(userRef, { 
  settings: { theme: 'dark' } 
});
```

**Expected Result:** Success! No error.

---

### **Test 4: Admin Can Modify Roles (Should Work if you're admin)**

```javascript
// As admin, give someone else admin role (should work)
const { doc, updateDoc } = await import('https://www.gstatic.com/firebasejs/10.0.0/firebase-firestore.js');
const userRef = doc(window.db, 'users', 'SOME_OTHER_USER_ID');
await updateDoc(userRef, { role: 'admin' });
```

**Expected Result:** Success if you're admin, error if not.

---

## ⚠️ **IMPORTANT: Python Scripts Still Work**

Your Python scripts use **Firebase Admin SDK** with service account credentials, which bypass these security rules. This is correct and expected!

The rules only apply to:
- ✅ Web app users (browser)
- ✅ Mobile app users
- ❌ **NOT** server-side scripts with admin credentials

So your exhaustive testing scripts will continue to save models to Firebase without any issues.

---

## 🔒 **Security Checklist**

After deploying, verify:

- [ ] Rules deployed successfully (no errors in console)
- [ ] Non-admin users cannot modify their `role` field
- [ ] Non-admin users cannot modify their `subscription` field
- [ ] Users can still update their settings/favorites
- [ ] Python scripts can still save models to Firebase
- [ ] Authenticated users can read picks
- [ ] Only admins can create/update picks

---

## 📝 **Next Steps**

Once rules are deployed:

1. ✅ **Test the rules** (use the tests above)
2. ✅ **Verify Python scripts still work** (check if models are still being saved)
3. ✅ **Move to Task 2:** Domain Purchase

---

**Estimated Time:** 10-15 minutes (including testing)  
**Status:** Ready to deploy!

