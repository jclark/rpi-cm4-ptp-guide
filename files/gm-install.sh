#!/bin/bash
# copy config files into place
for f in `cat gm-files.txt`; do cp `basename $f` $f; done
# reload the service files
systemctl daemon-reload
