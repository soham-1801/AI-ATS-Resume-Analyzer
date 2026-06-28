import requests
import time
import subprocess
import os
import uuid

PORT = 8007
BASE_URL = f"http://127.0.0.1:{PORT}/api"

def start_server():
    env = os.environ.copy()
    python_exe = os.path.join(os.path.abspath(os.path.dirname(__file__)), "venv", "Scripts", "python.exe")
    server_process = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--port", str(PORT)],
        cwd=os.path.abspath(os.path.dirname(__file__)),
        env=env
    )
    
    for _ in range(20):
        try:
            r = requests.get(f"http://127.0.0.1:{PORT}")
            if r.status_code == 200:
                return server_process
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
            
    server_process.kill()
    return None

def run_tests():
    print("--- Starting Restart Recovery Test ---")
    
    # PHASE 1: Initial Start & Data Creation
    print("\n[Phase 1] Starting Server for the first time...")
    server = start_server()
    if not server:
        print("Failed to start server.")
        return
        
    try:
        uid = str(uuid.uuid4())[:8]
        email = f"recovery_{uid}@example.com"
        password = "Password123!"
        
        # Register and Login
        print("Registering user and getting JWT...")
        requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password, "name": "Recovery User"})
        r_login = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
        token = r_login.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create Data
        print("Creating Job Description data...")
        r_jd = requests.post(f"{BASE_URL}/job-description/", headers=headers, json={"description": "Restart recovery test JD."})
        jd_id = r_jd.json().get("id")
        
        print("Data created successfully.")
    except Exception as e:
        print(f"Error in Phase 1: {e}")
        server.kill()
        return
        
    # PHASE 2: Restart Server
    print("\n[Phase 2] Shutting down the server...")
    server.kill()
    time.sleep(2) # ensure port is freed
    
    print("Restarting the server...")
    server2 = start_server()
    if not server2:
        print("Failed to restart server.")
        return
        
    # PHASE 3: Verification
    print("\n[Phase 3] Verifying Data and JWT Integrity after Restart...")
    try:
        # Check JWT Validity
        print("Checking if old JWT is still valid...")
        r_me = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if r_me.status_code == 200:
            print(f" -> SUCCESS: Token valid. Logged in as: {r_me.json().get('name')}")
        else:
            print(f" -> FAILURE: Token invalid. Status: {r_me.status_code}")
            
        # Check Data Integrity
        print("Checking if database data persisted...")
        r_jds = requests.get(f"{BASE_URL}/job-description/all", headers=headers)
        jd_exists = False
        if r_jds.status_code == 200:
            for jd in r_jds.json():
                if jd.get("id") == jd_id:
                    jd_exists = True
                    break
                    
        if jd_exists:
            print(f" -> SUCCESS: Database data is intact! (Found JD ID: {jd_id})")
        else:
            print(" -> FAILURE: Database data was lost or unreadable.")
            
    except Exception as e:
        print(f"Error in Phase 3: {e}")
    finally:
        server2.kill()
        print("\n--- Restart Recovery Test Finished ---")

if __name__ == "__main__":
    run_tests()
