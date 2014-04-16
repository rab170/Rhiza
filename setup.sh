#!/bin/sh
#sudo python gdata-2.0.18/setup.py install
#sudo python python-magic/setup.py install
python google_sync.py
crontab -l | { cat; echo "*/10 * * * * python $(pwd)/google_sync.py"; } | crontab -
