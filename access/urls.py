from django.urls import path

from . import views

app_name = "access"

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("menu/", views.MenuPageView.as_view(), name="menu"),
]