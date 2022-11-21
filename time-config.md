# Configure time synchronization

This page describes how to set things up yourself, using open source software.

If this isn't your idea of fun, you might want to try [Timebeat](https://timebeat.app/). It is a commercial synchronization solution, but offers a free download. The people behind it were instrumental in implementing the kernel support for the PHC in the CM4's Ethernet PHY. 

## Verify GPS connection

Download and compile `testptp` program:

```
wget https://raw.githubusercontent.com/torvalds/linux/master/tools/testing/selftests/ptp/testptp.c
gcc -o testptp testptp.c -lrt
```

Use testptp to check PPS signal on SYNC_OUT pin:

```
# Configure SYNC_OUT pin to be an input pin
sudo ./testptp  -d /dev/ptp0 -L 0,1
# Read some timestamps (e.g. 5)
sudo ./testptp  -d /dev/ptp0 -e 5
```

The ethernet needs to be plugged in for PTP hardware clock to work.

Check serial connection to GPS

```
cat </dev/ttyAMA0
```

This should show some NMEA sentences.

## Minimal PTP test setup

This section describes a minimal setup suitable for PTP testing purposes.

Install Linux PTP

```
sudo apt install linuxptp
```

This enables the timemaster service, which we don't want at this point, so disable it:

```
sudo systemctl disable timemaster.service
```

In this first stage, we are just going focus on getting the PTP hardware clocks synchronized and not worry about the system clock.

Create a file `ptp.config` with the following:

```
[global]
ts2phc.nmea_serialport /dev/ttyAMA0
leapfile /usr/share/zoneinfo/leap-seconds.list
tx_timestamp_timeout 100
[eth0]
```

Set the PHC clock time from the system time:

```
sudo phc_ctl eth0 "set;" adj 37
```

The `adj 37` is because the PHC uses the TAI timescale, which is 37 seconds ahead of UTC.

