from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("reports/", views.AddEventsPage, name="addevents"),
    path("reports/save_tmp", views.SaveEvents, name="save_tmp"),
    path("reports/finalizework", views.FinaliseWorkShift, name="finalizework"),
    path("reports/removeline", views.RemoveLine, name="removeline"),
    path("reports/graphreport", views.GraphReport, name="graphreport"),
    path("reports/graphreportanual", views.GraphReportAnual, name="graphreportanual"),
]