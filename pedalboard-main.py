#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
import rtmidi
from functools import partial
from enum import Enum


class Song():
    def __init__(self):
        self.buttons = []
        for button in range(0, 11):
            self.buttons.append(Button())


class Button():
    def __init__(self):
        self.actions = []


class ButtonAction():
    def execute(self):
        pass


class MusicAction(ButtonAction):
    def __init__(self, file_path, repeat, stoppable):
        self.file_path = file_path
        self.repeat = repeat
        self.stoppable = stoppable

    def execute(self):
        pass

class sysExMsg():
    pass


class MidiMsgAction(ButtonAction):
    def __init__(self, midiout, message):
        self.midiout = midiout
        self.message = message

    def execute(self):
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
class CallBackOpts():
    def __init__(self, midiin_korg, midiout_korg, midiout_cs, split):
        self.midiin_korg = midiin_korg
        self.midiout_korg = midiout_korg
        self.midiout_cs = midiout_cs
        self.split = split


def midi_callback(msg_time, call_opts):
    midiout_cs = call_opts.midiout_cs
    midiout_korg = call_opts.midiout_korg
    new_msg = list(msg_time[0])

    if new_msg[0] is not 145 and new_msg[0] is not 129:
        return

    if new_msg[1] > call_opts.split:
        new_msg[0] = (new_msg[0] - 1)
        midiout_cs.send_message(new_msg)
    else:
        midiout_korg.send_message(new_msg)

def main():
    try:
        my_keyboards = ['microKORG XL:microKORG XL MIDI 2',
                        'reface CS:reface CS MIDI 1 24'
                        ]
        # midiout to just read ports, not used later
        midiout = rtmidi.MidiOut()
        midiin_korg = rtmidi.MidiIn()
        midiout_korg = rtmidi.MidiOut()
        midiout_cs = rtmidi.MidiOut()

        for index, dev in enumerate(midiout.get_ports()):
            if my_keyboards[0] in dev:
                midiout_korg.open_port(index)
                # Only korg will be input at the moment
                midiin_korg.open_port(index)
                print("korg:", dev, index)
            elif my_keyboards[1] in dev:
                midiout_cs.open_port(index)
                print("cs:", dev, index)

        # Disable omni mode on reface CS, channel 16
        midiout_cs.send_message([191, 0x7C, 0])

        # set the Pi to reference the GPIOs with the BCM convention
        GPIO.setmode(GPIO.BCM)

        # This list holds all the songs
        # TODO add more songs
        songs = [Song()]

        # sysEx message header for reface cs
        #cs_head = [0xF0, 0x43, 0x10, 0x7F, 0x1C, 0x03]

        # Fill out song/button info
        # TODO generate this data structure from a xml file
        #songs[0].buttons[0].actions.append(MidiMsgAction(midiout, cs_head + [0x00, 0x00, 0x06, 0x01, 0xF7]))
        #songs[0].buttons[0].actions.append(MidiMsgAction(midiout, cs_head + [0x00, 0x00, 0x00, 0x00, 0xF7]))
        #songs[0].buttons[1].actions.append(MidiMsgAction(midiout, cs_head + [0x00, 0x00, 0x06, 0x00, 0xF7]))
        #songs[0].buttons[1].actions.append(MidiMsgAction(midiout, cs_head + [0x00, 0x00, 0x00, 0x01, 0xF7]))

        # This list keeps track of the song setup the pedal is currently using
        curr_song = 0
        curr_led_on = -1

        # Lists of GPIO pins in use
        gpio_in = range(2, 12)
        gpio_out = [12, 13, 16, 17] + list(range(22, 28))
        gpio_to_button = {}

        # State machine (implemented in the infinite while loop) variable
        system_state = [State.idle]

        f = partial(button_callback, gpio_to_button, system_state)

        # Setup all pins, create states for input pins
        for gpio, index in enumerate(gpio_in):
            GPIO.setup(gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(gpio, GPIO.FALLING,
                                  callback=f, bouncetime=300)
            gpio_to_button[index] = gpio
        for gpio in gpio_out:
            GPIO.setup(gpio, GPIO.OUT, initial=GPIO.LOW)

        # Midi callback
        # TODO: fix split for each button press
        call_back_opts = CallBackOpts(midiin_korg, midiout_korg, midiout_cs, 60)
        midiin_korg.set_callback(midi_callback, (call_back_opts))

        # State Machine
        # TODO Add if statements to handle bank buttons
        while True:
            # Idle state
            if system_state[0] == State.idle:
                time.sleep(0.0002)
                continue

            # Service a button press
            # State Machine can only enter a state other than Idle through the IRQ

            # Get button index from system_state
            button_index = system_state[0].value - 1
            gpio_pin = gpio_out[button_index]

            # Turn on respective LED, turn off last LED
            if curr_led_on != -1:
                GPIO.output(curr_led_on, GPIO.LOW)
            GPIO.output(gpio_pin, GPIO.HIGH)
            curr_led_on = gpio_pin

            # Excecute through action sequence associated with button
            for action in songs[curr_song].buttons[button_index].actions:
                action.execute()

            # Return system state to Idle
            system_state[0] = State.idle

    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        GPIO.cleanup()
        del midiout
    except RuntimeError:
        print("PortNumber for rtmidi is invalid, quitting")


if __name__ == '__main__':
    main()
