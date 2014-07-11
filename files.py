from Crypto.Cipher import AES
from dho import dho_connect
import calendar
import datetime
import dateutil.parser
import fnmatch
import gzip
import hashlib
import os
import random
import struct


class Backup_Zone(object):

    def __init__(self, directory, bucket, logger, encrypt=False, ekey=None, exclude=[]):
        self.directory = directory
        self.bucketname = bucket
        self.logger = logger
        self.encrypt = encrypt
        self.exclude = exclude
        self.ekey = ekey
        self.bucket_contents = {
            key.name.encode('utf-8'): {
                'last_modified': key.last_modified,
                'etag': key.etag.strip('"')
            } for key in dho_connect().get_bucket(self.bucketname).list()}
        return

    def backup_all(self, testing=False):

        stats = {
            'new': [],
            'modified': [],
            'unmodified': [],
            'skipped': [],
            'failed': []
        }

        for fname in get_file_list(self.directory):

            if self.skip(fname):
                self.logger.debug("Skipped: " + fname)
                stats['skipped'].append(fname)
                continue

            f = File(fname, self.bucketname, self.encrypt, self.ekey)

            if not self.file_exists_in_dho(f):
                self.logger.info("Uploading new: " + f.name)

                if not testing:
                    try:
                        f.upload_new()
                        stats['new'].append(f.name)

                    except KeyboardInterrupt:
                        self.logger.warning("User skipped: " + f.name)
                        stats['skipped'].append(f.name)

                    except:
                        self.logger.error("Upload failed: " + f.name)
                        self.logger.exception("Error/Exception detected:")

                elif self.is_stale(f):
                    self.logger.info("Uploading modified: " + f.name)

                if not testing:
                    try:
                        f.upload_modified()
                        stats['modified'].append(f.name)

                    except KeyboardInterrupt:
                        self.logger.warning("User skipped: " + f.name)
                        stats['skipped'].append(f.name)

                    except:
                        self.logger.error("Upload failed: " + f.name)
                        self.logger.exception("Error/Exception detected:")
                else:
                    if testing:
                        print "Unmodified: " + f.name
                        stats['unmodified'].append(f.name)
                        self.logger.info("Unmodified: " + f.name)

        if testing:
            print "New files uploaded: %d" % len(stats['new'])
            print "Modified files uploaded: %d" % len(stats['modified'])
            print "Unmodified files: %d" % len(stats['unmodified'])
            print "Files skipped: %d" % len(stats['skipped'])
            print "Failed uploads: %d" % len(stats['failed'])

        return stats

    def file_exists_in_dho(self, file):
        return file.keyname in self.bucket_contents.keys()

    def is_stale(self, file):

        k = self.bucket_contents.get(file.keyname)

        if file.encryptOnUpload:
            return file.last_modified > datetime_to_epoch(k['last_modified'])
        else:
            return (file.last_modified > datetime_to_epoch(k['last_modified'])) and not (file.get_checksum() == k['etag'])

    def check_orphaned(self, delete_orphaned=False):

        orphaned = []

        for k in dho_connect().get_bucket(self.bucketname).list():
            if not os.path.exists(k.name):
                if delete_orphaned:
                    self.logger.info('Deleting ' + k.name)
                else:
                    self.logger.info('Orphaned: ' + k.name)

            orphaned.append(k.name)
            return orphaned

    def skip(self, filename):
        for ex in self.exclude:
            if fnmatch.fnmatch(filename, ex):
                return True
        return False


