import spacy
import spacy.cli
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.services.skill_extractor import SkillExtractor

# Lazy loader for spaCy to keep startup times fast
_nlp = None


def get_nlp_model():
    """Dynamically load or download the spaCy model to prevent runtime failures."""
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("spaCy model 'en_core_web_sm' not found. Downloading...")
            spacy.cli.download("en_core_web_sm")
            _nlp = spacy.load("en_core_web_sm")
    return _nlp


class ATSEngine:
    @staticmethod
    def extract_name(resume_text: str, fallback_name: str) -> str:
        """Extracts candidate name from the top of the resume using heuristics and NER."""
        if not resume_text or not resume_text.strip():
            return fallback_name
            
        # 1. Primary Heuristic: First reasonable line (highly accurate for resumes)
        try:
            lines = [line.strip() for line in resume_text[:500].split('\n') if line.strip()]
            invalid_words = ["resume", "curriculum", "cv", "email", "phone", "mobile", "address", "page", "contact"]
            for line in lines:
                # Clean markdown characters that might interfere
                clean_line = line.replace('*', '').replace('_', '').replace('#', '').replace('`', '').strip()
                if not clean_line or clean_line.lower() in ["json", "markdown", "html", "text"]:
                    continue
                if any(kw in clean_line.lower() for kw in invalid_words) or "@" in clean_line or sum(c.isdigit() for c in clean_line) > 0:
                    continue
                words = clean_line.split()
                if 1 <= len(words) <= 5:
                    return clean_line.title()
        except Exception as e:
            print(f"Name extraction heuristic error: {e}")

        # 2. Fallback to NER if heuristic fails
        try:
            nlp = get_nlp_model()
            
            # Try NER on original text
            doc = nlp(resume_text[:500])
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    clean_name = ent.text.strip().split('\n')[0].title()
                    if 2 <= len(clean_name) <= 40 and clean_name.lower() not in ["resume", "curriculum vitae", "cv"]:
                        return clean_name
                        
            # Try NER on title-cased text
            doc_title = nlp(resume_text[:500].title())
            for ent in doc_title.ents:
                if ent.label_ == "PERSON":
                    clean_name = ent.text.strip().split('\n')[0].title()
                    if 2 <= len(clean_name) <= 40 and clean_name.lower() not in ["resume", "curriculum vitae", "cv"]:
                        return clean_name
        except Exception as e:
            print(f"Name extraction NER error: {e}")
            
        return fallback_name

    @staticmethod
    def extract_email(resume_text: str, fallback_email: str) -> str:
        """Extracts candidate email from the resume using regex."""
        if not resume_text or not resume_text.strip():
            return fallback_email
            
        import re
        # Standard email regex pattern
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        try:
            # Search in the entire document
            match = re.search(email_pattern, resume_text)
            if match:
                return match.group(0).lower()
        except Exception as e:
            print(f"Email extraction error: {e}")
            
        return fallback_email

    @staticmethod
    def extract_job_title(jd_text: str, fallback_title: str) -> str:
        """Extracts job title from the top of the job description using heuristics."""
        if not jd_text or not jd_text.strip():
            return fallback_title
            
        try:
            lines = [line.strip() for line in jd_text[:1000].split('\n') if line.strip()]
            title_keywords = ["engineer", "developer", "analyst", "manager", "designer", "scientist", 
                              "architect", "consultant", "administrator", "specialist", "director", 
                              "executive", "coordinator", "lead", "associate", "intern", "technician", 
                              "programmer", "officer", "assistant", "clerk", "representative", "strategist", "expert",
                              "doctor", "teacher", "professor", "nurse", "accountant", "auditor"]
            invalid_words = ["about", "we are", "description", "requirements", "responsibilities", "role", "looking for", "you will", "design", "build", "create", "implement", "optimize", "work"]
            remove_words_from_title = ["uploaded", "profile", "job", "description", "resume", "cv", "candidate", "role", "position", "for", "the", "a", "an"]
            
            for line in lines:
                # Clean markdown characters
                clean_line = line.replace('*', '').replace('_', '').replace('#', '').replace('`', '').strip()
                if not clean_line or clean_line.lower() in ["json", "markdown", "html", "text"]:
                    continue
                
                lower_line = clean_line.lower()
                
                # Check for verbs indicating responsibilities
                if any(lower_line.startswith(kw) for kw in invalid_words):
                    continue
                    
                # If the line is short enough and contains a job title keyword
                words = clean_line.split()
                if len(words) <= 8:
                    if any(kw in lower_line for kw in title_keywords):
                        cleaned_words = [w for w in words if w.lower() not in remove_words_from_title]
                        if cleaned_words:
                            return " ".join(cleaned_words).title()
                        return clean_line.title()
            
            # Fallback heuristic: search for the first title keyword in the text
            import re
            text_chunk = jd_text[:500].replace('\n', ' ')
            words = text_chunk.split()
            for i, word in enumerate(words):
                clean_word = word.lower().strip('.,;:!?"()')
                if clean_word in title_keywords:
                    # Extract up to 2 words before and 1 word after
                    start = max(0, i - 2)
                    end = min(len(words), i + 2)
                    extracted = " ".join(words[start:end])
                    extracted = re.sub(r'[^a-zA-Z\s]', '', extracted).title()
                    # Clean common stop words at the ends
                    extracted_words = [w for w in extracted.split() if w.lower() not in ['a', 'an', 'the', 'to', 'for', 'we', 'are', 'hiring', 'looking', 'in', 'our', 'team']]
                    if extracted_words:
                        return " ".join(extracted_words)
        except Exception as e:
            print(f"Job title extraction error: {e}")
            
        return fallback_title

    @staticmethod
    def calculate_match(resume_text: str, job_description: str) -> dict:
        """
        Calculates NLP-based alignment metrics:
        1. Keyword Match Score using TF-IDF and Cosine Similarity
        2. Semantic Similarity Score using spaCy natural language models
        3. Final combined ATS score: (Keyword Score * 0.6) + (Semantic Score * 0.4)
        """
        import re

        # Handle empty/missing input scenarios
        if not resume_text or not resume_text.strip(
        ) or not job_description or not job_description.strip():
            return {
                "keyword_score": 0.0,
                "semantic_score": 0.0,
                "final_score": 0.0,
                "ats_score": 0.0,
                "matched_skills": [],
                "missing_skills": [],
                "match_percentage": 0.0,
                "category_breakdown": [],
                "improvement_roadmap": [],
                "keywords_impact_analysis": "No text provided.",
                "skill_validation_explanation": "No text provided.",
                "estimated_future_score": "0% - 0%",
                "intelligence_layer": {
                    "grade": "Needs Improvement",
                    "readiness_indicator": "Not Ready",
                    "hiring_probability": "Low",
                    "current_score": 0.0,
                    "recoverable_score": 0.0,
                    "max_score": 95.0,
                    "projected_score": 0.0,
                    "keyword_impact_score": 0.0,
                    "strengths": [],
                    "weaknesses": [],
                    "priority_fixes": [],
                    "formatting_recovery": 0.0,
                    "keywords_recovery": 0.0,
                    "content_recovery": 0.0,
                    "validation_recovery": 0.0,
                    "missing_skills_impact": [],
                    "total_skills_impact_gain": 0.0
                }
            }

        # 1. TF-IDF Cosine Similarity for Keyword Score
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(
                [resume_text, job_description])
            cos_sim = cosine_similarity(
                tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            round(max(0.0, min(100.0, cos_sim * 100)), 1)
        except Exception as e:
            print(f"Error computing TF-IDF Cosine Similarity: {e}")
            pass

        # 2. spaCy Document Similarity for Semantic Score
        try:
            nlp = get_nlp_model()
            doc_resume = nlp(resume_text)
            doc_jd = nlp(job_description)

            # Extract basic similarity (returns 0.0 to 1.0)
            similarity = doc_resume.similarity(doc_jd)
            semantic_score = round(max(0.0, min(100.0, similarity * 100)), 1)
        except Exception as e:
            print(f"Error computing spaCy semantic similarity: {e}")
            semantic_score = 0.0

        # 3. Extract skill overlaps
        resume_skills = set(SkillExtractor.extract_skills(resume_text))
        jd_skills = set(SkillExtractor.extract_skills(job_description))

        matched_skills = resume_skills.intersection(jd_skills)
        missing_skills = jd_skills.difference(resume_skills)

        # Helper to extract sections from resume text
        def extract_section(text, section_keywords, next_section_keywords):
            text_lower = text.lower()
            start_idx = -1
            for kw in section_keywords:
                idx = text_lower.find(kw)
                if idx != -1:
                    start_idx = idx + len(kw)
                    break
            if start_idx == -1:
                return ""

            end_idx = len(text)
            for kw in next_section_keywords:
                idx = text_lower.find(kw, start_idx)
                if idx != -1 and idx < end_idx:
                    end_idx = idx
            return text[start_idx:end_idx]

        resume_lower = resume_text.lower()

        experience_keywords = [
            "experience",
            "employment",
            "work history",
            "history",
            "career",
            "professional experience"]
        projects_keywords = [
            "projects",
            "personal projects",
            "academic projects",
            "key projects"]
        education_keywords = [
            "education",
            "academic",
            "university",
            "credentials",
            "qualifications"]
        skills_keywords = [
            "skills",
            "technologies",
            "tech stack",
            "technical skills",
            "tools"]
        summary_keywords = [
            "summary",
            "profile",
            "about me",
            "professional summary",
            "objective"]

        all_headers = experience_keywords + projects_keywords + \
            education_keywords + skills_keywords + summary_keywords

        experience_text = extract_section(
            resume_text, experience_keywords, [
                h for h in all_headers if h not in experience_keywords])
        projects_text = extract_section(
            resume_text, projects_keywords, [
                h for h in all_headers if h not in projects_keywords])

        # 4. Calculate Formatting Score
        # Split resume text into pages by Form Feed (\f) character
        pages = resume_text.split("\f")

        # Section keywords for heading checks
        section_keywords = [
            "experience",
            "employment",
            "work history",
            "history",
            "career",
            "professional experience",
            "projects",
            "personal projects",
            "academic projects",
            "key projects",
            "education",
            "academic",
            "university",
            "credentials",
            "qualifications",
            "skills",
            "technologies",
            "tech stack",
            "technical skills",
            "tools",
            "summary",
            "profile",
            "about me",
            "professional summary",
            "objective",
            "certifications",
            "awards",
            "publications",
            "languages"]

        def is_heading(line):
            line_clean = line.strip().lower().replace(
                ":",
                "").replace(
                "**",
                "").replace(
                "__",
                "")
            if len(line_clean) > 30 or len(line_clean) < 3:
                return False
            return any(line_clean == kw or line_clean.startswith(
                kw) or line_clean.endswith(kw) for kw in section_keywords)

        def ends_with_bullet(page_text):
            lines = [line.strip() for line in page_text.split("\n") if line.strip()]
            if not lines:
                return False
            last_line = lines[-1]
            starts_with_bullet = any(
                last_line.startswith(b) for b in [
                    "-", "*", "•", "▪", "◦"])
            ends_open = last_line[-1] not in [".",
                                              "!", "?"] if last_line else False
            return starts_with_bullet and ends_open

        def starts_with_continuation(page_text):
            lines = [line.strip() for line in page_text.split("\n") if line.strip()]
            if not lines:
                return False
            first_line = lines[0]
            starts_with_bullet = any(
                first_line.startswith(b) for b in [
                    "-", "*", "•", "▪", "◦"])
            is_head = is_heading(first_line)
            return not starts_with_bullet and not is_head

        # Check section presence
        has_email = re.search(
            r'[\w\.-]+@[\w\.-]+\.\w+',
            resume_text) is not None
        has_phone = re.search(
            r'\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b|\+?\d{1,4}[-.\s]??\(?\d{1,3}?\)?[-.\s]??\d{3,4}[-.\s]??\d{4}\b',
            resume_text) is not None
        has_email_phone = has_email or has_phone
        has_linkedin = "linkedin" in resume_lower
        has_summary = any(re.search(rf"\b{re.escape(x)}\b", resume_lower) for x in summary_keywords)
        has_education = any(re.search(rf"\b{re.escape(x)}\b", resume_lower) for x in education_keywords)
        has_experience = any(re.search(rf"\b{re.escape(x)}\b", resume_lower) for x in experience_keywords)
        has_skills = any(re.search(rf"\b{re.escape(x)}\b", resume_lower) for x in skills_keywords)
        has_structure = any(
            b in resume_text for b in [
                "-", "*", "•", "▪", "◦"])

        # Check layout consistency spacing
        spacing_inconsistent = "\n\n\n" in resume_text or "\r\n\r\n\r\n" in resume_text

        # Check layout consistency margins
        bullet_lines = [
            line for line in resume_text.split("\n") if any(
                line.strip().startswith(b) for b in [
                    "-", "*", "•", "▪", "◦"])]
        margins_inconsistent = False
        if bullet_lines:
            indents = [len(line) - len(line.lstrip()) for line in bullet_lines]
            if len(set(indents)) >= 3:
                margins_inconsistent = True

        # Check heading capitalization casing hierarchy consistency
        headings = [line.strip()
                    for line in resume_text.split("\n") if is_heading(line)]
        casing_inconsistent = False
        if headings:
            isupper = [h.isupper() for h in headings]
            if any(isupper) and not all(isupper):
                casing_inconsistent = True

        # Compute deductions
        deductions = []
        if not has_email_phone:
            deductions.append(
                ("Missing Contact Information (Email/Phone)", 15))
        if not has_linkedin:
            deductions.append(("Missing LinkedIn URL", 5))
        if not has_summary:
            deductions.append(("Missing Summary Section", 15))
        if not has_education:
            deductions.append(("Missing Education Section", 15))
        if not has_experience:
            deductions.append(("Missing Experience Section", 20))
        if not has_skills:
            deductions.append(("Missing Skills Section", 15))
        if not has_structure:
            deductions.append(("No Bullet Points in descriptions", 15))

        # Advanced formatting checks
        if len(pages) > 1:
            for p in range(len(pages) - 1):
                page_lines = [line.strip()
                              for line in pages[p].split("\n") if line.strip()]
                if page_lines:
                    last_line = page_lines[-1]
                    if is_heading(last_line):
                        clean_head = last_line.replace(
                            "**",
                            "").replace(
                            "__",
                            "").replace(
                            ":",
                            "").strip()
                        deductions.append(
                            (f"{clean_head} heading split across pages (orphan heading)", 5))

                if ends_with_bullet(
                        pages[p]) and starts_with_continuation(pages[p + 1]):
                    deductions.append(
                        ("Bullet list split incorrectly across page break", 3))

        if spacing_inconsistent:
            deductions.append(
                ("Inconsistent layout spacing (consecutive blank lines)", 3))
        if margins_inconsistent:
            deductions.append(
                ("Inconsistent bullet margin spacing/alignments", 3))
        if casing_inconsistent:
            deductions.append(
                ("Inconsistent heading capitalization casing hierarchy", 2))

        total_deductions = sum(d[1] for d in deductions)
        formatting_score = max(0, 100 - total_deductions)

        form_issues = []
        form_recs = []
        form_reasons = []

        for desc, ded in deductions:
            form_issues.append(desc)
            form_reasons.append(f"{desc} (-{ded}%)")

            # Populate action items
            if "Contact Information" in desc:
                form_recs.append(
                    "Add your Email Address and Phone Number to the header.")
            elif "LinkedIn" in desc:
                form_recs.append(
                    "Add a link to your LinkedIn profile in the contact block.")
            elif "Summary" in desc:
                form_recs.append(
                    "Add a Professional Summary or objective statement at the top.")
            elif "Education" in desc:
                form_recs.append(
                    "Add an Education section outlining your degrees and institutions.")
            elif "Experience" in desc:
                form_recs.append(
                    "Add a Work Experience section detailing your professional history.")
            elif "Skills" in desc:
                form_recs.append(
                    "Add a Skills section listing your technical competencies.")
            elif "Bullet" in desc:
                form_recs.append(
                    "Use bullet points (-, *, •) to describe your project achievements and roles.")
            elif "heading split" in desc.lower() or "orphan" in desc.lower():
                form_recs.append(
                    "Prevent headings from getting orphaned at page bottoms. Group them with their trailing text.")
            elif "spacing" in desc:
                form_recs.append(
                    "Avoid consecutive empty lines to maintain a uniform page spacing.")
            elif "margin" in desc:
                form_recs.append(
                    "Ensure consistent left indentation margins for all bullet points.")
            elif "capitalization" in desc or "casing" in desc:
                form_recs.append(
                    "Establish casing consistency (e.g., all UPPERCASE) for all major section headings.")

        if not deductions:
            form_why = "Formatting Score: 100%\n\nIssues Found:\n* None detected\n\nTotal Formatting Deduction: -0%"
        else:
            issues_str = "\n".join(
                f"* {desc} (-{ded}%)" for desc,
                ded in deductions)
            form_why = (
                f"Formatting Score: {formatting_score}%\n\n"
                f"Issues Found:\n"
                f"{issues_str}\n\n"
                f"Total Formatting Deduction: -{total_deductions}%"
            )

        # 5. Calculate Keywords Score
        # Matched Skills / Total Required Skills
        total_skills = len(matched_skills) + len(missing_skills)
        keyword_score = round((len(matched_skills) /
                               max(1, total_skills)) *
                              100, 1) if total_skills > 0 else 100.0
        each_skill_weight = round(
            100.0 / max(1, total_skills), 1) if total_skills > 0 else 0.0

        key_issues = []
        key_recs = []
        key_reasons = []

        if missing_skills:
            for skill in sorted(list(missing_skills)):
                key_issues.append(f"Missing keyword: {skill}")
                key_recs.append(f"Add keyword: {skill}")
                key_reasons.append(f"Missing {skill} (-{each_skill_weight}%)")

        matched_lines = "\n".join(
            sorted(list(matched_skills))) if matched_skills else "None"
        missing_lines = "\n".join(
            sorted(list(missing_skills))) if missing_skills else "None"
        score_lost_lines = "\n".join(
            f"Missing {skill} (-{each_skill_weight}%)" for skill in sorted(
                list(missing_skills))) if missing_skills else "None"

        key_why = f"Matched:\n{matched_lines}\n\nMissing:\n{missing_lines}\n\nScore lost:\n{score_lost_lines}"

        # 6. Calculate Content Quality Score
        # Action Verbs Present = +40 (min 5 verbs, or +8 per verb)
        active_verbs = [
            "led",
            "developed",
            "managed",
            "designed",
            "created",
            "built",
            "implemented",
            "optimized",
            "increased",
            "reduced",
            "delivered",
            "coordinated",
            "engineered",
            "programmed",
            "analyzed",
            "architected",
            "formulated",
            "established"]
        found_verbs = [v for v in active_verbs if re.search(rf"\b{v}\b", resume_lower)]
        active_verbs_score = min(40, len(found_verbs) * 8)

        # Quantified Achievements Present = +30 (min 3 metrics, or +10 per
        # metric)
        metrics = re.findall(
            r'\b\d+(?:%|\s*percent\b|\s*x\b|\+)?',
            resume_text)
        quantified_score = min(30, len(metrics) * 10)

        proj_kws = ["project", "developed", "built", "engineered", "design", "github.com", "portfolio"]
        has_proj_kws = any(re.search(rf"\b{re.escape(x)}\b", resume_lower) for x in proj_kws)
        projects_score = 30 if has_proj_kws else 0

        content_quality_score = active_verbs_score + quantified_score + projects_score

        qual_issues = []
        qual_recs = []
        qual_reasons = []
        if active_verbs_score < 40:
            loss = 40 - active_verbs_score
            qual_issues.append("Low Action Verb Count")
            qual_recs.append(
                "Incorporate more active verbs like Led, Developed, Optimized")
            qual_reasons.append(f"Action Verbs missing (-{loss}%)")
        if quantified_score < 30:
            loss = 30 - quantified_score
            qual_issues.append("Few Quantified Achievements")
            qual_recs.append("Add quantifiable metrics (e.g. %, $, numbers)")
            qual_reasons.append(f"Missing quantified achievements (-{loss}%)")
        if projects_score == 0:
            qual_issues.append("Missing Project Descriptions")
            qual_recs.append(
                "Add Project Descriptions detailing engineering achievements")
            qual_reasons.append("Missing project descriptions (-30%)")

        qual_why = "Reason:\n" + ("\n".join(qual_reasons) if qual_reasons else "All Content Quality Components Found") + \
            f"\n\nPotential Recovery:\n+{100 - int(content_quality_score)}%"

        # 7. Calculate Skill Validation Score
        # Claimed Skills Found In Projects = +50
        # Claimed Skills Found In Experience = +50
        claimed_skills = resume_skills
        skills_in_projects = [s for s in claimed_skills if s.lower(
        ) in projects_text.lower()] if claimed_skills else []
        skills_in_experience = [s for s in claimed_skills if s.lower(
        ) in experience_text.lower()] if claimed_skills else []

        if claimed_skills:
            proj_ratio = len(skills_in_projects) / len(claimed_skills)
            exp_ratio = len(skills_in_experience) / len(claimed_skills)
        else:
            proj_ratio = 1.0
            exp_ratio = 1.0

        proj_val_score = round(proj_ratio * 50, 1)
        exp_val_score = round(exp_ratio * 50, 1)
        skill_validation_score = round(proj_val_score + exp_val_score, 1)

        val_issues = []
        val_recs = []
        val_reasons = []

        sample_skills = ", ".join(
            list(claimed_skills)[
                :3]) if claimed_skills else "skills"

        if proj_val_score < 50:
            loss = round(50.0 - proj_val_score, 1)
            val_issues.append("Claimed skills not found in Projects section")
            val_recs.append(
                f"Incorporate skills (e.g. {sample_skills}) inside your Projects descriptions")
            val_reasons.append(f"Skills missing in projects (-{loss}%)")
        if exp_val_score < 50:
            loss = round(50.0 - exp_val_score, 1)
            val_issues.append("Claimed skills not found in Experience section")
            val_recs.append(
                f"Incorporate skills (e.g. {sample_skills}) inside your Experience history bullets")
            val_reasons.append(f"Skills missing in experience (-{loss}%)")

        val_why = "Reason:\n" + ("\n".join(val_reasons) if val_reasons else "All claimed skills validated in projects & experience") + \
            f"\n\nPotential Recovery:\n+{round(100.0 - skill_validation_score, 1)}%"

        # 8. Calculate ATS Compatibility Score
        # Combined ATS Structure + Keywords
        # 50% Formatting Score, 50% Keywords Score
        ats_compatibility_score = round(
            (formatting_score + keyword_score) / 2, 1)

        structure_loss = round(50.0 - (formatting_score * 0.5), 1)
        keyword_loss = round(50.0 - (keyword_score * 0.5), 1)

        comp_issues = []
        comp_recs = []
        comp_reasons = []

        if structure_loss > 0:
            comp_issues.append("Formatting structural gaps")
            comp_recs.append("Resolve formatting and structural warnings")
            comp_reasons.append(f"ATS Structure Gaps (-{structure_loss}%)")
        if keyword_loss > 0:
            comp_issues.append("Keyword matching gaps")
            comp_recs.append("Inject missing job description keywords")
            comp_reasons.append(f"Keyword Matching Gaps (-{keyword_loss}%)")

        comp_why = "Reason:\n" + ("\n".join(comp_reasons) if comp_reasons else "ATS compatibility is optimal") + \
            f"\n\nPotential Recovery:\n+{round(100.0 - ats_compatibility_score, 1)}%"

        # 9. Compute Weighted Final Score
        # Formatting Score (20%), Keywords & Skills (25%), Content Quality
        # (25%), Skill Validation (15%), ATS Compatibility (15%)
        final_score = round(
            (formatting_score * 0.20) +
            (keyword_score * 0.25) +
            (content_quality_score * 0.25) +
            (skill_validation_score * 0.15) +
            (ats_compatibility_score * 0.15),
            1
        )

        # 10. Add category-specific recommendations if scores are below target
        # (80%)
        if formatting_score < 80:
            for rec in [
                "Improve section spacing",
                "Use ATS-friendly headings",
                    "Maintain consistent formatting"]:
                if rec not in form_recs:
                    form_recs.append(rec)
        if keyword_score < 80:
            for rec in ["Add missing JD keywords",
                        "Include technical skills from job description"]:
                if rec not in key_recs:
                    key_recs.append(rec)
        if content_quality_score < 80:
            for rec in [
                "Add measurable achievements",
                    "Improve project descriptions"]:
                if rec not in qual_recs:
                    qual_recs.append(rec)
        if skill_validation_score < 80:
            for rec in [
                "Demonstrate skills through projects",
                    "Add practical implementations"]:
                if rec not in val_recs:
                    val_recs.append(rec)
        if ats_compatibility_score < 80:
            for rec in [
                "Remove tables/icons",
                    "Use standard resume structure"]:
                if rec not in comp_recs:
                    comp_recs.append(rec)

        # Category breakdowns
        breakdown = []

        # Formatting
        breakdown.append({
            "name": "Formatting",
            "score": formatting_score,
            "target_score": 80.0,
            "improvement_needed": float(max(0.0, 80.0 - formatting_score)),
            "deduction_reason": "Missing contact, summary, or structural headers." if form_issues else "Fully compliant format.",
            "issues": form_issues,
            "recommendations": form_recs,
            "potential_gain": float(100.0 - formatting_score),
            "calculation_reason": "\n".join(form_reasons) if form_reasons else "All Formatting Components Found",
            "why_this_score": form_why,
            "missing_elements": [f.replace("Missing ", "") for f in form_issues]
        })

        # Keywords & Skills
        breakdown.append({
            "name": "Keywords & Skills",
            "score": keyword_score,
            "target_score": 80.0,
            "improvement_needed": float(max(0.0, 80.0 - keyword_score)),
            "deduction_reason": "Missing keywords in tech stack." if missing_skills else "Full vocabulary overlap.",
            "issues": key_issues,
            "recommendations": key_recs,
            "potential_gain": float(100.0 - keyword_score),
            "calculation_reason": "\n".join(key_reasons) if key_reasons else "All Keyword Requirements Met",
            "why_this_score": key_why,
            "missing_elements": sorted(list(missing_skills))
        })

        # Content Quality
        breakdown.append({
            "name": "Content Quality",
            "score": content_quality_score,
            "target_score": 80.0,
            "improvement_needed": float(max(0.0, 80.0 - content_quality_score)),
            "deduction_reason": "Lack of quantifiable outcomes or action phrasing." if qual_issues else "High impact vocabulary.",
            "issues": qual_issues,
            "recommendations": qual_recs,
            "potential_gain": float(100.0 - content_quality_score),
            "calculation_reason": "\n".join(qual_reasons) if qual_reasons else "All Content Quality Components Found",
            "why_this_score": qual_why,
            "missing_elements": [q.replace("Missing ", "").replace("Few ", "") for q in qual_issues]
        })

        # Skill Validation
        breakdown.append({
            "name": "Skill Validation",
            "score": skill_validation_score,
            "target_score": 80.0,
            "improvement_needed": float(max(0.0, 80.0 - skill_validation_score)),
            "deduction_reason": "Standalone skills missing contextual details." if val_issues else "Strong semantic contextual validation.",
            "issues": val_issues,
            "recommendations": val_recs,
            "potential_gain": float(100.0 - skill_validation_score),
            "calculation_reason": "\n".join(val_reasons) if val_reasons else "All claimed skills validated in projects & experience",
            "why_this_score": val_why,
            "missing_elements": [v.replace("skills missing in ", "") for v in val_issues]
        })

        # ATS Compatibility
        breakdown.append({
            "name": "ATS Compatibility",
            "score": ats_compatibility_score,
            "target_score": 80.0,
            "improvement_needed": float(max(0.0, 80.0 - ats_compatibility_score)),
            "deduction_reason": "Compound parsing risks due to structural gaps." if comp_issues else "100% parser safe.",
            "issues": comp_issues,
            "recommendations": comp_recs,
            "potential_gain": float(100.0 - ats_compatibility_score),
            "calculation_reason": "\n".join(comp_reasons) if comp_reasons else "ATS compatibility is optimal",
            "why_this_score": comp_why,
            "missing_elements": [c.replace("Gaps", "") for c in comp_issues]
        })

        # Roadmap
        roadmap = []
        if formatting_score < 80:
            roadmap.append(
                f"Improve Formatting: Fix section headers and layouts (Recover up to +{int(100 - formatting_score)}%)")
        if keyword_score < 80:
            roadmap.append(
                f"Inject Keywords: Add missing skills to match target job descriptors (Recover up to +{int(100 - keyword_score)}%)")
        if content_quality_score < 80:
            roadmap.append(
                f"Polish Content: Add action verbs and quantifiable metrics (Recover up to +{int(100 - content_quality_score)}%)")
        if skill_validation_score < 80:
            roadmap.append(
                f"Validate Skills: Contextualize skills in experience narratives (Recover up to +{int(100 - skill_validation_score)}%)")
        if not roadmap:
            roadmap.append(
                "Your resume matches closely with all ATS criteria! Ready to submit.")

        # Keywords Impact Analysis
        if missing_skills:
            keywords_impact = f"Your resume currently misses key technologies such as {', '.join(sorted(list(missing_skills))[:3])}. Injecting these missing keywords will directly optimize your search ranking density, which controls 60% of search indexing weights in modern ATS filters."
        else:
            keywords_impact = "No critical missing keywords. Keyword density is in the optimal range."

        # Skill Validation Explanation
        skill_val_expl = "ATS algorithms look for semantic proof. Simply listing technologies in a skills grid is not enough; they must be contextualized and appear alongside action verbs in your experience bullets to be validated as proven skills."

        # Grade
        if final_score >= 90:
            grade = "A+"
        elif final_score >= 80:
            grade = "A"
        elif final_score >= 70:
            grade = "B+"
        elif final_score >= 60:
            grade = "B"
        elif final_score >= 50:
            grade = "C"
        else:
            grade = "Needs Improvement"

        # Readiness
        if final_score >= 80:
            readiness = "Interview Ready"
        elif final_score >= 60:
            readiness = "Partially Interview Ready"
        else:
            readiness = "Not Interview Ready"

        # Hiring Probability
        if final_score >= 80:
            hiring_prob = "High"
        elif final_score >= 65:
            hiring_prob = "Medium"
        else:
            hiring_prob = "Low"

        # Calculator
        # Recovery calculation: formatting(20%), keywords(25%), content
        # quality(25%), validation(15%), compatibility(15%)
        gain_formatting = round(max(0.0, 100.0 - formatting_score) * 0.20, 1)
        gain_keywords = round(max(0.0, 100.0 - keyword_score) * 0.25, 1)
        gain_quality = round(max(0.0, 100.0 - content_quality_score) * 0.25, 1)
        gain_validation = round(
            max(0.0, 100.0 - skill_validation_score) * 0.15, 1)
        gain_compatibility = round(
            max(0.0, 100.0 - ats_compatibility_score) * 0.15, 1)

        recoverable_ats = round(
            gain_formatting +
            gain_keywords +
            gain_quality +
            gain_validation +
            gain_compatibility,
            1)
        projected_score = min(100.0, max(final_score, round(final_score + recoverable_ats, 1)))

        # Missing Skills Impact Analysis
        missing_skills_impact = []
        total_skills_impact_gain = 0.0
        if missing_skills:
            each_impact = round(gain_keywords / len(missing_skills), 1)
            if each_impact == 0.0 and gain_keywords > 0:
                each_impact = 0.1
            for skill in sorted(list(missing_skills)):
                missing_skills_impact.append({
                    "skill": skill,
                    "impact": each_impact
                })
                total_skills_impact_gain += each_impact
            total_skills_impact_gain = round(total_skills_impact_gain, 1)

        # Strengths & Weaknesses
        strengths = []
        weaknesses = []

        # Check checked/crossed bullets
        if final_score >= 75:
            strengths.append("High contextual relevance to job requirements")
        if formatting_score >= 80:
            strengths.append("Clean document hierarchy and layout structure")
        if content_quality_score >= 75:
            strengths.append(
                "Action-oriented narrative with quantifiable achievements")
        # Ensure we add standard ones if lists are small
        if "python" in resume_lower:
            strengths.append("Python proficiency verified")
        if "sql" in resume_lower:
            strengths.append("SQL proficiency verified")
        if "education" in resume_lower:
            strengths.append("Good Education section mapping")

        if not strengths:
            strengths.append("Standard contact and structural headers found")

        if keyword_score < 70:
            weaknesses.append("Missing Data Science Keywords")
        if formatting_score < 80:
            weaknesses.append(
                "Non-standard section divisions or bullet style consistency issues")
        if content_quality_score < 70:
            weaknesses.append("Weak Project Descriptions")
            weaknesses.append("No Quantified Achievements")
        if semantic_score < 70:
            weaknesses.append(
                "Standalone skills listed without narrative support in past roles")
        if not weaknesses:
            weaknesses.append(
                "None detected. Focus on minor vocabulary adjustments.")

        # Priority Fixes
        priority_fixes = []
        if keyword_score < 80:
            priority_fixes.append(
                {
                    "title": "Inject Missing Technical Keywords",
                    "impact": "High" if gain_keywords >= 10 else "Medium",
                    "description": f"Add missing keywords: {', '.join(sorted(list(missing_skills))[:3])} to skills and experience sections.",
                    "points_recovery": round(
                        gain_keywords,
                        1)})
        if skill_validation_score < 80:
            priority_fixes.append({
                "title": "Contextualize stand-alone skills",
                "impact": "High" if gain_validation >= 10 else "Medium",
                "description": "Describe projects and experience using your tech stack in action rather than just a sidebar list.",
                "points_recovery": round(gain_validation, 1)
            })
        if formatting_score < 80:
            priority_fixes.append({
                "title": "Standardize layout divisions",
                "impact": "Medium" if gain_formatting >= 10 else "Low",
                "description": "Convert tables to standard clean text blocks and use bold titles for Work and Education.",
                "points_recovery": round(gain_formatting, 1)
            })
        if content_quality_score < 80:
            priority_fixes.append({
                "title": "Quantify role outcomes",
                "impact": "Medium" if gain_quality >= 10 else "Low",
                "description": "Use percentage improvements and project scale metrics inside your experience narratives.",
                "points_recovery": round(gain_quality, 1)
            })

        # Ensure priority fixes are sorted by impact
        impact_order = {"High": 0, "Medium": 1, "Low": 2}
        priority_fixes.sort(key=lambda x: impact_order.get(x["impact"], 3))

        # Predicted Future Score range calculation
        cats = [
            (formatting_score, 0.20),
            (keyword_score, 0.25),
            (content_quality_score, 0.25),
            (skill_validation_score, 0.15),
            (ats_compatibility_score, 0.15)
        ]
        f_min = round(sum(max(80.0, S) * W for S, W in cats) - 2.0)
        f_max = round(
            sum(max(85.0, S + (100.0 - S) * 0.5) * W for S, W in cats))
        future_min = min(100, max(int(final_score), int(f_min)))
        future_max = min(100, max(future_min + 2, int(f_max)))
        estimated_future = f"{future_min}% - {future_max}%"

        # Generate "How to Reach 80% ATS Score" improvement summary
        improvement_summary = []
        if formatting_score < 80:
            improvement_summary.append(
                f"Improve Formatting by {int(round(80.0 - formatting_score))}%")
        if keyword_score < 80:
            improvement_summary.append(
                f"Improve Keywords & Skills by {int(round(80.0 - keyword_score))}%")
        if content_quality_score < 80:
            improvement_summary.append(
                f"Improve Content Quality by {int(round(80.0 - content_quality_score))}%")
        if skill_validation_score < 80:
            improvement_summary.append(
                f"Improve Skill Validation by {int(round(80.0 - skill_validation_score))}%")
        if ats_compatibility_score < 80:
            improvement_summary.append(
                f"Improve ATS Compatibility by {int(round(80.0 - ats_compatibility_score))}%")
        if missing_skills:
            improvement_summary.append(
                f"Add {len(missing_skills)} missing skill{'s' if len(missing_skills) > 1 else ''}")
        if content_quality_score < 80:
            improvement_summary.append("Strengthen project descriptions")

        # Section detection logic
        contact_kws = ["contact", "email", "phone", "address"]
        cert_kws = ["certification", "certifications", "certified", "award", "awards", "credentials"]
        
        sections_map = {
            "Contact Information": has_email_phone or any(re.search(rf"\b{re.escape(x)}\b", resume_lower) for x in contact_kws),
            "Professional Summary": has_summary,
            "Work Experience": has_experience,
            "Education": has_education,
            "Skills / Technical Expertise": has_skills,
            "Projects": has_proj_kws,
            "Certifications & Awards": any(re.search(rf"\b{re.escape(x)}\b", resume_lower) for x in cert_kws)
        }
        found_sections = [sec for sec, found in sections_map.items() if found]
        missing_sections = [
            sec for sec,
            found in sections_map.items() if not found]

        # Keyword Coverage calculations
        required_keywords = sorted(list(jd_skills))
        found_keywords = sorted(list(matched_skills))
        missing_kws = sorted(list(missing_skills))
        keyword_coverage_percentage = round(
            (len(matched_skills) / max(1, len(jd_skills))) * 100, 1) if jd_skills else 100.0

        return {
            "keyword_score": keyword_score,
            "semantic_score": semantic_score,
            "final_score": final_score,
            "ats_score": final_score,
            "matched_skills": sorted(list(matched_skills)),
            "missing_skills": sorted(list(missing_skills)),
            "match_percentage": final_score,
            "category_breakdown": breakdown,
            "improvement_roadmap": roadmap,
            "keywords_impact_analysis": keywords_impact,
            "skill_validation_explanation": skill_val_expl,
            "estimated_future_score": estimated_future,
            "intelligence_layer": {
                "grade": grade,
                "readiness_indicator": readiness,
                "hiring_probability": hiring_prob,
                "current_score": final_score,
                "recoverable_score": recoverable_ats,
                "max_score": 95.0,
                "projected_score": projected_score,
                "keyword_impact_score": round(keyword_score * 0.9, 1),
                "strengths": strengths,
                "weaknesses": weaknesses,
                "priority_fixes": priority_fixes,
                "formatting_recovery": gain_formatting,
                "keywords_recovery": gain_keywords,
                "content_recovery": gain_quality,
                "validation_recovery": gain_validation,
                "compatibility_recovery": gain_compatibility,
                "improvement_summary": improvement_summary,
                "missing_skills_impact": missing_skills_impact,
                "total_skills_impact_gain": total_skills_impact_gain,
                "found_sections": found_sections,
                "missing_sections": missing_sections,
                "required_keywords": required_keywords,
                "found_keywords": found_keywords,
                "keyword_coverage_percentage": keyword_coverage_percentage,
                "missing_keywords": missing_kws
            }
        }
