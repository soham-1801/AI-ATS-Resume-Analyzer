from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_resume(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=14,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        alignment=TA_LEFT
    )
    
    normal_style = styles['Normal']
    
    story = []
    
    # Header
    story.append(Paragraph("<b>John Doe</b>", title_style))
    story.append(Paragraph("john.doe@example.com | (123) 456-7890 | linkedin.com/in/johndoe | GitHub: johndoe", normal_style))
    story.append(Spacer(1, 20))
    
    # Summary
    story.append(Paragraph("<b>PROFESSIONAL SUMMARY</b>", heading_style))
    story.append(Paragraph("Results-driven Software Engineer with 5+ years of experience in full-stack web development. Proven expertise in Python, React, and cloud technologies. Adept at building scalable microservices and improving system performance by 30%. Strong problem-solving skills and a passion for clean, maintainable code.", normal_style))
    story.append(Spacer(1, 15))
    
    # Skills
    story.append(Paragraph("<b>TECHNICAL SKILLS</b>", heading_style))
    story.append(Paragraph("<b>Languages:</b> Python, JavaScript, TypeScript, SQL, HTML/CSS<br/>"
                           "<b>Frameworks:</b> React, Node.js, Django, FastAPI, Express<br/>"
                           "<b>Tools/DevOps:</b> Docker, Kubernetes, AWS, CI/CD, Git, PostgreSQL, MongoDB", normal_style))
    story.append(Spacer(1, 15))
    
    # Experience
    story.append(Paragraph("<b>EXPERIENCE</b>", heading_style))
    story.append(Paragraph("<b>Senior Software Engineer</b> - Tech Innovators Inc. (Jan 2021 - Present)", normal_style))
    story.append(Paragraph("• Architected and developed a scalable microservices architecture using FastAPI and Docker, improving API response times by 40%.<br/>"
                           "• Mentored a team of 4 junior developers and led weekly code reviews to ensure best practices.<br/>"
                           "• Implemented robust CI/CD pipelines using GitHub Actions, reducing deployment time by 50%.<br/>"
                           "• Designed dynamic and responsive UI components using React and Tailwind CSS.", normal_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Software Developer</b> - Web Solutions LLC (Jun 2018 - Dec 2020)", normal_style))
    story.append(Paragraph("• Developed full-stack web applications using Node.js and React, serving over 10,000 daily active users.<br/>"
                           "• Optimized database queries in PostgreSQL, resolving performance bottlenecks and improving load times by 20%.<br/>"
                           "• Integrated third-party APIs (Stripe, Twilio) for payment processing and SMS notifications.", normal_style))
    story.append(Spacer(1, 15))
    
    # Education
    story.append(Paragraph("<b>EDUCATION</b>", heading_style))
    story.append(Paragraph("<b>Bachelor of Science in Computer Science</b>", normal_style))
    story.append(Paragraph("University of Technology - Graduated: May 2018 (GPA: 3.8/4.0)", normal_style))
    story.append(Spacer(1, 15))
    
    # Projects
    story.append(Paragraph("<b>PROJECTS</b>", heading_style))
    story.append(Paragraph("<b>AI ATS Resume Analyzer:</b> Built an end-to-end platform using FastAPI and React to analyze resumes against job descriptions using Gemini AI.", normal_style))
    story.append(Paragraph("<b>E-commerce Platform:</b> Developed a scalable e-commerce site handling 5,000+ products with Elasticsearch integration.", normal_style))

    doc.build(story)

if __name__ == "__main__":
    import sys
    filename = sys.argv[1] if len(sys.argv) > 1 else "Sample_Resume_John_Doe.pdf"
    generate_resume(filename)
    print(f"Generated {filename} successfully.")
