# CM4/CM5-based computer

A computer based on the CM4 or CM5 includes

* the compute module itself (a CM4 or CM5)
* a carrier board
* a case for the carrier board and compute module
* additional storage; this is needed only when using the CM4Lite or CM5Lite variants of the compute module, which do not have onboard eMMC storage; it can be either
	* a microSD card, which works only with the CM4Lite or CM5Lite, or
	* an M.2 NVMe SSD, which works only with the CM5, including the CM5Lite
* CR2032 coin cell battery for RTC 
* a power supply

The CM4/CM5 come in many different configurations. Any configuration should work for our purposes

- RAM - 1Gb RAM should be enough, since we will not be installing a full desktop environment (I haven't tested less then 4Gb)
- eMMC storage - all the carrier boards have a micro SD card slot, so eMMC storage can be used but is not essential
- wifi - we won't be using wifi, because the antenna connector on the case is used for the GPS, but it doesn't hurt to have it

There are many carrier boards available for the CM4/CM5, but we need one that
gives access to the SYNC_OUT pin, and there are only a few of those. On the CM4, there are two sync pins, called SYNC_OUT and SYNC_IN, but actually SYNC_OUT does both input and output, and is the one that matters. On the CM5, there is only a SYNC_OUT pin.

The CM4 and CM5 have the same form factor and it is possible to use the CM5 with cases designed for the CM4 and vice-versa,
but what will and will not work is not clearly documented, so I recommend not doing this.

The choice of case depends on the carrier board.

All the boards discussed below include a battery-powered Real Time Clock (RTC), which is useful. You will need to buy a CR2032 battery for it, unless you get the Edatec case, which comes with a battery.

## CM4 carrier boards and cases

### Official Raspberry Pi CM4 IO board

The obvious choice is the [CM4 IO Board](https://www.raspberrypi.com/products/compute-module-4-io-board/) from the Raspberry Pi Foundation, which costs about $50. This is a good choice, if it's available.

There are three suitable cases for this board:

* [Waveshare case](https://www.waveshare.com/product/cm4-io-board-case-a.htm). There appear to be two versions of this. The newer version has a GPIO adapter that makes the 40-pin GPIO header available at the side; the older version does not.  This adapter would get in the way of an internal GPS unit; if it's not used, then there would be a hole in the side of the case.
* [Edatec case](https://www.edatec.cn/en/Product/Accessories/2021/0322/101.html)
* [Acrylic case](https://www.aliexpress.com/item/1005002085299389.html)

The Waveshare case has a significantly better fan than the Edatec case: it's a 40mm fan and has PWM support, which matches the controller on the IO board. The Edatec case has a 25mm fan, which lacks PWM support.

The Waveshare case is also a few millimeters taller than the Edatec case, which makes it easier to fit an internal GPS unit.

The Edatec case comes with a Wifi antenna - but this isn't very useful, since we will be using the antenna hole on the case
for either the GPS antenna or a PPS signal.

The acrylic case is cheap, but there's no way to fit a GPS inside it. I find it convenient for experimenting.

You will also need a 12V DC power supply with a 5.5x2.1mm barrel connector: 2A is plenty since we are not using the PCIe slot.

### Waveshare boards

Waveshare make two boards that expose the sync pins. Each of these has its own case. You can buy the board without the case, but not vice-versa, so it makes to buy the board and case together.

* [PoE board and case](https://www.waveshare.com/product/cm4-io-poe-box-a.htm)
* [PoE board and case (Type B)](https://www.waveshare.com/product/cm4-io-poe-box-b.htm)

I have the first of these. Compared to the official IO board, it

- does not provide a PCIe slot
- provides 4 USB 3.0 ports
- can be powered over PoE
- supports a wide-range of DC input voltages

The board fits snugly in the case with no spare space on any side, which makes it a little bit more difficult to fit an internal unit in.  It's a good choice if you are using an external GPS. The extra USB ports are more useful than the PCIe slot for this application.

## CM5 carrier boards and cases

### Official Raspberry Pi CM5 IO board

The obvious choice is the official [CM5 IO Board](https://www.raspberrypi.com/products/compute-module-5-io-board/) from the Raspberry Pi Foundation, which costs about $25. It includes a slot for an M.2 NVMe SSD.

There is also an official matching [case](https://www.raspberrypi.com/products/io-case-cm5/), which I would recommend getting as well. The case comes with a fan, but you can also buy an official [heatsink](https://www.raspberrypi.com/products/cooler/), which can be used instead of the fan and gives a quieter system.

### Waveshare CM5 PoE board

Waveshare make a [carrier board](https://www.waveshare.com/product/raspberry-pi/boards-kits/cm5/cm5-poe-base-a.htm), which is also available as a mini-computer kit that includes a case and a power supply. This supports PoE.

It includes a 40-pin GPIO adapter, which makes the Raspberry Pi 40-pin header available outside the case. This makes it easy to connect it to a GPS board outside the case. If you want to put the GPS board in the case, then you can remove this adapter, but this leaves a hole in the case.

### Power supply

The above carrier boards all require a USB PD power supply.

They can make use of a 5V5A power profile and Raspberry Pi have an official [27W USB C power supply](https://www.raspberrypi.com/products/27w-power-supply/) that can provide this. Only a few 3rd party power supplies support this. One example is from [Radxa](https://docs.radxa.com/en/accessories/pd_30w); this has a separate cable, folding prongs, and separate side-on plug adapters for European and UK sockets. Note that 5V5A as a PPS does not work: a fixed PDO is necessary.

However, in practice, I have found a 5V3A power supply to be plenty when using a CM5 as a time server.


