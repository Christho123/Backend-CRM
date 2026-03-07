from django.urls import path

from .views.analytics import (
    AnalyticsSummaryView,
    ClicksTimeSeriesView,
    NewEmployeesTimeSeriesView,
    NewUsersTimeSeriesView,
)

app_name = "analytics"

urlpatterns = [
    path("summary/", AnalyticsSummaryView.as_view(), name="summary"),
    path("clicks/", ClicksTimeSeriesView.as_view(), name="clicks_timeseries"),
    path("new-employees/", NewEmployeesTimeSeriesView.as_view(), name="new_employees_timeseries"),
    path("new-users/", NewUsersTimeSeriesView.as_view(), name="new_users_timeseries"),
]

