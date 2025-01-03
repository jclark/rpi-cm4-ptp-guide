# PPS measurement setup

## Enable PPS output

You can output a PPS signal driven by the PHC clock on the SYNC_OUT pin,
which you can then measure on an external device (e.g. oscilloscope or logic analyzer).

```
# Configure SYNC_OUT pin for periodic output
sudo ./testptp -d /dev/ptp0 -L 0,2
# Generate pulse of width 1us every second
sudo ./testptp -d /dev/ptp0 -p 1000000000 -w 1000
```
The `-p` argument gives the time between the start of each pulse in nanoseconds;
the only acceptable values are `1000000000`, meaning 1 second, and `0`, meaning
to stop generating pulses.
The `-w` argument gives the width of the pulse in nanoseconds; the maximum value, which is
also the default, is 4095, meaning just over 4 microseconds.

The RJ45 ethernet port should have a carrier (e.g. be plugged into a switch).

## Measure PPS output

If you have an oscilloscope, you can of course use that. Bear in mind that the PPS pulse width generated is much shorter than usual. (Typical PPS width from a GPS is 100ms, whereas this is 0.004ms.)

If you do not possess any suitable measuring equipment, the cheapest way to see the pulse is to use [sigrok](https://sigrok.org/wiki/Main_Page) with a cheap [Cypress FX2-based logic analyzer](https://sigrok.org/wiki/VKTECH_saleae_clone). These are available for about $10 on AliExpress: search for "USB 24MHz 8 channel logic analyzer".

The [TAPR TICC](https://tapr.org/product/tapr-ticc/) looks like a good option for doing much more precise measurements, at a relatively affordable price.

## Example setup

Here's a photo showing a measurement using the CM5 and an inexpensive oscilloscope (an FNIRSI 5014D). Note that on the CM5 the SYNC_OUT is on pin 6 (which the silkscreen incorrectly labels as USB_OTG). This is using a pigtail (15cm SMA bulkhead female to Dupont 2.54mm female bought from [AliExpress](https://www.aliexpress.com/item/1005006226703757.html)) with the Wifi antenna mounting hole on the CM5 IO board case to make the SYNC_OUT signal available outside the case.

![image](https://github.com/user-attachments/assets/5921d777-9a1c-4a1d-8a3b-d2fa47ff6901)



