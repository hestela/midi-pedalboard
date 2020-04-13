#!/usr/bin/env bash
# bring all gpio to input and pulldown

for gpio in $(seq 2 27); do
  echo "$gpio" > /sys/class/gpio/export
done
