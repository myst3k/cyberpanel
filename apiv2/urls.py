from django.urls import path

from apiv2.backup_views import ListBackups

urlpatterns = [
    path('backups', ListBackups.as_view(), name="backups"),
]
