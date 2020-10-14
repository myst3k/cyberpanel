from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from backup.api.serializers import BackupSerializer, ListBackupsSerializer
from loginSystem.models import Administrator
from plogical.acl import ACLManager
from websiteFunctions.models import Websites


class ListBackups(APIView):
    """
    Returns a list of all backups for a domain.

    * POST: {domain: "example.com"}
    """
    def post(self, request):
        try:
            userID = request.session['userID']
        except KeyError:
            raise PermissionDenied

        data = JSONParser().parse(request)
        serializer = ListBackupsSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        domain = serializer.validated_data['domain']
        currentACL = ACLManager.loadedACL(userID)
        user = Administrator.objects.get(pk=userID)

        if ACLManager.checkOwnership(domain, user, currentACL) == 0:
            raise PermissionDenied

        website = Websites.objects.get(domain=domain)
        backups = website.backups_set.all()
        serializer = BackupSerializer(backups, many=True)
        return JsonResponse(serializer.data, safe=False)

