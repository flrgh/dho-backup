Encrypted backups to DreamObjects with Python
---------------------------------------------

### Required libraries:

* Pycrypto
* Boto

### Configuration

Rename/copy `config.example.py` to `config.py` and edit appropriately.

### Performing backups

Run the `backup.py` script to backup everything. Set this up as a cron for automatic backups.

### Todo

* Use ConfigParser for .ini config files instead of config.py
* Incorporate command line flags for runtime configuration and options
