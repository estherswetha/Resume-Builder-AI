import os

import re

from io import BytesIO




from django.contrib import messages

from django.contrib.auth.decorators import login_required

from django.core.exceptions import ValidationError

from django.core.validators import validate_email

from django.db.models import Q

from django.http import Http404

from django.shortcuts import get_object_or_404, redirect, render

from django.views.decorators.http import require_POST



from .forms import BuilderResumeForm, ResumeForm

from .models import BuilderResume, Resume






# ============================================================

# SIX CAREER FEATURES

# ============================================================



FEATURE_PAGES = {

    "architect": {

        "number": "01 / CREATE",

        "title": "AI Resume Architect",

        "description": (

            "Build professional and ATS-friendly resumes "

            "with AI assistance."

        ),

        "tools": [

            "Create a resume from scratch",

            "Upload PDF or DOCX resume",

            "Generate professional summaries",

            "Improve project descriptions",

            "Choose professional templates",

            "Preview and download resumes",

        ],

    },



    "ats-intelligence": {

        "number": "02 / ANALYZE",

        "title": "ATS Intelligence",

        "description": "Analyze your resume and improve ATS compatibility.",

        "tools": [

            "ATS compatibility estimation",

            "Keyword analysis",

            "Missing section detection",

            "Formatting review",

            "Improvement recommendations",

            "ATS report",

        ],

    },



    "job-match": {

        "number": "03 / MATCH",

        "title": "Job Match AI",

        "description": "Compare your resume with a target job description.",

        "tools": [

            "Paste job description",

            "Compare your skills",

            "Find missing keywords",

            "Analyze experience",

            "Get recommendations",

            "Create job-specific resume versions",

        ],

    },



    "skill-enhancer": {

        "number": "04 / IMPROVE",

        "title": "Smart Skill Enhancer",

        "description": "Improve project descriptions and professional skills.",

        "tools": [

            "Rewrite project descriptions",

            "Improve grammar",

            "Suggest technical skills",

            "Generate achievement statements",

            "Improve action verbs",

            "Compare original and improved content",

        ],

    },



    "interview-coach": {

        "number": "05 / PREPARE",

        "title": "AI Interview Coach",

        "description": "Practice interviews using personalized questions.",

        "tools": [

            "Technical questions",

            "HR questions",

            "Behavioral questions",

            "Voice and text practice",

            "Answer feedback",

            "Interview history",

        ],

    },



    "career-vault": {

        "number": "06 / MANAGE",

        "title": "Career Vault",

        "description": "Manage your resumes and career documents.",

        "tools": [

            "Save multiple resumes",

            "Edit saved resumes",

            "Resume history",

            "Download documents",

            "Save GitHub and portfolio links",

            "Manage certificates",

        ],

    },

}





# ============================================================

# FEATURE DETAIL PAGE

# ============================================================



def feature_detail(request, feature_slug):



    feature = FEATURE_PAGES.get(feature_slug)



    if feature is None:

        raise Http404("Career feature not found.")



    # Architect gets its own functional workspace.

    if feature_slug == "architect":



        resumes = BuilderResume.objects.none()

        total_resumes = 0



        if request.user.is_authenticated:

            resumes = BuilderResume.objects.filter(

                user=request.user

            )

            total_resumes = resumes.count()



        return render(

            request,

            "resumes/architect.html",

            {

                "feature": feature,

                "resumes": resumes[:5],

                "total_resumes": total_resumes,

            },

        )



    return render(

        request,

        "resumes/feature_detail.html",

        {

            "feature": feature,

            "feature_slug": feature_slug,

        },

    )





# ============================================================

# HELPER: GET USER'S OWN RESUME

# ============================================================



def get_user_resume(request, pk):



    return get_object_or_404(

        BuilderResume,

        pk=pk,

        user=request.user,

    )





# ============================================================

# HELPER: GENERATE PROFESSIONAL SUMMARY

# ============================================================



# ============================================================
# FREE LOCAL RESUME HELPERS
# No paid API, API key, external service or internet connection.
# ============================================================


def clean_summary_text(value, max_chars=500):
    """Normalize candidate-provided text without inventing facts."""
    value = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(value) > max_chars:
        value = value[:max_chars].rsplit(" ", 1)[0].rstrip(" ,;:-") + "..."
    return value


