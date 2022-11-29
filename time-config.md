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
(stty 9600 -echo -icrnl; cat) </dev/ttyAMA0
```

This should show some NMEA sentences (lines starting with `$`).

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

If you get the error `nmea: unable to find utc time in leap second table` from `ts2phc`,
then you can install the fixed linuxptp package, as described in the next section.

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

## PTP grandmaster setup

This section describes how to setup a PTP grandmaster. It also
sets up chrony to get time from the GPS via the PHC.

You can install everything needed using the following commands.

```
# Install chrony
sudo apt install chrony
# Clone this repository
https://github.com/jclark/rpi-cm4-ptp-guide.git
# Change into the files directory
cd rpi-cm4-ptp-guide/files/
# Install fixed version of linuxptp package
sudo dpkg -i linuxptp/linuxptp_3.1.1-4jclark1_arm64.deb
# Copy the configuration files into place.
sudo bash gm-install.sh
```

You can then start everything up by doing:

```
sudo systemctl start ptp4l-gm phc2shm
```

Do *not* use systemctl to enable the ptp4l-gm service. (It will get started on boot
by a dhcpcd hook.)

### Explanation

You can skip this section if you are uninterested in what the above is doing.

The `gm-install.sh` script is very straightforward: it just copies the files
listed in `gm-files.txt` into the right directories, and then tells systemd
about the new service unit files.

The reason to install a new linuxptp package is that there is an uninitialized variable bug in the existing package which will cause `ts2phc -s nmea` sometimes to give the error

```
nmea: unable to find utc time in leap second table
```

This bug is fixed in the upstream git repository. The fixed package just incorporates
this fix along with a few selected other fixes from upstream.

This sets up the following three new services:
- ts2phc: this runs synchronizes the PHC from the GPS by running `ts2phc -s nmea`
- ptp4l-gm: this starts ptp4l and then uses pmc (the PTP management client) to make some additonal settings needed when it is running as a grandmaster; this depends on the ts2phc service
- phc2shm: this runs `phc2sys -E ntpshm` to put samples from the PHC into an NTP-compatible shared memory segment, where they can be used by chrony (via an SHM refclock); this also depends on the ts2phc service

These services are not enabled (and you should not enable them). Instead they are started up by a dhcpcd hook when a carrier is detected on eth0, and stopped when the carrier is lost. This is because the PHC driver does not work properly when there is no carrier.

The three services all use some configuration options in `/etc/default/ptp4l-gm`, which you
can edit to taste.

The settings made by pmc are needed for interoperability with the Windows PTP client.

Chrony is sychronized to the PHC using the phc2shm service rather than by using a PHC refclock, because phc2sys provides more control over how the PHC is accessed and we can use this to better workaround a hardware limitation that causes PHC access to interfere with reading the PPS from the GPS.

### Monitoring

If you change LOG_LEVEL to 7 in `/etc/default/ptp4l-gm`, there will be detailed logs in /var/log/user.log.

You can use `systemctl status` to look at the status of the `ts2phc`, `ptp4l-gm` and `phc2shm` services.

Doing

```
sudo pmc -u -b 0 'get GRANDMASTER_SETTINGS_NP' 
```

should show the same settings as are in `ptp4l-gm-set.sh`.

After a minute or so, you can check the PHC, by doing

```
sudo phc_ctl eth0 cmp
```

This should report an offset close to to -37s (i.e. -37000000000 ns).

The output of `chronyc tracking` should show (in the Reference Id line) that it is using the SHM0 refclock, and after a while the RMS offset should be small (single digit number of microseconds).

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

where `192.168.0.10` is the address of the NTP server.

Then enable the timemaster service:

```
sudo systemctl enable timemaster.service
```


