
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render


def home(request):
    return render(request, "home.html")


def features(request):
    return render(request, "features.html")


def how_it_works(request):
    return render(request, "how_it_works.html")


def about(request):
    return render(request, "about.html")


urlpatterns = [

    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "",
        home,
        name="home",
    ),

    # Resume application
    path(
        "resumes/",
        include("resumes.urls"),
    ),

    # Main website pages
    path(
        "features/",
        features,
        name="features",
    ),

    path(
        "how-it-works/",
        how_it_works,
        name="how_it_works",
    ),

    path(
        "about/",
        about,
        name="about",
    ),

    # User authentication
    path(
        "accounts/",
        include("accounts.urls"),
    ),

]
