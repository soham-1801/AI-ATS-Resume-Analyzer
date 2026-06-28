import os
import json
from unittest.mock import patch, MagicMock
import sys

# Ensure backend directory is in path so absolute imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.ai_suggestions import AISuggestions

# Mock class for Gemini Response
class MockResponse:
    def __init__(self, text):
        self.text = text

# Mock GenerateContent
def mock_generate_content(*args, **kwargs):
    print("[MOCK] model.generate_content was called!")
    mock_json = {
        "summary_improvement": "This is a REAL AI SUGGESTION from the mock.",
        "missing_keywords": ["AI", "Mocking"],
        "project_suggestions": ["Create a mock project"],
        "experience_suggestions": ["Re-word as mock expert"],
        "ats_tips": ["Use standard fonts"]
    }
    return MockResponse(json.dumps(mock_json))

def test_ai_suggestions():
    print("--- Testing AI Suggestions Flow ---")
    
    resume_text = "Experienced software engineer"
    job_description = "Software engineer"
    ats_score = 80.0
    matched_skills = ["Python"]
    missing_skills = ["Django"]

    # 1. Test Without API Key (Fallback)
    print("\n1. Testing Path: API Key Missing -> Graceful Fallback")
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
        
    result_fallback = AISuggestions.generate_gemini_suggestions(
        resume_text, job_description, ats_score, matched_skills, missing_skills
    )
    print(f"Result (Fallback): {result_fallback.get('summary_improvement', 'Not Found')}")

    # 2. Test With API Key (Real AI)
    print("\n2. Testing Path: API Key Present -> Real AI Suggestions")
    os.environ["GEMINI_API_KEY"] = "DUMMY_KEY_FOR_TESTING"
    
    # Patch the genai.Client
    with patch('app.services.ai_suggestions.genai.Client') as mock_client_class:
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = mock_generate_content
        mock_client_class.return_value = mock_client
        
        result_real = AISuggestions.generate_gemini_suggestions(
            resume_text, job_description, ats_score, matched_skills, missing_skills
        )
        print(f"Result (Real AI Mocked): {result_real.get('summary_improvement', 'Not Found')}")
        assert "REAL AI SUGGESTION" in result_real.get('summary_improvement', '')
        
    print("\n--- Both paths tested successfully! ---")

if __name__ == "__main__":
    test_ai_suggestions()
