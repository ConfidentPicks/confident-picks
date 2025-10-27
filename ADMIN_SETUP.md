# Admin Role Setup - Production Ready

This document explains how the admin role system works and how to set it up.

## Overview

The admin system now uses **Firebase Firestore** to store and check user roles, making it production-ready and secure.

## How It Works

### 1. **Firebase Storage**
Admin roles are stored in the `users` collection in Firestore:

```javascript
// Firebase structure
users/
  └── {userId}/
      ├── role: "admin"              // Admin role indicator
      ├── email: "user@example.com"
      ├── subscription: {...}         // Subscription data
      └── updatedAt: "2025-10-25..."
```

### 2. **Authentication Flow**

```
User Signs In
    ↓
Firebase Authentication verifies credentials
    ↓
App fetches user document from Firestore
    ↓
Check role field:
    - role === "admin" → Set state.auth = 'admin'
    - subscription.status === "active" → Set state.auth = 'paid'
    - else → Set state.auth = 'free'
    ↓
UI updates based on auth state
```

### 3. **Admin Privileges**

Admin users get:
- ✅ Full access to all picks (unlimited)
- ✅ Access to Favorites feature
- ✅ Access to Outcomes tracking
- ✅ Exclusive access to Admin Panel
- ✅ No upgrade prompts
- ✅ "Administrator" status badge

## Setup Instructions

### Step 1: Sign Up with Your Email

1. Go to your app
2. Sign up with `durelwilliams@gmail.com` (or your desired admin email)
3. Complete the sign-up process

### Step 2: Set Admin Role in Firebase

Run the Python script to add the admin role to your user:

```bash
cd confident-picks-automation
python set_admin_role.py
```

This script will:
1. Find your user by email in Firebase Authentication
2. Add `role: "admin"` to your user document in Firestore
3. Verify the update was successful

### Step 3: Sign In

1. Sign out if you're currently signed in
2. Sign in again with your admin email
3. The app will automatically detect your admin role
4. The "Admin" button will appear in the navigation

## Verification

To verify the admin role is working:

1. **Check Console Logs:**
   - Open browser DevTools (F12)
   - Look for: `👑 Admin user detected from Firebase!`

2. **Check UI:**
   - "Admin" button visible in navigation
   - Account page shows "Status: Administrator"
   - All picks are visible (no 3-pick limit)

3. **Check Firebase:**
   - Go to Firebase Console
   - Navigate to Firestore Database
   - Open `users` collection
   - Find your user document
   - Verify `role: "admin"` field exists

## Manual Setup (Alternative)

If you prefer to set the admin role manually in Firebase Console:

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: "Confident-Picks-App"
3. Go to Firestore Database
4. Navigate to `users` collection
5. Find your user document (by UID)
6. Click "Add field"
7. Field name: `role`
8. Field value: `admin`
9. Click "Add"

## Adding More Admins

To add additional admin users:

1. Update the `ADMIN_EMAIL` in `set_admin_role.py`
2. Run the script again
3. Or manually add the `role: "admin"` field in Firebase Console

## Security Notes

### ✅ What's Secure:

- Admin role is stored in Firebase (server-side)
- Firebase Authentication verifies user identity
- Role is checked on every sign-in
- Cannot be modified from browser DevTools
- Requires Firebase Admin SDK to modify roles

### ⚠️ Important for Production:

1. **Firebase Security Rules:**
   Update your Firestore security rules to prevent users from modifying their own roles:

   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /users/{userId} {
         // Users can read their own data
         allow read: if request.auth != null && request.auth.uid == userId;
         
         // Users can update their own data EXCEPT the role field
         allow update: if request.auth != null 
                       && request.auth.uid == userId
                       && !request.resource.data.diff(resource.data).affectedKeys().hasAny(['role']);
         
         // Only allow creation without role field
         allow create: if request.auth != null 
                       && request.auth.uid == userId
                       && !('role' in request.resource.data);
       }
       
       // Admin can read/write everything
       match /{document=**} {
         allow read, write: if request.auth != null 
                            && get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
       }
     }
   }
   ```

2. **Backend Validation:**
   For critical operations, always validate the user's role on the backend (Cloud Functions, etc.)

3. **Audit Logging:**
   Consider adding audit logs for admin actions

## Troubleshooting

### Admin button not showing?

1. Check console for errors
2. Verify `role: "admin"` exists in Firebase
3. Try signing out and signing in again
4. Clear browser cache and localStorage

### "No user document found" error?

1. Make sure you've signed up first
2. Check if the user exists in Firebase Authentication
3. Run `set_admin_role.py` to create the user document

### Role not persisting?

1. Check Firebase security rules
2. Verify the user document wasn't deleted
3. Check for JavaScript errors in console

## Code References

### Frontend (index.html)

- **Auth sync:** Line 7558 - `syncAuthWithFirebase()`
- **User data fetch:** Line 7631 - `getUserData()`
- **Admin UI updates:** Line 2143 - `updateAdminUI()`

### Backend (Python)

- **Set admin role:** `confident-picks-automation/set_admin_role.py`

## Testing

To test the admin system:

1. **As Admin:**
   - Sign in with admin email
   - Verify all features are accessible
   - Check Admin panel loads

2. **As Regular User:**
   - Sign in with different email
   - Verify Admin button is hidden
   - Verify limited picks (3 per league for free)

3. **As Anonymous:**
   - Sign out
   - Verify Admin button is hidden
   - Verify public picks only

## Migration Notes

### From Old System (Hardcoded Email)

The old system checked the email in the frontend:
```javascript
// OLD - Don't use
if (user.email === ADMIN_EMAIL) {
  setAuth('admin');
}
```

The new system checks Firebase:
```javascript
// NEW - Production ready
const userData = await getUserData(user.uid);
if (userData?.role === 'admin') {
  setAuth('admin');
}
```

**No migration needed** - just run `set_admin_role.py` to add the role to Firebase.

## Support

If you encounter issues:
1. Check the console logs for detailed error messages
2. Verify Firebase credentials are correct
3. Ensure Firebase SDK is loaded properly
4. Check network tab for failed API calls

---

**Last Updated:** October 25, 2025  
**Version:** 1.0 (Production Ready)

