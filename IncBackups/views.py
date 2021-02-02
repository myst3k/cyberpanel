# -*- coding: utf-8 -*-

import json
import os
import stat
import time
from pathlib import Path
from random import randint

from django.shortcuts import HttpResponse, redirect
from django.shortcuts import render

from loginSystem.models import Administrator
from loginSystem.views import loadLoginPage
from plogical.CyberCPLogFileWriter import CyberCPLogFileWriter as logging
from plogical.acl import ACLManager
from plogical.processUtilities import ProcessUtilities as pu
from plogical.virtualHostUtilities import virtualHostUtilities as vhu
from websiteFunctions.models import Websites
from .IncBackupProvider import IncBackupProvider
from .IncBackupPath import IncBackupPath
from .IncBackupsControl import IncJobs
from .models import IncJob, BackupJob, JobSites


def defRenderer(request, templateName, args):
    return render(request, templateName, args)


def createBackup(request):
    try:
        user_id = request.session['userID']
        current_acl = ACLManager.loadedACL(user_id)

        if ACLManager.currentContextPermission(current_acl, 'createBackup') == 0:
            return ACLManager.loadError()

        websites = ACLManager.findAllSites(current_acl, user_id)

        destinations = ['local']

        path = Path(IncBackupPath.SFTP.value)
        if path.exists():
            for item in path.iterdir():
                destinations.append('sftp:%s' % item.name)

        path = Path(IncBackupPath.AWS.value)
        if os.path.exists(path):
            for item in path.iterdir():
                destinations.append('s3:s3.amazonaws.com/%s' % item.name)

        return defRenderer(request, 'IncBackups/createBackup.html',
                           {'websiteList': websites, 'destinations': destinations})
    except BaseException as msg:
        logging.writeToFile(str(msg))
        return redirect(loadLoginPage)


def backupDestinations(request):
    try:
        user_id = request.session['userID']
        current_acl = ACLManager.loadedACL(user_id)

        if ACLManager.currentContextPermission(current_acl, 'addDeleteDestinations') == 0:
            return ACLManager.loadError()

        return defRenderer(request, 'IncBackups/incrementalDestinations.html', {})
    except BaseException as msg:
        logging.writeToFile(str(msg))
        return redirect(loadLoginPage)


def addDestination(request):
    try:
        user_id = request.session['userID']
        current_acl = ACLManager.loadedACL(user_id)

        if ACLManager.currentContextPermission(current_acl, 'addDeleteDestinations') == 0:
            return ACLManager.loadErrorJson('destStatus', 0)

        data = json.loads(request.body)

        if data['type'].lower() == IncBackupProvider.SFTP.name.lower():
            path = Path(IncBackupPath.SFTP.value)
            path.mkdir(exist_ok=True)

            ip_address = data['IPAddress']
            password = data['password']

            address_file = path / ip_address
            port = data.get('backupSSHPort', '22')

            if address_file.exists():
                final_dic = {'status': 0, 'error_message': 'This destination already exists.'}
                final_json = json.dumps(final_dic)
                return HttpResponse(final_json)

            python_path = Path('/usr/local/CyberCP/bin/python')
            backup_utils = Path(vhu.cyberPanel) / "plogical/backupUtilities.py"

            exec_args = "submitDestinationCreation --ipAddress %s --password %s --port %s --user %s" % \
                        (ip_address, password, port, 'root')

            exec_cmd = "%s %s %s" % (python_path, backup_utils, exec_args)

            if Path(pu.debugPath).exists():
                logging.writeToFile(exec_cmd)

            output = pu.outputExecutioner(exec_cmd)

            if Path(pu.debugPath).exists():
                logging.writeToFile(output)

            if output.find('1,') > -1:
                content = '%s\n%s' % (ip_address, port)
                with open(address_file, 'w') as outfile:
                    outfile.write(content)

                command = 'cat /root/.ssh/config'
                current_config = pu.outputExecutioner(command)

                tmp_file = '/home/cyberpanel/sshconfig'
                with open(tmp_file, 'w') as outfile:
                    if current_config.find('cat') == -1:
                        outfile.write(current_config)

                    content = "Host %s\n" \
                              "    IdentityFile ~/.ssh/cyberpanel\n" \
                              "    Port %s\n" % (ip_address, port)
                    if current_config.find(ip_address) == -1:
                        outfile.write(content)

                command = 'mv %s /root/.ssh/config' % tmp_file
                pu.executioner(command)

                command = 'chown root:root /root/.ssh/config'
                pu.executioner(command)

                final_dic = {'status': 1, 'error_message': 'None'}
            else:
                final_dic = {'status': 0, 'error_message': output}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

        if data['type'].lower() == IncBackupProvider.AWS.name.lower():
            path = Path(IncBackupPath.AWS.value)
            path.mkdir(exist_ok=True)

            access_key = data['AWS_ACCESS_KEY_ID']
            secret_key = data['AWS_SECRET_ACCESS_KEY']

            aws_file = path / access_key

            with open(aws_file, 'w') as outfile:
                outfile.write(secret_key)

            aws_file.chmod(stat.S_IRUSR | stat.S_IWUSR)

            final_dic = {'status': 1}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)

    except BaseException as msg:
        final_dic = {'status': 0, 'error_message': str(msg)}
        final_json = json.dumps(final_dic)
        return HttpResponse(final_json)


