import hashlib
import os
import time
from collections import namedtuple
import subprocess


#File = namedtuple('File', ['filename', 'basedir', 'size', 'encrypt'], verbose=False, rename=False)
from files import File




def file_md5(filename):
    md5 = hashlib.md5()
    with open(filename,'rb') as f: 
        for chunk in iter(lambda: f.read(8192), b''): 
             md5.update(chunk)
    return md5.hexdigest()



def back_it_on_up(files, dho_bucket, logFile, skipSize=1073741824):
    
    bucket_contents = [key.name for key in dho_bucket.list()]
    failed = []
    skipped = []
    success = []

    for file in files:
        shortName = file.filename[len(file.basedir)+1:]
        
        if not shortName.decode('utf8') in bucket_contents and file.size < skipSize:
            
            logit('Uploading: ' + file.filename, logFile)
            
            try:
                key = dho_bucket.new_key(shortName)
                key.set_contents_from_filename(file.filename)
                key.set_canned_acl('private')

                logit('Success! Uploaded ' + file.filename, logFile)
                success.append(file.filename)
            
            except KeyboardInterrupt:
                logit('User skipped {filename}'.format(filename=file.filename), logFile)
                print '\nKeyboard interrupt--skipping {filename}'.format(filename=file.filename)

            except Exception as e:
                logit('FAILURE: ' + e.strerror, logFile)
                failed.append(file.filename)

        else:
            logit('Skipping {filename}'.format(filename=file.filename), logFile)
            skipped.append(file.filename)

    return failed, skipped, success


def run_bash(command):
    result = subprocess.Popen(command.split(), stdout=subprocess.PIPE).stdout.read()
    if result.endswith('\n'):
        result = result[:-1]
    return result



