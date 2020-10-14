from django.conf.urls import url, include
from . import views

app_name = 'backup'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^backupSite', views.backupSite, name='backupSite'),
    url(r'^restoreSite', views.restoreSite, name='restoreSite'),
    url(r'^backupDestinations', views.backupDestinations, name='backupDestinations'),
    url(r'^scheduleBackup', views.scheduleBackup, name='scheduleBackup'),
    url(r'^gDrive$', views.gDrive, name='gDrive'),
    url(r'^remoteBackups', views.remoteBackups, name='remoteBackups'),
    url(r'^backupLogs$', views.backupLogs, name='backupLogs'),

    url(r'^', include('backup.api.urls_v1')),
]