def populateCurrentRecords(request):
    try:
        user_id = request.session['userID']
        current_acl = ACLManager.loadedACL(user_id)

        if ACLManager.currentContextPermission(current_acl, 'addDeleteDestinations') == 0:
            return ACLManager.loadErrorJson('fetchStatus', 0)

        data = json.loads(request.body)

        json_data = []
        if data['type'].lower() == IncBackupProvider.SFTP.name.lower():
            path = Path(IncBackupPath.SFTP.value)

            if path.exists():
                for item in path.iterdir():
                    with open(item, 'r') as infile:
                        _file = infile.readlines()
                        json_data.append({
                            'ip': _file[0].strip('\n'),
                            'port': _file[1],
                        })
            else:
                final_json = json.dumps({'status': 1, 'error_message': "None", "data": ''})
                return HttpResponse(final_json)

        if data['type'].lower() == IncBackupProvider.AWS.name.lower():
            path = Path(IncBackupPath.AWS.value)

            if path.exists():
                for item in path.iterdir():
                    json_data.append({'AWS_ACCESS_KEY_ID': item.name})
            else:
                final_json = json.dumps({'status': 1, 'error_message': "None", "data": ''})
                return HttpResponse(final_json)

        final_json = json.dumps({'status': 1, 'error_message': "None", "data": json_data})
        return HttpResponse(final_json)

    except BaseException as msg:
        final_dic = {'status': 0, 'error_message': str(msg)}
        final_json = json.dumps(final_dic)
        return HttpResponse(final_json)


def removeDestination(request):
    try:
        user_id = request.session['userID']
        current_acl = ACLManager.loadedACL(user_id)

        if ACLManager.currentContextPermission(current_acl, 'addDeleteDestinations') == 0:
            return ACLManager.loadErrorJson('destStatus', 0)

        data = json.loads(request.body)

        if 'IPAddress' in data:
            file_name = data['IPAddress']

            if data['type'].lower() == IncBackupProvider.SFTP.name.lower():
                dest_file = Path(IncBackupPath.SFTP.value) / file_name
                dest_file.unlink()

            if data['type'].lower() == IncBackupProvider.AWS.name.lower():
                dest_file = Path(IncBackupPath.AWS.value) / file_name
                dest_file.unlink()

        final_dic = {'status': 1, 'error_message': 'None'}
        final_json = json.dumps(final_dic)
        return HttpResponse(final_json)

    except BaseException as msg:
        final_dic = {'destStatus': 0, 'error_message': str(msg)}
        final_json = json.dumps(final_dic)
        return HttpResponse(final_json)


