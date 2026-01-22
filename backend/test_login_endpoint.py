
import requests
import json

def test_login():
    url = "http://localhost:8000/api/auth/login"
    payload = {
        "email": "admin@crm.com",
        "password": "admin123"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Sending POST to {url} with payload: {payload}")
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_login()
