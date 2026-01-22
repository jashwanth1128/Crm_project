
import requests
import json

def test_create_lead():
    # Login
    login_url = "http://localhost:8000/api/auth/login"
    login_payload = {"email": "admin@crm.com", "password": "admin123"}
    headers = {"Content-Type": "application/json"}
    
    try:
        resp = requests.post(login_url, json=login_payload, headers=headers)
        token = resp.json().get("access_token")
    except:
        print("Login failed")
        return

    # Get a customer ID (we just created one, or list them)
    cust_url = "http://localhost:8000/api/customers"
    headers["Authorization"] = f"Bearer {token}"
    resp = requests.get(cust_url, headers=headers)
    customers = resp.json()
    if not customers:
        print("No customers found, cannot create lead")
        return
    cust_id = customers[0]["id"]

    # Create Lead
    url = "http://localhost:8000/api/leads"
    payload = {
        "title": "Big Deal",
        "description": "Potential big sale",
        "value": 10000,
        "status": "NEW",
        "source": "WEBSITE",
        "customer_id": cust_id
    }
    
    print(f"Sending POST to {url} with payload: {payload}")
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_create_lead()