def fetchCurrentBackups(request):
    try:
        user_id = request.session['userID']
        current_acl = ACLManager.loadedACL(user_id)
        admin = Administrator.objects.get(pk=user_id)

        data = json.loads(request.body)
        backup_domain = data['websiteToBeBacked']

        if ACLManager.checkOwnership(backup_domain, admin, current_acl) == 1:
            pass
        else:
            return ACLManager.loadErrorJson('fetchStatus', 0)

        if 'backupDestinations' in data:
            backup_destinations = data['backupDestinations']
            extra_args = {'website': backup_domain, 'backupDestinations': backup_destinations}

            if 'password' in data:
                extra_args['password'] = data['password']
            else:
                final_json = json.dumps({'status': 0, 'error_message': "Please supply the password."})
                return HttpResponse(final_json)

            start_job = IncJobs('Dummy', extra_args)
            return start_job.fetchCurrentBackups()
        else:
            website = Websites.objects.get(domain=backup_domain)
            backups = website.incjob_set.all()
            json_data = []
            for backup in reversed(backups):
                snapshots = []
                jobs = backup.jobsnapshots_set.all()
                for job in jobs:
                    snapshots.append({'type': job.type, 'snapshotid': job.snapshotid, 'destination': job.destination})
                json_data.append({'id': backup.id,
                                  'date': str(backup.date),
                                  'snapshots': snapshots
                                  })
            final_json = json.dumps({'status': 1, 'error_message': "None", "data": json_data})
            return HttpResponse(final_json)
    except BaseException as msg:
        final_dic = {'status': 0, 'error_message': str(msg)}
        final_json = json.dumps(final_dic)
        return HttpResponse(final_json)


def submitBackupCreation(request):
    try:
        user_id = request.session['userID']
        current_acl = ACLManager.loadedACL(user_id)
        admin = Administrator.objects.get(pk=user_id)

        data = json.loads(request.body)
        backup_domain = data['websiteToBeBacked']
        backup_destinations = data['backupDestinations']

        if ACLManager.checkOwnership(backup_domain, admin, current_acl) == 1:
            pass
        else:
            return ACLManager.loadErrorJson('metaStatus', 0)

        temp_path = Path("/home/cyberpanel/") / str(randint(1000, 9999))

        extra_args = {}
        extra_args['website'] = backup_domain
        extra_args['tempPath'] = str(temp_path)
        extra_args['backupDestinations'] = backup_destinations
        extra_args['websiteData'] = data['websiteData'] if 'websiteData' in data else False
        extra_args['websiteEmails'] = data['websiteEmails'] if 'websiteEmails' in data else False
        extra_args['websiteSSLs'] = data['websiteSSLs'] if 'websiteSSLs' in data else False
        extra_args['websiteDatabases'] = data['websiteDatabases'] if 'websiteDatabases' in data else False

        start_job = IncJobs('createBackup', extra_args)
        start_job.start()

        time.sleep(2)

        final_json = json.dumps({'status': 1, 'error_message': "None", 'tempPath': str(temp_path)})
        return HttpResponse(final_json)

    except BaseException as msg:
        logging.writeToFile(str(msg))
        final_dic = {'status': 0, 'metaStatus': 0, 'error_message': str(msg)}
        final_json = json.dumps(final_dic)
        return HttpResponse(final_json)


def getBackupStatus(request):
    try:
        data = json.loads(request.body)

        status = data['tempPath']
        backupDomain = data['websiteToBeBacked']

        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)
        admin = Administrator.objects.get(pk=userID)

        if ACLManager.checkOwnership(backupDomain, admin, currentACL) == 1:
            pass
        else:
            return ACLManager.loadErrorJson('fetchStatus', 0)

        if (status[:16] == "/home/cyberpanel" or status[:4] == '/tmp' or status[:18] == '/usr/local/CyberCP') \
                and status != '/usr/local/CyberCP/CyberCP/settings.py' and status.find('..') == -1:
            pass
        else:
            data_ret = {'abort': 1, 'installStatus': 0, 'installationProgress': "100",
                        'currentStatus': 'Invalid status file.'}
            json_data = json.dumps(data_ret)
            return HttpResponse(json_data)

        ## file name read ends

        if os.path.exists(status):
            command = "cat " + status
            result = pu.outputExecutioner(command, 'cyberpanel')

            if result.find("Completed") > -1:

                ### Removing Files

                os.remove(status)

                final_json = json.dumps(
                    {'backupStatus': 1, 'error_message': "None", "status": result, "abort": 1})
                return HttpResponse(final_json)

            elif result.find("[5009]") > -1:
                ## removing status file, so that backup can re-run
                try:
                    os.remove(status)
                except:
                    pass

                final_json = json.dumps(
                    {'backupStatus': 1, 'error_message': "None", "status": result,
                     "abort": 1})
                return HttpResponse(final_json)
            else:
                final_json = json.dumps(
                    {'backupStatus': 1, 'error_message': "None", "status": result,
                     "abort": 0})
                return HttpResponse(final_json)
        else:
            final_json = json.dumps({'backupStatus': 1, 'error_message': "None", "status": 1, "abort": 0})
            return HttpResponse(final_json)

    except BaseException as msg:
        final_dic = {'backupStatus': 0, 'error_message': str(msg)}
        final_json = json.dumps(final_dic)
        logging.writeToFile(str(msg) + " [backupStatus]")
        return HttpResponse(final_json)


