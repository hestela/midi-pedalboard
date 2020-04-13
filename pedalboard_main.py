#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
from functools import partial
from enum import Enum
from midi_classes import MidiUtil, MidiError


class Song():
    def __init__(self):
        self.buttons = []
        for button in range(0, 8):
            self.buttons.append(Button())


class Button():
    def __init__(self):
        self.midi_msgs = []
        self.split_point = 0
        self.high_module = ''
        self.low_module = ''


class ButtonAction():
    def execute(self):
        pass


class MusicAction(ButtonAction):
    def __init__(self, file_path, repeat, stoppable):
        self.file_path = file_path
        self.repeat = repeat
        self.stoppable = stoppable

    def send_message(self):
        pass


class MidiMsgAction(ButtonAction):
    def __init__(self, midiout, message):
        self.midiout = midiout
        self.message = message

    def send_message(self):
        self.midiout.send_message(self.message)


class State(Enum):
    idle = 0
    button_0 = 1
    button_1 = 2
    button_2 = 3
    button_3 = 4
    button_4 = 5
    button_5 = 6
    button_6 = 7
    button_7 = 8
    button_8 = 9
    button_9 = 10


def button_callback(gpio_to_button, system_state, channel):
    button_to_state = {
            0: State.button_0,
            1: State.button_1,
            2: State.button_2,
            3: State.button_3,
            4: State.button_4,
            5: State.button_5,
            6: State.button_6,
            7: State.button_7,
            8: State.button_8,
            9: State.button_9
            }
    system_state[0] = button_to_state[gpio_to_button[channel]]


# options and devices for callback
class MidiCallBackOpts():
    def __init__(self, high_module, low_module, split):
        self.high_module = high_module
        self.low_module = low_module
        self.split = split


def midi_callback(msg_time, call_opts):
    high_module = call_opts.high_module
    low_module = call_opts.low_module
    new_msg = list(msg_time[0])

    if new_msg[0] is not 144 and new_msg[0] is not 128:
        return

    if new_msg[1] > call_opts.split:
        high_module.send_message(new_msg)
    else:
        low_module.send_message(new_msg)


def parse_conf_file(songs, f_name):
    file_data = [
        # Song 1
        [
            # Buttons
            {'midi_msgs': [{'name': 'korg', 'msg': [192, 16]}],
             'split_point': 60, 'high': 'reface', 'low': 'korg'},
            {'midi_msgs': [{'name': 'korg', 'msg': [192, 24]}],
             'split_point': 70, 'high': 'korg', 'low': 'reface'},
            {'midi_msgs': [{'name': 'korg', 'msg': [192, 32]}],
             'split_point':  0, 'high': 'korg', 'low': 'reface'},
            {'midi_msgs': [{'name': 'korg', 'msg': [192, 40]}],
             'split_point': 60, 'high': 'reface', 'low': 'reface'}
        ]
    ]

    for i, song in enumerate(file_data):
        for j, button in enumerate(song):
            for msg in button['midi_msgs']:
                songs[i].buttons[j].midi_msgs.append(msg)
            songs[i].buttons[j].split_point = button['split_point']
            songs[i].buttons[j].high_module = button['high']
            songs[i].buttons[j].low_module = button['low']


def main():
    try:
        controllers, modules = MidiUtil.get_midi_devs()

        # set the Pi to reference the GPIOs with the BCM convention
        GPIO.setmode(GPIO.BCM)

        # This list holds all the songs
        # TODO add more songs
        songs = [Song()]

        # Fill out song/button info
        parse_conf_file(songs, 'dummy.txt')

        # This list keeps track of the song setup the pedal is currently using
        curr_song = 0
        curr_led_on = -1

        # Lists of GPIO pins in use
        gpio_in = range(2, 12)
        gpio_out = [12, 13, 16, 17] + list(range(22, 28))
        gpio_to_button = {}

        # State machine initialize
        system_state = [State.button_0]
        f = partial(button_callback, gpio_to_button, system_state)

        # Setup all pins, create states for input pins
        for gpio, index in enumerate(gpio_in):
            GPIO.setup(gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(gpio, GPIO.FALLING,
                                  callback=f, bouncetime=300)
            gpio_to_button[index] = gpio
        for gpio in gpio_out:
            GPIO.setup(gpio, GPIO.OUT, initial=GPIO.LOW)

        # Midi callback, with defaults
        call_back_opts = MidiCallBackOpts(modules['korg'],
                                          modules['reface'], 60)
        # FIXME: just using the first controller for now
        controllers['reface'].set_callback(midi_callback, (call_back_opts))

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
            if curr_led_on != -1:
                GPIO.output(curr_led_on, GPIO.LOW)
            GPIO.output(gpio_pin, GPIO.HIGH)
            curr_led_on = gpio_pin

            # Excecute through action sequence associated with button
            curr_button = songs[curr_song].buttons[button_index]
            for msg in curr_button.midi_msgs:
                modules[msg['name']].send_message(msg['msg'])
                call_back_opts.split = curr_button.split_point
                call_back_opts.high_module = modules[curr_button.high_module]
                call_back_opts.low_module = modules[curr_button.low_module]

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
