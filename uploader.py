import time
import dho
from config import backupList, logFile, phrase
from backupFunctions import *

startTime = time.time()
logit('Backup starting...', logFile)




totals = [0, 0, 0,]

for item in backupList:
    logit('Backing up {directory} to bucket \'{bucket}\' now.'.format(directory=item['directory'], bucket=item['bucket']), logFile)

    files_for_backup = get_file_list(backupDirectory=item['directory'], baseDirectory=item['basedir'], encrypted=item['encrypt'])
    logit('This directory contains a total of {number} files... backing up now'.format(number=len(files_for_backup)), logFile)

    bucket = dho.conn.get_bucket(item['bucket'])
    failed, skipped, success = back_it_on_up(files_for_backup, bucket, logFile)


    finished = 'Done with {directory}. Files backed up: {success}, Files skipped: {skipped}, Failures: {failed}, Total: {summ}.'.format(
        directory=item['directory'],
        success=len(success),
        skipped=len(skipped),
        failed=len(failed),
        summ=(len(success)+len(skipped)+len(failed))
    )

    delim = '\n' + ('-'*90)

    logit(finished + delim, logFile)

    totals[0] += len(success)
    totals[1] += len(skipped)
    totals[2] += len(failed)


backupTime = round(((time.time() - startTime)/60.0), 2)

print 'Aaaand we\'re done here. Some stats:\n'

stats = '\n\tBackup time: {time} minutes\n\tFiles skipped: {skipped}\n\tFiles Failed: {failed}\n\tFiles uploaded: {uploaded}\n\tTotal: {total}'.format(
    time=backupTime,
    skipped=totals[1],
    failed=totals[2],
    uploaded=totals[0],
    total = sum(totals)
    )

print stats
logit(stats, logFile)