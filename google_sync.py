#!/usr/bin/env python
"""
* Rhiza Screening -- Google Sync *
**********************************
**********************************
*** Rob Brown; rab170@pitt.edu ***
**********************************

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

****************************************************************************************
"""
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import gdata.docs.data
import gdata.docs.client
import os, time, logging, magic


LOGIN_PATH=os.path.expanduser('~/login.txt')
GOOGLE_DRIVE_PATH=os.path.expanduser('~/Dropbox/coursework/Pitt')
LAST_UPDATE_PATH='.last_update'
LOG_PATH='.google_sync_logs'

directory_map = {'':None}   #hash table for mapping local paths to GData folder "resource" objects. Map an empty path (which coresponds to ~/GoogleDrive)to None, since this is our root in the cloud
logger = None

def logger_init():
    global logger
    logger = logging.getLogger('google_sync')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(LOG_PATH)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)

def get_last_update():
    if not os.path.isfile(LAST_UPDATE_PATH): return None
    f = open(LAST_UPDATE_PATH)
    return time.strptime(f.readline(), '%Y-%m-%d %H:%M:%S')

def change_last_update():
    f =open(LAST_UPDATE_PATH, 'w+')
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    f.write(time_str)

def connect_client():
    """" modifies the (global) "client" variable to allow the user identified in "~/login.txt" to communicate with google drive """
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
        for file_name in files:
            abs_path = root + "/" +  file_name
            if time.gmtime(os.stat(abs_path).st_mtime) >= LAST_UPDATE:              #check files at each depth, append to_update if they have been modified since LAST_UPDATE
                to_update.append(abs_path)
    return to_update

def create_file(file_path, parent_collection):
    """
        creates Google Drive file inside of "parent_collection". Its data is "file_path", and is uploaded generically and irrespective of file type
        returns the created file resource
    """
    for attempt in range(1,6):
        try:
            new_resource = gdata.docs.data.Resource(file_path, os.path.basename(file_path))
            media = gdata.data.MediaSource()
            media_type = magic.from_file(file_path, mime=True)
            media.SetFileHandle(file_path, media_type)
            """
            A URI is a query ID, and there are different calling conventions for retreving this value based on whether or not you have a parent directory (parent_collection)
            Additionally, the string being appended ('?convert=false') keeps Google Drive from converting filetypes (they like *.gdocs extensions, evidently).
            """
            if parent_collection is not None:
                new_resource = client.CreateResource(new_resource, media=media, collection=parent_collection, create_uri=parent_collection.GetResumableCreateMediaLink().href + '?convert=false' )
            else:
                new_resource = client.CreateResource(new_resource, media=media, create_uri = gdata.docs.client.RESOURCE_UPLOAD_URI + '?convert=false')
            logger.info('created ' + file_path + ' on attempt %i',  attempt)
            return new_resource
        except Exception as e:
            logger.info('failed to create ' + file_path + ' on attempt %i', attempt)
            logger.error(e)
            logger.error("re-trying...")
            continue
    return None     #future work: implement rollback functionality, out of the scope of this project -- files will be lost if connection fails 5 times (until next modification)

def search_file(file_name, parent_collection):
    """
        searches Google Drive for a file named "file_name" who is a child of the folder "parent_collection"
        returns file resource if found, None if not found
    """
    if parent_collection is None:
        query = gdata.docs.client.DocsQuery(title=file_name, title_exact='true')
        search_results = client.GetResources(q=query, limit=5000).entry
        if len(search_results) > 0:             #future work:: watch duplicate titles --  out of the scope for this project. G-data allows users to specify parent directories for everything but queryinig (very inconvenient)
            logger.info('file ' + file_name + ' found.')
            return search_results[0]
    else:
        parent_contents = client.GetResources(uri=parent_collection.content.src,limit=5000).entry
        for entry in parent_contents:           #future work:: fix efficiency -- out of the scope for this project. Queries don't allow for parent folder specification, and return unordered lists. Lots of overhead.
            if entry.title.text == file_name:
                logger.info('file ' + file_name + ' found.')
                return entry
    return None

def update_file(file_path, file_resource):
    """"
        updates the Google Drive file "file_resource" with the modified data found in "file_path"
        saves in Google Drive as a new revision (maintaining past data for the user)
        returns updated file resource
    """
    for attempt in range(1,6):
        try:
            updated_media = gdata.data.MediaSource()
            media_type = magic.from_file(file_path, mime=True)
            updated_media.SetFileHandle(file_path, media_type)
            updated_entry = client.UpdateResource(file_resource, media=updated_media, new_revision=True)
            logger.info('updated ' + file_path + ' on attempt %i', attempt)
            return updated_entry
        except Exception as e:
            logger.info('failed to update ' + file_path + ' on attempt %i', attempt)
            logger.error(e)
            logger.error("re-trying...")
            continue
    return None

