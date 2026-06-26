import sys
import os

# Append the parent directory of backend/app to Python path to import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ats_engine import ATSEngine

def run_formatting_tests():
    print("=== STARTING ATS FORMATTING ENGINE TEST ===")
    
    # 1. Create a dummy resume text with multiple formatting issues:
    # - Email exists, phone exists, but LinkedIn is missing (-5%)
    # - Professional Summary is missing (-15%)
    # - Orphan heading: "Education" is at the bottom of Page 1 (before \f) (-5%)
    # - Split bullet list: Page 2 ends with a bullet item without punctuation, and Page 3 starts with continuation text (-3%)
    # - Spacing inconsistent: contains 3 newlines in a row (-3%)
    # - Margins inconsistent: bullets have 0, 4, and 8 leading spaces (-3%)
    # - Capitalization inconsistent: one heading is "WORK EXPERIENCE" (all caps) and another is "Skills" (title case) (-2%)
    
    resume_text = (
        "Raj Pandya\n"
        "Email: raj@example.com\n"
        "Phone: 123-456-7890\n"
        "\n\n\n"  # spacing inconsistent
        "WORK EXPERIENCE\n"  # all caps
        "- Senior Developer (2024 - Present): Developed backend systems using FastAPI.\n"
        "    - Managed databases.\n"
        "        - Integrated API endpoints.\n"  # margins inconsistent (0, 4, 8 spaces)
        "Education\f"  # orphan heading (at bottom of Page 1)
        "BS in Computer Science from Tech University (2020 - 2024)\n"
        "\n"
        "Skills\n"  # title case (capitalization inconsistent)
        "- Python\n"
        "- SQL\n"
        "- JavaScript\n"
        "- React\n"
        "- Git\n"
        "- Docker\n"
        "- AWS\n"
        "- HTML\n"
        "- CSS\n"
        "- Node.js\n"
        "- TypeScript\n"
        "- FastAPI\n"
        "- PostgreSQL\n"
        "- Spark\n"
        "- Pandas\n"
        "\n"
        "Projects\n"
        "- ATS Resume Parser: Developed parsing tool\f"  # Split bullet item ends here without punctuation
        "built with python and react to calculate compatibility\n"  # Page 3 starts with continuation text
    )
    
    job_description = (
        "We are looking for a Software Engineer with experience in Python, SQL, JavaScript, React, Git, Docker, and AWS."
    )
    
    # Calculate match
    result = ATSEngine.calculate_match(resume_text, job_description)
    
    # Extract formatting breakdown
    formatting_category = next(c for c in result["category_breakdown"] if c["name"] == "Formatting")
    
    print(f"Calculated Formatting Score: {formatting_category['score']}%")
    print("\nCalculated Diagnostics Reason:\n")
    print(formatting_category["why_this_score"])
    print("\nAction Items Suggested:")
    for rec in formatting_category["recommendations"]:
        print(f"- {rec}")
        
    # Assertions
    assert formatting_category["score"] < 100, "Score should have deductions"
    assert any("orphan heading" in issue for issue in formatting_category["issues"]), "Should detect orphan heading"
    assert any("spacing" in issue for issue in formatting_category["issues"]), "Should detect spacing issue"
    assert any("margin" in issue for issue in formatting_category["issues"]), "Should detect margins issue"
    assert any("casing" in issue for issue in formatting_category["issues"]), "Should detect casing issue"
    assert any("LinkedIn" in issue for issue in formatting_category["issues"]), "Should detect missing LinkedIn"
    
    print("\n=== ALL ATS FORMATTING ENGINE TESTS PASSED ===")

if __name__ == "__main__":
    run_formatting_tests()
