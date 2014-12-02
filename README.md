Rhiza Screening - Google Drive Sync
===================================

This set of python scripts sets up an automatic sync between a local directory (~/GoogleDrive/)
and a Google account's Drive, while providing version control for all files.



The purpose of this program is to emulate the charachteristics of the Dropbox in order to sync
files with Google Drive, as this Google does not provide this
functionality.


HOW TO RUN
=======================================

Create a file called "login.txt" in your home directory (~).
Enter your username on the first line (eg, john.doe@gmail.com).
Enter your password on the second line (eg, myPass123).


Now install required packages (gdata and magic), by navigating to
the directories "gdata-2.0.18" and "python-magic" and executing
"sudo python setup.py install"


Now run setup.sh to:
    *run google_sync.py once for an initial sync
    *create a cron job to run google_sync.py periodically


That's it! You're done!


If you want to sync a different folder, change the GOOGLE_DRIVE_PATH variable.
