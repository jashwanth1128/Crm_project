import requests
import json

def test_register():
    url = "http://localhost:8000/api/auth/register"
    data = {
        "email": "test_debug@example.com",
        "password": "password123",
        "first_name": "Debug",
        "last_name": "User",
        "role": "ADMIN"
    }
    
    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_register()
