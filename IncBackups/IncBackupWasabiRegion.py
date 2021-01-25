from enum import Enum


class IncBackupWasabiRegion(Enum):
    US_EAST_1 = {'name': 'US-East-1', 'url': 's3.us-east-1.wasabisys.com'}
    US_EAST_2 = {'name': 'US-East-2', 'url': 's3.us-east-2.wasabisys.com'}
    US_CENTRAL_1 = {'name': 'US-Central-1', 'url': 's3.us-central-1.wasabisys.com'}
    US_WEST_1 = {'name': 'US-West-1', 'url': 's3.us-west-1.wasabisys.com'}
    EU_CENTRAL_1 = {'name': 'EU-Central-1', 'url': 's3.eu-central-1.wasabisys.com'}
    AP_NORTHEAST_1 = {'name': 'AP-Northeast-1', 'url': 's3.ap-northeast-1-ntt.wasabisys.com'}

    @staticmethod
    def list_names():
        return list(map(lambda s: s.value.name, IncBackupWasabiRegion))

    @staticmethod
    def get_url_by_name(name):
        return next(filter(lambda s: s.value.name.lower() == name.lower(), IncBackupWasabiRegion)).url
