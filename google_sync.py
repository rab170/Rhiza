#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""
********************************
Rhiza Screening -- Google Sync *
********************************
** Rob Brown; rab170@pitt.edu **
********************************

TL;DR --this program syncs ~/GoogleDrive/* with the google account identified in ~/login.txt

This program emulates a simple subset** of the auto-sync behaviors found in Dropbox (from my experience as a UNIX user). In dropbox (unlike Google Drive) users have a local (mutable) directory
in which their Dropbox data operates. This directory is automatically synced with their Cloud data, eliminating the overhead of backing up their files (in addition to providing seemless version control).
This program operates in unison with a CRON job, which watches ~/GoogleDrive/* for modifications.

**Note that you will not find auto-removal functionality, nor upstream changes being pulled to the local ~/GoogleDrive directory

"""

import gdata.docs.data
import gdata.docs.client

import os.path, time


def get_last_update():
    if not os.path.isfile('last_update.txt'): return None
    f =open('last_update.txt')
    return time.strptime(f.readline(), '%Y-%m-%d %H:%M:%S')

def change_last_update():
    f =open('last_update.txt', 'w+')
    time_str = time.strftime('%Y-%m-%d %H:%M:%S')
    f.write(time_str)

def connect_client():
    global client
    LOGIN_PATH=os.path.expanduser("~/login.txt")
    login_file = open(LOGIN_PATH);
    USER=login_file.readline()
    PASS=login_file.readline()
    client = gdata.docs.client.DocsClient(source='google_sync.py')
    client.api_version = "3"
    client.ssl = True
    client.ClientLogin(USER, PASS, client.source)



if __name__ == "__main__":
    last_update = get_last_update()
    change_last_update()
    connect_client()


    filePath = "/home/rob/SPRING_2014.txt"
    newResource = gdata.docs.data.Resource(filePath, os.path.basename(filePath))
    media = gdata.data.MediaSource()
    media.SetFileHandle(filePath, 'set/forget')     #second argument is for intern google useage. Examples are 'image/jpeg' or 'text/plain'. Serverside, this is extrapolated from the file extension. Thus, set and forget.
    newDocument = client.CreateResource(newResource, create_uri=gdata.docs.client.RESOURCE_UPLOAD_URI, media=media)





















