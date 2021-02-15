from enum import Enum


class State(Enum):
    idle = 0
    update_button = 1
    bank_up = 2
    bank_down = 3


class ButtonCallback():
    def __init__(self):
        # TODO: create button to reset program
        # TODO: create button to clear all notes
        # TODO: create button to change songs
        self.button_to_state = {
            }


        # Lists of GPIO pins in use
        self.gpio_to_button = {}

    def __call__(self, system_state, channel):
        system_state[0] = self.button_to_state[self.gpio_to_button[channel]]


def midi_callback(midi_msg, data):
    new_msg = list(midi_msg[0])

    if new_msg[0] is not 144 and new_msg[0] is not 128:
        return

    if new_msg[1] > data.split_point:
        # FIXME: need to set for which module
        new_msg[1] = new_msg[1] + data.transpose_high
        if new_msg[1] <= 127:
            data.high_module.send_message(new_msg)
    else:
        new_msg[1] = new_msg[1] + data.transpose_low
        if new_msg[1] >= 0:
            data.low_module.send_message(new_msg)
