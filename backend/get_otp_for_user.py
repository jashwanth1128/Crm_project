import sqlite3
import sys
import os

# Adjust path to find the db if needed
db_path = "crm.db"
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
    # Try looking in app/ if not in root
    if os.path.exists("app/crm.db"):
        db_path = "app/crm.db"
    else:
        # Check current dir listing from previous step to be sure
        pass

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # We want the latest otp or for a specific email
    email = "jashwanthmudiraj5@gmail.com" 
    cursor.execute("SELECT otp FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    
    if result:
        print(f"OTP for {email}: {result[0]}")
    else:
        print(f"No user found for {email}. Dumping all users:")
        cursor.execute("SELECT email, otp FROM users")
        for row in cursor.fetchall():
            print(f"Email: {row[0]}, OTP: {row[1]}")
            
    conn.close()
except Exception as e:
    print(f"Error reading DB: {e}")
