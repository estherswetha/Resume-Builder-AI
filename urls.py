
from django.urls import path
from . import views


app_name = "resumes"


urlpatterns = [

    # ==================================================
    # 1. EXISTING AI RESUME GENERATOR
    # ==================================================

    # Create a resume
    path(
        "create/",
        views.create_resume,
        name="create_resume"
    ),

    # Preview existing resume
    path(
        "preview/<int:resume_id>/",
        views.resume_preview,
        name="resume_preview"
    ),

    # Existing resume history
    path(
        "history/",
        views.resume_history,
        name="resume_history"
    ),


    # ==================================================
    # 2. SMART RESUME BUILDER
    # ==================================================

    # Create a new resume
    path(
        "builder/",
        views.builder_create,
        name="builder_create"
    ),

    # Edit an existing resume
    path(
        "builder/<int:pk>/edit/",
        views.builder_edit,
        name="builder_edit"
    ),

    # Preview generated resume
    path(
        "builder/<int:pk>/preview/",
        views.builder_preview,
        name="builder_preview"
    ),

    # View saved resume history
    path(
        "builder/history/",
        views.builder_history,
        name="builder_history"
    ),

    # Delete a resume
    path(
        "builder/<int:pk>/delete/",
        views.builder_delete,
        name="builder_delete"
    ),

    # Generate AI professional summary
    path(
        "builder/<int:pk>/ai-summary/",
        views.builder_ai_summary,
        name="builder_ai_summary"
    ),

    # ATS keyword analysis
    path(
        "builder/<int:pk>/ats-analysis/",
        views.builder_ats_analysis,
        name="builder_ats_analysis"
    ),

    # Download / Print resume
    path(
        "builder/<int:pk>/download/",
        views.builder_download,
        name="builder_download"
    ),

]
