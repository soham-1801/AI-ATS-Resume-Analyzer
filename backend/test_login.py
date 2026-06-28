import requests
import time
import subprocess
import os
import uuid

PORT = 8003
BASE_URL = f"http://127.0.0.1:{PORT}/api"
ROOT_URL = f"http://127.0.0.1:{PORT}"

def wait_for_server():
    for _ in range(20):
        try:
            r = requests.get(ROOT_URL)
            if r.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
    return False

def run_tests():
    print("--- Starting Login Tests ---")
    
    env = os.environ.copy()
    python_exe = os.path.join(os.path.abspath(os.path.dirname(__file__)), "venv", "Scripts", "python.exe")
    server_process = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--port", str(PORT)],
        cwd=os.path.abspath(os.path.dirname(__file__)),
        env=env
    )
    
    if not wait_for_server():
        print("Failed to start server")
        server_process.kill()
        return

    try:
        uid = str(uuid.uuid4())[:8]
        email = f"user_{uid}@example.com"
        password = "Password123!"
        
        print("\n1. Testing Login for NON-EXISTENT user")
        r_fail = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "doesnotexist@example.com",
            "password": "Password123!"
        })
        print(f"Status Code: {r_fail.status_code}")
        print(f"Response: {r_fail.text}")
        
        print("\n2. Registering NEW user")
        r_reg = requests.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password,
            "name": "Login Test User"
        })
        print(f"Status Code: {r_reg.status_code}")
        print(f"Response: {r_reg.text}")
        
        print("\n3. Testing Login for EXISTING user")
        r_success = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        print(f"Status Code: {r_success.status_code}")
        if r_success.status_code == 200:
            print("Login successful, token received.")
        else:
            print(f"Response: {r_success.text}")
            
        print("\n4. Testing duplicate registration (409 Conflict check)")
        r_dup = requests.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password,
            "name": "Login Test User"
        })
        print(f"Status Code: {r_dup.status_code}")
        print(f"Response: {r_dup.text}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        server_process.kill()
        print("\n--- Tests Finished ---")

if __name__ == "__main__":
    run_tests()
