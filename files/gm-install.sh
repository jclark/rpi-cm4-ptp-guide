#!/bin/bash
# copy config files into place
for f in `cat gm-files.txt`; do cp --preserve=mode `basename $f` $f; done
# reload the service files
systemctl daemon-reload
