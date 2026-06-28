import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.ats_engine import ATSEngine

def test_scoring():
    print("--- ATS Scoring Correctness Test ---")
    
    jd = """We are looking for a Senior Software Engineer with strong experience in Python, Django, REST APIs, PostgreSQL, and AWS. 
The ideal candidate has experience building scalable microservices, deploying with Docker/Kubernetes, and writing robust unit tests."""

    resumes = [
        {
            "name": "High Quality (Exact Match)",
            "text": "Senior Software Engineer. Over 6 years of experience building scalable microservices and REST APIs using Python and Django. Managed databases using PostgreSQL and deployed applications on AWS using Docker and Kubernetes. Strong background in unit testing with pytest and CI/CD pipelines."
        },
        {
            "name": "Mid Quality (Partial Match)",
            "text": "Software Developer. 3 years of experience. Proficient in Python and Flask. Some experience with SQL databases and Git. I have built a few web applications and REST APIs. Familiar with basic cloud deployment."
        },
        {
            "name": "Poor Quality (Marketing - No Match)",
            "text": "Marketing Executive. Experienced in digital marketing, SEO, and social media campaigns. Managed Google Ads and Facebook marketing. Excellent communication and teamwork skills."
        },
        {
            "name": "Poor Quality (Very Short/Vague)",
            "text": "I am a hard worker. I know computer. Hire me."
        }
    ]
    
    for r in resumes:
        print(f"\nEvaluating: {r['name']}")
        try:
            score_data = ATSEngine.calculate_match(r['text'], jd)
            print(f"  Overall Final Score : {score_data['final_score']:.1f}%")
            print(f"  Keyword Score       : {score_data['keyword_score']:.1f}%")
            print(f"  Semantic Score      : {score_data['semantic_score']:.1f}%")
            print(f"  Matched Skills      : {len(score_data['matched_skills'])} found")
            print(f"  Missing Skills      : {len(score_data['missing_skills'])} missing")
        except Exception as e:
            print(f"  Error calculating score: {e}")

if __name__ == "__main__":
    test_scoring()
