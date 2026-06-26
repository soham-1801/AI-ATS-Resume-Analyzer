import sys
import os
import unittest
from fastapi.testclient import TestClient

# Add parent directory of 'app' to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database.database import Base, engine, SessionLocal
from app.models.user import User

class TestPasswordValidation(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()
        # Clean any existing test users
        self.db.query(User).filter(User.email.in_([
            "test_strength@example.com",
            "test_strength2@example.com"
        ])).delete(synchronize_session=False)
        self.db.commit()
        
        self.client = TestClient(app)

    def tearDown(self):
        self.db.query(User).filter(User.email.in_([
            "test_strength@example.com",
            "test_strength2@example.com"
        ])).delete(synchronize_session=False)
        self.db.commit()
        self.db.close()

    def test_registration_password_strength(self):
        # 1. Test short password
        response = self.client.post("/api/auth/register", json={
            "name": "Test User",
            "email": "test_strength@example.com",
            "password": "Ab1!"  # < 8 chars
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("at least 8 characters long", response.json()["detail"])

        # 2. Test missing uppercase
        response = self.client.post("/api/auth/register", json={
            "name": "Test User",
            "email": "test_strength@example.com",
            "password": "password123!"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("uppercase letter", response.json()["detail"])

        # 3. Test missing lowercase
        response = self.client.post("/api/auth/register", json={
            "name": "Test User",
            "email": "test_strength@example.com",
            "password": "PASSWORD123!"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("lowercase letter", response.json()["detail"])

        # 4. Test missing number
        response = self.client.post("/api/auth/register", json={
            "name": "Test User",
            "email": "test_strength@example.com",
            "password": "Password!"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("number", response.json()["detail"])

        # 5. Test missing special character
        response = self.client.post("/api/auth/register", json={
            "name": "Test User",
            "email": "test_strength@example.com",
            "password": "Password123"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("special character", response.json()["detail"])

        # 6. Test successful registration
        response = self.client.post("/api/auth/register", json={
            "name": "Test User",
            "email": "test_strength@example.com",
            "password": "Password123!"
        })
        self.assertEqual(response.status_code, 201)

    def test_password_change_validation(self):
        # Register a user
        self.client.post("/api/auth/register", json={
            "name": "Test User",
            "email": "test_strength@example.com",
            "password": "Password123!"
        })

        # Login to get JWT
        login_res = self.client.post("/api/auth/login", json={
            "email": "test_strength@example.com",
            "password": "Password123!"
        })
        self.assertEqual(login_res.status_code, 200)
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Test change password with incorrect old password
        response = self.client.post("/api/auth/change-password", json={
            "old_password": "WrongPassword!",
            "new_password": "NewPassword123!"
        }, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Incorrect old password", response.json()["detail"])

        # 2. Test change password with weak new password
        response = self.client.post("/api/auth/change-password", json={
            "old_password": "Password123!",
            "new_password": "short"
        }, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("at least 8 characters long", response.json()["detail"])

        # 3. Test successful change password
        response = self.client.post("/api/auth/change-password", json={
            "old_password": "Password123!",
            "new_password": "NewPassword123!"
        }, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Password changed successfully.")

    def test_password_reset_flow(self):
        # Register user
        self.client.post("/api/auth/register", json={
            "name": "Test User",
            "email": "test_strength@example.com",
            "password": "Password123!"
        })

        # Request password reset
        req_res = self.client.post("/api/auth/reset-password-request", json={
            "email": "test_strength@example.com"
        })
        self.assertEqual(req_res.status_code, 200)
        self.assertIn("debug_token", req_res.json())
        token = req_res.json()["debug_token"]

        # Confirm password reset with weak password
        conf_res = self.client.post("/api/auth/reset-password", json={
            "email": "test_strength@example.com",
            "token": token,
            "new_password": "weak"
        })
        self.assertEqual(conf_res.status_code, 400)
        self.assertIn("at least 8 characters long", conf_res.json()["detail"])

        # Confirm password reset with invalid token
        conf_res = self.client.post("/api/auth/reset-password", json={
            "email": "test_strength@example.com",
            "token": "INVALID",
            "new_password": "ResetPassword123!"
        })
        self.assertEqual(conf_res.status_code, 400)
        self.assertIn("Invalid or expired reset token", conf_res.json()["detail"])

        # Confirm password reset with valid token and strong password
        conf_res = self.client.post("/api/auth/reset-password", json={
            "email": "test_strength@example.com",
            "token": token,
            "new_password": "ResetPassword123!"
        })
        self.assertEqual(conf_res.status_code, 200)

        # Login with new password
        login_res = self.client.post("/api/auth/login", json={
            "email": "test_strength@example.com",
            "password": "ResetPassword123!"
        })
        self.assertEqual(login_res.status_code, 200)

if __name__ == "__main__":
    unittest.main()
