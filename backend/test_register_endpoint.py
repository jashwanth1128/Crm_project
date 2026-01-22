
import requests
import json

def test_register():
    url = "http://localhost:8000/api/auth/register"
    # Matching the payload seen in frontend code
    payload = {
        "email": "test@user.com",
        "password": "test1234",
        "first_name": "Test",
        "last_name": "User",
        "role": "EMPLOYEE"
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
    test_register()
