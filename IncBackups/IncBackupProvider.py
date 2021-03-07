from enum import Enum, auto


class IncBackupProvider(Enum):
    LOCAL = auto()
    SFTP = auto()
    AWS = auto()
    S3COMPATIBLE = "s3-compatible"
