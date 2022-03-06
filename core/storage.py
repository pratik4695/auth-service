from storages.backends.s3boto import S3BotoStorage


def media_root_s3():
    return S3BotoStorage(location='media')
