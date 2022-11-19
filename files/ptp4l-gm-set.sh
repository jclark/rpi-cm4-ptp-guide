#!/bin/bash
. /etc/default/ptp4l-gm
/usr/sbin/pmc -u -b 0 \
"set GRANDMASTER_SETTINGS_NP
		clockClass              6
                clockAccuracy           $CLOCK_ACCURACY
                offsetScaledLogVariance 0xffff
                currentUtcOffset        $UTC_OFFSET
                leap61                  0
                leap59                  0
                currentUtcOffsetValid   1 
                ptpTimescale            1
                timeTraceable           1
                frequencyTraceable      0
                timeSource              0xa0
"
