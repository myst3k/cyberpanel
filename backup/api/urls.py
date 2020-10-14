from django.urls import path

from backup.api.views import ListBackups

urlpatterns = [
    path('', ListBackups.as_view(), name="listBackups"),
]
