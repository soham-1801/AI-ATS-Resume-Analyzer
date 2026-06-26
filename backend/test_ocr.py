import os
from app.services.resume_parser import ResumeParser

file_path = r"C:\Users\SOHAM MANGROLIYA\OneDrive\Desktop\ATS_KIRO\backend\uploads\resumes\20260611_111619_004cb9986c79_RajPandya1.pdf"
try:
    print("Parsing scanned PDF...")
    text = ResumeParser.parse(file_path)
    print(f"Extraction succeeded! Length: {len(text)}")
except Exception as e:
    print(f"Extraction failed: {e}")
