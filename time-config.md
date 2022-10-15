# Configure time synchronization

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
sudo ./testptp -s
```
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
sudo ptp4l -f ptp.config -2 -m -q
```

The `-2` specifies the Ethernet (Layer 2) transport.

You can run a slave just by running ptp4l adding `-s` to the options used on the master.

```
sudo ptp4l -f ptp.config -2 -m -q
```

## PTP/NTP production setup

This section is how to set things up robustly for production, using PTP in parallel with NTP.

There are several different possible approaches to setting up the server.

### Server side dual PPS with gpsd

This recipe assumes you have two PPS input signals:

1. GPIO pin 18 (available through `/dev/pps0`), used by gpsd
2. the SYNC_OUT pin (available through `/dev/ptp0`), used by ts2phc

U-blox timing modules have two time pulse outputs, and these are exposed by some boards, in particular the ones in the telecom form factor.

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

Add `/etc/chrony/sources.d/pool.sources` with

```
pool th.pool.ntp.org iburst
```

where `th` is your two-character country code.
Comment out the `pool` line from `/etc/chrony/chrony.conf`.

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
# ethernet transport
network_transport L2
```
Then

```
sudo systemctl enable ptp4l@eth0
sudo systemctl start ptp4l@eth0
```

Use `ts2phc` with the `-s generic` rather than `-s nmea`. This will get the time of day from the system clock.

```
sudo ts2phc -f ptp.config -s generic -m -q -l 7 >ts2phc.log &
```

TODO: manage ts2phc with systemd 

### Server side without gpsd

You can use `ts2phc -s nmea` (as in the test setup) to adjust the PHC using the NMEA and PPS output from the GPS.

You can then use chrony with `refclock PHC` to synchronize the system clock from the PHC.

TODO: explain this in more detail
Q: On the client side, it's better to sychronize the system clock from the PHC by using `phc2sys -E ntpshm` and then using chrony with `refclock SHM`, because this ensures that chrony will not use the refclock if PTP has lost synchronization. Does this apply on the server side also?

### Client side

We can use the timemaster service to manage this (which gets installed with linuxptp).

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