(This shouldn't be necessary, but I get `nmea: unable to find utc time in leap second table` errors from `ts2phc` otherwise.)

Run `ts2phc` to synchronize the PTP hardware clock from the GPS:

```
sudo ts2phc -f ptp.config -s nmea -m -q -l 7 >ts2phc.log &
```

Look at `ts2phc.log` to check everything is working:

```
tail -f ts2phc.log
```

The number following `master offset` should be small in magnitude (certainly less than 100).  Leave it running for a while.
Then make sure you are seeing consistently small offsets.

```
awk '/master offset/ { if (($5 > 0 ? $5 : -$5) > 99) print $5 }' ts2phc.log
```

will print out offsets of 100ns or more. There should only be a few of those at the start while ts2phc is settling.

When that's working, you can then start the PTP daemon

```
sudo ptp4l -f ptp.config -m -q
```

You can run a slave on another machine just by running ptp4l adding `-s` to the options used on the master.

```
sudo ptp4l -f ptp.config -m -q -s
```

## PTP server

This sets up a PTP server using `ts2phc -s nmea` to handle the GPS NMEA output.

This assumes you have already installed linuxptp and disabled the timemaster service as described above.

Create `/etc/linuxptp/ts2phc.conf` with the following:

```
[global]
ts2phc.nmea_serialport /dev/ttyAMA0
ts2phc.pulsewidth 100000000
leapfile /usr/share/zoneinfo/leap-seconds.list
tx_timestamp_timeout 100
# Uncomment the next line to get detailed logs
#logging_level 7
```

Create `/etc/systemd/system/ts2phc@.service` with the following

```
[Unit]
Description=Synchronize PTP hardware clock (PHC) of %I to external time stamp signal
Documentation=man:ts2phc
After=sys-subsystem-net-devices-%i.device
Requires=sys-subsystem-net-devices-%i.device

After=time-sync.target
Before=ptp4l@%i.service

[Service]
Type=simple
# We use /dev/ptp0 to avoid problem with eth0 not being attached in time
ExecStartPre=/usr/sbin/phc_ctl /dev/ptp0 "set;" adj 37
ExecStart=/usr/sbin/ts2phc -f /etc/linuxptp/ts2phc.conf -s nmea -c %I

[Install]
WantedBy=multi-user.target
``` 

Then tell systemd about the new service:

```
sudo systemctl daemon-reload
```

Then enable and start the ts2phc service

```
sudo systemctl enable ts2phc@eth0
sudo systemctl start ts2phc@eth0
```

After a minute or so, you can check the PHC, by doing

```
sudo phc_ctl eth0 cmp
```

This should report an offset close to to -37s (i.e. -37000000000 ns).

If you have enabled logging_level 7, then you can see detailed logs in `/var/log/user.log`:

```
Oct 22 12:08:26 rpi ts2phc: [182024.331] nmea sentence: GPRMC,050826.00,A,1343.91497,N,10038.69720,E,0.000,,221022,,,A,V
Oct 22 12:08:27 rpi ts2phc: [182025.228] nmea delay: 150159254 ns
Oct 22 12:08:27 rpi ts2phc: [182025.228] eth0 extts index 0 at 1666415343.999999987 corr 0 src 1666415344.897189013 diff -13
Oct 22 12:08:27 rpi ts2phc: [182025.229] eth0 master offset        -13 s2 freq    +912
```

Note that the time from the GPMRC sentence "050826.00" meaning 05:08:26.00 UTC matches the log time "12:08:25", since
my local time is UTC+7.

Modify /etc/linuxptp/ptp4l.conf so it contains the following (you can leave the other lines as is or delete them)

```
[global]
# work around bug/limitation in CM4 hardware
tx_timestamp_timeout 100
# 6 means synchronized to primary reference time source (e.g. GPS) and using PTP timescale
clockClass 6
# Meaning of accuracy values
# 0x20 25ns
# 0x21 100ns
# 0x22 250ns
# 0x23 1us
# 0x24 2.5us
# 0x25 10us
clockAccuracy 0x20
```
Then

```
sudo systemctl enable ptp4l@eth0
sudo systemctl start ptp4l@eth0
```

In kernel 5.15.61-v8+, the support for the CM4 NIC appears to have the limitation that getting time from the PHC interferes with ts2phc getting timestamp events. To make things work reliably, we therefore need to avoid reading the PHC on the server. We accordingly:

- don't run phc2sys
- don't run an NTP server (just rely on `systemd-timesyncd`) on this machine

You should run your NTP server on a separate machine that is sychronized using PTP to this machine.
You can use the PTP client section below for this.

## PTP and NTP server

This section is about how to set things using PTP server and NTP server on the same machine.

To avoid reading the PHC, this needs PPS inputs to be connected in two places.

1. GPIO pin 18 (available through `/dev/pps0`), used by chrony to control the system clock
2. the SYNC_OUT pin (available through `/dev/ptp0`), used by ts2phc to control the PHC

The RCB-F9T exposes two PPS signals which we can then connect to this pins.

**This is the approach I am currently using, but the RCB-F9T is really overkill for this.**

TODO: for other GPS receivers, is there an easy way to connect the single PPS output to both of these pins?

This approach uses gpsd rather thean ts2phc to process the GPS's NMEA output.

Install gpsd.

```
sudo apt install gpsd
```

In `/etc/default/gpsd`, set

```
DEVICES="/dev/ttyAMA0"
GPSD_OPTIONS="-n"
```

Install chrony.

```
sudo apt install chrony
```

Comment out the `pool` line from `/etc/chrony/chrony.conf` and instead
add `/etc/chrony/sources.d/pool.sources` with

```
pool th.pool.ntp.org iburst
```

where `th` is your two-character country code.


Add `/etc/chrony/conf.d/gps.conf` with:

```
refclock SHM 0 refid NMEA noselect offset 0.4 delay 0.2
refclock SHM 1 refid PPS precision 1e-7 lock NMEA
```

Add `/etc/chrony/conf.d/allow.conf` with the line:

```
allow
```

Create /etc/linuxptp/ptp4l.conf with the following:

```
[global]
# work around bug/limitation in CM4 hardware
tx_timestamp_timeout 100
clockClass 6
clockAccuracy 0x20
masterOnly 1
```
Then

```
sudo systemctl enable ptp4l@eth0
sudo systemctl start ptp4l@eth0
```

Create `/etc/linuxptp/ts2phc.conf` with the following:

```
[global]
leapfile /usr/share/zoneinfo/leap-seconds.list
tx_timestamp_timeout 100
```

Create `/etc/systemd/system/ts2phc@.service` with the following

```
[Unit]
Description=Synchronize PTP hardware clock (PHC) of %I to external time stamp signal
Documentation=man:ts2phc
After=sys-subsystem-net-devices-%i.device
After=time-sync.target
Before=ptp4l@%i.service

[Service]
Type=simple
ExecStart=/usr/sbin/ts2phc -f /etc/linuxptp/ts2phc.conf -s generic -c %I

[Install]
WantedBy=multi-user.target
``` 

This uses `ts2phc` with the `-s generic` option, which will get the time of day from the system clock.

Then tell systemd about the new services:

```
sudo systemctl daemon-reload
```

Then enable and start the ts2phc service

```
sudo systemctl enable ts2phc@eth0
sudo systemctl enable ptp4l@eth0
sudo systemctl start ts2phc@eth0
sudo systemctl enable ts2phc@eth0
```

## PTP client with NTP on CM4

This runs PTP as a client on a CM4 together with an NTP server that is synced from PTP. 

We can manage this using the timemaster service, which is part of linuxptp.

Install linuxptp and chrony:
```
apt install linuxptp chrony
```

Change `/etc/linuxptp/timemaster.conf` to the following
```
# Configuration file for timemaster

[ntp_server 192.168.0.10]
minpoll 4
maxpoll 4

[ptp_domain 0]
interfaces eth0
ptp4l_option network_transport L2
delay 1e-8

[timemaster]
ntp_program chronyd

[chrony.conf]
include /etc/chrony/chrony.conf

[ptp4l.conf]
tx_timestamp_timeout 100
clock_servo linreg

[chronyd]
path /usr/sbin/chronyd
makestep 1 3
# Uncomment the next line to allow this to be used as a server
# allow

[phc2sys]
path /usr/sbin/phc2sys

[ptp4l]
path /usr/sbin/ptp4l
```

where `192.168.0.10` is the address of the NTP server, and uncomment the `ptp_domain` section.

If you disabled timemaster earlier, then reenable it:

```
sudo systemctl enable timemaster.service
```


