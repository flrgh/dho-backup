Encrypted backups to DreamObjects with Python
---------------------------------------------

### Required libraries:

* Pycrypto
* Boto

### Configuration

Rename/copy `backup.conf.sample` to `backup.conf` and edit appropriately.

### Performing backups

Run the `backup.py` script to backup everything. Set this up as a cron for automatic backups.

### Todo

* Incorporate command line flags for runtime configuration and options
* Implement options to exlcude certain directories/files and filetypes
* The all-important restore feaure
