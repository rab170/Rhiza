#!/bin/sh
python google_sync.py
crontab -l | { cat; echo "*/10 * * * * python $(pwd)/google_sync.py"; } | crontab -