def get_resume_skills(value):
    """Return unique skills from comma-, semicolon- or line-separated text."""
    items = re.split(r"[,;\n|•]+", str(value or ""))
    result = []
    seen = set()

    for item in items:
        skill = clean_summary_text(item, max_chars=80)
        key = skill.casefold()
        if skill and key not in seen:
            result.append(skill)
            seen.add(key)

    return result[:15]


def generate_builder_summary(resume):
    """
    Build a professional, ATS-readable summary from saved resume details.

    This is a local rule-based generator, not a generative language model.
    It uses only information entered by the candidate and does not call OpenAI.
    """
    name = clean_summary_text(getattr(resume, "full_name", ""), 120)
    role = clean_summary_text(getattr(resume, "target_role", ""), 150)
    education = clean_summary_text(getattr(resume, "education", ""))
    experience = clean_summary_text(getattr(resume, "experience", ""))
    projects = clean_summary_text(getattr(resume, "projects", ""))
    certifications = clean_summary_text(getattr(resume, "certifications", ""))
    career_level = ""

    display_level = getattr(resume, "get_career_level_display", None)
    if callable(display_level):
        career_level = clean_summary_text(display_level(), 60)

    skills = get_resume_skills(getattr(resume, "skills", ""))

    if not any([role, education, experience, projects, skills, certifications]):
        raise ValueError(
            "Please add at least a target role, education, skills, "
            "experience, projects or certifications before generating "
            "your professional summary."
        )

    sentences = []

    if name and role:
        article = "an" if role[:1].lower() in "aeiou" else "a"
        sentences.append(f"{name} is targeting opportunities as {article} {role}.")
    elif name:
        sentences.append(f"{name} is building a professional profile.")
    elif role:
        article = "an" if role[:1].lower() in "aeiou" else "a"
        sentences.append(f"Candidate targeting professional opportunities as {article} {role}.")

    if career_level:
        sentences.append(f"Career level: {career_level}.")

    if education:
        sentences.append(f"Educational background: {education}.")

    if skills:
        if len(skills) == 1:
            skill_text = skills[0]
        elif len(skills) == 2:
            skill_text = f"{skills[0]} and {skills[1]}"
        else:
            skill_text = ", ".join(skills[:-1]) + f" and {skills[-1]}"
        sentences.append(f"Core skills include {skill_text}.")

    if experience:
        sentences.append(f"Experience includes {experience}.")

    if projects:
        sentences.append(f"Project work includes {projects}.")

    if certifications:
        sentences.append(f"Certifications include {certifications}.")

    return " ".join(sentences)


def improve_project_description(project_description):
    """Lightly polish and format project text without inventing achievements."""
    text = str(project_description or "").strip()
    if not text:
        raise ValueError("Enter your original project description.")

    if len(text) > 12000:
        raise ValueError("Please keep the project description under 12,000 characters.")

    # Prefer the user's existing line breaks. If they supplied one paragraph,
    # split it into sentences to make the result easier to scan.
    raw_items = [line.strip() for line in text.splitlines() if line.strip()]
    if len(raw_items) <= 1:
        raw_items = re.split(r"(?<=[.!?])\s+", text)

    bullets = []
    for item in raw_items:
        item = re.sub(r"^\s*(?:[-*•]+|\d+[.)])\s*", "", item).strip()
        item = re.sub(r"\s+", " ", item)
        if not item:
            continue

        # Remove first-person phrasing while retaining the candidate's claim.
        item = re.sub(r"^I have\s+", "", item, flags=re.IGNORECASE)
        item = re.sub(r"^I had\s+", "", item, flags=re.IGNORECASE)
        item = re.sub(r"^I\s+", "", item, flags=re.IGNORECASE)
        item = item[0].upper() + item[1:] if item else item

        if item and item[-1] not in ".!?":
            item += "."

        if item:
            bullets.append(item)

    if not bullets:
        raise ValueError("No usable project text was found.")

    return "\n".join(f"• {item}" for item in bullets)


