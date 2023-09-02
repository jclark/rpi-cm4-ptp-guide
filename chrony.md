# Configuring chrony

## Getting started

Initially I recommend you just wire up the PPS output and the GND from the GPS receiver. Don't worry yet about the serial connection. The PPS output says exactly when a second starts; chrony can figure which second it is from network sources.

Before trying to get chrony working, it's a good idea to check that the kernel is seeing the PPS signal, which can be done
with these commands:

```
echo 1 0 | sudo tee /sys/class/ptp/ptp0/pins/SYNC_OUT
echo 0 1 | sudo tee /sys/class/ptp/ptp0/extts_enable
sudo cat /sys/class/ptp/ptp0/fifo
```

The last command should output a line, which represents a timestamp of an input pulse and consists of 3 numbers (channel number, which is zero in this case, seconds count, nanoseconds count). Repeating the last command will give lines for successive input pulses.

Add this line to `/etc/chrony.conf`:

```
refclock PHC /dev/ptp0:extpps poll 0 precision 1e-7
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

It should should a line starting with `#* PHC0`. This means it has successfully synced to the PHC refclock.

## Using serial connection from GPS

Approach is to use gpsd with a chrony SOCK refclock.

## Hardware timestamping

TODO: use chrony's NTP-in-PTP feature.



