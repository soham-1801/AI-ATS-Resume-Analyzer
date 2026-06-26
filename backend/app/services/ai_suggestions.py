import os
import json
from google import genai
from dotenv import load_dotenv

# Load env variables from backend/.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

class AISuggestions:
    @staticmethod
    def generate_gemini_suggestions(
        resume_text: str,
        job_description: str,
        ats_score: float,
        matched_skills: list[str],
        missing_skills: list[str]
    ) -> dict:
        """
        Invokes Gemini 1.5 Flash to analyze candidate data and output
        structured recommendations in JSON matching the exact schema requirements.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("GEMINI_API_KEY environment variable not configured. Using fallback suggestions.")
            return AISuggestions.get_fallback_suggestions(missing_skills, ats_score)
            
        try:
            client = genai.Client(api_key=api_key)
            
            prompt = (
                f"You are an expert resume reviewer and ATS alignment optimization agent.\n"
                f"Analyze this candidate profile alignment data:\n\n"
                f"Candidate Resume Text (excerpt): {resume_text[:3000]}\n\n"
                f"Target Job Description (excerpt): {job_description[:3000]}\n\n"
                f"ATS Score: {ats_score}%\n"
                f"Matched Skills: {matched_skills}\n"
                f"Missing Skills: {missing_skills}\n\n"
                f"Based on this, generate tailored optimization suggestions in JSON format. The JSON must match this structure exactly:\n"
                f"{{\n"
                f"  \"summary_improvement\": \"A summary of improvements for the resume overall (3-4 sentences)\",\n"
                f"  \"missing_keywords\": [\"list of specific keywords or buzzwords to add\"],\n"
                f"  \"project_suggestions\": [\"2-3 bullet suggestions for new projects or modifying existing projects to show skills\"],\n"
                f"  \"experience_suggestions\": [\"2-3 bullet suggestions on rewording work experience to be impact-driven\"],\n"
                f"  \"ats_tips\": [\"3 specific formatting, structural, or scanning tips to increase ATS score\"]\n"
                f"}}\n\n"
                f"Ensure the JSON output is clean and parses perfectly."
            )
            
            # Enforce JSON output type
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            
            result_json = json.loads(response.text)
            return result_json
            
        except Exception as e:
            print(f"Gemini API execution failed: {e}. Reverting to fallback suggestions.")
            return AISuggestions.get_fallback_suggestions(missing_skills, ats_score)

    @staticmethod
    def get_fallback_suggestions(missing_skills: list[str], ats_score: float) -> dict:
        """Fallback suggestion payload when Gemini API is unavailable."""
        return {
            "summary_improvement": (
                "Optimize your resume summary section by explicitly aligning your profile summary "
                "with the target roles. Make sure to call out your technical skills near the top "
                "and focus on business impact and outcomes rather than task lists."
            ),
            "missing_keywords": missing_skills if missing_skills else ["CI/CD", "Docker", "AWS", "SQL", "Unit Testing"],
            "project_suggestions": [
                f"Develop a project implementing {missing_skills[0] if missing_skills else 'cloud computing frameworks'} to showcase hands-on experience.",
                "Create a multi-tiered backend architecture and deploy it using automated containers to demonstrate DevOps proficiency."
            ],
            "experience_suggestions": [
                "Structure experience using the STAR method (Situation, Task, Action, Result) with impact metrics.",
                "Replace passive phrases (e.g. 'was responsible for') with action verbs (e.g. 'Spearheaded', 'Optimized')."
            ],
            "ats_tips": [
                "Use standard, clear section headers like 'Professional Experience' and 'Skills'.",
                "Ensure your document formatting is simple, avoiding multi-columns, text boxes, or icons.",
                "Export and save your final resume file in PDF or DOCX format for clean scanning."
            ]
        }

    @classmethod
    def generate_suggestions(
        cls,
        resume_text: str,
        job_description: str,
        matched_skills: list[str],
        missing_skills: list[str],
        score: float
    ) -> str:
        """
        Legacy text-based suggestions wrapper. Integrates the Gemini structured output
        and formats it as a clean, styled Markdown string for database compatibility.
        """
        data = cls.generate_gemini_suggestions(
            resume_text=resume_text,
            job_description=job_description,
            ats_score=score,
            matched_skills=matched_skills,
            missing_skills=missing_skills
        )
        
        # Format the JSON data structure into Markdown
        markdown_output = []
        markdown_output.append(f"### Summary Improvement Suggestions\n{data.get('summary_improvement', '')}\n")
        
        if data.get("missing_keywords"):
            markdown_output.append("### Recommended Keywords to Add")
            markdown_output.append(", ".join([f"**{kw}**" for kw in data["missing_keywords"]]) + "\n")
            
        if data.get("project_suggestions"):
            markdown_output.append("### Project Recommendations")
            for proj in data["project_suggestions"]:
                markdown_output.append(f"* {proj}")
            markdown_output.append("")
            
        if data.get("experience_suggestions"):
            markdown_output.append("### Experience Formatting Tips")
            for exp in data["experience_suggestions"]:
                markdown_output.append(f"* {exp}")
            markdown_output.append("")
            
        if data.get("ats_tips"):
            markdown_output.append("### General ATS Optimizations")
            for tip in data["ats_tips"]:
                markdown_output.append(f"* {tip}")
            markdown_output.append("")
            
        return "\n".join(markdown_output)

    @staticmethod
    def rewrite_resume_section(section: str, content: str) -> str:
        """
        Rewrite a resume section (summary, experience, project, skills)
        to make it professional and impactful using Gemini 1.5 Flash.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return f"[Polished Fallback] {content.strip()} (Tip: Add a strong action verb or metrics to demonstrate impact)"
            
        try:
            client = genai.Client(api_key=api_key)
            
            section_lower = section.lower()
            if "summary" in section_lower:
                role_prompt = "Rewrite this professional resume summary to be modern, concise, and focused on business impact and technical expertise."
            elif "experience" in section_lower:
                role_prompt = "Rewrite this work experience description/bullet point to use strong action verbs and format achievements using the STAR methodology with metrics if possible."
            elif "project" in section_lower:
                role_prompt = "Rewrite this project description to clearly highlight technical stack, architectural challenge solved, and the engineering outcome."
            elif "skill" in section_lower:
                role_prompt = "Clean up, format, and categorize this skills list to be presentable and structured for ATS readability."
            else:
                role_prompt = "Polishing and rewriting this resume section to be highly professional and impactful."

            prompt = (
                f"{role_prompt}\n\n"
                f"Original Content:\n{content}\n\n"
                f"Provide ONLY the rewritten improved text. Do not add conversational intro, comments, or explanations."
            )
            
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Gemini Rewrite API execution failed: {e}")
            return f"[Fallback Optimization] {content.strip()} (Add action verbs and outcomes to improve scan value)"

