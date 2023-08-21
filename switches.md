# Inexpensive switches with PTP support

You can use PTP with normal network switches, but a switch with PTP support will improve the accuracy. There are plenty of expensive enterprise switches with PTP support. Inexpensive switches are less common.

## FS

FS have the IES3110 series. I own two of them:

* [IES3110-8TF](https://www.fs.com/products/138510.html), with a list price of US$279 ([Web UI manual](https://resource.fs.com/mall/file/user_manual/ies3110-8tf-and-ies3110-8tf-p-switches-configuration-guide.pdf), [CLI manual](https://resource.fs.com/mall/file/user_manual/ies3110-series-switches-cli-reference-guide.pdf))
* [IES3110-8TF-R](https://www.fs.com/products/148180.html), with a list price of US$159 ([Web UI manual](https://resource.fs.com/mall/doc/20230626110916xmfm0h.pdf), [CLI manual](https://resource.fs.com/mall/doc/20230424145026qmzzpt.pdf))

They both have 8 x 1Gb RJ45 ports and 2 x SFP ports. The major spec difference is that the SFP ports are 2.5Gb in the IES3110-8TF model and 1Gb in IES3110-8TF-R. However, the two models have significantly different firmware (and
distinct manuals). Most importantly for our purposes, the IES3110-8TF-R model has more complete PTP support, which allows the switch to work either as a transparent clock or a boundary clock, whereas the IES3110-8TF can only work as a transparent clock.

There are other models in the IES3110 series:
* the IES3110-8TF has a variant with PoE support, the IES3110-8TF-P, and also models with more ports; these all share the same manual
* the IES3110-8TF-R has a variant with PoE support, the IES3110-8TFP-R; these both share the same manual.

These switches are designed for industrial use. There's no fan (which is nice), but they don't come with a power supply or even an DC input jack (just a terminal block). I attached a DC power female pigtail and then used a spare 12V DC power supply.

The PTP support has to be enabled by adding a PTP clock from the PTP page in the Web UI, which is under Switching in the IES3110-8TF, and under Advanced Configure in the IES3110-8TF-R. You have to make sure that the clock uses the same transport you have configured for Linux PTP. For example, with the Linux PTP UDPv4 network transport, you have to choose the IPv4Multi protocol. I have been using a device type of E2e transp (i.e. transparent clock), which works with the default E2E delay mechanism of Linux PTP.

## Mikrotik

Some Mikrotik switches offer [PTP support](https://help.mikrotik.com/docs/display/ROS/Precision+Time+Protocol).
The cheapest is the CRS326-24G-2S, which has two variants:

- CRS326-24G-2S+RM, which is rack-mounted
- CRS326-24G-2S+IN, which is desktop

I own the RM version, but haven't yet properly tested it:

https://mikrotik.com/product/CRS326-24G-2SplusRM

List price is US$209.  It seems to be widely available: I was able to buy it from a local retailer in Thailand.

The ports are

- 1Gb RJ45 x 24
- 10Gb SFP+ x 2

As regards PTP support

* works as boundary clock
* does not support working as a transparent clock
* only the RJ45 ports have PTP support
* all ports have to have the same PTP profile
* has support for 802.1as

## MOTU

[MOTU AVB Switch](https://motu.com/en-us/products/avb/avb-switch/) has 5 ports and is $395 on [Amazon](https://www.amazon.com/MOTU-AVB-Switch-5-Port-Bridging/dp/B00M8IA7AU). However, it is designed specifically for Audio Video Bridging (AVB), and is not a general-purpose PTP switch.
