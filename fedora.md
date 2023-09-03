# Installing and configuring Fedora on the CM4

## Fedora compared to Raspberry Pi OS

Fedora added support for the Raspberry Pi 4 (including the CM4) with release 37. At the time of writing (September 2023) the current version is release 38. It's considerably less mature than Raspberry Pi OS, which is the offical OS for the Raspberry Pi.

Fedora has some advantages, which I think give it the potential in the future to be a better platform than Raspberry Pi OS.

* Fedora has a strong [upstream focus](https://docs.fedoraproject.org/en-US/package-maintainers/Staying_Close_to_Upstream_Projects/), particularly for the kernel.
* RedHat has strong expertise PTP and NTP. In particular, the maintainer of [chrony](https://chrony-project.org/) (an NTP implementation) works for RedHat, so Fedora always has the latest version of chrony.
* Fedora includes [Cockpit](https://cockpit-project.org/), which is a very nice web interface for server administration.
* Fedora has an IoT variant; this provides a [non-traditional immutable approach](https://docs.fedoraproject.org/en-US/iot/) to an OS, which could be a more robust approach when a CM4 is being used as a PTP or NTP appliance (although I haven't tried this yet).

Fedora currently has some disadvantages compared to Raspberry Pi OS

* the documentation specific to the Raspberry Pi and particularly the CM4 is not as good (this page is trying to help with that)
* on the CM4, it's less polished and has some bugs (notably with HDMI output)
* it packages version 4.0 of Linux PTP, which is [not compatible](https://github.com/jclark/rpi-cm4-ptp-guide/issues/23) with the CM4; this can [easily be patched](https://www.mail-archive.com/linuxptp-devel@lists.sourceforge.net/msg06374.html), but as far as I know Fedora has not yet done so

The last point means that Raspberry Pi OS is the more convenient option for using PTP. But chrony can make use of the CM4's PTP hardware support for NTP; Fedora is a good basis for experimenting with that. There is a separate page for [chrony](chrony.md) configuration.

## RAM and storage requirements

CM4 RAM sizes range from 1Gb to 8Gb; eMMC sizes range from 8Gb to 32Gb.
I tried Fedora Server 38 on a CM4 with 8Gb of RAM and an 8Gb eMMC. 8Gb eMMC is plenty for just running a NTP/PTP server. From a cursory look at `/proc/meminfo`: 8Gb RAM is more than is useful: 4Gb should be plenty; 2Gb should be OK; 1Gb would be tight.

## Installation and configuration overview

The installation process needs a separate desktop computer, which can be Windows, Linux or Mac.

We can split the installation process into the following stages:

1. on the desktop system, select and download an appropriate image
2. make the CM4 storage available as a disk on the desktop system
3. on the desktop system, write the image to this disk
4. boot the CM4 for the first time from eMMC and perform initial setup
5. perform CM4-specific configuration

Fedora has good [documentation for installing on a SBC](https://docs.fedoraproject.org/en-US/fedora-server/installation/on-sbc/), but it doesn't address stage 2 for the CM4, which has internal eMMC storage (except in the CM4 Lite version).

The normal Fedora approach for step 4 requires using an HDMI monitor and keyboard connected to the CM4 to do the initial setup, most importantly to setup a user account. You cannot just skip this, since the image does not allow ssh login without some configuration for security reasons. However, it is possible to avoid this requirement if you really want to (in my case, I wanted to install a Fedora 39 nightly image, but HDMI output wasn't working properly). This requires that step 3 be done using the `arm-image-installer program`, which has options that can configure the image to allow you to ssh in as root. But `arm-image-installer` is available only on Fedora, which implies that you need to use a desktop computer that is running Fedora.

## Select and download the image

Fedora has three editions that could potentially be used with the CM4: Workstation, Server and IoT. This guide uses the Server edition, which is comparable to Raspberry Pi OS Lite.

To download, visit [getfedora.org](https://getfedora.org/) on the desktop. Then

1. Follow the link to download Fedora Server
2. Go to the section for `For ARM® aarch64 systems`
3. Download the raw `raw.xz` image

## Making CM4 storage accessible from desktop

In this stage, we need to make the storage used by the CM4 available as a disk on the desktop system.

The CM4 is available with or without an eMMC. A CM4 without an eMMC is sometimes called a CM4 Lite. Most of the CM4s that I have seen available for sale have an eMMC.

A CM4 without an eMMC uses an SD card for storage. In this case, all you have to do for this stage is to plug the CM4 into your desktop.

If you have a CM4 with an eMMC, things are more complicated. (Note that you cannot use an SD card to boot a CM4 that has an eMMC.) We need to connect the CM4 using USB to the desktop and then boot it in a way that makes the eMMC appear as a disk on the desktop. This requires running the rpiboot program on the desktop.

The steps are:

1. Install rpiboot on the desktop
2. Power on the CM4 so it will boot from USB rather than from eMMC
3. Run rpiboot on the desktop
4. Identify the disk on your desktop corresponding to the CM4

The steps other than step 2 depend on which desktop OS you are using. The details of Step 2 depend on the carrier board you are using. For the official IO board, the procedure is:

1. Disconnect all cables from the CM4 IO board.
2. Locate the J2 jumpers on the CM4 IO board. This is the 14-pin, 2 row set of pins located in the rear, center of the board. Connect the leftmost two pins, which are labelled `Fit jumper to disable eMMC Boot`. I use a female-female Dupont cable for this.
3. Connect a USB port on your desktop to the Micro USB port on the CM4 IO board (to the right of the 2 USB A ports, labeled `SLAVE` on the Waveshare cases).
4. Connect power to the CM4.

Note that after writing the image and before booting from eMMC, you will need to remove the jumper disabling eMMC boot, as well as disconnecting the Micro USB cable.

### rpiboot on Fedora desktop

Install packages needed for building rpiboot:

```
sudo dnf install git gcc make libusb1 libusb1-devel 
```

Get the rpiboot source

```
git clone --depth=1 https://github.com/raspberrypi/usbboot
```

Build rpiboot

```
cd usbboot
make
```

After powering on the CM4 so it boots from USB as described above, check that your desktop is recognizing the CM4 by doing

```
sudo dmesg | grep BCM2711
```

Then, in the usbboot directory, do

```
sudo ./rpiboot
```

The output should look something like this:

```
RPIBOOT: build-date Aug 31 2023 version 20221215~105525 c4b12f85
Waiting for BCM2835/6/7/2711...
Loading embedded: bootcode4.bin
Sending bootcode.bin
Successful read 4 bytes
Waiting for BCM2835/6/7/2711...
Loading embedded: bootcode4.bin
Second stage boot server
Cannot open file config.txt
Cannot open file pieeprom.sig
Loading embedded: start4.elf
File read: start4.elf
Cannot open file fixup4.dat
Second stage boot server done
```

After `rpiboot`` exits, the CM4 should show up as a disk. You can run

```
udisksctl status
```

to find out which disk. The output should include a line starting with `RPi` like this:

```
RPi-MSD- 0001             0001      d9e799b6             sdc
```

The last column says which disk it is, in this case, `/dev/sdc`.

### rpiboot on non-Fedora desktop

You can follow the offical Raspberry Pi [instructions](https://www.raspberrypi.com/documentation/computers/compute-module.html#flashing-the-compute-module-emmc). Jeff Geerling also has a useful [blog post](https://www.jeffgeerling.com/blog/2020/how-flash-raspberry-pi-os-compute-module-4-emmc-usbboot) and video on this.

Note that Ubuntu packages rpiboot, so you can install it with

```
sudo apt install rpiboot
```

rather than building from source.

## Writing the image

### Fedora desktop

If you are using Fedora on your desktop, you can use `arm-image-installer` to write the image.

First, install it:
```
sudo dnf install arm-image-installer
```

Now, run it. The command looks something like this:

```
sudo arm-image-installer --target=rpi4 --image=Fedora-Server-38-1.6.aarch64.raw.xz   --media=/dev/sdX --addkey=/home/jjc/.ssh/id_ecdsa.pub
```
You will need to adjust the command:
* you will always need `--target=rpi4` for the CM4
* the `--image` option specifies the image to write; it expects a compressed `.xz` image
* the `--media` option specifies the device name where you made the CM4 storage available in the previous stage
* the `--addkey` option is only necessary if you want to be able to do initial setup using SSH rather than using a monitor and keyboard connected to the CM4; the argument for the `--addkey` option needs to point to your public SSH key (I generated mine with `ssh-keygen -t ecdsa -b 521`)

It takes about 25 minutes for arm-image-installer to write the image.

### Windows desktop

On Windows, [balenaEtcher](https://etcher.balena.io/) is convenient, because it can automatically decompress `.xz` files.

## First boot and initial setup

Before booting from eMMC for the first time, you obviously need to do either

- remove the jumper that disabled eMMC boot (for a CM4 with internal eMMC), or
- insert the SD card (for a CM4 without an internal eMMC)

The offical Fedora documentation has a good description of the [normal setup](https://docs.fedoraproject.org/en-US/fedora-server/installation/on-sbc/#_basic_installation_and_configuration) process, which requires connecting an HDMI monitor or mouse.
Note that the boot process will take a few minutes, and that during the process the screen will go blank for a while; be patient,
and wait for the initial setup prompt to appear.

If you have decided not to use the normal processs, then you need to have used the appropriate options with arm-image-installer when writing the image.
You will need to figure out what IP address it got from DHCP; one method is to look at your DHCP server's log or lease file.
You can then ssh in as root, and perform initial setup on the command-line as follows:

```
# Set the time zone. I use this.
timedatectl set-timezone Asia/Bangkok
# Set the hostname. I name my computers after cheeses.
hostnamectl set-hostname pecorino
# Setup a static IPv4 address
nmcli con mod "Wired connection 1" ipv4.method manual ipv4.address 192.168.1.15/24 ipv4.gateway 192.168.1.254 ipv4.dns 192.168.1.254
# We don't need to use the normal initial setup process.
systemctl disable initial-setup
# Add a user account. Here jjc is the user name.
groupadd jjc
useradd -g jjc -c "James Clark" -G wheel -m jjc
# This will prompt to enter a password
passwd jjc
```

Note that you shouldn't do the manual setup over ssh while the normal setup process is working. 

## CM4-specific setup

Fedora has some [documentation on Raspberri Pi HATs](https://fedoraproject.org/wiki/Architectures/ARM/Raspberry_Pi/HATs) that is also applicable to the CM4 with an IO board (even without additional HATs).

TODO: The serial port explanation didn't seem consistent with what I had understood about the serial ports from the official Raspberry Pi [documentation](https://www.raspberrypi.com/documentation/computers/configuration.html#configuring-uarts).

After making the changes in this section, I recommend shutting down (with `shutdown -h now`) and power cycling.

TODO: Not sure if this is strictly necessary, but I had problems when I just rebooted without power cycling.

### Enable use of config.txt

To enable use of `config.txt`, in a similar way to Raspberry Pi OS, we have to make Fedora use the firmware device tree rather than the kernel device tree. 

First, remove the `/boot/dtb` symbolic link:

```
sudo rm /boot/dtb
```

Next, create `/etc/u-boot.conf` with the line

```
FirmwareDT=True
```

TODO: I had problems switching back to use the kernel device tree. Should be just a matter of
restoring the `/boot/dtb` link and removing `/etc/u-boot.conf`, but that didn't appear to work for me.

### Realtime clock

Add the following to the bottom of `/boot/efi/config.txt`:

```
dtoverlay=i2c-rtc,pcf85063a,i2c_csi_dsi
```

After rebooting, check the RTC

```
sudo hwclock --show
```

Also check that the current date is correct:

```
date
```

### Fan controller

Add the following to the bottom of `/boot/efi/config.txt`:

```
dtoverlay=i2c-fan,emc2301,i2c_csi_dsi
```

The fan controller needs the `emc2305` module. To load the module right away use

```
sudo modprobe emc2305
```

To ensure the module is loaded on boot, create a file `/etc/modules-load.d/fan.conf` containing the line

```
emc2305
```

When the fan controller is recognized, you should see a file ` /sys/class/thermal/cooling_device0`. If you have a fan,
the difference will be immediately audible.

TODO: The emc2305 module is not autoloading because the emc2305 driver is missing an of_device_id table. Need
to test a [patch](https://github.com/jclark/linux/commit/f951d73adebd5a69a603fd77e0a9cf8d60b75e48).

### UART

When using an GPS inside the IO board case, we will want to connect the GPS to one of the UARTs
provided by the CM4.

With Fedora, it is not convenient to use the UART that is connected to the TXD and RXD pins
on the 40-pin header (pins 8 and 10). This is because U-Boot by default enables the serial console
on that UART, which makes it try to interpret output from the GPS as keyboard input to U-boot.
(Although in theory we could [make U-Boot not do this](https://fedoraproject.org/wiki/Architectures/ARM/Raspberry_Pi/HATs#Deactivate_Serial_Console_entirely), keyboard input to U-Boot appears
not to be working at the moment, so this would require a custom version of U-Boot.)

Fortunately, the hardware provides other UARTs (numbers 2 through 5) that we can enable on other pins.
UART number *n* will appear as `/dev/ttyAMA`*n*. UART 2 is used for other functions (eeprom reading and poe fan).
So a sensible choice is UART 3. This can be enabled by adding the following to the bottom of `/boot/efi/config.txt`.

```
# UART configuration
# Make UART3 TXD, RXD available on pins 7, 29 (GPIOs 4, 5) respectively
# Device will be /dev/ttyAMA3
dtoverlay=uart3
```

You can use UART 4 instead with the following:
```
# Make UART4 TXD, RXD available on pins 24, 21 (GPIOs 8, 9) respectively
# Device will be /dev/ttyAMA4
dtoverlay=uart4
```

This means an internal GPS needs to be wired up differently when using Fedora. Here's an example assuming we are
using the `uart3` overlay.

![image](https://github.com/jclark/rpi-cm4-ptp-guide/assets/499966/cdef0aab-8628-43f4-baa5-4bc705612529)


The wiring is as follows

| Color | GPS pin | Jumpers | Pin # | Pin function |
| --- | --- | --- | --- | --- |
| yellow | PPS | J2 | 9 | SYNC_OUT |
| white | RX | HAT | 7 | GPIO 4, TXD3 |
| green | TX | HAT | 29 | GPIO 5, RXD3 |
| black | GND | HAT | 6 | Ground |
| red | VCC | HAT | 4 | 5V power |


## Post installation

Update packages

```
sudo dnf update
```

With Fedora 38, after updating everything, HDMI output no longer works.

You can make use of the Cockpit web administration interface by connecting to port 9090 on the CM4.
