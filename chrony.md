# Configuring chrony

[Chrony](https://chrony-project.org/) is an NTP implementation, but it has the ability to take advantage of hardware support designed for PTP in two ways:

- it can read PPS input connected a pin of a PTP hardware clock (e.g. the SYNC_OUT pin on a CM4)
- it can use hardware timestamping

This page is written assuming [Fedora](fedora.md) as the OS.

## PPS input

Chrony can work fine with just the PPS signal from the GPS: the pulse says exactly when a second starts; chrony can figure out which second it is from network sources.

Before trying to get chrony working, it's a good idea to check that the kernel is seeing the PPS signal, which can be done
with these commands:

```
echo 1 0 | sudo tee /sys/class/ptp/ptp0/pins/SYNC_OUT
echo 0 1 | sudo tee /sys/class/ptp/ptp0/extts_enable
sudo cat /sys/class/ptp/ptp0/fifo
```

The last command should output a line, which represents a timestamp of an input pulse and consists of 3 numbers (channel number, which is zero in this case, seconds count, nanoseconds count). Repeating the last command will give lines for successive input pulses.

To use the PPS as a source of time, add this line to `/etc/chrony.conf`:

```
refclock PHC /dev/ptp0:extpps poll 0 precision 1e-7 refid PPS
```

To use chrony as a server in your network, you will also need something like:

```
allow 192.168.1.0/24
```

On Fedora, you will also need to add firewall rules:

```
sudo firewall-cmd --add-service ntp
sudo firewall-cmd --add-service ntp --permanent
```

Then restart chrony:

```
sudo systemctl restart chronyd
```


Check that it started OK:

```
sudo systemctl status chronyd
```

Now run

```
chronyc sources
```

It should should a line starting with `#* PPS`. This means it has successfully synced to the PHC refclock.

## Using serial connection from GPS

Connecting up the serial output from the GPS allows chrony to work even when there is no connection to any other NTP server.

First check that your GPS is producing output. You can do this with

Check serial connection to GPS

```
(stty 9600 -echo -icrnl; cat) </dev/ttyAMA3
```

(This is using `/dev/ttyAMA3` because Fedora has issues with `/dev/ttyAMA0`. With Raspberry Pi OS, you could use `/dev/ttyAMA0`.)

The most common default speed is 9600, but some receivers default to 38400.

Install gpsd:

```
sudo dnf install gpsd
```

Edit OPTIONS line in `/etc/sysyconfig/gpsd`:

```
OPTIONS="-n /dev/ttyAMA3"
```

GPSd is usually activated by a socket, but this isn't what we want. So:

```
sudo systemctl stop gpsd.socket
sudo systemctl disable gpsd.socket
sudo systemctl start gpsd.service
sudo systemctl enable gpsd.service
```

Now use

```
gpsmon
```

to check that gpsd is seeing the GPS. Use Ctrl-C to exit.

Now we can make chrony use this, by making the refclocks in `/etc/chrony/chrony.conf` look like this:

```
refclock PHC /dev/ptp0:extpps poll 0 precision 1e-7 refid PPS lock UART
refclock SOCK /run/chrony.clk.ttyAMA3.sock poll 3 offset 0.35 noselect refid UART
```

There's a lot packed into these two lines. Consider the refclock SOCK line first.
 * When gpsd starts reading from /dev/ttyX, it checks for the existence of the socket /run/chrony.clk.ttyX.sock; if this socket exists, then it will send the messages with the current date-time derived from messages received from the GPS over this socket.
 * The refclock SOCK line causes chrony to create the socket in the place where gpsd expects. Chrony will then read date-time messages from that.
  * The `refid UART` option gives the name `UART` to this reference clock.
 * The `offset 0.35` means that chrony should assume that there are 0.35 seconds delay between the instant when the second started and the instant when it receives the date-time message for that second through the socket. The figure of 0.35 will be depend on the hardware. You can adjust it so that the offset for UART refclock in `chronyc sources` is small.
 * The `noselect` option means that this refclock is not going to be used as a time source on its own: it's too inaccurate for that. (Instead it's going to be used to supplement the pulse-per-second signal.)

Now let's look at the `refclock PHC` line.
 * Usually the PHC (PTP Hardware Clock) refclock expects the PTP Hardware Clock to have been synchronized with PTP; the `extpps` option enables a different mode of operation, in which it reads thes timestamps of pulses on a pin on the PTP hardware clock; it defaults to pin 0, which is what we need.
 * `/dev/ptp0` is the device for the PTP hardware clock.
 * the `refid` option names this refclock `PPS`.
 * the `lock UART` option means that the pulse should be combined with the date-time from the UART refclock to provide a complete and accurate time sample.

Now

```
sudo systemctl restart chronyd
```

The /run/chrony.clk.ttyX.sock feature was added in gpsd 3.25. Before that, it supported only a /run/chrony.ttyX.sock, which works only for PPS data. If you're using a version of gpsd that does not support /run/chrony.clk.ttyX.sock, then you can instead use the SHM 0 refclock.

```
refclock SHM 0 poll 3 offset 0.35 noselect refid UART
```

## Hardware timestamping

*This isn't working reliably yet.*

The hardware on the CM4 cannot timestamp arbitrary packets: it can only timestamp PTP packets.
This means we have to use [NTP-over-PTP](https://datatracker.ietf.org/doc/draft-ietf-ntp-over-ptp/) in order to use hardware timestamping.
Reading the PTP hardware clock on the CM4 is unusually slow, so we need the
the `hwtstimeout` directive, which was added in chrony version 4.4 (released in August 2023).

We can configure this by adding the following lines to `/etc/chrony.conf`.

```
ptpport 319
# Ethernet interface is named end0 on Fedora.
hwtimestamp end0 rxfilter ptp
hwtstimeout 0.1
```

You will also need to add firewall rules to allow inbound traffic on the PTP port:

```
sudo firewall-cmd --add-service ptp
sudo firewall-cmd --add-service ptp --permanent
```

On the client side, you will need something like this:

```
server 192.168.1.2 minpoll 0 maxpoll 0 xleave port 319
hwtimestamp enp1s0 rxfilter ptp
ptpport 319
```

Chrony only supports NTP-over-PTP between server and client running the same versions of chrony.





