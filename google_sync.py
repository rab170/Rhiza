#!/usr/bin/env python
"""
**********************************
* Rhiza Screening -- Google Sync *
**********************************
*** Rob Brown; rab170@pitt.edu ***
**********************************

TL;DR --this program syncs ~/GoogleDrive/* with the google account identified in ~/login.txt

This program emulates a simple subset** of the auto-sync behaviors found in Dropbox (from my experience as a UNIX user). In dropbox (unlike Google Drive) users have a local (mutable) directory
in which their Dropbox data operates. This directory is automatically synced with their Cloud data, eliminating the overhead of backing up their files (in addition to providing seemless version control).
This program operates in unison with a CRON job, which watches ~/GoogleDrive/* for modifications.

**Note that you will not find auto-removal functionality, nor upstream changes being pulled to the local ~/GoogleDrive directory

"""
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import gdata.docs.data
import gdata.docs.client
import os, time

GOOGLE_DRIVE_PATH=os.path.expanduser("~/Dropbox")
LAST_UPDATE_PATH='.last_update'     #hidden file storing time of last execution, hidden according to UNIX filename conventions (preceding .)

def get_last_update():
    if not os.path.isfile(LAST_UPDATE_PATH): return None
    f =open(LAST_UPDATE_PATH)
    return time.strptime(f.readline(), '%Y-%m-%d %H:%M:%S')

def change_last_update():
    f =open(LAST_UPDATE_PATH, 'w+')
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    f.write(time_str)

def connect_client():   #creates connection client for user identified in ~/login.txt
    global client
    LOGIN_PATH=os.path.expanduser("~/login.txt")
    login_file = open(LOGIN_PATH);
    USER=login_file.readline()
    PASS=login_file.readline()

    client = gdata.docs.client.DocsClient(source='google_sync.py')
    client.api_version = "3"
    client.ssl = True
    client.ClientLogin(USER, PASS, client.source)


def get_modifications(LAST_UPDATE):
    """
        get_modifications(LAST_UPDATE) returns a list of absolute paths in ~/GoogleDrive/* that have been modified since LAST_UPDATE.
        LAST_UPDATE is a struct_time object representing the last time the script updated files in Google Drive -- see get_last_update()

        all times are UTC
    """
    to_update = []
    for root, dirs, files in os.walk(GOOGLE_DRIVE_PATH):
        #if not time.gmtime(os.stat(root).st_mtime) >= LAST_UPDATE:     #Unfortunately, last modification time of directories is only effected by adding/removing/renaming subdirectories (not files).
            #del dirs[:]                                                #can't avoid full-depth recursion (without maintaining logs)
        for file_name in files:
            abs_path = root + "/" +  file_name
            if time.gmtime(os.stat(abs_path).st_mtime) >= LAST_UPDATE:      #check files at each depth, append to_update if they have been modified since LAST_UPDATE
                to_update.append(abs_path)
    return to_update

def sync(paths):
    #TODO build directory structure,
    #TODO check if file exists, if so overwrite with new revision, else create
    for path in paths:
        print path

def sync_modifications():
    filePath = "/home/rob/SPRING_2014.txt"
    newResource = gdata.docs.data.Resource(filePath, os.path.basename(filePath))
    media = gdata.data.MediaSource()
    media.SetFileHandle(filePath, 'set/forget')     #'set/forget' is a serverside parameter for file type identifaction. Examples are 'image/jpeg' or 'text/plain'. Google fills in the blanks based on file extensions. Thus, set and forget.
    newDocument = client.CreateResource(newResource, create_uri=gdata.docs.client.RESOURCE_UPLOAD_URI, media=media)

if __name__ == "__main__":
    LAST_UPDATE = get_last_update()
    change_last_update()
    connect_client()
    paths = get_modifications(LAST_UPDATE)
    sync(paths)



















