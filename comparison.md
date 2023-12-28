# Comparison

One method to compare the PTP sync performance in an end-to-end fashion is to observe the PHC time of the synced NIC and compare it against the PTP grandmaster using a scope.
Most if not all commercial PTP grandmaster do have a PPS output that can be used for that purpose. On the other end a NIC with configurable pins, such as the Intei i210 or the
Microship XYZ), can be used to measure the PHC's time.

## Test setup

The test setup comprises the PTP GM solution, the device under test (DUT), that shall be able to output a PPS signal. The PTP GM is connected over Ethernet, over which we
run the PTP protocol - to the PTP client that shall be able to output it's NICs PHC state over a programmable pin. 

Additionally, a third and independent PPS signal can be used to measure the initial offset of the DUT's PPS.
This is also helpful to later verify the PTP sync performance when then GPS sync is lost.

For the following measurements we've used an Intel i210 NIC and connected a scope to the SDP0 pin on the NIC. See [1] and [2] for additional details.
To enable the PPS output on the NIC we again use the `testptp` tool but with slightly different parameters as the i210 doesn't support the width argument.

```
# Configure SDP0 pin for periodic output
sudo ./testptp -d /dev/ptp0 -L 0,2
# Generate periodic pulse of width 500us
sudo ./testptp -d /dev/ptp0 -p 1000000000
```

The PPS logic in the driver generates a rectangular 1Hz signal on SDP0 with a positive and negative width of 500us. All signals are observed using a Siglent SDS1104X-E,
a four channel 100MHz oscillosope.

All components have been running for at least 24h to warm up. 


## Qulsar Qg 2 PTP grandmaster

We picked a Qulsar Systems Qg 2 as the DUT. The device is equipped with the default oscillator. We use
the latest firmware and use the factory configuration

The only modification was to enable the PPS output which is disabled by default.

### With GPS locked

The figure below shows the sync with the Qulsar as GM. The GMs PPS output is on channel 3. The PPT output of the PTP client is on channel 2.
Channel 4 is a reference GPSDO with PPS output. We trigger on a rising edge of channel 4 and observe the delay and jitter of the signals relative to it.

We can see that the jitter between the two (GPS-locked) PPS signals is approximtely 20ns after roughly 20mins of operating.

The jitter of the NICs PHC is even a bit larger, approx. 30ns.

![Alt text](qg2_gps_lcoked.png)








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

## Measure PPS output

If you have an oscilloscope, you can of course use that. Bear in mind that the PPS pulse width generated is much shorter than usual. (Typical PPS width from a GPS is 100ms, whereas this is 0.004ms.)

If you do not possess any suitable measuring equipment, the cheapest way to see the pulse is to use [sigrok](https://sigrok.org/wiki/Main_Page) with a cheap [Cypress FX2-based logic analyzer](https://sigrok.org/wiki/VKTECH_saleae_clone). These are available for about $10 on AliExpress: search for "USB 24MHz 8 channel logic analyzer".

The [TAPR TICC](https://tapr.org/product/tapr-ticc/) looks like a good option for doing much more precise measurements, at a relatively affordable price.



## References

[1] https://linuxptp.sourceforge.net/i210-rework/i210-rework.html
[2] https://pebblebay.com/qnx-ptp-pulse-per-second-output-on-the-intel-i210/