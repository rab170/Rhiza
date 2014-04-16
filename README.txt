* Rhiza Screening -- Google Sync *
**********************************
**********************************
*** Rob Brown; rab170@pitt.edu ***
**********************************

TL;DR -- syncs ~/GoogleDrive/* with the google account identified in ~/login.txt

This program emulates a simple subset** of the auto-sync behaviors found in Dropbox (from my experience as a UNIX user). In dropbox (unlike Google Drive) users have a local (mutable) directory
in which their Dropbox data operates. This directory is automatically synced with their Cloud data, eliminating the overhead of backing up their files (in addition to providing seemless version control).
This program operates in unison with a CRON job to push all local changes upstream to their Google Drive account.

**Note that you will not find auto-removal functionality (when you delete a file/folder), nor upstream changes being pulled to the local ~/GoogleDrive directory. This can effectively be considered
a constant upload script, more than a "sync" script.

****************************************************************************************

ADDITIONAL (POST-MORTOM) RESPONSES TO INTERVIEW QUESTION REGARDING "FAVORITE PYTHON FEATURES" (after writing python code again for the first time in months):
    -- lambda functions and lambda sorting (best feature in my opinion/experience)
    -- versitility of data structures:
            *x=[math.pow(i,i) for i in range(0,10)] style declaration
            *x[:], x[1:5], etc
            *dynamic size
    -- modularity and simplicity. This program would have been a thousand lines in Java/C++.
    -- enumerate

****************************************************************************************

HOW TO RUN:

    On your prefered UNIX distribution, run the bash scrip (setup.sh) which can be found
    in the same directory as this file. Must run as super user.

    Doing this:
        --installs the required modules (gdata and magic)
        --runs this script once for an initial sync
        --creates a cron job to run google_sync.py periodically to check for updates

    That's it! You're done!

    If you want to sync a different folder, simply modify the GOOGLE_DRIVE_PATH variable.
    If you DON'T want your system running this every 10 minutes, comment out the crontab line in setup.sh

****************************************************************************************

