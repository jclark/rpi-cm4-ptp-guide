# CM4-based computer

A CM4-based computer needs

* CM4 (or CM4Lite)
* Carrier board for the CM4
* Case for the carrier board and CM4 module
* microSD card (only if you are using a CM4Lite, which does not include eMMC storage)
* CR2032 coin cell battery for RTC 
* Power supply

The CM4 has been hard to buy for retail customers during 2022, unless you pay significantly above the recommended retail price. The [rpilocator](https://rpilocator.com/) site can help you find one.

The CM4 comes in many different configurations. Any configuration should work for our purposes

- RAM - 1Gb RAM should be enough, since we will not be installing a full desktop environment (I haven't tested less then 4Gb)
- eMMC storage - all the carrier boards have a micro SD card slot, so eMMC storage can be used but is not essential
- wifi - we won't be using wifi, because the antenna connector on the case is used for the GPS, but it doesn't hurt to have it

There are many carrier boards available for the CM4, but we need one that
gives access to the ethernet sync pins on the CM4, and there are only a few of those. There are two sync pins, called SYNC_OUT and SYNC_IN. But actually SYNC_OUT does both input and output, and is the one that matters. The choice of case depends on the carrier board.

All the boards discussed below include a battery-powered Real Time Clock (RTC), which is useful. You will need to buy a CR2032 battery for it, unless you get the Edatec case, which comes with a battery.

## Official Raspberry Pi CM4 IO board

The obvious choice is the [IO Board](https://www.raspberrypi.com/products/compute-module-4-io-board/) from the Raspberry Pi Foundation, which costs about $50. This is a good choice, if it's available.

There are three suitable cases for this board:

* [Waveshare case](https://www.waveshare.com/product/cm4-io-board-case-a.htm). There appear to be two versions of this. The newer version has a GPIO adapter that makes the 40-pin GPIO header available at the side. The older version does does.  This adapter gets would get in the way of an internal GPS unit; if it's not used, then there would be a hole in the side of the case.
* [Edatec case](https://www.edatec.cn/en/Product/Accessories/2021/0322/101.html)
* [Acrylic case](https://www.aliexpress.com/item/1005002085299389.html)

The Waveshare case has a significantly better fan than the Edatec case: it's 40mm fan and has PWM support, which makes the controller on the IO board. The Edatec case has a 25mm fan, which lacks PWM support.

The Waveshare case is also a few millimeters taller than the Edatec case, which makes it easier to fit an internal GPS unit.

The Edatec case comes with a Wifi antenna - but this isn't very useful, since we will be using the antenna hole on the case
for either the GPS antenna or a PPS signal.

The acrylic case is cheap, but there's no way to fit a GPS inside it. I find it convenient for experimenting.

You will also need a 12V DC power supply with a 5.5x2.1mm barrel connector: 2A is plenty since we are not using the PCIe slot.

## Waveshare boards

Waveshare make two boards that expose the sync pins. Each of these has its own case. You can buy the board without the case, but not vice-versa, so it makes to buy the board and case together.

* [PoE board and case](https://www.waveshare.com/product/cm4-io-poe-box-a.htm)
* [PoE board and case (Type B)](https://www.waveshare.com/product/cm4-io-poe-box-b.htm)

I have the first of these. Compared to the official IO board, it

- does not provide a PCIe slot
- provides 4 USB 3.0 ports
- can be powered over PoE
- supports a wide-range of DC input voltages

The board fits snugly in the case with no spare space on any side, which makes it a little bit more difficult to fit an internal unit in.  It's a good choice if you are using an external GPS. The extra USB ports are more useful than the PCIe slot for this application.

