import requests

BASE_URL = "http://localhost:8000/api"

def test_oauth_endpoints():
    print("=== STARTING OAUTH ROUTE VERIFICATION ===")

    # 1. Test Google OAuth code exchange fallback
    print("1. Testing Google OAuth code exchange callback...")
    google_res = requests.post(f"{BASE_URL}/auth/oauth/google", json={
        "code": "mock_google_auth_code",
        "redirect_uri": "http://localhost:5173/oauth/callback/google"
    })
    assert google_res.status_code == 200, f"Google OAuth exchange failed: {google_res.text}"
    google_data = google_res.json()
    assert "access_token" in google_data, "Missing access token"
    assert "refresh_token" in google_data, "Missing refresh token"
    google_token = google_data["access_token"]
    print("[OK] Google exchange successful")

    # Verify Google user info
    google_me = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {google_token}"})
    assert google_me.status_code == 200, f"Google /me failed: {google_me.text}"
    google_user = google_me.json()
    assert google_user["email"] == "google_dev_user@example.com", f"Expected mock email, got {google_user['email']}"
    assert google_user["oauth_provider"] == "google", f"Expected provider 'google', got {google_user['oauth_provider']}"
    print(f"[OK] Google mock user validated: {google_user['name']} ({google_user['email']})")

    # 2. Test GitHub OAuth code exchange fallback
    print("\n2. Testing GitHub OAuth code exchange callback...")
    github_res = requests.post(f"{BASE_URL}/auth/oauth/github", json={
        "code": "mock_github_auth_code",
        "redirect_uri": "http://localhost:5173/oauth/callback/github"
    })
    assert github_res.status_code == 200, f"GitHub OAuth exchange failed: {github_res.text}"
    github_data = github_res.json()
    assert "access_token" in github_data, "Missing access token"
    github_token = github_data["access_token"]
    print("[OK] GitHub exchange successful")

    # Verify GitHub user info
    github_me = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {github_token}"})
    assert github_me.status_code == 200, f"GitHub /me failed: {github_me.text}"
    github_user = github_me.json()
    assert github_user["email"] == "github_dev_user@example.com", f"Expected mock email, got {github_user['email']}"
    assert github_user["oauth_provider"] == "github", f"Expected provider 'github', got {github_user['oauth_provider']}"
    print(f"[OK] GitHub mock user validated: {github_user['name']} ({github_user['email']})")

    # 3. Test Apple OAuth code/token validation fallback
    print("\n3. Testing Apple Sign In token exchange callback...")
    apple_res = requests.post(f"{BASE_URL}/auth/oauth/apple", json={
        "code": "mock_apple_auth_code",
        "id_token": "mock_apple_id_token",
        "redirect_uri": "http://localhost:5173/oauth/callback/apple"
    })
    assert apple_res.status_code == 200, f"Apple Sign In exchange failed: {apple_res.text}"
    apple_data = apple_res.json()
    assert "access_token" in apple_data, "Missing access token"
    apple_token = apple_data["access_token"]
    print("[OK] Apple exchange successful")

    # Verify Apple user info
    apple_me = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {apple_token}"})
    assert apple_me.status_code == 200, f"Apple /me failed: {apple_me.text}"
    apple_user = apple_me.json()
    assert apple_user["email"] == "apple_dev_user@example.com", f"Expected mock email, got {apple_user['email']}"
    assert apple_user["oauth_provider"] == "apple", f"Expected provider 'apple', got {apple_user['oauth_provider']}"
    print(f"[OK] Apple mock user validated: {apple_user['name']} ({apple_user['email']})")

    print("\n=== ALL OAUTH ENDPOINTS PASSED VERIFICATION ===")

if __name__ == "__main__":
    test_oauth_endpoints()
