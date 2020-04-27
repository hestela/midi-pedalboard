#!/usr/bin/env python2
from __future__ import print_function
import RPi.GPIO as GPIO
import time
from functools import partial
from midi_classes import MidiUtil, MidiError
from callbacks import State, ButtonCallback, midi_callback


def setup_gpio(system_state, gpio_in, gpio_out):
    callback = ButtonCallback()
    f = partial(callback, system_state)

    # set the Pi to reference the GPIOs with the BCM convention
    GPIO.setmode(GPIO.BCM)

    # Setup all pins, create states for input pins
    for index, gpio in enumerate(gpio_in):
        GPIO.setup(gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(gpio, GPIO.FALLING,
                              callback=f, bouncetime=170)
        callback.gpio_to_button[gpio] = index
    for gpio in gpio_out:
        GPIO.setup(gpio, GPIO.OUT, initial=GPIO.LOW)


def main():
    # This list keeps track of the song setup the pedal is currently using
    curr_song = 0

    try:
        # Fill out song/button info
        songs, controllers, modules, hw_info = MidiUtil.parse_conf_file()

        # State machine initialize
        system_state = [State.button_0]
        curr_led_on = hw_info['gpio_out'][0]
        setup_gpio(system_state, hw_info['gpio_in'], hw_info['gpio_out'])
        num_songs = len(songs)

        # Midi callback, with defaults
        # FIXME: depends on setup from config
        # FIXME: remove hardcoded module names
        # FIXME: just using the first controller for now
        initial_button = songs[0].buttons[0]
        controllers['reface'].set_callback(midi_callback, initial_button)

        # State Machine
        # TODO Add if statements to handle bank buttons
        time_ceil = 0.9
        last_button_time = time.time()
        button_index = State.button_0
        while True:
            # Idle state
            if system_state[0] == State.idle:
                time.sleep(0.0002)
                continue
            elif system_state[0].value >= State.bank_up.value:
                system_state[0] = State.button_0
                if system_state[0] == State.bank_up:
                    curr_song = (curr_song + 1) % num_songs
                else:
                    curr_song = (curr_song - 1) % num_songs

            # Get button index from system_state
            last_button = button_index
            button_index = system_state[0].value - 1

            # Ignore button if it is not programmed in this song
            if songs[curr_song].buttons[button_index] is None:
                system_state[0] = State.idle
                continue

            curr_time = time.time()
            time_diff = curr_time - last_button_time

            # Check for double press to go to first song
            if last_button == button_index \
                    and time_diff <= time_ceil:
                curr_song = 0
                system_state[0] = State.button_0
                button_index = State.button_0.value - 1

            last_button_time = curr_time
            gpio_pin = hw_info['gpio_out'][button_index]

            # Turn on respective LED, turn off last LED
            GPIO.output(curr_led_on, GPIO.LOW)
            GPIO.output(gpio_pin, GPIO.HIGH)
            curr_led_on = gpio_pin

            # TODO: add clear all notes on new button

            # Excecute through action sequence associated with button
            curr_button = songs[curr_song].buttons[button_index]
            for msg in curr_button.midi:
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
