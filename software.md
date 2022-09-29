# Setting up software for PTP support

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

## Verify setup

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

## PTP grandmaster setup

Install Linux PTP

```
sudo apt install linuxptp
```

This enables the timemaster service, which we don't want, so disable it:

```
sudo systemctl disable timemaster.service
```

Create a file `ptp.config` with the following:

```
[global]
ts2phc.nmea_serialport /dev/ttyAMA0
leapfile /usr/share/zoneinfo/leap-seconds.list
tx_timestamp_timeout 100
[eth0]
```

Run `ts2phc` to synchronize the PTP hardware clock from the GPS:

```
sudo ts2phc -f ptp.config -s nmea -m -q -l 7 >ts2phc.log &
```

Look at `ts2phc.log` to check everything is working:

```
tail -f ts2phc.log
```

When that's working, you can then start the PTP daemon

```
sudo ptp4l -f ptp.config -2 -m -q
```


