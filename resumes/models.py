
from django.conf import settings
from django.db import models


class Resume(models.Model):

    JOB_ROLES = [
        ("Python Developer", "Python Developer"),
        ("Data Analyst", "Data Analyst"),
        ("Web Developer", "Web Developer"),
        ("Java Developer", "Java Developer"),
        ("Full Stack Developer", "Full Stack Developer"),
        ("AI Engineer", "AI Engineer"),
        ("Other", "Other"),
    ]

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="generated_resumes"
    )

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=200, blank=True)

    target_role = models.CharField(
        max_length=100,
        choices=JOB_ROLES
    )

    education = models.TextField()
    skills = models.TextField()
    experience = models.TextField(blank=True)
    projects = models.TextField()
    certifications = models.TextField(blank=True)
    professional_summary = models.TextField(blank=True)
    generated_content = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.target_role}"


class BuilderResume(models.Model):

    CAREER_LEVELS = [
        ("student", "Student"),
        ("fresher", "Fresher"),
        ("experienced", "Experienced Professional"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="builder_resumes"
    )

    title = models.CharField(
        max_length=200,
        default="My Professional Resume"
    )

    career_level = models.CharField(
        max_length=20,
        choices=CAREER_LEVELS,
        default="fresher"
    )

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=200, blank=True)

    linkedin = models.URLField(blank=True)
    portfolio = models.URLField(blank=True)
    github = models.URLField(blank=True)

    target_role = models.CharField(max_length=150, blank=True)
    professional_summary = models.TextField(blank=True)

    education = models.TextField(
        blank=True,
        help_text="Enter each qualification on a separate line."
    )

    experience = models.TextField(
        blank=True,
        help_text="Enter your work experience or internships."
    )

    skills = models.TextField(
        blank=True,
        help_text="Separate skills with commas."
    )

    projects = models.TextField(
        blank=True,
        help_text="Enter your projects and descriptions."
    )

    certifications = models.TextField(blank=True)
    job_description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    ats_score = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title} - {self.full_name}"
