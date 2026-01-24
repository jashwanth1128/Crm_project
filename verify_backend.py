import requests
import time
import sys

BASE_URL = "http://localhost:8000/api"

def test_backend():
    print("Waiting for server to start...")
    time.sleep(5) # Give uvicorn a moment
    
    # 1. Health Check
    try:
        r = requests.get("http://localhost:8000/")
        assert r.status_code == 200
        print("✅ Health Check Passed")
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        return

    # 2. Register
    email = f"test_{int(time.time())}@example.com"
    password = "password123"
    user_data = {
        "email": email,
        "password": password,
        "first_name": "Test",
        "last_name": "User",
        "role": "ADMIN"
    }
    
    print(f"Registering {email}...")
    r = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    if r.status_code != 200:
        print(f"❌ Registration Failed: {r.text}")
        return
    print("✅ Registration Passed")
    
    # Needs manual verification in real app, but we can cheat via DB or manually call verify endpoint if we knew OTP.
    # Since we can't easily see console output of the server to get OTP, we might need to inspect the DB or rely on the fact that 
    # the server prints it. 
    # For automated test, let's login (which should fail if inactive)
    
    print("Attempting login (should fail initially)...")
    r = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if r.status_code == 401:
        print("✅ Login correctly blocked for unverified user")
    else:
        print(f"❌ Login unexpected status: {r.status_code}")

    # To fully test, we'd need to fetch the OTP from the DB. 
    # Since we are using SQLite, we could connect and get it.
    
    import sqlite3
    try:
        conn = sqlite3.connect("backend/crm.db")
        cursor = conn.cursor()
        cursor.execute("SELECT otp FROM users WHERE email = ?", (email,))
        otp = cursor.fetchone()[0]
        conn.close()
        print(f"Found OTP in DB: {otp}")
        
        # Verify
        r = requests.post(f"{BASE_URL}/auth/verify-email", json={"email": email, "otp": otp})
        assert r.status_code == 200
        print("✅ Email Verification Passed")
        
        # Login again
        r = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login Passed")
        
        # 3. Create Customer
        print("Creating customer...")
        customer_data = {"name": "Test Company", "email": "contact@test.com", "company": "Test Inc"}
        r = requests.post(f"{BASE_URL}/customers/", json=customer_data, headers=headers)
        assert r.status_code == 200
        customer_id = r.json()["id"]
        print("✅ Customer Creation Passed")
        
        # 4. Create Lead
        print("Creating lead...")
        lead_data = {"title": "Big Deal", "customer_id": customer_id, "value": 10000}
        r = requests.post(f"{BASE_URL}/leads/", json=lead_data, headers=headers)
        assert r.status_code == 200
        print("✅ Lead Creation Passed")
        
    except Exception as e:
        print(f"❌ DB Verification Failed: {e}")

if __name__ == "__main__":
    test_backend()
