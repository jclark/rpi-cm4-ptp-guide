# CM4 OS installation and configuration

These instructions are for the Raspberry Pi OS Lite. Raspberry Pi OS used to be called Raspbian.
We are using the version based on Debian 11 (Bullseye), since that is current at the time of writing (late 2022). We are using Raspberry Pi OS, because we depend on kernel support that has not yet available in other distributions. We are using the Lite version, since we do not need or want a desktop environment for this application. We are also using the 64-bit version, since this takes best advantage of the CM4 hardware (particularly with 8Gb RAM).

## OS installation

Install Raspberry Pi OS Lite 64-bit.

If your CM4 has eMMC, follow these [instructions](https://www.raspberrypi.com/documentation/computers/compute-module.html#flashing-the-compute-module-emmc).
When using the Raspberry Pi Imager, select `Raspberry Pi OS (other)` and then  `Raspberry Pi OS Lite (64-bit)`.

TODO: installation without eMMC

TODO: What is the minimum amount of RAM for 64-bit to be a better choice than 32-bit? Not sure if 1Gb RAM would work better with a 32-bit OS. 

## OS configuration

If you want to do this using SSH from your main machine, then

* run `raspi-config` to enable SSH (under Interfacing)
* find the current IP address using `ifconfig`

Kernel support for PTP on the CM4 is broken in some kernel versions. So we need
to prevent them from being installed by creating a file `/etc/apt/preferences`
before upgrading.

```
Package: src:raspberrypi-firmware
Pin: version 1:1.20221028-1
Pin: version 1:1.20221104-1
Pin-Priority: -1
```

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
* wifi country (under System Options > Wireless LAN)
* hostname (under System Options)

Reboot.

## Verify OS setup


Check that your kernel includes the necessary have ethernet PTP hardware support

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

If you don't see the hardware-transmit/-receive/-raw-clock lines, then
you don't have the right kernel version. Look at your version using:

```
uname -r
```

If this is a later version than `5.15.61-v8+`, you can try downgrading to a version
that works:

```
wget -r -l1 --no-parent -A.20220830-1_arm64.deb http://archive.raspberrypi.org/debian/pool/main/r/raspberrypi-firmware/
sudo dpkg -i archive.raspberrypi.org/debian/pool/main/r/raspberrypi-firmware/*.20220830-1_arm64.deb
```

Alternatively, you could try updating to a bleeting-edge kernel by doing:

```
sudo rpi-update
```


Check the RTC

```
sudo hwclock --show
```

Check that the current date is correct:

```
date
```

Check support for the fan controller. Do

```
ls /sys/class/thermal
```

You should see:

```
cooling_device0  thermal_zone0
```
