# CM4/CM5 OS installation and configuration

These instructions are for the Raspberry Pi OS Lite. Raspberry Pi OS used to be called Raspbian.

As of the time of writing (early 2025), the current version of Raspberry Pi OS is based on Debian Bookworm.
The legacy version of Raspberry Pi OS is based on Debian Bullseye.
The CM5 requires Bookworm.
We are using Raspberry Pi OS, since it is optimized for the Raspberry Pi hardware.
We are using the Lite version, since we do not need or want a desktop environment for this application. We are also using the 64-bit version, since this takes best advantage of the CM4 hardware (particularly with 8Gb RAM).

## OS installation

Install Raspberry Pi OS Lite 64-bit.

If your CM4/CM5 has eMMC, follow these [instructions](https://www.raspberrypi.com/documentation/computers/compute-module.html#flashing-the-compute-module-emmc).
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

and reboot.

On the CM5, it is necessary to have at least kernel version 6.12 for PTP hardware timestamping to work.
You can check your kernel version with `uname -r`.
If that says you are running something earlier than 6.12 (e.g. 6.6.x), then you will need to update to a more recent kernel.
At the time of writing (January 2025), this can be done using the command `sudo rpi-update next`. See
this [forum thread](https://forums.raspberrypi.com/viewtopic.php?t=379745).
This is not necessary nor recommended for the CM4. 

Run `raspi-config`:

* enable serial port (under Interface/Serial Port); answer
   * No to login shell accessible over serial
   * Yes to enable serial port hardware

For the CM4, but not the CM5, add the following
at the end of `/boot/firmware/config.txt` (on Bullseye, it's `/boot/config.txt`).
This should not 

```
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

Raspberry Pi OS Bookworm by default uses Network Manager to manage network connections.

You can see the current connections using

```
nmcli c show
```

Assuming the connection on the interface is named `Wired connection 1`, you can change it to a static IP using a command like:

```
nmcli c mod "Wired connection 1" ipv4.method manual ipv4.addresses 192.168.0.5/24 ipv4.gateway 192.168.0.1 \
   ipv4.dns 8.8.8.8 ipv4.dns-search lan
```

You can activate this by doing:

```
nmcli d reapply eth0
```

### dhcpcd

Raspberry Pi OS Bullseye by default uses dhcpcd to manage the network. Edit the section of `/etc/dhcpcd.conf` starting with `Example static IP configuration`.

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

## Verify GPS connection

You should verify that the GPS is properly connected. There are two connections

- the serial connection
- the PPS connection

### Serial connection

Assuming you have specified `dtoverlay=disable-bt` above and you have connected the GPS
RX (white) and TX (green) pins to pins 8 and 10 respectively on the J8 HAT connector,
then the serial device will be `/dev/ttyAMA0`.

Do:

```
(stty 9600 -echo -icrnl; cat) </dev/ttyAMA0
```

Here 9600 is the speed. The most common default speed is 9600, but some receivers default to 38400 or 115200.

You should see  lines starting with `$`.
In particular look for a line starting with `$GPRMC` or `$GNRMC`. The number following that should be the current UTC time;
for example, `025713.00` means `02:57:13.00` UTC.
After another 8 commas, there will be a field that should have the current UTC date;
for example, `140923` means 14th Septemember 2023.

### PPS connection

To verify that the PPS connection is working, first configure the SYNC_OUT for input: 

```
echo 1 0 | sudo tee /sys/class/ptp/ptp0/pins/SYNC_OUT
```

Replace the `0` in `ptp0` with whatever `ethtool` said was the number.
`SYNC_OUT` here is the name of the pin to which the PPS is connected. In the `echo 1 0`, 1 means to use the pin for input and 0 means the pin should use input channel 0.


Now do:
```
echo 0 1 | sudo tee /sys/class/ptp/ptp0/extts_enable
```

This means to enable timestamping of pulses on channel 0. In the `echo 0 1`, 0 means channel 0 and 1 means to enable timestamping.


Now see if we're getting timestamps:

```
sudo cat /sys/class/ptp/ptp0/fifo
```

The `cat` command should output a line, which represents a timestamp of an input pulse and consists of 3 numbers: channel number, which is zero in this case, seconds count, nanoseconds count. Repeating the last command will give lines for successive input timestamps.

If `cat` outputs nothing, then it's not working.