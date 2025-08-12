#!/usr/bin/env python3
"""
Admin User Setup Script for AgriLink

This script creates the initial admin user for the AgriLink platform.
Run this after the database is initialized and the backend is running.
"""

import requests
import json
import sys

# Configuration
API_BASE = "http://localhost:8000"
ADMIN_EMAIL = "admin@agrilink.com"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123456"
ADMIN_FULL_NAME = "System Administrator"

def create_admin_user():
    """Create the initial admin user"""
    
    print("🚀 Setting up AgriLink Admin User...")
    
    # Check if backend is running
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code != 200:
            print("❌ Backend is not running. Please start the backend first.")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Please ensure it's running on port 8000.")
        return False
    
    # Admin user data
    admin_data = {
        "email": ADMIN_EMAIL,
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "full_name": ADMIN_FULL_NAME,
        "role": "admin",
        "phone": "+2348000000000",
        "business_name": "AgriLink Platform",
        "business_address": "Lagos, Nigeria"
    }
    
    try:
        # Create admin user
        print("📝 Creating admin user...")
        response = requests.post(
            f"{API_BASE}/api/v1/auth/register",
            json=admin_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Admin user created successfully!")
            print(f"   Email: {ADMIN_EMAIL}")
            print(f"   Username: {ADMIN_USERNAME}")
            print(f"   Password: {ADMIN_PASSWORD}")
            print(f"   Access Token: {data['access_token'][:50]}...")
            print("\n🔐 You can now log in to the admin panel at:")
            print("   http://localhost:3000/auth/login")
            print("\n⚠️  IMPORTANT: Change the default password after first login!")
            return True
        else:
            error_data = response.json()
            if "already registered" in error_data.get("detail", "").lower():
                print("ℹ️  Admin user already exists.")
                return True
            else:
                print(f"❌ Failed to create admin user: {error_data}")
                return False
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("🌱 AgriLink Admin Setup")
    print("=" * 50)
    
    success = create_admin_user()
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Log in to the admin panel")
        print("2. Review and approve KYC applications")
        print("3. Monitor platform activity")
        print("4. Change default admin password")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
