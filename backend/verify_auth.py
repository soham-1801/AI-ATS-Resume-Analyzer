import sys
import requests
import random
import string

BASE_URL = "http://localhost:8000/api"

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def run_tests():
    print("=== STARTING AUTH VERIFICATION ===")
    
    # Generate random email to avoid duplicate errors
    email = f"user_{random_string()}@example.com"
    password = "SecurePassword123!"
    name = "QA tester"
    
    print(f"1. Registering user {email}...")
    reg_r = requests.post(f"{BASE_URL}/auth/register", json={
        "name": name,
        "email": email,
        "password": password
    })
    assert reg_r.status_code == 201, f"Registration failed: {reg_r.text}"
    print("[OK] Registration successful")
    
    print("2. Logging in with credentials...")
    login_r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_r.status_code == 200, f"Login failed: {login_r.text}"
    login_data = login_r.json()
    assert "access_token" in login_data, "No access token"
    assert "refresh_token" in login_data, "No refresh token"
    access_token = login_data["access_token"]
    refresh_token = login_data["refresh_token"]
    print("[OK] Login successful, retrieved tokens")
    
    print("3. Querying /me with invalid token...")
    me_invalid = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": "Bearer fake_token"})
    assert me_invalid.status_code == 401, f"Invalid token accepted: {me_invalid.text}"
    print("[OK] Invalid token rejected with 401")
    
    print("4. Querying /me with correct access token...")
    me_valid = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me_valid.status_code == 200, f"Valid token rejected: {me_valid.text}"
    me_data = me_valid.json()
    assert me_data["email"] == email, "Email mismatch"
    print("[OK] Access token validated successfully")
    
    print("5. Refreshing token using refresh token...")
    refresh_r = requests.post(f"{BASE_URL}/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert refresh_r.status_code == 200, f"Token refresh failed: {refresh_r.text}"
    refresh_data = refresh_r.json()
    assert "access_token" in refresh_data, "No new access token"
    assert "refresh_token" in refresh_data, "No new refresh token"
    new_access_token = refresh_data["access_token"]
    print("[OK] Token refreshed successfully")
    
    print("6. Querying /me with new access token...")
    me_new = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {new_access_token}"})
    assert me_new.status_code == 200, f"New access token rejected: {me_new.text}"
    print("[OK] New access token validated successfully")
    
    print("7. Testing OAuth login (Google)...")
    oauth_email = f"google_{random_string()}@example.com"
    oauth_r = requests.post(f"{BASE_URL}/auth/oauth", json={
        "provider": "google",
        "oauth_id": "google_test_12345",
        "email": oauth_email,
        "name": "Google Tester"
      })
    assert oauth_r.status_code == 200, f"OAuth login failed: {oauth_r.text}"
    oauth_data = oauth_r.json()
    assert "access_token" in oauth_data, "No OAuth access token"
    oauth_access_token = oauth_data["access_token"]
    print("[OK] OAuth login successful")
    
    print("8. Querying /me for OAuth user...")
    me_oauth = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {oauth_access_token}"})
    assert me_oauth.status_code == 200, f"OAuth user /me failed: {me_oauth.text}"
    me_oauth_data = me_oauth.json()
    assert me_oauth_data["oauth_provider"] == "google", "Provider mismatch"
    assert me_oauth_data["oauth_id"] == "google_test_12345", "OAuth ID mismatch"
    print("[OK] OAuth user validated, columns correctly set")
    
    print("=== ALL TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_tests()
