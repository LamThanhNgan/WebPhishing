from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.about, name="about"),
    path("details", views.details, name="details"),
]
