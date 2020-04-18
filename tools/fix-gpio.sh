#!/usr/bin/env bash
# bring all gpio to input and pulldown
# Fixes this error:  This channel is already in use, continuing anyway.

for gpio in $(seq 2 27); do
  echo "$gpio" > /sys/class/gpio/export
done
