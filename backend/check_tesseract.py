import os

common_paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe"),
    os.path.expandvars(r"%PROGRAMFILES%\Tesseract-OCR\tesseract.exe")
]

found = False
for path in common_paths:
    if os.path.exists(path):
        print(f"FOUND Tesseract at: {path}")
        found = True
        break

if not found:
    print("Tesseract binary NOT found in common Windows paths.")
