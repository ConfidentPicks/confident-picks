"""
Set Admin Role in Firebase
===========================
This script adds the 'role: admin' field to a specific user in Firebase Firestore.

Usage:
    python set_admin_role.py

This will set your user (durelwilliams@gmail.com) as an admin in Firebase.
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth
import os

# Initialize Firebase Admin SDK
CRED_PATH = r'C:\Users\durel\Downloads\confident-picks-app-8-25-firebase-adminsdk-fbsvc-5a1df3b9f2.json'

if not firebase_admin._apps:
    cred = credentials.Certificate(CRED_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def find_user_by_email(email):
    """Find a user by email address"""
    try:
        user = firebase_auth.get_user_by_email(email)
        return user
    except Exception as e:
        print(f"[ERROR] Could not find user: {e}")
        return None

def set_admin_role(user_id, email):
    """Set admin role for a user"""
    try:
        # Get reference to user document
        user_ref = db.collection('users').document(user_id)
        
        # Check if document exists
        user_doc = user_ref.get()
        
        if user_doc.exists:
            print(f"[INFO] User document found for {email}")
            print(f"[INFO] Current data: {user_doc.to_dict()}")
        else:
            print(f"[INFO] No user document found, creating new one for {email}")
        
        # Update or create user document with admin role
        user_ref.set({
            'role': 'admin',
            'email': email,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }, merge=True)
        
        print(f"[SUCCESS] ✅ Admin role set for {email} (UID: {user_id})")
        
        # Verify the update
        updated_doc = user_ref.get()
        print(f"[INFO] Updated data: {updated_doc.to_dict()}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to set admin role: {e}")
        return False

def list_all_users():
    """List all users in Firebase Authentication"""
    try:
        print("\n" + "="*80)
        print("ALL USERS IN FIREBASE AUTHENTICATION")
        print("="*80)
        
        page = firebase_auth.list_users()
        count = 0
        
        for user in page.users:
            count += 1
            print(f"\n{count}. Email: {user.email}")
            print(f"   UID: {user.uid}")
            print(f"   Email Verified: {user.email_verified}")
            print(f"   Created: {user.user_metadata.creation_timestamp}")
            
            # Check if user has document in Firestore
            user_doc = db.collection('users').document(user.uid).get()
            if user_doc.exists:
                data = user_doc.to_dict()
                print(f"   Firestore Role: {data.get('role', 'not set')}")
                print(f"   Subscription: {data.get('subscription', {}).get('status', 'not set')}")
            else:
                print(f"   Firestore: No document found")
        
        print(f"\n[INFO] Total users: {count}")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"[ERROR] Failed to list users: {e}")

def main():
    print("="*80)
    print("FIREBASE ADMIN ROLE SETTER")
    print("="*80)
    
    # Admin email to set
    ADMIN_EMAIL = 'durelwilliams@gmail.com'
    
    print(f"\n[INFO] Looking for user: {ADMIN_EMAIL}")
    
    # Find user by email
    user = find_user_by_email(ADMIN_EMAIL)
    
    if user:
        print(f"[SUCCESS] Found user with UID: {user.uid}")
        
        # Set admin role
        success = set_admin_role(user.uid, ADMIN_EMAIL)
        
        if success:
            print("\n" + "="*80)
            print("✅ ADMIN ROLE SUCCESSFULLY SET!")
            print("="*80)
            print(f"\nUser {ADMIN_EMAIL} is now an admin.")
            print("\nNext steps:")
            print("1. Sign in to your app with this email")
            print("2. The app will automatically detect your admin role from Firebase")
            print("3. The 'Admin' button will appear in the navigation")
            print("="*80)
    else:
        print(f"\n[ERROR] User {ADMIN_EMAIL} not found in Firebase Authentication")
        print("\nPlease make sure you've signed up with this email first.")
        print("\nListing all users to help you find the correct email...")
        list_all_users()

if __name__ == '__main__':
    main()


