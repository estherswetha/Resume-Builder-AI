from django.urls import path
from . import views

app_name = "resumes"

urlpatterns = [

    # =================================================
    # EXISTING RESUME GENERATOR
    # =================================================

    path(
        "create/",
        views.create_resume,
        name="create_resume",
    ),

    path(
        "preview/<int:resume_id>/",
        views.resume_preview,
        name="resume_preview",
    ),

    path(
        "history/",
        views.resume_history,
        name="resume_history",
    ),

    # =================================================
    # EXISTING SMART RESUME BUILDER
    # =================================================

    path(
        "builder/",
        views.builder_create,
        name="builder_create",
    ),

    path(
        "builder/<int:pk>/edit/",
        views.builder_edit,
        name="builder_edit",
    ),

    path(
        "builder/<int:pk>/preview/",
        views.builder_preview,
        name="builder_preview",
    ),

    path(
        "builder/history/",
        views.builder_history,
        name="builder_history",
    ),

    path(
        "builder/<int:pk>/delete/",
        views.builder_delete,
        name="builder_delete",
    ),

    path(
        "builder/<int:pk>/ai-summary/",
        views.builder_ai_summary,
        name="builder_ai_summary",
    ),

    path(
        "builder/<int:pk>/ats-analysis/",
        views.builder_ats_analysis,
        name="builder_ats_analysis",
    ),

    path(
        "builder/<int:pk>/download/",
        views.builder_download,
        name="builder_download",
    ),

    # =================================================
    # AI RESUME ARCHITECT WORKSPACE
    # =================================================

    path(
        "architect/",
        views.feature_detail,
        {"feature_slug": "architect"},
        name="resume_architect",
    ),

    path(
        "architect/upload/",
        views.architect_upload,
        name="architect_upload",
    ),

    path(
        "architect/summaries/",
        views.architect_summary_hub,
        name="architect_summary_hub",
    ),

    path(
        "architect/summaries/generate/",
        views.architect_summaries,
        name="architect_summaries",
    ),

    path(
        "architect/project-enhancer/",
        views.architect_project_enhancer,
        name="architect_project_enhancer",
    ),

    path(
        "architect/templates/",
        views.architect_templates,
        name="architect_templates",
    ),

    path(
        "architect/library/",
        views.architect_library,
        name="architect_library",
    ),

    path(
        "architect/<int:pk>/preview/",
        views.architect_preview,
        name="architect_preview",
    ),

    path(
        "architect/<int:pk>/download/",
        views.architect_download,
        name="architect_download",
    ),

    # =================================================
    # SIX HOMEPAGE FEATURE LINKS
    # =================================================

    path(
        "career-tools/<slug:feature_slug>/",
        views.feature_detail,
        name="career_tool_detail",
    ),

    # Other feature pages
    path(
        "ats-intelligence/",
        views.feature_detail,
        {"feature_slug": "ats-intelligence"},
        name="ats_intelligence",
    ),

    path(
        "job-match/",
        views.feature_detail,
        {"feature_slug": "job-match"},
        name="job_match",
    ),

    path(
        "skill-enhancer/",
        views.feature_detail,
        {"feature_slug": "skill-enhancer"},
        name="skill_enhancer",
    ),

    path(
        "interview-coach/",
        views.feature_detail,
        {"feature_slug": "interview-coach"},
        name="interview_coach",
    ),

    path(
        "career-vault/",
        views.feature_detail,
        {"feature_slug": "career-vault"},
        name="career_vault",
    ),
]