def search_collection(folder_name, parent_collection):
    """"
    searches google drive for collections named "folder_name" which are immediate children of the "parent_collection" folder
    """
    if parent_collection is None:
        query = gdata.docs.client.DocsQuery(title=folder_name, title_exact='true', show_collections ='true')
        search_results = client.GetResources(q=query, limit=5000).entry
        if len(search_results) > 0:         #future work:: watch duplicate titles --  out of the scope for this project. GDATA allows users to specify parent directories for everything but queryinig (very inconvenient)
            logger.info('folder ' + folder_name + ' found.')
            return search_results[0]
    else:
        query = gdata.docs.client.DocsQuery(show_collections ='true')
        parent_contents = client.GetResources(uri=parent_collection.content.src, q=query, limit=5000).entry
        for entry in parent_contents:       #future work:: fix efficiency -- out of the scope for this project. Queries don't allow for parent folder specification, and return unordered lists. Lots of overhead.
            if entry.title.text == folder_name:
                logger.info('folder ' + folder_name + ' found.')
                return entry
    return None

def create_collection(folder_name, parent_collection):
    """
    creates a new google drive folder named "folder_name" inside of the "parent_collection" directory
    returns collection resource
    """
    for attempt in range(1,6):
        try:
            new_collection = gdata.docs.data.Resource(type='folder', title=folder_name)
            new_collection = client.CreateResource(new_collection, collection=parent_collection)
            logger.info('created folder ' + folder_name + ' on attempt %i', attempt)
            return new_collection
        except Exception as e:
            logger.info('failed to create folder ' + folder_name + ' on attempt %i', attempt)
            logger.error(e)
            logger.error("re-trying...")
            continue
    return None     #future work: implement rollback functionality

def build_path(google_drive_path):
    """
    finds or creates the file structure contained in the list "google_drive_path", and inserts into directory_map

    eg: google_drive_path = ['foo', 'bar', 'car']

    First, search for 'foo' in the Google Drive root. If you find it, save its gdata Resource object into "directory_map". If you dont find it, create it and save the new resource into directory_map.
    Next, search the folder 'foo' for a subfolder called 'bar'. If you find it, save it. Otherwise, create it.
    Finally, search the folder 'bar' (discussed above) for a subfolder called 'car'. If you find it, save it. Otherwise, create it (and save it).
    etc.

    """
    global directory_map
    built_path= ''
    for folder in google_drive_path:
        new_path = os.path.join(built_path, folder)
        if not new_path in directory_map:
            search_result = search_collection(folder, directory_map[built_path])
            if search_result is not None:
                directory_map[new_path] = search_result
            else:
                directory_map[new_path] = create_collection(folder, directory_map[built_path])
        built_path = new_path

def sync(paths):
    """
        sync(paths) accepts a list of absolute file paths and transfers those files to Google Drive (while maintaining the directory structure/heirarchy of those paths).

        First, the folder heirarchy is reconstructed in Google Drive; this is done by the function "build_path", which stores Google folder objects ("collection resources") inside the dictionary "directory_map"
        Next, we search the Google folder objects for our file. If we find it, we add a new revision to that file and upload the modified data. If we don't find it, we create it.
    """
    global directory_map
    for path in paths:
        google_drive_path = path.replace(GOOGLE_DRIVE_PATH, '')[1:].split('/')
        file_name = google_drive_path.pop(-1)   #Modify absolute path to something suitable for google drive. Remove GOOGLE_DRIVE_PATH=~/GoogleDrive and the file handle, leaving our Google Drive folders (to construct)
        build_path(google_drive_path)           #Find the Google Drive folder heirarchy associated with the given file (or create it if it doesn't exist yet)
        google_drive_path = '/'.join(google_drive_path)
        search_result = search_file(file_name, directory_map[google_drive_path])    #The folder heirarchy has now been constructed (and stored in google_drive_map). Search for our file.
        if search_result is None:
           create_file(path, directory_map[google_drive_path])
        else:
            update_file(path, search_result)

if __name__ == "__main__":
    logger_init()
    logger.info('starting google drive sync')
    LAST_UPDATE = get_last_update()
    change_last_update()
    paths = get_modifications(LAST_UPDATE)
    connect_client()
    sync(paths)
