# Inexpensive switches with PTP support

You can use PTP with normal network switches, but a switch with PTP support will improve the accuracy. There are plenty of expensive enterprise switches with PTP support. Inexpensive switches are less common.

## FS

FS have the IES3110 series. I have the [IES3110-8TF](https://www.fs.com/products/138510.html), which has 8 x 1Gb RJ45 ports and 2 x 2.5Gb SFP ports, and costs $279. There is a cheaper model: the [IES3110-8TF-R](https://www.fs.com/products/148180.html) has 1Gb SFP ports and costs $159, but is out of stock until Jan 2023. There are also more expensive variants with PoE support and/or more ports.

It's designed for industrial use. There's no fan (which is nice), but it doesn't come with a power supply or even an DC input jack (just a terminal block). I attached a DC power female pigtail and then used a spare 12V DC power supply.

The PTP support has to be enabled by adding a PTP clock from the PTP page in the Web UI, which is under Switching. You have to make sure that the clock uses the same transport you have configured for Linux PTP. For example, with the Linux PTP UDPv4 network transport, you have to choose the IPv4Multi protocol. I have been using a device type of E2e transp (i.e. transparent clock), which works with the default E2E delay mechanism of Linux PTP. The [manual](https://resource.fs.com/mall/file/user_manual/ies3110-8tf-and-ies3110-8tf-p-switches-configuration-guide.pdf) has the details.

## Motu

[Motu AVB Switch](https://motu.com/en-us/products/avb/avb-switch/) which has 5 ports and is $395 on [Amazon](https://www.amazon.com/MOTU-AVB-Switch-5-Port-Bridging/dp/B00M8IA7AU).
