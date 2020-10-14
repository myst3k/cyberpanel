from rest_framework import serializers

from websiteFunctions.models import Backups


class BackupSerializer(serializers.ModelSerializer):
    file = serializers.CharField(source='fileName')
    status = serializers.SerializerMethodField('get_status')

    class Meta:
        model = Backups
        fields = ['id', 'file', 'date', 'size', 'status']

    @staticmethod
    def get_status(obj):
        if obj.status == 0:
            return "Pending"
        else:
            return "Completed"


# noinspection PyAbstractClass
class ListBackupsSerializer(serializers.Serializer):
    domain = serializers.CharField(required=True, max_length=200, allow_null=False)
