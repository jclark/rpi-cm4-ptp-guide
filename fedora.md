# Installing and configuring Fedora on the CM4

## Fedora compared to Raspberry Pi OS

Fedora added support for the Raspberry Pi 4 (including the CM4) with release 37. At the time of writing (September 2023) the current version is release 38. It's considerably less mature than Raspberry Pi OS, which is the offical OS for the Raspberry Pi.

Fedora has some advantages, which mean that is has the potential in the future to be a better approach than Raspberry Pi OS.

* Fedora has a strong [upstream focus](https://docs.fedoraproject.org/en-US/package-maintainers/Staying_Close_to_Upstream_Projects/), particularly for the kernel.
* RedHat has strong expertise PTP and NTP. In particular, the maintainer of [chrony](https://chrony-project.org/) (an NTP server) works for RedHat, so Fedora always has the latest version of chrony.
* Fedora includes [Cockpit](https://cockpit-project.org/), which is a very nice web interface for server administration.
* Fedora has an IoT variant; this provides a [non-traditional immutable approach](https://docs.fedoraproject.org/en-US/iot/) to an OS, which could be a more robust approach for using a CM4 is being used as a PTP or NTP appliance (I haven't tried this yet).

Fedora currently has some disadvantages compared to Raspberry Pi OS

* the documentation specific to the Raspberry Pi and particularly the CM4 is not as good (this page is trying to help with that)
* on the CM4, it's less polished and has some bugs (notably with HDMI output)
* it packages version 4.0 of Linux PTP, which is [not compatible](https://github.com/jclark/rpi-cm4-ptp-guide/issues/23) with the CM4; this can [easily be patched](https://www.mail-archive.com/linuxptp-devel@lists.sourceforge.net/msg06374.html), but as far as I know Fedora has not yet done so

The last point means that Raspberry Pi OS is the more convenient option for using PTP. But chrony can make use of the CM4's PTP hardware support for NTP; Fedora is a good basis for experimenting with that. There is a separate page for [chrony](chrony.md) configuration.

## Installation and configuration overview

The installation process needs a separate desktop computer, which can be Windows, Linux or Mac.

We can split the installation process into the following stages:

1. on the desktop system, select and download an appropriate image
2. make the CM4 storage available as a disk on the desktop system
3. on the desktop system, write the image to this disk
4. boot the CM4 for the first time from eMMC and perform initial setup
5. perform CM4-specific configuration

Fedora has good [documentation for installing on a SBC](https://docs.fedoraproject.org/en-US/fedora-server/installation/on-sbc/), but it doesn't address stage 2 for the CM4, which has internal eMMC storage (except in the CM4 Lite version).

The normal Fedora approach for step 4 requires using an HDMI monitor and keyboard connected to the CM4 to do the initial setup, most importantly to setup a user account. You cannot just skip this, since the image does not allow ssh login without some configuration. However, it is possible to avoid the requirement to use an HDMI monitor and keyboard, if it is inconvenient or not possible for you for some reason (in my case, I wanted to install a Fedora 39 nightly image, but HDMI output wasn't working properly). This requires that step 3 be done using the arm-image-installer program, which is available only on Fedora; the arm-image-installer program has options that can configure the image to allow you to ssh in as root. This then requires that you need to use a desktop computer that is running Fedora.

After the above process is complete, you use make use of the Cockpit web administration interface by connecting to port 9090 on the CM4.

## Select and download the image

Fedora has three editions that could potentially be used with the CM4: Workstation, Server and IoT. This guide uses the Server edition, which is comparable to Raspberry Pi OS Lite.

To download, visit `https://getfedora.org/` on the desktop. Then

1. Follow the link to download Fedora server
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
3. Connect a USB port on your desktop to the Micro USB port on the CM4 IO board (to the right of the 2 USB A ports).
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

After `rpiboot`` exits, the CM4 should show up as a disk. You can run

```
udisksctl status
```

to find out which. The output should include a line like:

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

If you are using Fedora on your desktop, you can use `arm-image-installer`.

First, install it:
```
sudo dnf install arm-image-installer
```

Now, run it. The command looks something like this:
```
sudo arm-image-installer --target=rpi4 --image=Fedora-Server-38-1.6.aarch64.raw.xz   --media=/dev/sdX --addkey=/home/jjc/.ssh/id_ecdsa.pub --norootpass
```
You will need to adjust the command:
* you will always need `--target=rpi4` for the CM4
* the `--image` options specifies the image to write; it expects a compressed `.xz` image
* the `--media` specifies the device name where you made the CM4 storage available in the previous stage
* the `--addkey` and `--norootpass` options are only necessary if you want to be able to do initial setup using SSH rather than using a monitor and keyboard connected to the CM4

### Windows desktop

On Windows, [balenaEtcher](https://etcher.balena.io/) is convenient, because it can automatically decompress `.xz` files.

## First boot and initial setup

Before booting from eMMC for the first time, you obviously need to do either

- remove the jumper that disabled eMMC boot (for a CM4 with internal eMMC)
- insert the SD card (for a CM4 without an internal eMMC)

The offical Fedora documentation has a good description of the [normal setup](https://docs.fedoraproject.org/en-US/fedora-server/installation/on-sbc/#_basic_installation_and_configuration) process, which requires connecting an HDMI monitor or mouse.

If you have decided not to do that, then you need to have used the appropriate options with arm-image-installer when writing the image. You can then ssh in as root, and perform initial setup on the command-line as follows:

```
# Set the time zone. I use this.
timedatectl set-timezone Asia/Bangkok
# Set the hostname. I give my computers cheese names.
hostnamectl set-hostname pecorino
# We don't need to use the normal initial setup process.
systemctl disable initial-setup
# Add a user account. Here jjc is the user name.
groupadd jjc
useradd -g jjc -c "James Clark" -G wheel -m -u 1000 jjc
passwd jjc
```

TODO: NetworkManager setup (this can be done conveniently in Cockpit)

## CM4-specific setup

Fedora has some [documentation](https://fedoraproject.org/wiki/Architectures/ARM/Raspberry_Pi/HATs) on this. The serial port explanation didn't seem consistent with what I had understood about the serial ports from the official Raspberry Pi [documentation](https://www.raspberrypi.com/documentation/computers/configuration.html#configuring-uarts).

### Enable use of config.txt

To enable use of config.txt, we have to make Fedora use the firmware device tree rather than the kernel device tree. 

First, remove the /boot/dtb symbolic link:

```
sudo rm /boot/dtb
```

Next, create `/etc/u-boot.conf` with the line

```
FirmwareDT=True
```

TODO: I had some problems switching to use the firmware device tree. I think the solution is to power off, before rebooting. I also had problems switching back to use the kernel device tree.

### Modify config.txt

Add this at the bottom of `/boot/efi/config.txt`:

```
# Realtime clock
dtoverlay=i2c-rtc,pcf85063a,i2c_csi_dsi
# Fan controller
dtoverlay=i2c-fan,emc2301,i2c_csi_dsi
# Make the PL011 UART available on GPIO header pins 8 and 10 as /dev/ttyAMA0
# This also disables Bluetooth
dtoverlay=disable-bt
```

The fan controller needs the emc2305 module:

```
sudo modprobe emc2305
```

When the fan controller is recognized, you should see a file ` /sys/class/thermal/cooling_device0`

TODO: get the emc2305 module loaded automatically
