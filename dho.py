import boto
import boto.s3.connection
from config import access_key, secret_key


def dho_connect():
    return boto.connect_s3(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        host='objects.dreamhost.com',
        calling_format=boto.s3.connection.OrdinaryCallingFormat(),
    )


def is_uploaded(bucketname, keyname):
    bucket = dho_connect().get_bucket(bucketname)
    if not bucket.get_key(keyname):
        return False
    else:
        return True