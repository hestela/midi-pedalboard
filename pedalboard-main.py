#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
import rtmidi
from functools import partial

class state_obj():
    def __init__(self):
        self.curr_state = 0
        self.last_msg_sent = 1

def main():
    try:
        midiout = rtmidi.MidiOut()

        # FIXME hardcoded '2' for microKORG XL
        midiout.open_port(2)

        GPIO.setmode(GPIO.BCM)

        # GPIO 24 set up as an input, pulled down, connected to 3V3 on button press
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # now we'll define two threaded callback functions
        # these will run in another thread when our events are detected
        def button_callback(state, channel):
            if state.last_msg_sent == 1:
                state.curr_state = 2
            elif state.last_msg_sent == 2:
                state.curr_state = 1

        state = state_obj()
        f = partial(button_callback, state)

        # when a rising edge is detected on gpio 4, regardless of whatever
        # else is happening in the program, the function my_callback will be run
        GPIO.add_event_detect(4, GPIO.RISING, callback=f, bouncetime=300)

        msg_one = [192, 5]
        msg_two = [192, 57]

        while True:
            if state.curr_state == 0:
                time.sleep(0.0002)
            elif state.curr_state == 1:
                # send midi message 1
                midiout.send_message(msg_one)
                state.last_msg_sent = 1
                state.curr_state = 0
            elif state.curr_state == 2:
                # send midi message 2
                midiout.send_message(msg_two)
                state.last_msg_sent = 2
                state.curr_state = 0

    except KeyboardInterrupt:
        GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    GPIO.cleanup()


if __name__ == '__main__':
    main()
