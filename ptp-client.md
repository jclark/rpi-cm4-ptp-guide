# PTP client with NTP on CM4/CM5

This runs PTP as a client on a CM4/CM5 together with an NTP server that is synced from PTP. 

We can manage this using the timemaster service, which is part of linuxptp.

Install linuxptp and chrony:
```
apt install linuxptp chrony
```

Copy [timemaster.conf](files/timemaster.conf) to `/etc/linuxptp/` and then change `192.168.0.10` in the ntp_server line to the address of your NTP server.

Then enable the timemaster service:

```
sudo systemctl enable timemaster.service
```

You may get the following error on startup from ptp4l:

```
interface 'eth0' does not support requested timestamping
```

You can avoid this by copying [phc@.service](files/phc%40.service) to `/etc/systemd/system/` and then do

```
sudo systemctl daemon-reload
sudo systemctl enable phc@eth0.service
```

This service makes sure the PHC is ready before ptp4l runs.
