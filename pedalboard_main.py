#!/usr/bin/env python2
from __future__ import print_function
import RPi.GPIO as GPIO
import time
from functools import partial
from midi_classes import MidiUtil, MidiError
from callbacks import State, ButtonCallback, midi_callback

gpio_in = range(2, 12)
gpio_out = [12, 13, 16, 17] + list(range(22, 28))


def setup_gpio(system_state):
    callback = ButtonCallback()
    f = partial(callback, system_state)

    # set the Pi to reference the GPIOs with the BCM convention
    GPIO.setmode(GPIO.BCM)

    # Setup all pins, create states for input pins
    # FIXME: gpio/index is swapped, pull up resister on chan 2/ind 4
    for index, gpio in enumerate(gpio_in):
        GPIO.setup(gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(gpio, GPIO.FALLING,
                              callback=f, bouncetime=300)
        callback.gpio_to_button[gpio] = index
    for gpio in gpio_out:
        GPIO.setup(gpio, GPIO.OUT, initial=GPIO.LOW)


def main():
    # This list keeps track of the song setup the pedal is currently using
    curr_song = 0

    try:
        # Fill out song/button info
        songs, controllers, modules = MidiUtil.parse_conf_file('dummy.txt')

        # State machine initialize
        system_state = [State.button_0]
        curr_led_on = gpio_out[0]
        setup_gpio(system_state)

        # Midi callback, with defaults
        # FIXME: depends on setup from config
        # FIXME: remove hardcoded module names
        # FIXME: just using the first controller for now
        initial_button = songs[0].buttons[0]
        controllers['reface'].set_callback(midi_callback, initial_button)

        # State Machine
        # TODO Add if statements to handle bank buttons
        while True:
            # Idle state
            if system_state[0] == State.idle:
                time.sleep(0.0002)
                continue

            # Get button index from system_state
            button_index = system_state[0].value - 1
            gpio_pin = gpio_out[button_index]

            # Turn on respective LED, turn off last LED
            GPIO.output(curr_led_on, GPIO.LOW)
            GPIO.output(gpio_pin, GPIO.HIGH)
            curr_led_on = gpio_pin

            # Excecute through action sequence associated with button
            curr_button = songs[curr_song].buttons[button_index]
            for msg in curr_button.midi_msgs:
                modules[msg['name']].send_message(msg['msg'])

            controllers['reface'].set_callback(midi_callback, curr_button)

            # Return system state to Idle
            system_state[0] = State.idle

    except MidiError as e:
        print(e.value)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        GPIO.cleanup()
    except RuntimeError:
        print("PortNumber for rtmidi is invalid, quitting")


if __name__ == '__main__':
    main()
