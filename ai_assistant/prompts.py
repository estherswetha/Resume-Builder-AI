
def build_resume_prompt(resume):

    return f"""
You are ResumeGen AI, a professional resume writing assistant.

Create a professional, ATS-friendly resume using only
the information supplied below.

CANDIDATE INFORMATION

Name: {resume.full_name}
Email: {resume.email}
Phone: {resume.phone}
Location: {resume.location}

Target Job Role: {resume.target_role}

Education:
{resume.education}

Skills:
{resume.skills}

Experience:
{resume.experience or "Fresher - no work experience provided"}

Projects:
{resume.projects}

Certifications:
{resume.certifications or "Not provided"}

INSTRUCTIONS

1. Write a strong professional summary.
2. Organize education and technical skills clearly.
3. Improve project descriptions using professional language.
4. Improve experience descriptions without inventing achievements.
5. Use relevant job-related keywords naturally.
6. Use clear bullet points.
7. Do not invent employers, qualifications, dates,
   certifications, achievements or technical skills.
8. If information is missing, do not make it up.

OUTPUT FORMAT

PROFESSIONAL SUMMARY

TECHNICAL SKILLS

WORK EXPERIENCE

PROJECTS

EDUCATION

CERTIFICATIONS

Generate clean, professional resume content.
"""
