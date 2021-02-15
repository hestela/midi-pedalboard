#!/usr/bin/env python2
from __future__ import print_function
import RPi.GPIO as GPIO
import time
from functools import partial
from midi_classes import MidiUtil, MidiError
from callbacks import State, midi_callback
from hw_actions import *


def main():
    print("pedalboard_main.py")
    # This list keeps track of the song setup the pedal is currently using
    curr_song = 0

    hw = Bohara_one()
    led = 0
    for led in range(0,10):
        hw.set_led(led)
        time.sleep(0.1)

    try:
        # Fill out song/button info
        #songs, controllers, modules, hw_info = MidiUtil.parse_conf_file()

        # State machine initialize
        system_state = State.idle
        songs = [0, 0, 0]
        num_songs = len(songs)

        # Midi callback, with defaults
        # FIXME: depends on setup from config
        # FIXME: remove hardcoded module names
        # FIXME: just using the first controller for now

        #initial_button = songs[0].buttons[0]
        #controllers['reface'].set_callback(midi_callback, initial_button)

        # State Machine
        # TODO Add if statements to handle bank buttons
        time_ceil = 0.9
        last_button_time = time.time()

        # Initialize LEDs to off
        while True:
            # Idle state
            if system_state == State.idle:
                # Poll button matrix
                system_state, button_index = hw.poll_buttons()
                continue
            elif system_state == State.bank_up:
                curr_song = (curr_song + 1) % num_songs
                system_state = State.idle
                continue
            elif system_state == State.bank_down:
                curr_song = (curr_song - 1) % num_songs
                system_state = State.idle
                continue

            # Get button index from system_state
            last_button = button_index

            # Ignore button if it is not programmed in this song
            #if songs[curr_song].buttons[button_index] is None:
            #    system_state = State.idle
            #    continue

            curr_time = time.time()
            time_diff = curr_time - last_button_time

            # Check for double press to go to first song
            #if last_button == button_index \
            #        and time_diff <= time_ceil:
            #    curr_song = 0
            #    system_state = State.bank_up
            #    button_index = State.bank_up.value - 1

            last_button_time = curr_time

            # Turn on respective LED, turn off last LED
            hw.set_led(button_index)

            # TODO: add clear all notes on new button

            # Excecute through action sequence associated with button
            #curr_button = songs[curr_song].buttons[button_index]
            #for msg in curr_button.midi:
            #    modules[msg['name']].send_message(msg['msg'])

            #controllers['reface'].set_callback(midi_callback, curr_button)

            # Return system state to Idle
            system_state = State.idle

    except MidiError as e:
        print(e.value)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        GPIO.cleanup()
    except RuntimeError:
        print("PortNumber for rtmidi is invalid, quitting")


if __name__ == '__main__':
    main()
