
from django.contrib import admin
from .models import BuilderResume


@admin.register(BuilderResume)
class BuilderResumeAdmin(admin.ModelAdmin):

    list_display = (
        "full_name",
        "email",
        "target_role",
        "status",
        "ats_score",
        "updated_at",
    )

    list_filter = ("status", "career_level")

    search_fields = (
        "full_name",
        "email",
        "target_role",
    )
