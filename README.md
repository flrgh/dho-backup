Encrypted backups to DreamObjects with Python
---------------------------------------------

### Required libraries:

* Pycrypto
* Boto
* Dateutil

(`pip install -r requirements.txt` should take care of these.)

### Configuration

Rename/copy `backup.conf.sample` to `backup.conf` and edit appropriately.

### Performing backups

Run the `backup.py` script to backup everything. Set this up as a cron for automatic backups.

### Todo

* Incorporate command line flags for runtime configuration and options
* The all-important restore feaure
* Auto-split large files and use multi-part upload
