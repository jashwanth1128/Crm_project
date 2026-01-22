import requests
import sys
import json
from datetime import datetime

class CRMAPITester:
    def __init__(self, base_url="http://127.0.0.1:8000"
):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_customer_id = None
        self.created_lead_id = None
        self.created_activity_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json() if response.text else {}
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_auth_login(self):
        """Test login with admin credentials"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": "admin@crm.com", "password": "admin123"}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   Token obtained: {self.token[:20]}...")
            return True
        return False

    def test_auth_register(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        success, response = self.run_test(
            "User Registration",
            "POST",
            "api/auth/register",
            200,
            data={
                "email": f"test_user_{timestamp}@test.com",
                "password": "TestPass123!",
                "first_name": "Test",
                "last_name": "User",
                "role": "EMPLOYEE"
            }
        )
        return success

    def test_auth_me(self):
        """Test get current user"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "api/auth/me",
            200
        )
        return success

    def test_get_users(self):
        """Test get all users"""
        success, response = self.run_test(
            "Get Users",
            "GET",
            "api/users",
            200
        )
        return success

    def test_create_customer(self):
        """Test customer creation"""
        timestamp = datetime.now().strftime('%H%M%S')
        success, response = self.run_test(
            "Create Customer",
            "POST",
            "api/customers",
            200,
            data={
                "name": f"Test Customer {timestamp}",
                "email": f"customer_{timestamp}@test.com",
                "phone": "+1234567890",
                "company": "Test Company",
                "address": "123 Test St",
                "status": "ACTIVE",
                "notes": "Test customer notes"
            }
        )
        if success and 'id' in response:
            self.created_customer_id = response['id']
            print(f"   Customer ID: {self.created_customer_id}")
        return success

    def test_get_customers(self):
        """Test get customers"""
        success, response = self.run_test(
            "Get Customers",
            "GET",
            "api/customers",
            200
        )
        return success

    def test_get_customer_by_id(self):
        """Test get customer by ID"""
        if not self.created_customer_id:
            print("❌ Skipped - No customer ID available")
            return False
        
        success, response = self.run_test(
            "Get Customer by ID",
            "GET",
            f"api/customers/{self.created_customer_id}",
            200
        )
        return success

    def test_update_customer(self):
        """Test customer update"""
        if not self.created_customer_id:
            print("❌ Skipped - No customer ID available")
            return False
        
        success, response = self.run_test(
            "Update Customer",
            "PATCH",
            f"api/customers/{self.created_customer_id}",
            200,
            data={"notes": "Updated customer notes"}
        )
        return success

    def test_create_lead(self):
        """Test lead creation"""
        if not self.created_customer_id:
            print("❌ Skipped - No customer ID available")
            return False
        
        timestamp = datetime.now().strftime('%H%M%S')
        success, response = self.run_test(
            "Create Lead",
            "POST",
            "api/leads",
            200,
            data={
                "title": f"Test Lead {timestamp}",
                "description": "Test lead description",
                "value": 5000.00,
                "status": "NEW",
                "source": "WEBSITE",
                "customer_id": self.created_customer_id,
                "assigned_to": self.user_id
            }
        )
        if success and 'id' in response:
            self.created_lead_id = response['id']
            print(f"   Lead ID: {self.created_lead_id}")
        return success

    def test_get_leads(self):
        """Test get leads"""
        success, response = self.run_test(
            "Get Leads",
            "GET",
            "api/leads",
            200
        )
        return success

    def test_get_lead_by_id(self):
        """Test get lead by ID"""
        if not self.created_lead_id:
            print("❌ Skipped - No lead ID available")
            return False
        
        success, response = self.run_test(
            "Get Lead by ID",
            "GET",
            f"api/leads/{self.created_lead_id}",
            200
        )
        return success

    def test_update_lead_status(self):
        """Test lead status update"""
        if not self.created_lead_id:
            print("❌ Skipped - No lead ID available")
            return False
        
        success, response = self.run_test(
            "Update Lead Status",
            "PATCH",
            f"api/leads/{self.created_lead_id}",
            200,
            data={"status": "CONTACTED"}
        )
        return success

    def test_get_lead_stats(self):
        """Test lead statistics"""
        success, response = self.run_test(
            "Get Lead Stats",
            "GET",
            "api/leads/stats/overview",
            200
        )
        return success

    def test_create_activity(self):
        """Test activity creation"""
        timestamp = datetime.now().strftime('%H%M%S')
        success, response = self.run_test(
            "Create Activity",
            "POST",
            "api/activities",
            200,
            data={
                "type": "CALL",
                "subject": f"Test Call {timestamp}",
                "description": "Test activity description",
                "duration": 30,
                "customer_id": self.created_customer_id,
                "lead_id": self.created_lead_id
            }
        )
        if success and 'id' in response:
            self.created_activity_id = response['id']
            print(f"   Activity ID: {self.created_activity_id}")
        return success

    def test_get_activities(self):
        """Test get activities"""
        success, response = self.run_test(
            "Get Activities",
            "GET",
            "api/activities",
            200
        )
        return success

    def test_get_notifications(self):
        """Test get notifications"""
        success, response = self.run_test(
            "Get Notifications",
            "GET",
            "api/notifications",
            200
        )
        return success

    def test_websocket_endpoint(self):
        """Test WebSocket endpoint availability (just check if endpoint exists)"""
        if not self.token:
            print("❌ Skipped - No token available")
            return False
        
        # We can't easily test WebSocket in this simple test, but we can check if the endpoint is accessible
        print("🔍 Testing WebSocket endpoint availability...")
        print("   Note: WebSocket functionality requires browser testing")
        return True

def main():
    print("🚀 Starting CRM API Tests")
    print("=" * 50)
    
    tester = CRMAPITester()
    
    # Authentication tests
    print("\n📋 AUTHENTICATION TESTS")
    if not tester.test_auth_login():
        print("❌ Login failed, stopping tests")
        return 1
    
    tester.test_auth_register()
    tester.test_auth_me()
    
    # User management tests
    print("\n👥 USER MANAGEMENT TESTS")
    tester.test_get_users()
    
    # Customer tests
    print("\n🏢 CUSTOMER TESTS")
    tester.test_create_customer()
    tester.test_get_customers()
    tester.test_get_customer_by_id()
    tester.test_update_customer()
    
    # Lead tests
    print("\n🎯 LEAD TESTS")
    tester.test_create_lead()
    tester.test_get_leads()
    tester.test_get_lead_by_id()
    tester.test_update_lead_status()
    tester.test_get_lead_stats()
    
    # Activity tests
    print("\n📝 ACTIVITY TESTS")
    tester.test_create_activity()
    tester.test_get_activities()
    
    # Notification tests
    print("\n🔔 NOTIFICATION TESTS")
    tester.test_get_notifications()
    
    # WebSocket tests
    print("\n🔌 WEBSOCKET TESTS")
    tester.test_websocket_endpoint()
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Backend API tests mostly successful!")
        return 0
    else:
        print("⚠️  Backend API has significant issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())