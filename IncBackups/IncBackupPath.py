from enum import Enum


class IncBackupPath(Enum):
    SFTP = "/home/cyberpanel/sftp"
    AWS = "/home/cyberpanel/aws"
    S3COMPATIBLE = "/home/cyberpanel/s3-compatible"
