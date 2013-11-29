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
    
        bd = bz.basedir[1:]
   
#        if not os.path.exists(new_name):
#            print 'WARNING object, {file} does not exist'.format(file=new_name.encode('utf-8', 'ignore'))
            
        if not TESTING:
            if not k.name.startswith(bd):
                new_name = bd + '/' + k.name
                print 'RENAMING key to {n}'.format(n=new_name.encode('utf-8', 'ignore'))
                k.copy(k.bucket.name, new_name)
                k.delete()
            elif k.name.startswith(bd + '/' + bd):
                print 'Fixing the stupid rename problem'
                k.copy(k.bucket.name, k.name.replace(bd+'/'+bd, bd))
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