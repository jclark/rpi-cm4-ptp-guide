# Guide to using the hardware PTP support in the Raspberry Pi CM4

The Raspberry Pi Compute Module 4 (CM4) has hardware support for the Precision Time Protocol (PTP).
Kernel support became available recently (2022), and is discussed in https://github.com/raspberrypi/linux/issues/4151.

There's a useful introductory [blog](https://www.jeffgeerling.com/blog/2022/ptp-and-ieee-1588-hardware-timestamping-on-raspberry-pi-cm4) from Jeef Geerling and also a [video](https://www.youtube.com/watch?v=RvnG-ywF6_s).

This goal of this repository is to be a guide to taking advantage of this. There are two aspects:

* [hardware](hardware.md) - additional bits of hardware needed
* [software](software.md) - how to configure the needed software

## References

Fedora has great [docs](https://docs.fedoraproject.org/en-US/fedora/latest/system-administrators-guide/servers/Configuring_PTP_Using_ptp4l/) for PTP, although some details are different for Raspberry Pi OS, which is Debian-based.


