from django.urls import path

from backup.api.views import ListBackups

urlpatterns = [
    path(r'^', ListBackups.as_view(), name="listBackups"),
]
