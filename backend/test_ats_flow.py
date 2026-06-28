import requests
import time
import subprocess
import os
import uuid

PORT = 8005
BASE_URL = f"http://127.0.0.1:{PORT}/api"

def run_tests():
    print("--- Starting ATS Flow Tests ---")
    env = os.environ.copy()
    
    # Check if GEMINI_API_KEY is available for real AI test
    has_gemini = "GEMINI_API_KEY" in env and env["GEMINI_API_KEY"].strip() != ""
    print(f"Gemini API Key configured: {has_gemini}")
    
    python_exe = os.path.join(os.path.abspath(os.path.dirname(__file__)), "venv", "Scripts", "python.exe")
    server_process = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--port", str(PORT)],
        cwd=os.path.abspath(os.path.dirname(__file__)),
        env=env
    )
    
    # Wait for server
    server_up = False
    for _ in range(20):
        try:
            r = requests.get(f"http://127.0.0.1:{PORT}")
            if r.status_code == 200:
                server_up = True
                break
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
            
    if not server_up:
        print("Failed to start server")
        server_process.kill()
        return

    try:
        # Register and login
        uid = str(uuid.uuid4())[:8]
        email = f"ats_{uid}@example.com"
        password = "Password123!"
        
        requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password, "name": "ATS Test User"})
        r_login = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
        token = r_login.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n1. Create Job Description")
        jd_req = requests.post(f"{BASE_URL}/job-description/", headers=headers, json={
            "description": "We are looking for an experienced Software Engineer skilled in Python, Django, REST APIs, and PostgreSQL. Machine learning experience is a plus."
        })
        jd_id = jd_req.json().get("id")
        print(f"JD ID: {jd_id} - Status: {jd_req.status_code}")
        
        print("\n2. Upload Resume")
        resume_txt = "John Doe\njohn@example.com\nSoftware Engineer with 4 years of experience. Expert in Python, Django, and RESTful APIs. Familiar with MySQL and PostgreSQL. Built scalable microservices."
        with open("test_resume.txt", "w") as f:
            f.write(resume_txt)
        
        with open("test_resume.txt", "rb") as f:
            files = {"file": ("test_resume.txt", f, "text/plain")}
            r_up = requests.post(f"{BASE_URL}/resume/upload", headers=headers, files=files)
        
        resume_id = r_up.json().get("id")
        print(f"Resume ID: {resume_id} - Status: {r_up.status_code}")
        
        print("\n3. Generate ATS Score and AI Suggestions")
        r_analyze = requests.post(f"{BASE_URL}/ats/analyze", headers=headers, json={
            "resume_id": resume_id,
            "job_description_id": jd_id
        })
        print(f"ATS Analyze Status: {r_analyze.status_code}")
        ats_result = r_analyze.json()
        ats_id = ats_result.get("id")
        
        print("\n--- ATS Results ---")
        print(f"Overall Score: {ats_result.get('final_score')}%")
        print(f"Keyword Score: {ats_result.get('keyword_score')}%")
        print(f"Semantic Score: {ats_result.get('semantic_score')}%")
        
        ai_suggestions = ats_result.get("ai_suggestions")
        if ai_suggestions:
            print("\nAI Suggestions:")
            print(f"- Strengths: {ai_suggestions.get('strengths', [])[:2]}")
            print(f"- Weaknesses: {ai_suggestions.get('weaknesses', [])[:2]}")
            print(f"- Improvement: {ai_suggestions.get('improvement_tips', [])[:2]}")
        else:
            print("\nAI Suggestions: Not generated.")

        print("\n4. PDF Report Download")
        r_pdf = requests.get(f"{BASE_URL}/ats/results/{ats_id}/pdf", headers=headers)
        if r_pdf.status_code == 200:
            print(f"PDF Download Success: {len(r_pdf.content)} bytes received.")
            with open("downloaded_report.pdf", "wb") as f:
                f.write(r_pdf.content)
            print("Saved as 'downloaded_report.pdf'")
        else:
            print(f"PDF Download Failed: {r_pdf.status_code}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        server_process.kill()
        for f in ["test_resume.txt", "downloaded_report.pdf"]:
            if os.path.exists(f):
                os.remove(f)
        print("\n--- ATS Flow Tests Finished ---")

if __name__ == "__main__":
    run_tests()
