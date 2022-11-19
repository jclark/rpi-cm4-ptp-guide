# copy config files into place
cp ptp4l-gm /etc/default/
cp phc2shm.service ts2phc.service ptp4l-gm.service /etc/systemd/system/
cp shm-refclock.conf /etc/chrony/conf.d/
cp ptp4l-gm-set.sh /usr/local/sbin/
cp dhcpcd.exit-hook /etc/
# reload the service files
systemctl daemon-reload

