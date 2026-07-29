# Verify GPS connections

Before setting up a time server, you should verify that the GPS is properly connected.
There are two connections:

* the serial connection, which carries the timing messages
* the PPS connection, which carries the pulse per second signal

This page uses only standard Linux commands.
[SatPulse](https://satpulse.net/) provides an easier way to do the same checks with
`satpulsetool gps` and `satpulsetool sdp`; see
[Verify serial connection to GPS module](https://satpulse.net/setup/gps-serial.html) and
[Precision timing with a PHC](https://satpulse.net/setup/phc.html).

## Serial connection

On a CM4 or CM5, assuming you have specified `dtoverlay=disable-bt` (see
[RPi UARTs](https://satpulse.net/setup/rpi-uart.html)) and you have connected the GPS
RX (white) and TX (green) pins to pins 8 and 10 respectively on the J8 HAT connector,
then the serial device will be `/dev/ttyAMA0`.

Do:

```
(stty 9600 -echo -icrnl; cat) </dev/ttyAMA0
```

where 9600 is the speed and `/dev/ttyAMA0` is the device.
The most common default speed is 9600, but some receivers default to 38400 or 115200.

You should see lines starting with `$`.
In particular look for a line starting with `$GPRMC` or `$GNRMC`. The number following that should be the current UTC time;
for example, `025713.00` means `02:57:13.00` UTC.
After another 8 commas, there will be a field that should have the current UTC date;
for example, `140923` means 14th September 2023.

## PPS connection

The PPS signal is timestamped by the PTP hardware clock (PHC) of a network interface,
so the first step is to identify the interface and its PHC device.

### Identifying the interface

On a CM4 or CM5, the interface is `eth0`. On a PC with an Intel NIC, the command

```
ls -l /sys/class/net/*/device/driver/module | grep 'ig[cb]'
```

will show the interfaces that have igb (for i210) or igc (for i225/i226) as their driver.

For example, on one of my machines, it shows

```
lrwxrwxrwx 1 root root 0 Sep 13 16:48 /sys/class/net/enp4s0/device/driver/module -> ../../../../module/igc
lrwxrwxrwx 1 root root 0 Sep 13 16:48 /sys/class/net/enp5s0/device/driver/module -> ../../../../module/igc
```

This tells me that I have interfaces enp4s0 and enp5s0 using the igc driver.

### Identifying the PHC for an interface

You can identify the PHC device for an interface using `ethtool -T`.

For example, on a CM4 or CM5

```
ethtool -T eth0
```

should show:

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
its PHC device.

If you don't get this, then your kernel probably lacks the necessary support.

### Ensure interface is up

Make sure the interface is in an UP state. For example:

```
ip link show eth0
```

If it's not up, then bring it up with

```
sudo ip link set eth0 up
```

### Verify PPS input

Now you know the PHC device, you can check if PPS input is working.
Assuming the PHC device is ptp0, you can see what pins it has with

```
ls /sys/class/ptp/ptp0/pins
```

To verify that the PPS connection is working on one of the pins, for example SYNC_OUT,
first configure that pin for input:

```
echo 1 0 | sudo tee /sys/class/ptp/ptp0/pins/SYNC_OUT
```

`SYNC_OUT` here is the name of the pin to which the PPS is connected.
In the `echo 1 0`, 1 means to use the pin for input and 0 means the pin should use input channel 0.

Now do:

```
echo 0 1 | sudo tee /sys/class/ptp/ptp0/extts_enable
```

This means to enable timestamping of pulses on channel 0.
In the `echo 0 1`, 0 means channel 0 and 1 means to enable timestamping.

Now see if we're getting timestamps:

```
sudo cat /sys/class/ptp/ptp0/fifo
```

The `cat` command should output a line, which represents a timestamp of an input pulse and consists of 3 numbers: channel number, which is zero in this case, seconds count, nanoseconds count. Repeating the last command will give lines for successive input timestamps.

If `cat` outputs nothing, then it's not working.
