
import requests
import json

def test_create_customer():
    # Login first to get token
    login_url = "http://localhost:8000/api/auth/login"
    login_payload = {"email": "admin@crm.com", "password": "admin123"}
    headers = {"Content-Type": "application/json"}
    
    try:
        resp = requests.post(login_url, json=login_payload, headers=headers)
        data = resp.json()
        token = data.get("access_token")
        if not token:
            print("Login failed, no token")
            return
    except Exception as e:
        print(f"Login request failed: {e}")
        return

    # Create Customer
    url = "http://localhost:8000/api/customers"
    payload = {
        "name": "Test Company",
        "email": "contact@testcompany.com",
        "phone": "555-0123",
        "status": "ACTIVE"
    }
    headers["Authorization"] = f"Bearer {token}"
    
    print(f"Sending POST to {url} with payload: {payload}")
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_create_customer()
