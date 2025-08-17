#!/usr/bin/env python3
"""
TEF AI Practice Tool - Testing Module
Comprehensive testing suite for the application
"""

import os
import sys
import asyncio
import requests
import json
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TEFEvaluatorTester:
    """Test suite for TEF AI Practice Tool."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        logger.info(f"{status} {test_name}: {message}")
        return success
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                return self.log_test(
                    "Health Check",
                    True,
                    f"Status: {data.get('status')}, Version: {data.get('version')}"
                )
            else:
                return self.log_test(
                    "Health Check",
                    False,
                    f"Status code: {response.status_code}"
                )
        except Exception as e:
            return self.log_test("Health Check", False, f"Exception: {str(e)}")
    
    def test_status_endpoint(self):
        """Test status endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/api/status")
            if response.status_code == 200:
                data = response.json()
                return self.log_test(
                    "Status Check",
                    True,
                    f"App: {data.get('application')}, DB: {data.get('database')}"
                )
            else:
                return self.log_test(
                    "Status Check",
                    False,
                    f"Status code: {response.status_code}"
                )
        except Exception as e:
            return self.log_test("Status Check", False, f"Exception: {str(e)}")
    
    def test_random_question(self):
        """Test random question endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/api/questions/random")
            if response.status_code == 200:
                data = response.json()
                return self.log_test(
                    "Random Question",
                    True,
                    f"Question length: {len(data.get('question', ''))} chars"
                )
            else:
                return self.log_test(
                    "Random Question",
                    False,
                    f"Status code: {response.status_code}"
                )
        except Exception as e:
            return self.log_test("Random Question", False, f"Exception: {str(e)}")
    
    def test_user_registration(self):
        """Test user registration."""
        try:
            test_user = {
                "username": f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "email": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
                "password": "testpassword123"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/register",
                json=test_user
            )
            
            if response.status_code == 200:
                data = response.json()
                return self.log_test(
                    "User Registration",
                    True,
                    f"User created: {data.get('username')}"
                )
            else:
                return self.log_test(
                    "User Registration",
                    False,
                    f"Status code: {response.status_code}, Response: {response.text}"
                )
        except Exception as e:
            return self.log_test("User Registration", False, f"Exception: {str(e)}")
    
    def test_user_login(self):
        """Test user login."""
        try:
            login_data = {
                "username": "testing",
                "password": "testing"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                if token:
                    # Store token for authenticated tests
                    self.session.headers.update({'Authorization': f'Bearer {token}'})
                    return self.log_test(
                        "User Login",
                        True,
                        "Login successful, token received"
                    )
                else:
                    return self.log_test(
                        "User Login",
                        False,
                        "No access token received"
                    )
            else:
                return self.log_test(
                    "User Login",
                    False,
                    f"Status code: {response.status_code}, Response: {response.text}"
                )
        except Exception as e:
            return self.log_test("User Login", False, f"Exception: {str(e)}")
    
    def test_authenticated_endpoints(self):
        """Test endpoints that require authentication."""
        try:
            # Test current user info
            response = self.session.get(f"{self.base_url}/api/auth/me")
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Get Current User",
                    True,
                    f"User: {data.get('username')}"
                )
            else:
                self.log_test(
                    "Get Current User",
                    False,
                    f"Status code: {response.status_code}"
                )
            
            # Test evaluations endpoint
            response = self.session.get(f"{self.base_url}/api/evaluations")
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Get User Evaluations",
                    True,
                    f"Found {len(data)} evaluations"
                )
            else:
                self.log_test(
                    "Get User Evaluations",
                    False,
                    f"Status code: {response.status_code}"
                )
                
            return True
        except Exception as e:
            self.log_test("Authenticated Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def test_writing_evaluation(self):
        """Test writing evaluation endpoint."""
        try:
            evaluation_data = {
                "task_a_question": "Décrivez votre ville idéale.",
                "task_a_response": "Ma ville idéale serait une ville moderne avec beaucoup de parcs et de transports en commun. J'aimerais vivre dans un endroit où je peux facilement me déplacer à pied ou en vélo.",
                "task_b_question": "Discutez des avantages et inconvénients des réseaux sociaux.",
                "task_b_response": "Les réseaux sociaux ont des avantages et des inconvénients. D'un côté, ils permettent de rester connecté avec des amis et de partager des moments. De l'autre, ils peuvent créer une dépendance et affecter la vie privée."
            }
            
            response = self.session.post(
                f"{self.base_url}/api/evaluate",
                json=evaluation_data
            )
            
            if response.status_code == 200:
                data = response.json()
                return self.log_test(
                    "Writing Evaluation",
                    True,
                    f"Evaluation completed, score: {data.get('score')}"
                )
            else:
                return self.log_test(
                    "Writing Evaluation",
                    False,
                    f"Status code: {response.status_code}, Response: {response.text}"
                )
        except Exception as e:
            return self.log_test("Writing Evaluation", False, f"Exception: {str(e)}")
    
    def test_frontend_access(self):
        """Test frontend HTML access."""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                content = response.text
                if "TEF AI Practice Tool" in content:
                    return self.log_test(
                        "Frontend Access",
                        True,
                        "HTML content loaded successfully"
                    )
                else:
                    return self.log_test(
                        "Frontend Access",
                        False,
                        "HTML content doesn't contain expected title"
                    )
            else:
                return self.log_test(
                    "Frontend Access",
                    False,
                    f"Status code: {response.status_code}"
                )
        except Exception as e:
            return self.log_test("Frontend Access", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests and return summary."""
        logger.info("🚀 Starting TEF AI Practice Tool tests...")
        logger.info("=" * 60)
        
        # Run tests
        tests = [
            self.test_health_endpoint,
            self.test_status_endpoint,
            self.test_random_question,
            self.test_frontend_access,
            self.test_user_registration,
            self.test_user_login,
            self.test_authenticated_endpoints,
            self.test_writing_evaluation,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, False, f"Test execution failed: {str(e)}")
        
        # Generate summary
        self.generate_summary()
        
        return self.test_results
    
    def generate_summary(self):
        """Generate test summary."""
        logger.info("=" * 60)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            logger.info("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    logger.info(f"  - {result['test']}: {result['message']}")
        
        logger.info("=" * 60)
        
        # Save results to file
        self.save_results()
    
    def save_results(self):
        """Save test results to file."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"test_results_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            
            logger.info(f"💾 Test results saved to: {filename}")
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")

def main():
    """Main test function."""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    logger.info(f"Testing TEF AI Practice Tool at: {base_url}")
    
    # Check if server is running
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Server is running and accessible")
        else:
            logger.error(f"❌ Server responded with status code: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Cannot connect to server at {base_url}")
        logger.error(f"Make sure the server is running with: python run.py")
        sys.exit(1)
    
    # Run tests
    tester = TEFEvaluatorTester(base_url)
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    failed_tests = sum(1 for result in results if not result['success'])
    sys.exit(1 if failed_tests > 0 else 0)

if __name__ == "__main__":
    main()
