import asyncio
import httpx
import time

URL = "http://127.0.0.1:8000/api/resume/upload/"
CONCURRENT_UPLOADS = 15

async def upload_file(client, index):
    # Create a dummy PDF file content in memory
    # Actually, the endpoint expects a valid PDF file. Let's create a minimal valid PDF structure.
    dummy_pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >>\nendobj\n4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n5 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 12 Tf\n72 712 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000219 00000 n \n0000000307 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n397\n%%EOF\n"
    
    files = {
        'file': (f'test_resume_{index}.pdf', dummy_pdf_content, 'application/pdf')
    }
    
    # We might need an Authorization header if the endpoint is protected, but let's check if the endpoint is protected.
    # Currently /api/resume/upload/ uses Depends(get_current_user).
    # Since we don't have a valid JWT token easily available here, let's login first to get one.
    return files

async def main():
    print("Logging in to get a token...")
    async with httpx.AsyncClient() as client:
        # First, register or login a test user
        user_data = {"email": "test_concurrent@example.com", "password": "password123", "full_name": "Test User"}
        
        try:
            await client.post("http://127.0.0.1:8000/api/auth/register", json=user_data)
        except Exception:
            pass

        # Login
        login_data = {"username": "test_concurrent@example.com", "password": "password123"}
        login_res = await client.post("http://127.0.0.1:8000/api/auth/login", data=login_data)
        
        if login_res.status_code != 200:
            print("Failed to login:", login_res.text)
            return

        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"Starting {CONCURRENT_UPLOADS} concurrent uploads...")
        start_time = time.time()
        
        # Prepare dummy files
        tasks = []
        for i in range(CONCURRENT_UPLOADS):
            files = await upload_file(client, i)
            # Make the request
            # We don't send Job Description here, just the file to see if it parses. Wait, upload endpoint might require more data if it does ATS check.
            # Usually upload just parses and saves to DB. Let's send only the file.
            task = client.post(URL, headers=headers, files=files, timeout=60.0)
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        
        success_count = 0
        error_count = 0
        
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                print(f"Request {i} failed with exception: {res}")
                error_count += 1
            else:
                if res.status_code == 200:
                    success_count += 1
                else:
                    print(f"Request {i} failed with status {res.status_code}: {res.text}")
                    error_count += 1
                    
        print(f"\\nTotal Time: {end_time - start_time:.2f} seconds")
        print(f"Successful: {success_count}")
        print(f"Failed: {error_count}")

if __name__ == "__main__":
    asyncio.run(main())