def deleteBackup(request):
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)
        admin = Administrator.objects.get(pk=userID)
        data = json.loads(request.body)
        backupDomain = data['websiteToBeBacked']

        if ACLManager.checkOwnership(backupDomain, admin, currentACL) == 1:
            pass
        else:
            return ACLManager.loadErrorJson('fetchStatus', 0)

        id = data['backupID']

        IncJob.objects.get(id=id).delete()

        final_dic = {'status': 1, 'error_message': 'None'}
        final_json = json.dumps(final_dic)
        return HttpResponse(final_json)

    except BaseException as msg:
        final_dic = {'destStatus': 0, 'error_message': str(msg)}
        final_json = json.dumps(final_dic)
        return HttpResponse(final_json)


def fetchRestorePoints(request):
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)
        admin = Administrator.objects.get(pk=userID)
        data = json.loads(request.body)
        backupDomain = data['websiteToBeBacked']

        if ACLManager.checkOwnership(backupDomain, admin, currentACL) == 1:
            pass
        else:
            return ACLManager.loadErrorJson('fetchStatus', 0)

        data = json.loads(request.body)
        id = data['id']

        incJob = IncJob.objects.get(id=id)

        backups = incJob.jobsnapshots_set.all()

        json_data = "["
        checker = 0

        for items in backups:

            dic = {'id': items.id,
                   'snapshotid': items.snapshotid,
                   'type': items.type,
                   'destination': items.destination,
                   }

            if checker == 0:
                json_data = json_data + json.dumps(dic)
                checker = 1
            else:
                json_data = json_data + ',' + json.dumps(dic)

        json_data = json_data + ']'
        final_json = json.dumps({'status': 1, 'error_message': "None", "data": json_data})
        return HttpResponse(final_json)
    except BaseException as msg:
        final_dic = {'status': 0, 'error_message': str(msg)}
        final_json = json.dumps(final_dic)
        return HttpResponse(final_json)


def restorePoint(request):
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)
        admin = Administrator.objects.get(pk=userID)

        data = json.loads(request.body)
        backupDomain = data['websiteToBeBacked']
        jobid = data['jobid']

        if ACLManager.checkOwnership(backupDomain, admin, currentACL) == 1:
            pass
        else:
            return ACLManager.loadErrorJson('metaStatus', 0)

        tempPath = "/home/cyberpanel/" + str(randint(1000, 9999))

        if data['reconstruct'] == 'remote':
            extraArgs = {}
            extraArgs['website'] = backupDomain
            extraArgs['jobid'] = jobid
            extraArgs['tempPath'] = tempPath
            extraArgs['reconstruct'] = data['reconstruct']
            extraArgs['backupDestinations'] = data['backupDestinations']
            extraArgs['password'] = data['password']
            extraArgs['path'] = data['path']
        else:
            extraArgs = {}
            extraArgs['website'] = backupDomain
            extraArgs['jobid'] = jobid
            extraArgs['tempPath'] = tempPath
            extraArgs['reconstruct'] = data['reconstruct']

        startJob = IncJobs('restorePoint', extraArgs)
        startJob.start()

        time.sleep(2)

        final_json = json.dumps({'status': 1, 'error_message': "None", 'tempPath': tempPath})
        return HttpResponse(final_json)

    except BaseException as msg:
        logging.writeToFile(str(msg))
        final_dic = {'status': 0, 'metaStatus': 0, 'error_message': str(msg)}
        final_json = json.dumps(final_dic)
        return HttpResponse(final_json)


