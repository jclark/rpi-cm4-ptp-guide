# CM4 OS installation and configuration

These instructions are for the Raspberry Pi OS Lite. Raspberry Pi OS used to be called Raspbian.

As of the time of writing (early 2024), the current version of Raspberry Pi OS is based on Debian 12 (Bookworm).
The legacy version of Raspberry Pi OS is based on Debian 11 (Bullseye).
We are using Raspberry Pi OS, since it is optimized for the Raspberry Pi hardware.
We are using the Lite version, since we do not need or want a desktop environment for this application. We are also using the 64-bit version, since this takes best advantage of the CM4 hardware (particularly with 8Gb RAM).

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
at the end of `/boot/firmware/config.txt` (on Raspberry Pi OS 11, it's `/boot/config.txt`).

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

Use raspi-config to set
* wifi country (under System Options > Wireless LAN)
* hostname (under System Options)

Reboot.

## Static IP address

Although it's not essential, you probably want a static IP address.

### Network Manager

Raspberry Pi OS 12 by default uses Network Manager to manage network connections.

You can see the current connections using

```
nmcli con show
```

Assuming the connection on the interface is named `Wired connection 1`, you can change it to a static IP using a command like:

```
nmcli con mod "Wired connection 1" ipv4.method manual ipv4.addresses 192.168.0.5/24 ipv4.gateway 192.168.0.1 \
   ipv4.dns 8.8.8.8 ipv4.dns-search lan
```

You can activate this by doing:

```
nmcli con down "Wired connection 1"
nmcli con up "Wired connection 1"
```

### dhcpcd

Raspberry Pi OS 11 by default uses dhcpcd to manage the network. Edit the section of `/etc/dhcpcd.conf` starting with `Example static IP configuration`.

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

Note that `PTP Hardware Clock: 0` means that this interface uses `/dev/ptp0` as
its hardware clock.

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
