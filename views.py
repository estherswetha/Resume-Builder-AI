import os
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Resume, BuilderResume
from .forms import ResumeForm, BuilderResumeForm
from ai_assistant.services import generate_ai_resume


# ============================================================
# HELPER 1: GET A BUILDER RESUME BELONGING TO THE LOGGED-IN USER
# ============================================================

def get_user_resume(request, pk):
    return get_object_or_404(
        BuilderResume,
        pk=pk,
        user=request.user
    )


# ============================================================
# HELPER 2: GENERATE AN AI PROFESSIONAL SUMMARY
# This generates the summary section, not every resume section.
# ============================================================

def generate_builder_summary(resume):
    api_key = (
        getattr(settings, "OPENAI_API_KEY", "")
        or os.getenv("OPENAI_API_KEY", "")
    )

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. Add it to your project .env file."
        )

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The OpenAI package is not installed. Run: "
            "python -m pip install openai"
        ) from exc

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=getattr(
            settings,
            "OPENAI_MODEL",
            os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        ),
        instructions=(
            "You are a professional resume writer. Create a concise, "
            "professional, ATS-friendly resume summary. Use only the "
            "information supplied by the candidate. Never invent "
            "qualifications, skills, achievements, dates, employers, "
            "or experience. For students and freshers, highlight "
            "education, projects, and relevant skills."
        ),
        input=f"""
Candidate Name:
{resume.full_name}

Career Level:
{resume.get_career_level_display()}

Target Role:
{resume.target_role}

Education:
{resume.education}

Experience:
{resume.experience}

Skills:
{resume.skills}

Projects:
{resume.projects}

Certifications:
{resume.certifications}

Job Description:
{getattr(resume, "job_description", "")}

Write only the professional resume summary. Do not add a heading.
"""
    )

    generated_text = (response.output_text or "").strip()

    if not generated_text:
        raise ValueError("The AI service returned an empty summary.")

    return generated_text


# ============================================================
# 1. EXISTING RESUME GENERATOR
# Keeps your original Resume model workflow.
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
                generated_text = generate_ai_resume(resume)
                resume.generated_content = generated_text
                resume.save()

                messages.success(
                    request,
                    "Your AI resume was generated successfully!"
                )

            except Exception:
                messages.error(
                    request,
                    "Resume saved, but AI generation failed. "
                    "Please check your AI configuration and try again."
                )

            return redirect(
                "resumes:resume_preview",
                resume_id=resume.id
            )

    else:
        form = ResumeForm()

    return render(
        request,
        "resumes/create_resume.html",
        {"form": form}
    )


# ============================================================
# 2. EXISTING RESUME PREVIEW
# ============================================================

def resume_preview(request, resume_id):
    resume = get_object_or_404(
        Resume,
        id=resume_id
    )

    if resume.created_by_id:
        if not request.user.is_authenticated:
            return redirect("accounts:login")

        if resume.created_by_id != request.user.id:
            return redirect("home")

    return render(
        request,
        "resumes/resume_preview.html",
        {"resume": resume}
    )


# ============================================================
# 3. EXISTING RESUME HISTORY
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
        {"resumes": resumes}
    )


# ============================================================
# 4. SMART RESUME BUILDER - CREATE
# ============================================================

@login_required
def builder_create(request):
    if request.method == "POST":
        form = BuilderResumeForm(request.POST)

        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user

            action = request.POST.get("action", "draft")

            # Save the candidate's information first so it is not lost
            # if the external AI service is unavailable.
            resume.status = "draft"
            resume.save()

            if action == "draft":
                messages.success(
                    request,
                    "Your resume draft has been saved successfully!"
                )
                return redirect(
                    "resumes:builder_preview",
                    pk=resume.pk
                )

            if action == "generate":
                try:
                    generated_text = generate_builder_summary(resume)

                    resume.professional_summary = generated_text
                    resume.status = "completed"
                    resume.save()

                    messages.success(
                        request,
                        "Your AI professional summary was generated. "
                        "Please review your resume."
                    )

                except Exception:
                    # Keep all submitted details saved as a draft.
                    resume.status = "draft"
                    resume.save()

                    messages.error(
                        request,
                        "Your resume details were saved as a draft, "
                        "but AI generation failed. Check your API key, "
                        "internet connection, and OpenAI package, then retry."
                    )

                return redirect(
                    "resumes:builder_preview",
                    pk=resume.pk
                )

            messages.error(request, "Invalid form action.")
            return redirect("resumes:builder_create")

    else:
        form = BuilderResumeForm()

    return render(
        request,
        "resumes/builder.html",
        {
            "form": form,
            "editing": False
        }
    )