def generate_local_resume_content(resume):
    """Create a plain-text resume document from the legacy Resume form."""
    lines = []
    full_name = clean_summary_text(getattr(resume, "full_name", ""), 150)
    target_role = clean_summary_text(getattr(resume, "target_role", ""), 150)

    if full_name:
        lines.append(full_name.upper())
    if target_role:
        lines.append(target_role)

    contact = [
        clean_summary_text(getattr(resume, "email", ""), 150),
        clean_summary_text(getattr(resume, "phone", ""), 50),
        clean_summary_text(getattr(resume, "location", ""), 150),
    ]
    contact = [item for item in contact if item]
    if contact:
        lines.append(" | ".join(contact))

    sections = [
        ("PROFESSIONAL SUMMARY", "professional_summary"),
        ("EDUCATION", "education"),
        ("EXPERIENCE", "experience"),
        ("SKILLS", "skills"),
        ("PROJECTS", "projects"),
        ("CERTIFICATIONS", "certifications"),
    ]

    for heading, field_name in sections:
        value = clean_summary_text(getattr(resume, field_name, ""), 5000)
        if value:
            lines.extend(["", heading, value])

    if len(lines) <= 1:
        raise ValueError("Add resume details before generating the resume content.")

    return "\n".join(lines).strip()


# EXISTING AI RESUME GENERATOR

# ============================================================



def create_resume(request):



    if request.method == "POST":



        form = ResumeForm(request.POST)



        if form.is_valid():



            resume = form.save(commit=False)



            if request.user.is_authenticated:

                resume.created_by = request.user



            resume.save()



            try:



                generated_text = generate_local_resume_content(resume)



                resume.generated_content = generated_text

                resume.save()



                messages.success(

                    request,

                    "Your resume content was prepared using the free local generator. No API credits were used.",

                )



            except Exception:



                messages.error(

                    request,

                    "Resume saved, but AI generation failed. "

                    "Check your AI configuration and try again.",

                )



            return redirect(

                "resumes:resume_preview",

                resume_id=resume.id,

            )



    else:



        form = ResumeForm()



    return render(

        request,

        "resumes/create_resume.html",

        {"form": form},

    )





# ============================================================

# EXISTING RESUME PREVIEW

# ============================================================



def resume_preview(request, resume_id):



    resume = get_object_or_404(

        Resume,

        id=resume_id,

    )



    if resume.created_by_id:



        if not request.user.is_authenticated:

            return redirect("accounts:login")



        if resume.created_by_id != request.user.id:

            return redirect("home")



    return render(

        request,

        "resumes/resume_preview.html",

        {"resume": resume},

    )





# ============================================================

# EXISTING RESUME HISTORY

# ============================================================



def resume_history(request):



    if request.user.is_authenticated:



        resumes = Resume.objects.filter(

            created_by=request.user

        )



    else:



        resumes = Resume.objects.none()



    return render(

        request,

        "resumes/resume_history.html",

        {"resumes": resumes},

    )





# ============================================================

# BUILDER: CREATE RESUME

# ============================================================



@login_required

def builder_create(request):



    if request.method == "POST":



        form = BuilderResumeForm(request.POST)



        if form.is_valid():



            resume = form.save(commit=False)

            resume.user = request.user



            action = request.POST.get(

                "action",

                "draft",

            )



            resume.status = "draft"

            resume.save()



            if action == "draft":



                messages.success(

                    request,

                    "Resume draft saved successfully!",

                )



                return redirect(

                    "resumes:builder_preview",

                    pk=resume.pk,

                )



            if action == "generate":



                try:



                    summary = generate_builder_summary(resume)



                    resume.professional_summary = summary

                    resume.status = "completed"

                    resume.save()



                    messages.success(

                        request,

                        "Professional summary generated using the free local generator. No API credits used!",

                    )



                except Exception as exc:



                    resume.status = "draft"

                    resume.save()



                    messages.error(

                        request,

                        f"Resume saved as draft. Local summary could not be generated: {exc}",

                    )



                return redirect(

                    "resumes:builder_preview",

                    pk=resume.pk,

                )



            messages.error(

                request,

                "Invalid form action.",

            )



            return redirect("resumes:builder_create")



    else:



        form = BuilderResumeForm()



    return render(

        request,

        "resumes/builder.html",

        {

            "form": form,

            "editing": False,

        },

    )





# ============================================================

# BUILDER: EDIT RESUME

# ============================================================



@login_required

