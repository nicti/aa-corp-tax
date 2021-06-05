from django.urls import path

from . import views

app_name = "corptax"

urlpatterns = [
    path("", views.index, name="index"),
]
