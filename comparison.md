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


![qg2_gps_locked](https://github.com/andrepuschmann/rpi-cm4-ptp-guide/assets/525775/d6e9e829-1e75-4826-a6b5-aa7960a5cd15)


### Without GPS lock

![qulsar_qg2_pps_drift_after_12h_no_lock](https://github.com/andrepuschmann/rpi-cm4-ptp-guide/assets/525775/cc015308-8186-4bee-94fd-36faeb16ba5e)






## References

[1] https://linuxptp.sourceforge.net/i210-rework/i210-rework.html
[2] https://pebblebay.com/qnx-ptp-pulse-per-second-output-on-the-intel-i210/