def builder_edit(request, pk):



    resume = get_user_resume(request, pk)



    if request.method == "POST":



        form = BuilderResumeForm(

            request.POST,

            instance=resume,

        )



        if form.is_valid():



            saved_resume = form.save(commit=False)



            action = request.POST.get(

                "action",

                "draft",

            )



            saved_resume.status = "draft"

            saved_resume.save()



            if action == "draft":



                messages.success(

                    request,

                    "Resume updated successfully!",

                )



                return redirect(

                    "resumes:builder_preview",

                    pk=saved_resume.pk,

                )



            if action == "generate":



                try:



                    summary = generate_builder_summary(

                        saved_resume

                    )



                    saved_resume.professional_summary = summary

                    saved_resume.status = "completed"

                    saved_resume.save()



                    messages.success(

                        request,

                        "Resume updated and professional summary generated using the free local generator!",

                    )



                except Exception as exc:



                    saved_resume.status = "draft"

                    saved_resume.save()



                    messages.error(

                        request,

                        f"Resume saved, but the local summary could not be generated: {exc}",

                    )



                return redirect(

                    "resumes:builder_preview",

                    pk=saved_resume.pk,

                )



    else:



        form = BuilderResumeForm(instance=resume)



    return render(

        request,

        "resumes/builder.html",

        {

            "form": form,

            "resume": resume,

            "editing": True,

        },

    )





# ============================================================

# BUILDER: REGENERATE SUMMARY

# ============================================================



@login_required

@require_POST

def builder_ai_summary(request, pk):



    resume = get_user_resume(request, pk)



    try:



        resume.professional_summary = generate_builder_summary(resume)

        resume.status = "completed"

        resume.save()



        messages.success(

            request,

            "Free local professional summary generated successfully!",

        )



    except Exception as exc:



        messages.error(

            request,

            f"Could not generate the local summary: {exc}",

        )



    return redirect(

        "resumes:builder_preview",

        pk=pk,

    )





# ============================================================

# BUILDER: PREVIEW

# ============================================================



@login_required

def builder_preview(request, pk):



    resume = get_user_resume(request, pk)



    return render(

        request,

        "resumes/preview.html",

        {"resume": resume},

    )





# ============================================================

# BUILDER: HISTORY

# ============================================================



@login_required

def builder_history(request):



    resumes = BuilderResume.objects.filter(

        user=request.user

    ).order_by("-updated_at")



    query = request.GET.get("q", "").strip()



    if query:



        resumes = resumes.filter(

            Q(full_name__icontains=query)

            | Q(target_role__icontains=query)

            | Q(title__icontains=query)

        )



    return render(

        request,

        "resumes/history.html",

        {

            "resumes": resumes,

            "query": query,

            "total_count": resumes.count(),

        },

    )





# ============================================================

# BUILDER: DELETE

# ============================================================



@login_required

@require_POST

def builder_delete(request, pk):



    resume = get_user_resume(request, pk)



    resume.delete()



    messages.success(

        request,

        "Resume deleted successfully!",

    )



    return redirect("resumes:builder_history")





# ============================================================

# BUILDER: ATS KEYWORD ANALYSIS

# This is an estimated keyword-overlap score, not a certified ATS score.

# ============================================================



@login_required

def builder_ats_analysis(request, pk):



    resume = get_user_resume(request, pk)



    job_text = (resume.job_description or "").lower()



    if not job_text.strip():



        messages.warning(

            request,

            "Add a job description before ATS analysis.",

        )



        return redirect(

            "resumes:builder_preview",

            pk=pk,

        )



    resume_text = " ".join([

        resume.target_role or "",

        resume.professional_summary or "",

        resume.education or "",

        resume.experience or "",

        resume.skills or "",

        resume.projects or "",

        resume.certifications or "",

    ]).lower()



    words = re.findall(

        r"[a-zA-Z0-9+#.]+",

        job_text,

    )



    stop_words = {

        "the", "and", "for", "with", "you",

        "your", "our", "are", "will", "this",

        "that", "from", "have", "has", "who",

        "what", "about", "into", "years", "their",

        "they", "them", "job", "role", "work",

        "year", "using", "such",

    }



    keywords = {

        word

        for word in words

        if len(word) > 2 and word not in stop_words

    }



    matched = []



    for keyword in sorted(keywords):



        pattern = (

            r"(?<![a-zA-Z0-9])"

            + re.escape(keyword)

            + r"(?![a-zA-Z0-9])"

        )



        if re.search(pattern, resume_text):

            matched.append(keyword)



    missing = sorted(

        keywords - set(matched)

    )



    score = (

        round(len(matched) / len(keywords) * 100)

        if keywords

        else 0

    )



    resume.ats_score = score

    resume.save()



    return render(

        request,

        "resumes/ats_result.html",

        {

            "resume": resume,

            "score": score,

            "matched": matched,

            "missing": missing,

        },

    )





