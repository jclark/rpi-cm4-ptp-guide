# GPS configuration

For best results, you are likely to need to configure your GPS module.

At a minimum, you will need to ensure the baud rate is 9600, since the version of ts2phc in the Bullseye version of Raspberry Pi OS requires this.
For many GPS modules, 9600 is default. But some more recent modules have a higher default baud rate (e.g. RCB-F9T defaults to 115200).

## U-blox

U-blox provide the u-center application for configuring their modules.  This is available only on Windows.

My preferred solution is to use `ser2net` on the CM4 to make the serial connection available on a TCP port. You can then connect to that TCP port using u-center from a Windows machine.  To do this


```
sudo apt install ser2net
```

Then create a file `/etc/ser2net.yaml` containing:

```
---
connection: &con0
    accepter: tcp,2002
    enable: on
    connector: serialdev,/dev/ttyAMA0,9600n81,local
```

In the above, you will need to change 9600 to whatever your GPS module expects.

Alternatively, you can use a USB to TTL converter to temporarily connect the GPS module to a Windows machine, and then use u-center with the COM
port that this creates on Windows. This is OK for initial setup, but not so convenient after everything is installed.

Another possibility is to use gpsd's [ubxtool](https://gpsd.gitlab.io/gpsd/ubxtool.html). To install that, use

```
sudo apt install gpsd python3-gps
```

Then prevent gpsd from starting automatically (otherwise it will intefere with `ts2phc` later):

```
systemctl stop gpsd.socket gpsd.service
systemctl disable gpsd.socket gpsd.service
```

Note that gpsd will put the GPS module into a mode where it communicates using the binary UBX protocol rather than NMEA, which will cause
problems for other tools that expect the GPS module to be using NMEA. You can fix this by doing

```
gpsctl --nmea
```

before stopping gpsd.
