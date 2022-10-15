# CM4-based computer

This page discusses the parts needed to create a CM4-based computer: 

* CM4
* Carrier board for the CM4
* Case for the carrier board and CM4 module
* Power supply

The case depends on the carrier board, so we will discuss those together.

The most restrictive constraint on the carrier board is that it needs to expose the ethernet sync pin on CM4. There are two sync pins, called SYNC_OUT and SYNC_IN. But actually SYNC_OUT does both input and output, and is the one that matters.

All the boards includes a battery-powered Real Time Clock (RTC), which is useful.  You will need to buy a CR2032 battery for it, unless you get the Edatec case, which comes with a battery.

## Official Raspberry Pi CM4 IO board

The obvious choice is the [IO Board](https://www.raspberrypi.com/products/compute-module-4-io-board/) from the Raspberry Pi Foundation, which costs about $50. This is a good choice, if it's available.

There are two suitable cases for this board:

* [Waveshare case](https://www.waveshare.com/product/cm4-io-board-case-a.htm). There appear to be two versions of this. The newer version has a GPIO adapter that makes the 40-pin GPIO header available at the side. The older version does does.  This adapter gets would get in the way of an internal GPS unit; if it's not used, then there would be a hole in the side of the case.
* [Edatec case](https://www.edatec.cn/en/Product/Accessories/2021/0322/101.html)

The Waveshare case has a significantly better fan than the Edatec case: it's 40mm fan and has PWM support, which makes the controller on the IO board. The Edatec case has a 25mm fan, which lacks PWM support.

The Waveshare case is also a few millimeters taller than the Edatec case, which makes it easier to fit an internal GPS unit.

The Edatec case comes with a wifi antenna - but this isn't very useful, since we will be using the antenna hole on the case
for either the GPS antenna or a PPS signal.

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