# ============================================================

# BUILDER: PRINT / SAVE AS PDF

# ============================================================



@login_required

def builder_download(request, pk):



    resume = get_user_resume(request, pk)



    return render(

        request,

        "resumes/preview.html",

        {

            "resume": resume,

            "print_mode": True,

        },

    )





# ============================================================

# AI RESUME ARCHITECT: COMMON AI HELPER

# ============================================================



# AI RESUME ARCHITECT: UPLOAD PDF OR DOCX

# ============================================================



@login_required

def architect_upload(request):



    # Save extracted resume as a draft.

    if (

        request.method == "POST"

        and request.POST.get("action") == "save"

    ):



        extracted_text = request.session.get(

            "architect_import_text",

            "",

        )



        if not extracted_text:



            messages.error(

                request,

                "Upload session expired. Please upload again.",

            )



            return redirect("resumes:architect_upload")



        full_name = request.POST.get(

            "full_name",

            "",

        ).strip()



        email = request.POST.get(

            "email",

            "",

        ).strip()



        phone = request.POST.get(

            "phone",

            "",

        ).strip()



        target_role = request.POST.get(

            "target_role",

            "",

        ).strip()



        if not full_name or not email:



            messages.error(

                request,

                "Name and email are required.",

            )



            return redirect("resumes:architect_upload")



        try:

            validate_email(email)



        except ValidationError:



            messages.error(

                request,

                "Enter a valid email address.",

            )



            return redirect("resumes:architect_upload")



        resume = BuilderResume.objects.create(

            user=request.user,

            title=f"{full_name} - Imported Resume",

            career_level="experienced",

            full_name=full_name[:150],

            email=email,

            phone=phone[:30],

            target_role=target_role[:150],

            experience=extracted_text[:30000],

            status="draft",

        )



        request.session.pop(

            "architect_import_text",

            None,

        )



        request.session.pop(

            "architect_import_filename",

            None,

        )



        messages.success(

            request,

            "Resume imported. Review and organize your draft.",

        )



        return redirect(

            "resumes:builder_edit",

            pk=resume.pk,

        )



    # Extract text from the uploaded file.

    if request.method == "POST":



        uploaded = request.FILES.get("resume_file")



        if not uploaded:



            messages.error(

                request,

                "Choose a PDF or DOCX file.",

            )



            return redirect("resumes:architect_upload")



        if uploaded.size > 8 * 1024 * 1024:



            messages.error(

                request,

                "Maximum file size is 8 MB.",

            )



            return redirect("resumes:architect_upload")



        extension = os.path.splitext(

            uploaded.name

        )[1].lower()



        file_bytes = uploaded.read()



        try:



            if extension == ".pdf":



                from pypdf import PdfReader



                reader = PdfReader(BytesIO(file_bytes))



                extracted_text = "\n".join(

                    page.extract_text() or ""

                    for page in reader.pages[:30]

                )



            elif extension == ".docx":



                from docx import Document



                document = Document(BytesIO(file_bytes))



                text_parts = [

                    paragraph.text

                    for paragraph in document.paragraphs

                    if paragraph.text.strip()

                ]



                for table in document.tables:



                    for row in table.rows:



                        text_parts.append(

                            " | ".join(

                                cell.text

                                for cell in row.cells

                            )

                        )



                extracted_text = "\n".join(text_parts)



            else:



                messages.error(

                    request,

                    "Only PDF and DOCX files are supported.",

                )



                return redirect("resumes:architect_upload")



        except ImportError:



            messages.error(

                request,

                "Install readers using: pip install pypdf python-docx",

            )



            return redirect("resumes:architect_upload")



        except Exception as exc:



            messages.error(

                request,

                f"Could not read this file: {exc}",

            )



            return redirect("resumes:architect_upload")



        extracted_text = extracted_text.strip()[:30000]



        if not extracted_text:



            messages.error(

                request,

                "No text extracted. Scanned PDFs require OCR.",

            )



            return redirect("resumes:architect_upload")



        email_match = re.search(

            r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}",

            extracted_text,

            re.IGNORECASE,

        )



        phone_match = re.search(

            r"\+?\d[\d\s().-]{7,}\d",

            extracted_text,

        )



        first_line = next(

            (

                line.strip()

                for line in extracted_text.splitlines()

                if line.strip()

            ),

            "",

        )



        if "@" in first_line or len(first_line) > 100:

            first_line = ""



        request.session["architect_import_text"] = extracted_text



        request.session["architect_import_filename"] = uploaded.name



        return render(

            request,

            "resumes/upload_resume.html",

            {

                "review": True,

                "extracted_text": extracted_text,

                "filename": uploaded.name,

                "full_name": first_line,

                "email": (

                    email_match.group(0)

                    if email_match

                    else request.user.email

                ),

                "phone": (

                    phone_match.group(0)

                    if phone_match

                    else ""

                ),

            },

        )



    return render(

        request,

        "resumes/upload_resume.html",

        {"review": False},

    )





