# Setting up PTP

## OS installation

Install Raspbian Lite 64-bit.

If your CM4 has eMMC, follow these [instructions](https://www.raspberrypi.com/documentation/computers/compute-module.html#flashing-the-compute-module-emmc).
When using the Raspberry Pi Imager, select `Raspberry Pi OS (other)` and then  `Raspberry Pi OS Lite (64-bit)`.

## OS setup

If you want to do this using SSH from your main machine, then

* run `raspi-config` to enable SSH (under Interfacing)
* find the current IP address using `ifconfig`

Update packages

```
sudo apt update
sudo apt upgrade
```

Run `raspi-config`:

* enable serial port (under Interface/Serial Port); answer
   * No to login shell accessible over serial
   * Yes to enable serial port hardware

Configure the Device Tree for the CM4 and the IO board by adding the following
at the end of `/boot/config.txt`

```
# Enable GPIO pin 18 for PPS (not necessary, but useful for testing)
dtoverlay=pps-gpio,gpiopin=18
# realtime clock
dtoverlay=i2c-rtc,pcf85063a,i2c_csi_dsi
# fan
dtoverlay=i2c-fan,emc2301,i2c_csi_dsi
# Make /dev/ttyAMA0 be connected to GPIO header pins 8 and 10
# This always disables Bluetooth
dtoverlay=disable-bt
```

Disable the system service that initialises the modem:
```
sudo systemctl disable hciuart
```

Set the timezone:

```
sudo dpkg-reconfigure tzdata
```

You probably want a static IP address. Edit the section of `/etc/dhcpcd.conf` starting
`Example static IP configuration`.

Use raspi-config to set
* wifi country (under System Options)
* hostname (under System Options)

Reboot.

## GPS setup

For best results, you are likely to need to configure your GPS module.

At a minimum, you will need to ensure the baud rate is 9600, since the version of ts2phc in the Bullseye version of Raspberry Pi OS requires this.
For many GPS modules, 9600 is default. But some more recent modules have a higher default baud rate (e.g. RCB-F9T defaults to 115200).

### U-blox

U-blox provide the u-center application for configuring their modules.  This is available only on Windows.

My preferred solution is to use `ser2net` on the CM4 to make the serial connection available on a TCP port. You can then connect to that TCP port using u-center from a Windows machine.  To do this


```
sudo apt install ser2net
```

Then create a file `/etc/ser2net.yaml` containing:

```
---
connection: &con0
    accepter: tcp,2002
    enable: on
    connector: serialdev,/dev/ttyAMA0,9600n81,local
```

In the above, you will need to change 9600 to whatever your GPS module expects.

Alternatively, you can use a USB to TTL converter to temporarily connect the GPS module to a Windows machine, and then use u-center with the COM
port that this creates on Windows. This is OK for initial setup, but not so convenient after everything is installed.

Another possibility is to use gpsd's [ubxtool](https://gpsd.gitlab.io/gpsd/ubxtool.html). To install that, use

```
sudo apt install gpsd python3-gps
```

Then prevernt gpsd from starting automatically (otherwise it will intefere with `ts2phc` later):

```
systemctl stop gpsd.socket gpsd.service
systemctl disable gpsd.socket gpsd.service
```

## Verify hardware setup

Check the check the kernel version using

```
uname -r
```

This should be at least `5.15.61-v8+`.

Check that you have PTP hardware support

```
ethtool -T eth0
```

You should see:

```
Time stamping parameters for eth0:
Capabilities:
        hardware-transmit
        hardware-receive
        hardware-raw-clock
PTP Hardware Clock: 0
Hardware Transmit Timestamp Modes:
        off
        on
        onestep-sync
        onestep-p2p
Hardware Receive Filter Modes:
        none
        ptpv2-event
```

If the `ethtool` output doesn't look right, or the kernel version is too low, you can run

```
sudo rpi-update
```

and then reboot to update to a bleeding edge kernel.

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

Check the RTC

```
sudo hwclock --show
```

Check that the current date is correct:

```
date
```

## Minimal test setup

This section describes a minimal setup suitable for testing purposes.

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

## PPS output

You can output a PPS signal driven by the PHC clock on the SYNC_OUT pin,
which you can then measure on an external device (e.g. oscilloscope or logic analyzer).

```
# Configure SYNC_OUT pin for periodic output
sudo ./testptp -d /dev/ptp0 -L 0,2
# Generate pulse of width 1us every second
sudo ./testptp -d /dev/ptp0 -p 1000000000 -w 1000
```
The `-p` argument gives the time between the start of each pulse in nanoseconds;
the only acceptable values are `1000000000`, meaning 1 second, and `0`, meaning
to stop generating pulses.
The `-w` argument gives the width of the pulse in nanoseconds; the maximum value, which is
also the default, is 4095, meaning just over 4 microseconds.

## NTP/PTP production setup

This section is how to set things up robustly for production, using PTP in parallel with NTP.

There are several different possible approaches to setting up the server.

### Server side dual PPS

This recipe assumes you have two PPS's input signals:

1. GPIO pin 18 (available through `/dev/pps0`), used by gpsd
2. the SYNC_OUT pin (available through `/dev/ptp0`), used by ts2phc

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

Use `ts2phc` with the `-s generic` rather than `-s nmea`. This will get the time of day from the system clock.

```
sudo ts2phc -f ptp.config -s generic -m -q -l 7 >ts2phc.log &
```

TODO: manage start/stop with systemd 

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
