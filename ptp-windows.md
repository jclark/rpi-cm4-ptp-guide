# PTP client support on Windows

Windows 10 v1809 includes a PTP client. This has been enhanced in Windows 11. The support for PTP in Windows is not as functional and mature as the support in Linux. 

There is a [Validation Guide](https://github.com/microsoft/W32Time/tree/master/Precision%20Time%20Protocol/docs) from Microsoft, which explains in detail how to enable it.

The client supports only the UDP transport and two-step mode, which matches the default for Linux PTP. However, it requires the `currentOffsetUtcValid` flags  to be 1 in the grandmaster settings.  You can set this with `pmc` on the Raspberry Pi. I use the following shell script:

```
#!/bin/sh
pmc -u -b 0 \
"set GRANDMASTER_SETTINGS_NP
        clockCss              6
        clockAccuracy           0x20
        offsetScaledLogVariance 0xffff
        currentUtcOffset        37
        leap61                  0
        leap59                  0
        currentUtcOffsetValid   1
        ptpTimescale            1
        timeTraceable           0
        frequencyTraceable      0
        timeSource              0xa0
"
```

Then to configure the client open an Administrator PowerShell and do the following steps.

1. [Configure](https://github.com/microsoft/W32Time/blob/master/Precision%20Time%20Protocol/Windows%20Configuration%20Helpers/PTPFirewall.txt) the firewall to open the necessary ports

2. Add some [registry keys](https://github.com/microsoft/W32Time/blob/master/Precision%20Time%20Protocol/Windows%20Configuration%20Helpers/PTPClientConfig.txt). Also enable MulticastTx `reg add HKLM\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\PtpClient /t REG_DWORD /v MulticastTxEnabled /d 1`.

3. On Windows 11, you can now use `w32time /ptp_monitor /duration:10` to check that you are receiving PTP packets correctly. If this doesn't work, then PTP won't work. Unfortunately, there seems to be a bug that stops PTP working with some drivers. (It works on one of my network adapters but not the others). Other people have had a similar [issue](https://github.com/microsoft/SDN/issues/438). I haven't found a workaround other than to use another adapter.

4. Now restart the time service. Using `stop-service w32time` and then `start-service w32time`.

5. Now use `w32time /query /status /verbose` to see if everything's working. You can also use Event Viewer to look at  `Applications and Services > Microsoft > Windows > Time-Service-PTP-Provider > PTP-Operational`.

Also set the Windows Time service Startup Type to Automatic.

I have not found many Windows drivers with support for hardware timestamps. The Intel E1R driver used for I210, I211, and I350 has [support](https://www.intel.com/content/www/us/en/support/articles/000033862/ethernet-products.html).

