import requests

def verify_user():
    url = "http://localhost:8000/api/auth/verify-email"
    # OTP retrieved from previous step
    data = {
        "email": "jashwanthmudiraj5@gmail.com",
        "otp": "351711" 
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("SUCCESS: User verified!")
            print(response.json())
        else:
            print(f"FAILED: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_user()
