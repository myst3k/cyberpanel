from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^createBackup$', views.create_backup, name='createBackupInc'),
    url(r'^restoreRemoteBackups$', views.restoreRemoteBackups, name='restoreRemoteBackupsInc'),
    url(r'^backupDestinations$', views.backup_destinations, name='backupDestinationsInc'),
    url(r'^addDestination$', views.add_destination, name='addDestinationInc'),
    url(r'^populateCurrentRecords$', views.populate_current_records, name='populateCurrentRecordsInc'),
    url(r'^removeDestination$', views.remove_destination, name='removeDestinationInc'),
    url(r'^fetchCurrentBackups$', views.fetch_current_backups, name='fetchCurrentBackupsInc'),
    url(r'^submitBackupCreation$', views.submit_backup_creation, name='submitBackupCreationInc'),
    url(r'^getBackupStatus$', views.get_backup_status, name='getBackupStatusInc'),
    url(r'^deleteBackup$', views.delete_backup, name='deleteBackupInc'),
    url(r'^fetchRestorePoints$', views.fetch_restore_points, name='fetchRestorePointsInc'),
    url(r'^restorePoint$', views.restore_point, name='restorePointInc'),
    url(r'^scheduleBackups$', views.scheduleBackups, name='scheduleBackupsInc'),
    url(r'^submitBackupSchedule$', views.submitBackupSchedule, name='submitBackupScheduleInc'),
    url(r'^scheduleDelete$', views.scheduleDelete, name='scheduleDeleteInc'),
    url(r'^getCurrentBackupSchedules$', views.getCurrentBackupSchedules, name='getCurrentBackupSchedulesInc'),
    url(r'^fetchSites$', views.fetchSites, name='fetchSites'),
    url(r'^saveChanges$', views.saveChanges, name='saveChanges'),
    url(r'^removeSite$', views.removeSite, name='removeSite'),
    url(r'^addWebsite$', views.addWebsite, name='addWebsite'),
]