# ============================================================

# AI RESUME ARCHITECT: SUMMARY PAGE

# ============================================================



@login_required

def architect_summary_hub(request):



    resumes = BuilderResume.objects.filter(

        user=request.user

    ).order_by("-updated_at")



    return render(

        request,

        "resumes/summary_hub.html",

        {"resumes": resumes},

    )





# ============================================================

# AI RESUME ARCHITECT: GENERATE SUMMARY

# ============================================================

@login_required

@require_POST

def architect_summaries(request):



    resume_id = request.POST.get("resume_id", "").strip()



    if not resume_id:

        messages.error(request, "Please select a resume.")

        return redirect("resumes:architect_summary_hub")



    # Verify that this resume belongs to the logged-in user.

    try:

        resume = get_user_resume(request, int(resume_id))

    except (ValueError, Http404):

        messages.error(request, "The selected resume was not found.")

        return redirect("resumes:architect_summary_hub")



    # Check whether there is enough information to create a summary.

    candidate_information = [

        resume.full_name,

        resume.target_role,

        resume.education,

        resume.experience,

        resume.skills,

        resume.projects,

        resume.certifications,

    ]



    if not any(value and value.strip() for value in candidate_information):

        messages.error(

            request,

            "Your resume is empty. Add your education, skills, "

            "experience or projects before generating a summary."

        )

        return redirect("resumes:architect_summary_hub")



    try:

        generated_summary = generate_builder_summary(resume)



        resume.professional_summary = generated_summary

        resume.status = "completed"

        resume.save(

            update_fields=[

                "professional_summary",

                "status",

                "updated_at",

            ]

        )



        messages.success(

            request,

            "Your professional summary was generated using the free local generator. No API credits used!"

        )



        return redirect(

            "resumes:architect_preview",

            pk=resume.pk,

        )



    except Exception as exc:



        # Print the actual error in the VS Code terminal.

        print("\n========== RESUME SUMMARY ERROR ==========")

        print(type(exc).__name__)

        print(str(exc))

        print("==========================================\n")



        # Show the error on the webpage too.

        resumes = BuilderResume.objects.filter(

            user=request.user

        ).order_by("-updated_at")



        return render(

            request,

            "resumes/summary_hub.html",

            {

                "resumes": resumes,

                "error_message": str(exc),

                "selected_resume_id": resume.pk,

            },

            status=502,

        )





# ============================================================

# AI RESUME ARCHITECT: PROJECT DESCRIPTION ENHANCER

# ============================================================



@login_required

