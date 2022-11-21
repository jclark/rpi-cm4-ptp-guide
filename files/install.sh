# copy config files into place
for f in `cat files.txt`; do cp `basename $f` $f; done
# reload the service files
systemctl daemon-reload