# ============================================================
# 5. EDIT EXISTING BUILDER RESUME
# ============================================================

@login_required
def builder_edit(request, pk):
    resume = get_user_resume(request, pk)

    if request.method == "POST":
        form = BuilderResumeForm(
            request.POST,
            instance=resume
        )

        if form.is_valid():
            saved_resume = form.save(commit=False)
            action = request.POST.get("action", "draft")

            # Save changes as a draft before trying AI generation.
            saved_resume.status = "draft"
            saved_resume.save()

            if action == "draft":
                messages.success(
                    request,
                    "Your draft was updated successfully."
                )
                return redirect(
                    "resumes:builder_preview",
                    pk=saved_resume.pk
                )

            if action == "generate":
                try:
                    generated_text = generate_builder_summary(saved_resume)

                    saved_resume.professional_summary = generated_text
                    saved_resume.status = "completed"
                    saved_resume.save()

                    messages.success(
                        request,
                        "Your resume was updated and the AI summary was generated!"
                    )

                except Exception:
                    saved_resume.status = "draft"
                    saved_resume.save()

                    messages.error(
                        request,
                        "Your changes were saved as a draft, but AI generation "
                        "failed. Check your AI configuration and try again."
                    )

                return redirect(
                    "resumes:builder_preview",
                    pk=saved_resume.pk
                )

            messages.error(request, "Invalid form action.")
            return redirect(
                "resumes:builder_edit",
                pk=saved_resume.pk
            )

    else:
        form = BuilderResumeForm(instance=resume)

    return render(
        request,
        "resumes/builder.html",
        {
            "form": form,
            "resume": resume,
            "editing": True
        }
    )


# ============================================================
# 6. RE-GENERATE AI PROFESSIONAL SUMMARY
# ============================================================

@login_required
@require_POST
def builder_ai_summary(request, pk):
    resume = get_user_resume(request, pk)

    try:
        generated_text = generate_builder_summary(resume)

        resume.professional_summary = generated_text
        resume.status = "completed"
        resume.save()

        messages.success(
            request,
            "AI professional summary generated successfully!"
        )

    except Exception:
        messages.error(
            request,
            "AI generation failed. Please check your API key and try again."
        )

    return redirect(
        "resumes:builder_preview",
        pk=pk
    )


# ============================================================
# 7. BUILDER RESUME PREVIEW
# ============================================================

@login_required
def builder_preview(request, pk):
    resume = get_user_resume(request, pk)

    return render(
        request,
        "resumes/preview.html",
        {"resume": resume}
    )


# ============================================================
# 8. BUILDER RESUME HISTORY WITH SEARCH
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
            "total_count": resumes.count()
        }
    )


# ============================================================
# 9. DELETE BUILDER RESUME
# ============================================================

@login_required
@require_POST
def builder_delete(request, pk):
    resume = get_user_resume(request, pk)
    resume.delete()

    messages.success(
        request,
        "Resume deleted successfully."
    )

    return redirect("resumes:builder_history")


# ============================================================
# 10. ATS KEYWORD ANALYSIS
# ============================================================

@login_required
def builder_ats_analysis(request, pk):
    resume = get_user_resume(request, pk)

    job_text = (resume.job_description or "").lower()

    if not job_text.strip():
        messages.warning(
            request,
            "Please add a job description before running ATS analysis."
        )
        return redirect(
            "resumes:builder_preview",
            pk=pk
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
        job_text
    )

    stop_words = {
        "the", "and", "for", "with", "you",
        "your", "our", "are", "will", "this",
        "that", "from", "have", "has", "who",
        "what", "about", "into", "years",
        "their", "they", "them", "job", "role",
        "work", "year", "using", "such"
    }

    keywords = {
        word for word in words
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

    missing = sorted(keywords - set(matched))

    score = (
        round(len(matched) / len(keywords) * 100)
        if keywords else 0
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
            "missing": missing
        }
    )


# ============================================================
# 11. RESUME DOWNLOAD / PRINT
# ============================================================

@login_required
def builder_download(request, pk):
    resume = get_user_resume(request, pk)

    return render(
        request,
        "resumes/preview.html",
        {
            "resume": resume,
            "print_mode": True
        }
    )
