#!/usr/bin/python

'''
Update existing objects with 'shortened' path names to include the full path
'''

from config import *
from dho import conn
from files import *
import os

TESTING = False

def rename_long_to_short(bz):

    bucket = conn.get_bucket(bz.bucketname)
    
    for k in bucket.list():
    
        new_name = os.path.join(bz.basedir, k.name)                
   
        if not os.path.exists(new_name):
            print 'WARNING object, {file} does not exist'.format(file=new_name)
            
        if not TESTING:
            print 'RENAMING key to {n}'.format(n=new_name)
            k.copy(k.bucket.name, new_name)
            k.delete()


           

for backup_object in backupList:

        bz = Backup_Zone(
            backup_object['directory'],
            backup_object['basedir'],
            backup_object['bucket'],
            backup_object['encrypt'],
            enckey
        )   

        rename_long_to_short(bz)
