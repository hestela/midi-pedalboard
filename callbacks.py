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


def midi_callback(midi_msg, data):
    new_msg = list(midi_msg[0])

    if new_msg[0] is not 144 and new_msg[0] is not 128:
        return

    if new_msg[1] > data.split_point:
        data.high_module.send_message(new_msg)
    else:
        data.low_module.send_message(new_msg)