def scheduleBackups(request):
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        if ACLManager.currentContextPermission(currentACL, 'scheDuleBackups') == 0:
            return ACLManager.loadError()

        websitesName = ACLManager.findAllSites(currentACL, userID)

        destinations = []
        destinations.append('local')

        path = '/home/cyberpanel/sftp'

        if os.path.exists(path):
            for items in os.listdir(path):
                destinations.append('sftp:%s' % (items))

        path = '/home/cyberpanel/aws'
        if os.path.exists(path):
            for items in os.listdir(path):
                destinations.append('s3:s3.amazonaws.com/%s' % (items))

        websitesName = ACLManager.findAllSites(currentACL, userID)

        return defRenderer(request, 'IncBackups/backupSchedule.html',
                           {'websiteList': websitesName, 'destinations': destinations})
    except BaseException as msg:
        logging.writeToFile(str(msg))
        return redirect(loadLoginPage)


def submitBackupSchedule(request):
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        if ACLManager.currentContextPermission(currentACL, 'scheDuleBackups') == 0:
            return ACLManager.loadErrorJson('scheduleStatus', 0)

        data = json.loads(request.body)

        backupDest = data['backupDestinations']
        backupFreq = data['backupFreq']
        websitesToBeBacked = data['websitesToBeBacked']

        try:
            websiteData = data['websiteData']
            websiteData = 1
        except:
            websiteData = False
            websiteData = 0

        try:
            websiteEmails = data['websiteEmails']
            websiteEmails = 1
        except:
            websiteEmails = False
            websiteEmails = 0

        try:
            websiteDatabases = data['websiteDatabases']
            websiteDatabases = 1
        except:
            websiteDatabases = False
            websiteDatabases = 0

        newJob = BackupJob(websiteData=websiteData, websiteDataEmails=websiteEmails, websiteDatabases=websiteDatabases,
                           destination=backupDest, frequency=backupFreq)
        newJob.save()

        for items in websitesToBeBacked:
            jobsite = JobSites(job=newJob, website=items)
            jobsite.save()

        final_json = json.dumps({'status': 1, 'error_message': "None"})
        return HttpResponse(final_json)


    except BaseException as msg:
        final_json = json.dumps({'status': 0, 'error_message': str(msg)})
        return HttpResponse(final_json)


def getCurrentBackupSchedules(request):
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        if ACLManager.currentContextPermission(currentACL, 'scheDuleBackups') == 0:
            return ACLManager.loadErrorJson('fetchStatus', 0)

        records = BackupJob.objects.all()

        json_data = "["
        checker = 0

        for items in records:
            dic = {'id': items.id,
                   'destination': items.destination,
                   'frequency': items.frequency,
                   'numberOfSites': items.jobsites_set.all().count()
                   }

            if checker == 0:
                json_data = json_data + json.dumps(dic)
                checker = 1
            else:
                json_data = json_data + ',' + json.dumps(dic)

        json_data = json_data + ']'
        final_json = json.dumps({'status': 1, 'error_message': "None", "data": json_data})
        return HttpResponse(final_json)

    except BaseException as msg:
        final_dic = {'status': 0, 'error_message': str(msg)}
        final_json = json.dumps(final_dic)
        return HttpResponse(final_json)


def fetchSites(request):
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        if ACLManager.currentContextPermission(currentACL, 'scheDuleBackups') == 0:
            return ACLManager.loadErrorJson('fetchStatus', 0)

        data = json.loads(request.body)

        job = BackupJob.objects.get(pk=data['id'])

        json_data = "["
        checker = 0

        for items in job.jobsites_set.all():
            dic = {'id': items.id,
                   'website': items.website,
                   }

            if checker == 0:
                json_data = json_data + json.dumps(dic)
                checker = 1
            else:
                json_data = json_data + ',' + json.dumps(dic)

        json_data = json_data + ']'
        final_json = json.dumps({'status': 1, 'error_message': "None", "data": json_data,
                                 'websiteData': job.websiteData, 'websiteDatabases': job.websiteDatabases,
                                 'websiteEmails': job.websiteDataEmails})
        return HttpResponse(final_json)

    except BaseException as msg:
        final_dic = {'status': 0, 'error_message': str(msg)}
        final_json = json.dumps(final_dic)
        return HttpResponse(final_json)


