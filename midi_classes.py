import rtmidi


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


class Message():
    def __init__(self, *args, **kwargs):
        pass


# Represents the other non-controller midi devices
class SoundModule():
    def __init__(self, dev_info):
        self.midi_port = rtmidi.MidiOut()
        self.midi_port.open_port(dev_info['port_index'])
        self.name = dev_info['name']

        for msg in dev_info['init_seq']:
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

        for msg in dev_info['init_seq']:
            midi_port_out.send_message(msg)

    def set_callback(self, call_back_fn, data):
        self.midi_port.set_callback(call_back_fn, data)


class Song():
    def __init__(self):
        self.buttons = []
        for button in range(0, 8):
            self.buttons.append(Button())


class Button():
    def __init__(self):
        self.midi_msgs = []
        self.split_point = 0
        self.high_module = None
        self.low_module = None


class MidiUtil():
    @staticmethod
    def parse_conf_file(f_name):
        songs = [Song()]

        # FIXME: hardcoded midi devices we wanted
        controller_data = [
            # Controller 1
            {'name': 'reface',
             'port_str': 'reface CS:reface CS MIDI 1',
             'init_seq': [[0xF0, 0x43, 0x10, 0x7F, 0x1C, 0x03,
                           0x00, 0x00, 0x06, 0x00, 0xF7]]}
        ]
        module_data = [
            {'name': 'korg',
             'port_str': 'microKORG XL:microKORG XL MIDI 2',
             'init_seq': []},
            {'name': 'reface',
             'port_str': 'reface CS:reface CS MIDI 1',
             'init_seq': []}
        ]

        controllers, modules = MidiUtil.get_midi_devs(controller_data,
                                                      module_data)

        # FIXME: static data from file
        file_data = [
            # Song 1
            [
                # Buttons
                {'midi_msgs': [{'name': 'korg', 'msg': [192, 16]}],
                 'split_point': 60, 'high': 'reface', 'low': 'korg'},
                {'midi_msgs': [{'name': 'korg', 'msg': [192, 24]}],
                 'split_point': 60, 'high': 'korg', 'low': 'reface'},
                {'midi_msgs': [{'name': 'korg', 'msg': [192, 32]}],
                 'split_point':  0, 'high': 'korg', 'low': 'reface'},
                {'midi_msgs': [{'name': 'korg', 'msg': [192, 40]}],
                 'split_point': 60, 'high': 'reface', 'low': 'reface'}
            ]
        ]

        for i, song in enumerate(file_data):
            for j, button_data in enumerate(song):
                for msg in button_data['midi_msgs']:
                    songs[i].buttons[j].midi_msgs.append(msg)
                songs[i].buttons[j].split_point = button_data['split_point']
                songs[i].buttons[j].high_module = modules[button_data['high']]
                songs[i].buttons[j].low_module = modules[button_data['low']]

        return songs, controllers, modules

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
                dev['port_index'] = get_dev_index(dev['port_str'])
                new_controller = Controller(dev)
                controllers[dev['name']] = new_controller

            for dev in module_data:
                dev['port_index'] = get_dev_index(dev['port_str'])
                new_module = SoundModule(dev)
                modules[dev['name']] = new_module
        # Raised by rtmidi when get_dev_index returns -1
        except OverflowError:
            raise MidiError('MidiError: No midi devices found')

        # Disable omni mode on reface CS, channel 16
        return controllers, modules
