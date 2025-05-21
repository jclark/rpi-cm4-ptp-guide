#!/bin/bash
. /etc/default/ptp4l-gm

# Wait for ptp4l UDS socket to appear
for i in {1..10}; do
  if [ -S /var/run/ptp4l ]; then
    break
  fi
  echo "Waiting for ptp4l to be ready..."
  sleep 0.5
done

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
                timeSource              0x20
"
