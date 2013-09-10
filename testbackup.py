from config import enckey
from files import Backup_Zone

backupList = (
    {
        'directory': '/storage/shares/michaelm/test_backups',
        'basedir': '/storage',
        'bucket': 'none',
        'encrypt': False
    },
)

for backup_object in backupList:
    bz = Backup_Zone(
        backup_object['directory'],
        backup_object['basedir'],
        backup_object['bucket'],
        backup_object['encrypt'],
        enckey
    )

    print "yay"