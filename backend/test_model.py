import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Hello"
    )
    print("1.5-flash:", response.text)
except Exception as e:
    print("1.5-flash Error:", e)

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello"
    )
    print("2.5-flash:", response.text)
except Exception as e:
    print("2.5-flash Error:", e)
