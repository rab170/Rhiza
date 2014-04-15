#!/usr/bin/env python
"""
**********************************
* Rhiza Screening -- Google Sync *
**********************************
*** Rob Brown; rab170@pitt.edu ***
**********************************

TL;DR -- syncs ~/GoogleDrive/* with the google account identified in ~/login.txt

This program emulates a simple subset** of the auto-sync behaviors found in Dropbox (from my experience as a UNIX user). In dropbox (unlike Google Drive) users have a local (mutable) directory
in which their Dropbox data operates. This directory is automatically synced with their Cloud data, eliminating the overhead of backing up their files (in addition to providing seemless version control).
This program operates in unison with a CRON job, which watches ~/GoogleDrive/* for modifications.

**Note that you will not find auto-removal functionality, nor upstream changes being pulled to the local ~/GoogleDrive directory


****************************************************************************************

ADDITIONAL (POST-MORTOM) RESPONSES TO INTERVIEW QUESTION REGARDING "FAVORITE PYTHON FEATURES" (after writing python code again for the first time in months):
    -- lambda functions and lambda sorting (best feature in my experience)
    -- versitility of data structures:
            *x=[math.pow(i,i) for i in range(0,10)] style declaration
            *x[:], x[1:5], etc
            *dynamic size
    -- modularity and simplicity. This program would have been a thousand lines in Java.
    -- enumerate

****************************************************************************************
"""
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

#TODO add logging
#TODO add update/versioning logic

import gdata.docs.data
import gdata.docs.client
import os, time, magic

LOGIN_PATH=os.path.expanduser('~/login.txt')
GOOGLE_DRIVE_PATH=os.path.expanduser('~/Dropbox')
#GOOGLE_DRIVE_PATH=os.path.expanduser('~/GoogleDrive')
LAST_UPDATE_PATH='.last_update'

directory_map = {'':None}           #hash table for mapping local paths to GData folder "resource" objects. Map an empty path (which coresponds to the ~/GoogleDrive/ directory to None, since this is our root in the cloud

def get_last_update():
    if not os.path.isfile(LAST_UPDATE_PATH): return None
    f = open(LAST_UPDATE_PATH)
    return time.strptime(f.readline(), '%Y-%m-%d %H:%M:%S')

def change_last_update():
    f =open(LAST_UPDATE_PATH, 'w+')
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    f.write(time_str)

def connect_client():
    """" modifies the global variable client to allow the user identified in "~/login.txt" to communicate with google drive """
    global client
    login_file = open(LOGIN_PATH);
    USER=login_file.readline()
    PASS=login_file.readline()
    client = gdata.docs.client.DocsClient(source='google_sync.py')
    client.api_version ='3'
    client.ssl = True
    client.ClientLogin(USER, PASS, client.source)

def get_modifications(LAST_UPDATE):
    """
        get_modifications(LAST_UPDATE) returns a list of absolute paths in ~/GoogleDrive/* that have been modified since LAST_UPDATE.
        LAST_UPDATE is a struct_time object representing the last time the script updated files in Google Drive -- see get_last_update()
    """
    to_update = []
    for root, dirs, files in os.walk(GOOGLE_DRIVE_PATH):
        #if not time.gmtime(os.stat(root).st_mtime) >= LAST_UPDATE: del dirs[:]     #Unfortunately, last modification time of directories is only effected by adding/removing/renaming subdirectories (not files).
        for file_name in files:                                                     #can't avoid full-depth recursion (without maintaining logs)
            abs_path = root + "/" +  file_name
            if time.gmtime(os.stat(abs_path).st_mtime) >= LAST_UPDATE:              #check files at each depth, append to_update if they have been modified since LAST_UPDATE
                to_update.append(abs_path)
    return to_update


def roll_back(error):
    print 'Runtime error', error

def search_file():
    return None
def search_collection(path, parent_resource):
    return None

def create_file(file_path, parent_collection):
    for attempts in range(0,5):
        try:
            new_resource = gdata.docs.data.Resource(file_path, os.path.basename(file_path))
            media = gdata.data.MediaSource()
            media_type = magic.from_file(file_path, mime=True)
            media.SetFileHandle(file_path, media_type)
            """
            uri is a unique id for the media, and there are different calling conventions for retreving this value based on whether or not you have a parent directory (parent_collection)
            the string being appended ('?convert=false') keeps Google Drive from converting filetypes willy-nilly (they like *.gdocs apparently).
            """
            if parent_collection is not None:
                return client.CreateResource(new_resource, media=media, collection=parent_collection, create_uri=parent_collection.GetResumableCreateMediaLink().href + '?convert=false' )
            else:
                return client.CreateResource(new_resource, media=media, create_uri = gdata.docs.client.RESOURCE_UPLOAD_URI + '?convert=false')
        except Exception as e:
            continue
    roll_back(e)

def create_collection(folder_name, parent_collection):
    """
     create_collection(folder_name, parent_collection) creates a new google drive folder named "folder_name" inside of the "parent_collection" directory
    """
    for attempts in range(0,5):
        try:
            new_collection = gdata.docs.data.Resource(type='folder', title=folder_name)
            new_collection = client.CreateResource(new_collection, collection=parent_collection)
            return new_collection
        except Exception as e:
            continue
    roll_back(e)

def build_path(google_drive_path):
    global directory_map
    built_path= ''
    for folder in google_drive_path:
        new_path = os.path.join(built_path, folder)
        if not new_path in directory_map: directory_map[new_path] = create_collection(folder, directory_map[built_path])
        built_path = new_path

def sync(paths):
    global directory_map
    for path in paths:
        google_drive_path = path.replace(GOOGLE_DRIVE_PATH, '')[1:].split('/')
        file_name = google_drive_path.pop(-1)
        build_path(google_drive_path)
        google_drive_path = '/'.join(google_drive_path)
        if not google_drive_path in directory_map: raise Exception('failed to properly construct directory structure in google_drive')
        create_file(path, directory_map[google_drive_path])

if __name__ == "__main__":
    LAST_UPDATE = get_last_update()
    change_last_update()
    paths = get_modifications(LAST_UPDATE)
    connect_client()
    sync(paths)

