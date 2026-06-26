import re

COMMON_SKILLS = [
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "go", "rust", "php", "swift", "kotlin", "sql", "html", "css",
    # Frameworks & Libraries
    "react", "angular", "vue", "next.js", "django", "flask", "fastapi", "spring boot", "express", "node.js", "laravel",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "spacy", "nltk", "langchain", "opencv",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle", "dynamodb", "cassandra",
    # Tools & Platforms
    "git", "docker", "kubernetes", "aws", "azure", "gcp", "firebase", "jenkins", "github actions", "gitlab ci",
    # Core Concepts / Methodologies
    "agile", "scrum", "rest api", "graphql", "microservices", "ci/cd", "machine learning", "deep learning", "nlp", "computer vision",
    "data science", "data structure", "algorithms", "system design"
]

class SkillExtractor:
    @staticmethod
    def extract_skills(text: str) -> list[str]:
        """Extract a list of matching tech skills from a given block of text."""
        if not text:
            return []
            
        extracted = []
        text_lower = text.lower()
        
        for skill in COMMON_SKILLS:
            # Word boundary regex to avoid partial matches (e.g. "go" matching inside "good")
            # For special chars like c++, c# or next.js, escape them
            escaped_skill = re.escape(skill)
            pattern = rf"\b{escaped_skill}\b"
            if skill in ["c++", "c#", "next.js", "node.js"]:
                # Custom boundary logic for programming languages with symbols
                pattern = rf"(?:^|\s|[.,\/#!$%\^&\*;:{{}}=\-_`~()]){escaped_skill}(?:$|\s|[.,\/#!$%\^&\*;:{{}}=\-_`~()])"
                
            if re.search(pattern, text_lower):
                extracted.append(skill)
                
        return list(set(extracted))
