import os, random, struct
import hashlib
from Crypto.Cipher import AES
import dateutil.parser, calendar, datetime

from dho import conn, is_uploaded


class File(object):


    def __init__(self, filename, base_dir, backup_bucket_name, encrypt_upload):
        self.name = os.path.abspath(filename)
        self.shortname = os.path.split(self.name)[-1]
        self.parent_directory = os.path.split(self.name)[0]
        self.size = os.path.getsize(self.name)
        self.last_modified = os.path.getmtime(self.name)
        self.checksum = None

        self.shortname = self.name[len(file.base_dir)+1:]
        self.bucket = conn.get_bucket(backup_bucket_name)
        self.encryptOnUpload = encrypt_upload
        return


    def nice_time(self, string_format=False):
        t = epoch_to_datetime(self.last_modified)
        if string_format:
            return t.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return t

    
    def get_checksum(self):
        if not self.checksum:
            self.checksum = md5_checksum(self.name)
        return self.checksum


    def update_self(self, fname):
        self.__init__(fname)


    def upload_new(self, ekey=None):

        # If it's not already uploaded, make a new s3 object and upload the file            
        if self.encryptOnUpload:
            src_file = '/tmp/' + self.shortname + '.enc'
            encrypt_file(ekey, self.name, src_file)
            k = self.bucket.new_key(self.shortname)
            k.set_contents_from_filename(src_file)
            os.unlink(src_file)
        else:
            k = self.bucket.new_key(self.shortname)
            k.set_contents_from_filename(self.name)
        
        k.set_canned_acl('private')

        return


    def upload_modified(self):

        self.last_modified = os.path.getmtime(self.name)
        self.checksum = None

        self.upload_new()
        return


    def is_stale(self):
        k = self.bucket.get_key(self.shortname)
        return (self.last_modified > datetime_to_epoch(k.last_modified)) and not (self.get_checksum() == k.etag.strip('"')



    def already_uploaded(self):

        return is_uploaded(self.shortname)


    def __repr__(self):
        return "<File %s, last modified %s>" % (self.shortname, self.nice_time().strftime('%Y-%m-%d %H:%M:%S'))




def datetime_to_epoch(time_string):
    t = dateutil.parser.parse(time_string)
    return calendar.timegm(t.utctimetuple())


def epoch_to_datetime(epoch_time_int):
    return datetime.datetime.fromtimestamp(epoch_time_int)


def md5_checksum(filename, block_size=1024*128):
    md5 = hashlib.md5()
    with open(filename,'rb') as f: 
        for chunk in iter(lambda: f.read(block_size), b''): 
             md5.update(chunk)
    return md5.hexdigest()


def encrypt_file(key, in_filename, out_filename=None, chunksize=64*1024):
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
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))


def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):
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