class File(object):

    def __init__(self, filename, backup_bucket_name, encrypt_upload, ekey=None):
        self.name = os.path.abspath(filename)
        self.keyname = self.name.lstrip('/')
        self.parent_directory = os.path.split(self.name)[0]
        self.shortname = os.path.split(self.name)[1]
        self.size = os.path.getsize(self.name)
        self.last_modified = os.path.getmtime(self.name)
        self.checksum = None

        self.bucketname = backup_bucket_name
        self.encryptOnUpload = encrypt_upload
        self.ekey = ekey
        return

    def nice_time(self, string_format=False):
        ''' Converts the file's Unix timestamp to a datetime
        object.

            string_format:
                If this is true, return a string format of the
                datetime instead (default is false)
                '''

        t = epoch_to_datetime(self.last_modified)
        if string_format:
            return t.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return t

    def get_checksum(self):
        ''' Returns the md5 checksum of the file and
        caches it for quicker retrieval later
        '''

        if not self.checksum:
            self.checksum = md5_checksum(self.name)
            return self.checksum

    def upload_new(self):
        '''Upload a new file to DreamObjects'''

        # Check if the file should be encrypted locally before uploading
        if self.encryptOnUpload:
            src_file = os.path.join(self.parent_directory, '.' + self.shortname + '.enc')
            encrypt_file(self.ekey, self.name, src_file)
            k = dho_connect().get_bucket(self.bucketname).new_key(self.keyname)
            k.set_contents_from_filename(src_file)
            os.unlink(src_file)
        else:
            k = dho_connect().get_bucket(self.bucketname).new_key(self.keyname)
            k.set_contents_from_filename(self.name)

        # Always make the uploaded key private
        k.set_canned_acl('private')

        return

    def upload_modified(self):
        '''Re-upload a file that has been modified.'''

        # Refresh the file's timestamp
        self.last_modified = os.path.getmtime(self.name)

        # Reset the file's stored md5 checksum so that it
        # must be re-checked later
        self.checksum = None
        self.delete_remote()
        self.upload_new()
        return

    def delete_remote(self):
        ''' Delete a file's corresponding key on DreamObjects'''

        k = dho_connect().get_bucket(self.bucketname).get_key(self.name)
        k.delete()
        return

    def __repr__(self):
        return "<File %s, last modified %s>" % (self.name, self.nice_time(string_format=True))


def gzip_file(infile, outfile=None):
    ''' Uses gzip to compress a file

        infile:
            Filename to be compressed

        outfile:
            If none is specified, this is <infile> + ".gz"
            '''

    if not outfile:
        outfile = infile + ".gz"

    f_in = open(infile, 'rb')
    f_out = gzip.open(outfile, 'wb')

    f_out.writelines(f_in)

    f_out.close()
    f_in.close()

    os.unlink(infile)

    return


def datetime_to_epoch(time_string):
    ''' Parses a time tring and returns a Unix style timestamp'''

    t = dateutil.parser.parse(time_string)
    return calendar.timegm(t.utctimetuple())


def epoch_to_datetime(epoch_time_int):
    ''' Translates a Unix style timestamp (int) and returns
    a datetime object.
    '''
    return datetime.datetime.fromtimestamp(epoch_time_int)


def md5_checksum(filename, block_size=1024 * 128):
    ''' Given a filename, returns the md5 checksum of that file'''

    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(block_size), b''):
            md5.update(chunk)
            return md5.hexdigest()


def encrypt_file(key, in_filename, out_filename=None, chunksize=64 * 1024):
    """ Encrypts a file using AES (CBC mode) with the
    given key.

        key:
            The encryption key - a string that must be
            either 16, 24 or 32 bytes long. Longer keys
            are more secure.

        in_filename:
            Name of the input file

        out_filename:
            If None, '<in_filename>.enc' will be used.

        chunksize:
            Sets the size of the chunk which the function
            uses to read and encrypt the file. Larger chunk
            sizes can be faster for some files and machines.
            chunksize must be divisible by 16.
            """
    if not out_filename:
        out_filename = in_filename + '.enc'

    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'w+b') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))


def decrypt_file(key, in_filename, out_filename=None, chunksize=24 * 1024):
    """ Decrypts a file using AES (CBC mode) with the
    given key. Parameters are similar to encrypt_file,
    with one difference: out_filename, if not supplied
    will be in_filename without its last extension
    (i.e. if in_filename is 'aaa.zip.enc' then
    out_filename will be 'aaa.zip')
    """
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)


def get_file_list(backupDirectory):
    ''' Given a directory, returns a generator with all files
    within that directory and its subdirectories
    '''
    for root, subFolders, files in os.walk(backupDirectory):
        for file in files:
            yield os.path.join(root, file)
