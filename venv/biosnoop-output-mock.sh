#!/bin/bash

## NOTE: This script was created to imitate BCC BIOSNOOP script output in ...
## ... order to debug the parsing.

# NOTE: Generating random number for IO statistics imitating
RANDOM=$$

biosnoopScriptHeading="TIME(s)     COMM           PID    DISK    T SECTOR     BYTES   LAT(ms)"
echo $biosnoopScriptHeading

while true
do
  for i in $(seq 1 1 45)
  do
    time=$((i*RANDOM))
    echo $time
    processId=$i
    latency=$((RANDOM/i))
    bytes=$((RANDOM*i*time))
    sector=$((RANDOM*time*time*i))
    echo "${time}    supervise      ${processId}   xvda1   W ${sector}   ${bytes}       ${latency}"
  done
done