def scheduleDelete(request):
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        if ACLManager.currentContextPermission(currentACL, 'scheDuleBackups') == 0:
            return ACLManager.loadErrorJson('scheduleStatus', 0)

        data = json.loads(request.body)

        id = data['id']

        backupJob = BackupJob.objects.get(id=id)
        backupJob.delete()

        final_json = json.dumps({'status': 1, 'error_message': "None"})
        return HttpResponse(final_json)

    except BaseException as msg:
        final_json = json.dumps({'status': 0, 'error_message': str(msg)})
        return HttpResponse(final_json)


def restoreRemoteBackups(request):
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        if ACLManager.currentContextPermission(currentACL, 'createBackup') == 0:
            return ACLManager.loadError()

        websitesName = ACLManager.findAllSites(currentACL, userID)

        destinations = []

        path = '/home/cyberpanel/sftp'

        if os.path.exists(path):
            for items in os.listdir(path):
                destinations.append('sftp:%s' % (items))

        path = '/home/cyberpanel/aws'
        if os.path.exists(path):
            for items in os.listdir(path):
                destinations.append('s3:s3.amazonaws.com/%s' % (items))

        return defRenderer(request, 'IncBackups/restoreRemoteBackups.html',
                           {'websiteList': websitesName, 'destinations': destinations})
    except BaseException as msg:
        logging.writeToFile(str(msg))
        return redirect(loadLoginPage)


def saveChanges(request):
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        if ACLManager.currentContextPermission(currentACL, 'scheDuleBackups') == 0:
            return ACLManager.loadErrorJson('scheduleStatus', 0)

        data = json.loads(request.body)

        id = data['id']
        try:
            websiteData = data['websiteData']
        except:
            websiteData = 0
        try:
            websiteDatabases = data['websiteDatabases']
        except:
            websiteDatabases = 0
        try:
            websiteEmails = data['websiteEmails']
        except:
            websiteEmails = 0

        job = BackupJob.objects.get(pk=id)

        job.websiteData = int(websiteData)
        job.websiteDatabases = int(websiteDatabases)
        job.websiteDataEmails = int(websiteEmails)
        job.save()

        final_json = json.dumps({'status': 1, 'error_message': "None"})
        return HttpResponse(final_json)


    except BaseException as msg:
        final_json = json.dumps({'status': 0, 'error_message': str(msg)})
        return HttpResponse(final_json)


def removeSite(request):
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        if ACLManager.currentContextPermission(currentACL, 'scheDuleBackups') == 0:
            return ACLManager.loadErrorJson('scheduleStatus', 0)

        data = json.loads(request.body)

        id = data['id']
        website = data['website']

        job = BackupJob.objects.get(pk=id)

        site = JobSites.objects.get(job=job, website=website)
        site.delete()

        final_json = json.dumps({'status': 1, 'error_message': "None"})
        return HttpResponse(final_json)


    except BaseException as msg:
        final_json = json.dumps({'status': 0, 'error_message': str(msg)})
        return HttpResponse(final_json)


def addWebsite(request):
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        if ACLManager.currentContextPermission(currentACL, 'scheDuleBackups') == 0:
            return ACLManager.loadErrorJson('scheduleStatus', 0)

        data = json.loads(request.body)

        id = data['id']
        website = data['website']

        job = BackupJob.objects.get(pk=id)

        try:
            JobSites.objects.get(job=job, website=website)
        except:
            site = JobSites(job=job, website=website)
            site.save()

        final_json = json.dumps({'status': 1, 'error_message': "None"})
        return HttpResponse(final_json)


    except BaseException as msg:
        final_json = json.dumps({'status': 0, 'error_message': str(msg)})
        return HttpResponse(final_json)
