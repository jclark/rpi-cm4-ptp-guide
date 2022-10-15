# CM4 OS installation and configuration

We will be using Raspbian.

## OS installation

Install Raspbian Lite 64-bit.

If your CM4 has eMMC, follow these [instructions](https://www.raspberrypi.com/documentation/computers/compute-module.html#flashing-the-compute-module-emmc).
When using the Raspberry Pi Imager, select `Raspberry Pi OS (other)` and then  `Raspberry Pi OS Lite (64-bit)`.

TODO: installation without eMMC

TODO: What is the minimum amount of RAM for 64-bit to be a better choice than 32-bit? Not sure if 1Gb RAM would work better with a 32-bit OS. 

## OS configuration

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
# Enable GPIO pin 18 for PPS (not always necessary, but useful for testing)
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

## Verify OS setup

Check the check the kernel version using

```
uname -r
```

This should be at least `5.15.61-v8+`.

Check that you have ethernet PTP hardware support

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

Check the RTC

```
sudo hwclock --show
```

Check that the current date is correct:

```
date
```