def architect_project_enhancer(request):



    resumes = BuilderResume.objects.filter(

        user=request.user

    ).order_by("-updated_at")



    context = {

        "resumes": resumes,

        "improved_text": "",

        "project_description": "",

        "selected_resume_id": "",

        "target_role": "",

    }



    if request.method == "POST":



        action = request.POST.get(

            "action",

            "improve",

        )



        resume_id = request.POST.get(

            "resume_id",

            "",

        ).strip()



        context["selected_resume_id"] = resume_id



        context["target_role"] = request.POST.get(

            "target_role",

            "",

        ).strip()



        # Save improved text to the selected resume.

        if action == "save":



            if not resume_id:



                messages.error(

                    request,

                    "Select a resume before saving.",

                )



                return redirect(

                    "resumes:architect_project_enhancer"

                )



            resume = get_user_resume(

                request,

                resume_id,

            )



            improved = request.POST.get(

                "improved_text",

                "",

            ).strip()



            if not improved:



                messages.error(

                    request,

                    "No improved text to save.",

                )



                return redirect(

                    "resumes:architect_project_enhancer"

                )



            resume.projects = improved

            resume.save()



            messages.success(

                request,

                "Improved project description saved.",

            )



            return redirect(

                "resumes:builder_edit",

                pk=resume.pk,

            )



        # Generate improved project content.

        original = request.POST.get(

            "project_description",

            "",

        ).strip()



        context["project_description"] = original



        if not original:



            messages.error(

                request,

                "Enter your original project description.",

            )



        else:



            role = (

                context["target_role"]

                or "the target role"

            )



            try:



                context["improved_text"] = improve_project_description(original)

            except Exception as exc:



                messages.error(

                    request,

                    f"Project improvement failed: {exc}",

                )



    return render(

        request,

        "resumes/project_enhancer.html",

        context,

    )





# ============================================================

# AI RESUME ARCHITECT: TEMPLATE CHOICES

# ============================================================



TEMPLATE_CHOICES = [

    {

        "id": "modern",

        "name": "Modern Professional",

        "description": "A contemporary design with a purple accent.",

    },

    {

        "id": "classic",

        "name": "Classic ATS",

        "description": "A simple single-column resume layout.",

    },

    {

        "id": "minimal",

        "name": "Minimal Clean",

        "description": "A clean monochrome resume layout.",

    },

]





# ============================================================

# AI RESUME ARCHITECT: SELECT TEMPLATE

# ============================================================



@login_required

def architect_templates(request):



    resumes = BuilderResume.objects.filter(

        user=request.user

    ).order_by("-updated_at")



    if request.method == "POST":



        resume_id = request.POST.get(

            "resume_id",

            "",

        ).strip()



        template_style = request.POST.get(

            "template_style",

            "modern",

        )



        allowed_styles = {

            item["id"]

            for item in TEMPLATE_CHOICES

        }



        if template_style not in allowed_styles:



            messages.error(

                request,

                "Choose a valid resume template.",

            )



            return redirect(

                "resumes:architect_templates"

            )



        if not resume_id:



            messages.error(

                request,

                "Select a resume first.",

            )



            return redirect(

                "resumes:architect_templates"

            )



        resume = get_user_resume(

            request,

            resume_id,

        )



        request.session[

            f"architect_template_{resume.pk}"

        ] = template_style



        messages.success(

            request,

            "Resume template selected successfully.",

        )



        return redirect(

            "resumes:architect_preview",

            pk=resume.pk,

        )



    return render(

        request,

        "resumes/template_gallery.html",

        {

            "resumes": resumes,

            "template_choices": TEMPLATE_CHOICES,

        },

    )





# ============================================================

# AI RESUME ARCHITECT: RESUME LIBRARY

# ============================================================



@login_required

def architect_library(request):



    resumes = BuilderResume.objects.filter(

        user=request.user

    ).order_by("-updated_at")



    return render(

        request,

        "resumes/architect_library.html",

        {"resumes": resumes},

    )





# ============================================================

# AI RESUME ARCHITECT: PREVIEW

# ============================================================



@login_required

def architect_preview(request, pk):



    resume = get_user_resume(

        request,

        pk,

    )



    template_style = request.session.get(

        f"architect_template_{resume.pk}",

        "modern",

    )



    if template_style not in {

        "modern",

        "classic",

        "minimal",

    }:

        template_style = "modern"



    return render(

        request,

        "resumes/architect_preview.html",

        {

            "resume": resume,

            "template_style": template_style,

            "print_mode": False,

        },

    )





# ============================================================

# AI RESUME ARCHITECT: PRINT / SAVE AS PDF

# ============================================================



@login_required

def architect_download(request, pk):



    resume = get_user_resume(

        request,

        pk,

    )



    template_style = request.session.get(

        f"architect_template_{resume.pk}",

        "modern",

    )



    if template_style not in {

        "modern",

        "classic",

        "minimal",

    }:

        template_style = "modern"



    return render(

        request,

        "resumes/architect_preview.html",

        {

            "resume": resume,

            "template_style": template_style,

            "print_mode": True,

        },

    )
