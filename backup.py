import time
import dho
import logging
from config import backupList, logFile, enckey
from files import Backup_Zone, logit, rotate_logs, gzip_file


def main():

    logger = logging.getLogger('backup')
    logger.setLevel(logging.DEBUG)
    fh = logging.handlers.TimedRotatingFileHandler(logFile, when='D', backupCount=5)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(fh)

    startTime = time.time()
    logger.info('Hold on to your butts. Backup starting.')

    totals = [0, 0, 0]

    for backup_object in backupList:

        bz = Backup_Zone(
            backup_object['directory'],
            backup_object['bucket'],
            logger,
            backup_object['encrypt'],
            enckey
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
    #logit(stats)
    #gzip_file(logFile, (logFile + "." + time.strftime('%Y-%m-%d') + ".gz"))
    #rotate_logs(logFile)
    fh.doRollover()

    return

if __name__ == '__main__':
    main()
