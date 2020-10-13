import os

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from loginSystem.models import Administrator
from loginSystem.views import loadLoginPage
from plogical.acl import ACLManager
from websiteFunctions.models import NormalBackupDests, BackupJob


def index(request: HttpRequest) -> HttpResponse:
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)
        return render(request, 'backup/index.html', currentACL)
    except KeyError:
        return redirect(loadLoginPage)


def backupSite(request: HttpRequest) -> HttpResponse:
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        if ACLManager.currentContextPermission(currentACL, 'createBackup') == 0:
            return ACLManager.loadError()

        websitesName = ACLManager.findAllSites(currentACL, userID)
        return render(request, 'backup/backup.html', {'websiteList': websitesName})
    except KeyError:
        return redirect(loadLoginPage)


def restoreSite(request: HttpRequest) -> HttpResponse:
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        if ACLManager.currentContextPermission(currentACL, 'restoreBackup') == 0:
            return ACLManager.loadError()

        websitesList = ACLManager.findAllSites(currentACL, userID)

        return render(request, 'backup/restore.html', {'websitesList': websitesList})
    except KeyError:
        return redirect(loadLoginPage)


def backupDestinations(request: HttpRequest) -> HttpResponse:
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        if ACLManager.currentContextPermission(currentACL, 'addDeleteDestinations') == 0:
            return ACLManager.loadError()

        return render(request, 'backup/backupDestinations.html', {})
    except KeyError:
        return redirect(loadLoginPage)


def scheduleBackup(request: HttpRequest) -> HttpResponse:
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        if ACLManager.currentContextPermission(currentACL, 'scheDuleBackups') == 0:
            return ACLManager.loadError()

        destinations = NormalBackupDests.objects.all()

        dests = []

        for dest in destinations:
            dests.append(dest.name)

        websitesName = ACLManager.findAllSites(currentACL, userID)

        return render(request, 'backup/backupSchedule.html', {'destinations': dests, 'websites': websitesName})
    except KeyError:
        return redirect(loadLoginPage)


def gDrive(request: HttpRequest) -> HttpResponse:
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        admin = Administrator.objects.get(pk=userID)

        if ACLManager.currentContextPermission(currentACL, 'createBackup') == 0:
            return ACLManager.loadError()

        gDriveAcctsList = []

        gDriveAccts = admin.gdrive_set.all()

        for items in gDriveAccts:
            gDriveAcctsList.append(items.name)

        websitesName = ACLManager.findAllSites(currentACL, userID)

        return render(request, 'backup/googleDrive.html', {'accounts': gDriveAcctsList, 'websites': websitesName})
    except KeyError:
        return redirect(loadLoginPage)


def remoteBackups(request: HttpRequest) -> HttpResponse:
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        if ACLManager.currentContextPermission(currentACL, 'remoteBackups') == 0:
            return ACLManager.loadError()

        return render(request, 'backup/remoteBackups.html')
    except KeyError:
        return redirect(loadLoginPage)


def backupLogs(request: HttpRequest) -> HttpResponse:
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        if currentACL['admin'] == 1:
            pass
        else:
            return ACLManager.loadError()

        all_files = []

        logFiles = BackupJob.objects.all().order_by('-id')

        for logFile in logFiles:
            all_files.append(logFile.logFile)

        return render(request, 'backup/backupLogs.html', {'backups': all_files})
    except KeyError:
        return redirect(loadLoginPage)
