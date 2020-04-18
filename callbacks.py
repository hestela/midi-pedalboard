from enum import Enum


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


class ButtonCallback():
    def __init__(self):
        self.button_to_state = {
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

        # Lists of GPIO pins in use
        self.gpio_to_button = {}

    def __call__(self, system_state, channel):
        system_state[0] = self.button_to_state[self.gpio_to_button[channel]]


# options and devices for callback
class MidiCallBack():
    def __init__(self, high_module, low_module, split):
        self.high_module = high_module
        self.low_module = low_module
        self.split = split

    def __call__(self, midi_msg, data=None):
        new_msg = list(midi_msg[0])

        if new_msg[0] is not 144 and new_msg[0] is not 128:
            return

        if new_msg[1] > self.split:
            self.high_module.send_message(new_msg)
        else:
            self.low_module.send_message(new_msg)

    def update(self, split=None, high_module=None, low_module=None):
        if split:
            self.split = split
        if high_module:
            self.high_module = high_module
        if low_module:
            self.low_module = low_module
