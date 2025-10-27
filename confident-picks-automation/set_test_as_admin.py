"""
Set Admin Role for test@example.com
====================================
This script sets the test@example.com user as admin.
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase Admin SDK
CRED_PATH = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CRED_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def set_admin_role():
    """Set admin role for test@example.com"""
    try:
        # UID from the list
        user_id = 'OhYuXcNoR3bnzFb0Dhed8dPdM4p1'
        email = 'test@example.com'
        
        # Get reference to user document
        user_ref = db.collection('users').document(user_id)
        
        # Check current data
        user_doc = user_ref.get()
        
        if user_doc.exists:
            print(f"[INFO] Current data for {email}:")
            print(f"       {user_doc.to_dict()}")
        
        # Update user document with admin role
        user_ref.set({
            'role': 'admin',
            'email': email,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }, merge=True)
        
        print(f"\n[SUCCESS] Admin role set for {email}")
        
        # Verify the update
        updated_doc = user_ref.get()
        print(f"\n[INFO] Updated data:")
        print(f"       {updated_doc.to_dict()}")
        
        print("\n" + "="*80)
        print("ADMIN ROLE SUCCESSFULLY SET!")
        print("="*80)
        print(f"\nUser {email} is now an admin.")
        print("\nNext steps:")
        print("1. Sign out if you're currently signed in")
        print("2. Sign in again with test@example.com")
        print("3. The app will automatically detect your admin role from Firebase")
        print("4. The 'Admin' button will appear in the navigation")
        print("="*80)
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to set admin role: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("="*80)
    print("SETTING test@example.com AS ADMIN")
    print("="*80)
    print()
    set_admin_role()

