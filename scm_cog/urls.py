"""scm_cog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import *
from . import views


app_name = "scm_cog"

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("menu/", views.MenuPageView, name="menu"),
    path("", views.HomePageView, name="home"),
    path("personal/changepassword/", views.ChangePasswordView, name="changepassword"),
    path("reports/", views.AddEventsPage, name="addevents"),
    path("reports/save_tmp", views.SaveEvents, name="save_tmp"),
    path("reports/finalizework", views.FinaliseWorkShift, name="finalizework"),
    path("reports/removeline", views.RemoveLine, name="removeline"),
    path("reports/graphreport", views.GraphReport, name="graphreport"),
    path("reports/graphreportanual", views.GraphReportAnual, name="graphreportanual"),
    
]

handler404 = "scm_cog.views.Handler_not_found"