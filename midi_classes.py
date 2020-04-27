import rtmidi
import os
from yaml import load
try:
        from yaml import CLoader as Loader
except ImportError:
        from yaml import Loader


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


class MidiError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ConfError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Message():
    def __init__(self, *args, **kwargs):
        pass


# Represents the other non-controller midi devices
class SoundModule():
    def __init__(self, dev_info):
        self.midi_port = rtmidi.MidiOut()
        self.midi_port.open_port(dev_info['port_index'])
        self.name = dev_info['name']

        for msg in dev_info.get('setup_messages', []):
            self.send_message(msg)

    def send_message(self, msg):
        self.midi_port.send_message(msg)


# Represents a controller midi device
class Controller():
    def __init__(self, dev_info):
        self.midi_port = rtmidi.MidiIn()
        self.midi_port.open_port(dev_info['port_index'])
        self.name = dev_info['name']

        midi_port_out = rtmidi.MidiOut()
        midi_port_out.open_port(dev_info['port_index'])

        for msg in dev_info['setup_messages']:
            midi_port_out.send_message(msg)

    def set_callback(self, call_back_fn, data):
        self.midi_port.set_callback(call_back_fn, data)


class Song():
    def __init__(self, num_buttons):
        self.buttons = []
        for button in range(0, num_buttons):
            self.buttons.append(None)


class Button():
    def __init__(self):
        self.midi = []
        self.split_point = 0
        self.high_module = None
        self.low_module = None
        self.transpose_high = 0
        self.transpose_low = 0


class MidiUtil():
    @staticmethod
    def parse_conf_file():
        pwd = os.path.dirname(os.path.realpath(__file__))
        peripheral_path = os.path.join(pwd, "config", "peripherals.yaml")
        hardware_path = os.path.join(pwd, "config", "hardware.yaml")

        with open(peripheral_path, 'r') as f:
            peripheral_data = load(f, Loader=Loader)
        with open(hardware_path, 'r') as f:
            hw_info = load(f, Loader=Loader)

        controllers, modules = MidiUtil.get_midi_devs(peripheral_data['controllers'],
                                                      peripheral_data['generators'])

        songs = []

        num_buttons = int(hw_info['num_buttons'])
        for i, gpio in enumerate(hw_info['gpio_in']):
            hw_info['gpio_in'][i] = int(gpio)
        for i, gpio in enumerate(hw_info['gpio_out']):
            hw_info['gpio_out'][i] = int(gpio)

        for i in range(0, len(peripheral_data['button_data'])):
            songs.append(Song(num_buttons))
            for j, button_data in enumerate(peripheral_data['button_data'][i]['buttons']):
                if j >= num_buttons:
                    break

                songs[i].buttons[j] = Button()

                name = None
                for msg in button_data.get('midi', []):
                    if isinstance(msg, str):
                        name = msg
                    else:
                        songs[i].buttons[j].midi.append({'name': name, 'msg': msg})

                songs[i].buttons[j].split_point = int(button_data['split'])
                songs[i].buttons[j].high_module = modules[button_data['high']]
                songs[i].buttons[j].low_module = modules[button_data['low']]
                if 'transpose_high' in button_data:
                    songs[i].buttons[j].transpose_high = \
                        int(button_data['transpose_high'])
                if 'transpose_low' in button_data:
                    songs[i].buttons[j].transpose_low = \
                        int(button_data['transpose_low'])

        return songs, controllers, modules, hw_info

    @staticmethod
    def get_midi_devs(controller_data, module_data):
        controllers = {}
        modules = {}

        # used only to read ports, not used afterwards
        rtmidi_devs = rtmidi.MidiOut()

        def get_dev_index(name):
            for index, dev in enumerate(rtmidi_devs.get_ports()):
                if name in dev:
                    return index
            print("Could not find: %s" % name)
            return -1

        try:
            for dev in controller_data:
                dev['port_index'] = get_dev_index(dev['midi_name'])
                new_controller = Controller(dev)
                controllers[dev['name']] = new_controller

            for dev in module_data:
                dev['port_index'] = get_dev_index(dev['midi_name'])
                new_module = SoundModule(dev)
                modules[dev['name']] = new_module
        # Raised by rtmidi when get_dev_index returns -1
        except OverflowError:
            raise MidiError('MidiError: No midi devices found')

        # Disable omni mode on reface CS, channel 16
        return controllers, modules
