import requests
import time
import subprocess
import os
import uuid

PORT = 8002
BASE_URL = f"http://127.0.0.1:{PORT}/api"
ROOT_URL = f"http://127.0.0.1:{PORT}"

def wait_for_server():
    for _ in range(20):
        try:
            r = requests.get(ROOT_URL)
            if r.status_code == 200:
                print("Server is up!")
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
    print("Failed to start server.")
    return False

def test_endpoints():
    print("--- Starting Endpoint Verification ---")
    
    # 1. Start server
    print("Starting FastAPI server on port", PORT)
    env = os.environ.copy()
    python_exe = os.path.join(os.path.abspath(os.path.dirname(__file__)), "venv", "Scripts", "python.exe")
    server_process = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--port", str(PORT)],
        cwd=os.path.abspath(os.path.dirname(__file__)),
        env=env
    )
    
    if not wait_for_server():
        server_process.kill()
        return

    try:
        # Generate unique user
        uid = str(uuid.uuid4())[:8]
        email = f"test_{uid}@example.com"
        password = "Password123!"
        
        print("\n1. All endpoints open (Basic public test)")
        r = requests.get(ROOT_URL)
        if r.status_code == 200:
            print(" - Root endpoint works.")
        else:
            print(" - Root endpoint failed:", r.status_code)
            
        print("\n2. Register and Login (Auth)")
        # Register
        r_reg = requests.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password,
            "name": "Test User"
        })
        if r_reg.status_code == 201:
            print(" - Registration successful.")
        else:
            print(" - Registration failed:", r_reg.status_code, r_reg.text)
            
        # Login
        r_login = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        
        token = ""
        if r_login.status_code == 200:
            token = r_login.json().get("access_token")
            print(" - Login successful. Got token.")
        else:
            print(" - Login failed:", r_login.status_code, r_login.text)
            
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n3. Protected endpoints working with Authorize token")
        # Try without token
        r_me_fail = requests.get(f"{BASE_URL}/auth/me")
        if r_me_fail.status_code == 403 or r_me_fail.status_code == 401:
            print(" - Protected endpoint correctly rejected request without token.")
        
        # Try with token
        r_me_success = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if r_me_success.status_code == 200:
            print(f" - Protected endpoint accepted token. Hello, {r_me_success.json().get('name')}")
        else:
            print(" - Protected endpoint failed with token:", r_me_success.status_code)
            
        print("\n4. Test Resume Upload & ATS Analysis")
        # Create JD
        r_jd = requests.post(f"{BASE_URL}/job-description/", headers=headers, json={
            "description": "We are looking for a software engineer with Python and React experience."
        })
        jd_id = r_jd.json().get("id")
        
        # Upload resume
        resume_path = "test_resume.txt"
        with open(resume_path, "w") as f:
            f.write("Jane Doe\njanedoe@example.com\nExperienced Software Engineer with Python and React skills.")
            
        with open(resume_path, "rb") as f:
            files = {"file": ("test_resume.txt", f, "text/plain")}
            r_up = requests.post(f"{BASE_URL}/resume/upload", headers=headers, files=files)
            
        resume_id = r_up.json().get("id")
        
        if r_up.status_code == 201:
            print(" - Resume uploaded successfully.")
        else:
            print(" - Resume upload failed:", r_up.status_code, r_up.text)

        # Analyze
        r_analyze = requests.post(f"{BASE_URL}/ats/analyze", headers=headers, json={
            "resume_id": resume_id,
            "job_description_id": jd_id
        })
        
        ats_id = r_analyze.json().get("id")
        
        print("\n5. Test PDF Endpoint Download")
        r_pdf = requests.get(f"{BASE_URL}/ats/results/{ats_id}/pdf", headers=headers)
        if r_pdf.status_code == 200:
            content_type = r_pdf.headers.get("Content-Type")
            if "application/pdf" in content_type:
                print(" - PDF generated and downloaded successfully! Size:", len(r_pdf.content), "bytes.")
            else:
                print(" - Endpoint returned 200 but content type is not PDF:", content_type)
        else:
            print(" - PDF generation failed:", r_pdf.status_code, r_pdf.text)
            
    except Exception as e:
        print(f"Test script encountered an error: {e}")
    finally:
        server_process.kill()
        if os.path.exists("test_resume.txt"):
            os.remove("test_resume.txt")
        print("\n--- Verification Finished ---")

if __name__ == "__main__":
    test_endpoints()
