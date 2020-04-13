#!/usr/bin/env python2
import rtmidi

midi = rtmidi.MidiOut()
for dev in midi.get_ports():
    print(str(dev))
