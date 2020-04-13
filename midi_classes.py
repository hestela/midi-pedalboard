import rtmidi


class Message():
    def __init__(self, *args, **kwargs):
        pass


class SoundModule():
    def __init__(self, dev_info):
        self.midi_port = rtmidi.MidiOut()
        self.midi_port.open_port(dev_info['port_index'])
        self.name = dev_info['name']

        for msg in dev_info['init_seq']:
            self.send_message(msg)

    def send_message(self, msg):
        self.midi_port.send_message(msg)


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


class MidiUtil():
    @staticmethod
    def get_midi_devs():
        # FIXME: hardcoded midi devices we wanted
        controller_data = [
            # Controller 1
            {'name': 'reface',
             'port_str': 'reface CS:reface CS MIDI 1 24',
             'init_seq': [[0xF0, 0x43, 0x10, 0x7F, 0x1C, 0x03, 0x00, 0x00, 0x06, 0x00, 0xF7]]}
        ]
        module_data = [
            {'name': 'korg',
             'port_str': 'microKORG XL:microKORG XL MIDI 2',
             'init_seq': []},
            {'name': 'reface',
             'port_str': 'reface CS:reface CS MIDI 1 24',
             'init_seq': []}
        ]

        controllers = {}
        modules = {}

        def get_dev_index(name):
            # used just read ports, not used afterwards
            rtmidi_devs = rtmidi.MidiOut()
            for index, dev in enumerate(rtmidi_devs.get_ports()):
                if name in dev:
                    return index

        for dev in controller_data:
            dev['port_index'] = get_dev_index(dev['port_str'])
            new_controller = Controller(dev)
            controllers[dev['name']] = new_controller

        for dev in module_data:
            dev['port_index'] = get_dev_index(dev['port_str'])
            new_module = SoundModule(dev)
            modules[dev['name']] = new_module

        # Disable omni mode on reface CS, channel 16
        return controllers, modules
