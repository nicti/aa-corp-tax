from django.urls import path

from . import views

app_name = "corptax"

urlpatterns = [
    path("", views.index, name="index"),
    path(r'admin/', views.admin, name="admin"),
    path(r'settings/', views.SettingsView.as_view(), name="settings"),
]
