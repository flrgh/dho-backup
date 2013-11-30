# Edit this file with the proper details then save as config.py

import hashlib

# Password for encrypted backups
password = 'SEEECRET PASSWORD'
enckey = hashlib.sha256(password).digest()

# DreamObjects keys
access_key = 'ACCESS KEY'
secret_key = 'SECRET KEY'


# Directories to be backed up. Add as many as you'd like.
# No trailing slashes!
backupList = (
    {
             'directory' : '/path/to/backup1',    # We'll backup everything in this directory
                'bucket' : 'bucketname',          # The name of the bucket to upload files to
               'encrypt' : False,                 # Do you want to encrypt files before uploading?
      'skip_directories' : ['/some/directory'],   # Skip some directories
      'ignore_filetypes' : ['mp3', 'docx']        # Ignore certain file types
    },
    {
             'directory' : '/path/to/encrypted/backup2',
                'bucket' : 'bucketname2',
               'encrypt' : True,
      'skip_directories' : [],
      'ignore_filetypes' : []
    }
)


# Logging
default_log_level = 'WARNING'
logFile = '/path/to/logfile.log'