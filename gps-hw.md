# GPS receiver

This discusses solutions for connecting a GPS receiver solutions that satisfy the following constraints.

* The Pulse Per Second (PPS) signal is connected to the CM4 NIC.
* Everything is nicely contained in a case.
* No DIY (no tools needed other than a screwdriver: no soldering, no crimping, no 3D printing)

The cases all have a hole that is designed to work with the [official antenna kit](https://www.raspberrypi.com/products/compute-module-4-antenna-kit/), which uses an SMA female bulkhead connector.
The CM4 SYNC_OUT pin can be connected in two ways:

* external: the SYNC_OUT signal on the carrier board can be exposed using an SMA connector on the case, and then, either
   * an external GPS receiver can be connected to the SMA connector on the case and to a USB port on te case
   * the SMA connector on the case can be connected to a device to measure the PPS signal
* internal: a GPS module can be mounted in the case containing the CM4, with the PPS pin connected to the SYNC_OUT pin and the TX/RX pins connected to the GPIO header

Note that the silkscreen on official CM5 IO board does not correctly label the SYNC_OUT pin: SYNC_OUT is pin 6 not pin 9 on the J2 jumpers.

## External

### SMA connector for SYNC_OUT

There are two ways to expose the SYNC_OUT signal using an SMA connector on the case:

* Use a cable that is an SMA female bulkhead connector on one end and a pair of Dupont female connectors on the other; this is available on eBay
* Use a [purpose-built board](https://store.timebeat.app/products/raspberry-pi-cm4-1pps-breakout-board) from Timebeat that exposes the pins on the IO board as a U.FL connector and then use a pigtail to connect that to a SMA connector on the case. Note that the pigtail needed here is not the same as the pigtail that comes with the official antenna kit. That uses an RP-SMA connector (suitable for wifi antennas); but we need a SMA connector (suitable for GPS/coaxial antennas).

We then need a external GPS receiver than can provide
- a serial connection through USB, and
- a PPS signal through the SMA connector

### GPS disciplined oscillator

There are a number of GPS disciplined oscillators available. One inexpensive Chinese model is the BG7TBL, which is widely available on AliExpress and eBay. This provides

- a PPS signal on a BNC connector: this needs an BNC male to SMA male cable
- a serial signal with NMEA data on a DB9 connector: this needs a RS232 DB9 male to USB A cable

The version I bought ([AliExpress](https://www.aliexpress.com/item/4001022596521.html)) is based on a u-blox M8030 chip.

### USB GPS module

(I haven't tried this.)

[GNSS store](https://www.gnss.store/) has a ZED-F9T packaged as a USB dongle with two SMA connectors (one for the antenna and one for PPS). There are two variants:

* [L1/L2 version](https://www.gnss.store/zed-f9t-timing-gnss-modules/108-ublox-zed-f9p-rtk-gnss-receiver-board-with-sma-base-or-rover.html)
* [L1/L5 version](https://www.gnss.store/zed-f9t-timing-gnss-modules/166-elt0147.html)

Downside is that it's expensive.

## Internal

### Timebeat CM4 module

This is a [purpose built module](https://store.timebeat.app/products/gnss-raspberry-pi-cm4-module) from Timebeat designed for use with the CM4. There aren't a lot of details on the Web page, but there is some [information](https://github.com/opencomputeproject/Time-Appliance-Project/tree/master/RPi-Timing/Time4CM4/Baseboard) for a slightly different version in the Time Appliance Project of the Open Compute Project (initiated by Facebook).

This has a unique form factor. It is a board that is interposed between the CM4 and the carrier board. This allows it to connect the CM4 pin for SYNC_OUT to LEA-M8F PPS out, and the LEA-M8F TX/RX into the CM4 UART TX/RX pins. This gives the simplest possible installation, with no jumper wires required. It also opens up the possibility of using carrier boards that do not expose the SYNC_OUT pin, but this is limited by the protrusion on the left for the SIT modules. In particular, it won't work with the Waveshare PoE board.

The LEA-M8F version, in particular, looks to me like the best solution for professional use. The LEA-M8F has some unique capabilities for holdover. The CM4 module allows the holdover capabilities to be dramatically enhanced by adding an SiT5711/5721; these are high performance OCXOs, in a small form-factor, with low power consumption, using MEMS technology.

### Mini double-sided form factor

On eBay and AliExpress there are many boards available that look like this. They seem to be intended for the Arduino market. They cost about $10.

![image](https://user-images.githubusercontent.com/499966/196853721-5315eba8-4fab-42ce-a54d-d6c02dc5e005.png)
![image](https://user-images.githubusercontent.com/499966/196853749-36751c30-d23c-4ace-a4c3-310d63a8d710.png)

Most of the ones being sold pretend to be u-blox modules, but aren't. The ones I have all use modules from [Zhongke Microelectronic](https://www.icofchina.com/).  So I think it's better to use one that honestly says what it is. This [ATGM332D](https://www.aliexpress.com/item/1005004402839841.html) from the Wavgat store worked well for me.

These can be mounted inside a case easily by using a single M2.5 standoff in the rear left hole of the IO board. Then you can wire it up with Dupont jumpers, and a SMA-IPEX pigtail.

![image](https://user-images.githubusercontent.com/499966/196886374-44272133-6a1d-4186-9a4b-4c521b167b88.png)

### Telecom form-factor

There are a variety of boards available that use a form-factor originally designed for use in the telecom industry in cellular base stations. This form factor has

* a SMB male (jack) antenna connector
* an 8-pin connector with 2 rows of 4 pins with a 2.0mm pitch; pins are 0.5mm square
* 4 mounting holes in the PCB with a spacing of 26x60.5mm

Mostly these use u-blox modules. The most recent of these is the u-blox [RCB-F9T](https://www.u-blox.com/en/product/rcb-f9t-timing-board), which is avaiable from [Mouser](https://www.mouser.com/ProductDetail/u-blox/RCB-F9T-0?qs=ljCeji4nMDkDS2PT5ijKCg%3D%3D) and [Digikey](https://www.digikey.com/en/products/detail/u-blox/RCB-F9T/12090682). This is expensive at USD$247. There are two variants

* RCB-F9T-0 - this is the original model and supports the L2 band as well as the normal L1 band
* RCB-F9T-1 - this is a newer model and supports the new L5 band (but not the L2 band) as well as the normal L5 band

However, there are much cheaper boards available on eBay that use the same form factor but older modules

* [u-blox LEA-M8T](https://www.ebay.com/itm/333619130232) - $50
* [u-blox LEA-6T](https://www.ebay.com/itm/134203045552) - $15
* [u-blox LEA-5T](https://www.ebay.com/itm/134203047949) - $12
* [Trimble 66266-45](https://www.ebay.com/itm/134243323986) - $9

Most of the modules on eBay seem to have been manufactured for use with a Huawei base stations (specifically to plug into the UMPT unit of a BBU3900 series). There are a lot of u-blox fakes on eBay, but this form factor does not appear to be a popular target
for fakes.

A board in this form factor needs two cables to connect it:

* a cable that plugs into the antenna connector on the board and attaches to the antenna hold in the case: this needs a SMB female (plug) to SMA female bulkhead pigtail; ideal length is about 15cm; and straight works better than right-angled
* a cable to connect from the pins on the board to the pins on the IO board: you can buy a 20cm cable consisting of a strip of 40 wires, with one end having 2.54mm Dupont 1-pin female connectors and the other end having 2.0mm 2-pin female Dupont connectors [AliExpress](https://www.aliexpress.com/item/32872192805.html), [AdaFruit](https://www.adafruit.com/product/1919), [eBay](https://www.ebay.com/itm/253963096627)

The pins need to be connected as follows:

| GPS pin no | u-blox pin name | IO header | header pin no | header pin name | description |
| --- | --- | --- | --- | --- | --- |
| 1 | VCC_ANT | HAT | 2 | 5V | Antenna power |
| 2 | VCC | HAT | 1 | 3V3 | Operating power for GPS |
| 3 | TXD | HAT | 10 | UART0_RXD | GPS to CM4 |
| 4 | RST | HAT |  | | Reset - not connected |
| 5 | RXD | HAT | 8 | UART0_TXD | CM4 to GPS |
| 6 | TP1 | J2 | 9 | SYNC_OUT | Time pulse |
| 7 | TP2 | HAT | 12 | GPIO18 | Time pulse 2 - only on RCB-F9T |
| 8 | GND | HAT | 6 or 14 | GND | Ground |

Pin 1 supplies power to the antenna; the precise range of allowed voltages depends on the board. All boards appear to accept a range of 3.3-5V.

We also need to mount the board within the case. This can be done by using the holes in the board to attach the board to the inside top of the case. It fits best over the area next to the GPIO header, which is designed to be used for a Raspbery Pi Hat, facing down, with the antenna connector facing inwards. To do this we need 4 PCB mounts suitable for M3 or M2.5 holes There are two kinds available:

* nylon PCB standoff with an adhesive base and a post that pushes through the PCB hole
* a metal stand with a magnetic base and a post threaded to accept an M3 screw; you can find these on AliExpress by searching for "M3 magnetic screw" (they seem to be mostly designed for used with LED light fittings)

Both kinds are available in a range of heights. A height of around 5mm is ideal. Things get tighter and more awkward with taller
stands. But 12mm stands work with the official IO board and Waveshare case (which has extra space on the left side).

I like the magnetic ones better. They attach very firmly and can be easily removed when needed.  I have used magnetic ones that are 12mm high, which I purchased [here](https://th.cytron.io/p-m3-pcb-stand-with-magnet-female-13x12mm). I have some [shorter ones](https://www.aliexpress.com/item/32858048503.html) on order. I am currently using a support that combines a 10x3mm magnet with a countersunk M3 hole ([AliExpress}(https://www.aliexpress.com/item/1005002932284493.htm)), a M2.5 4mm countersunk screw, a M2.5 5mm nylon spacer, and a M2.5 4mm nylon pan head screw. (I found that an M3 countersunk screw wasn't completely flush.)

![image](https://user-images.githubusercontent.com/499966/194740152-2782eff4-5990-4798-9cb2-7234b29dc3fe.png)

![image](https://user-images.githubusercontent.com/499966/196852504-f2f5c5d3-2563-40eb-bf34-1ff9bd247e5b.png)






