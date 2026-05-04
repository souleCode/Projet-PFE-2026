from storages.backends.s3boto3 import S3Boto3Storage
import mimetypes


class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False

    def get_object_parameters(self, name):
        params = super().get_object_parameters(name)
        content_type, _ = mimetypes.guess_type(name)
        if content_type:
            params['ContentType'] = content_type
        params.pop('ContentDisposition', None)
        return params


class StaticStorage(S3Boto3Storage):
    location = 'static'
    file_overwrite = True