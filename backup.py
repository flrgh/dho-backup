import time
import dho
import hashlib
import logging
import os
from configuration import parse_config
from files import Backup_Zone, gzip_file


def main():

    # Parse config file
    config = parse_config('backup.conf')

    os.environ['dho_access_key'] = config['dho_access_key']
    os.environ['dho_secret_key'] = config['dho_secret_key'] 
        
    # Set up logging
    logger = logging.getLogger('backup')
    logger.setLevel(logging.__getattribute__(config['log_level']))
    fh = logging.handlers.TimedRotatingFileHandler(
        config['log_file'],
        when='D',
        backupCount=config['max_logs']
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(fh)

    startTime = time.time()
    logger.info('Hold on to your butts. Backup starting.')

    totals = [0, 0, 0]

    enckey = hashlib.sha256(config['passphrase']).digest()

    for backup_object in config['backup_zones']:

        bz = Backup_Zone(
            backup_object['directory'],
            backup_object['bucket'],
            logger,
            backup_object['encrypt'],
            enckey,
            exclude=backup_object['exclude']
        )

        logger.info('''Backing up [{directory}] to bucket [{bucket}] now.'''.format(
            directory=bz.directory, bucket=bz.bucketname))

        statistics = bz.backup_all()

        finished = 'Done with {directory}. Files backed up: {success}, Files skipped: {skipped}, Failures: {failed}'.format(
            directory=bz.directory,
            success=(len(statistics['new']) + len(statistics['modified'])),
            skipped=len(statistics['skipped']),
            failed=len(statistics['failed']),
        )

        delim = '\n' + ('-' * 90)

        logger.info(finished)

        totals[0] += (len(statistics['new']) + len(statistics['modified']))
        totals[1] += len(statistics['skipped'])
        totals[2] += len(statistics['failed'])

    backupTime = round(((time.time() - startTime) / 60.0), 2)

    print 'Aaaand we\'re done here. Some stats:\n'

    stats = '''\
        \tBackup time: {time} minutes
        \tFiles skipped: {skipped}
        \tFiles Failed: {failed}
        \tFiles uploaded: {uploaded}
        \tTotal: {total}\
        '''.format(
        time=backupTime,
        skipped=totals[1],
        failed=totals[2],
        uploaded=totals[0],
        total=sum(totals)
    )

    print stats
    #gzip_file(logFile, (logFile + "." + time.strftime('%Y-%m-%d') + ".gz"))
    fh.doRollover()

    return

if __name__ == '__main__':
    main()
