import os
import sys
from pathlib import Path

import boto3
import django


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from django.conf import settings


def build_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )


def main():
    if not settings.AWS_STORAGE_BUCKET_NAME:
        raise RuntimeError('AWS_STORAGE_BUCKET_NAME is missing in Django settings.')

    local_media_path = Path(settings.MEDIA_ROOT)
    if not local_media_path.exists():
        raise RuntimeError(f'Local media folder does not exist: {local_media_path}')

    s3_client = build_s3_client()

    for local_path in local_media_path.rglob('*'):
        if not local_path.is_file():
            continue

        s3_key = local_path.relative_to(local_media_path.parent).as_posix()

        try:
            s3_client.upload_file(
                str(local_path),
                settings.AWS_STORAGE_BUCKET_NAME,
                s3_key,
            )
            print(f'Uploade: {s3_key}')
        except Exception as exc:
            print(f'Erreur pour {s3_key}: {exc}')


if __name__ == '__main__':
    main()