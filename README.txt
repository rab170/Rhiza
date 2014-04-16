* Rhiza Screening -- Google Sync *
==================================
*** Rob Brown; rab170@pitt.edu ***
----------------------------------


TL;DR --  Syncs a local directory (~/GoogleDrive/*) with a google user's account.
          Provides version control for all files.

This program emulates a simple subset** of the auto-sync behaviors found in
Dropbox (from my experience as a UNIX user). In dropbox (unlike Google Drive)
users have a local (mutable) directory that is linked to their  Dropbox data.
In my experience, this linking reduces the overhead in backing up or sharing
files (and additionally provides seemless version control).

The purpose of this program (with the help of cron) is to emulate this
effect in the Google Drive ecosystem.

**Note that you will not find delete functionality, nor upstream changes
  being pulled to the local ~/GoogleDrive directory.

HOW TO RUN:

    Create a file called "login.txt" in your home directory (~).
    Enter your username on the first line (eg, john.doe@gmail.com).
    Enter your password on the second line (eg, myPass123).

    Now install required packages (gdata and magic), by navigating to
    the directories "gdata-2.0.18" and "python-magic" and executing
    "sudo python setup.py install"

    Now run setup.sh to:
        --run google_sync.py once for an initial sync
        --create a cron job to run google_sync.py periodically

    That's it! You're done!

    If you want to sync a different folder, change the GOOGLE_DRIVE_PATH variable.
