from enum import Enum


class IncBackupProvider(Enum):
    LOCAL = "local"
    SFTP = "sftp"
    S3 = "Amazon S3"
    WASABI = "Wasabi"

    @staticmethod
    def list():
        return list(map(lambda s: s.name, IncBackupProvider))
