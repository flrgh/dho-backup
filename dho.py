import boto
import boto.s3.connection
import os

def dho_connect():

    access_key = os.environ['dho_access_key']
    secret_key = os.environ['dho_secret_key']

    return boto.connect_s3(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        host='objects.dreamhost.com',
        calling_format=boto.s3.connection.OrdinaryCallingFormat(),
    )
