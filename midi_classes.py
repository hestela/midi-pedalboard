import rtmidi


class Message():
    def __init__(self, *args, **kwargs):
        pass


class SoundModule():
    def __init__(self, port_index, init_msgs=None):
        self.midi_port = rtmidi.MidiOut()
        self.midi_port.open_port(port_index)

        if init_msgs:
            for msg in init_msgs:
                self.send_message(msg)

    def send_message(self, msg):
        self.midi_port.send_message(msg)


class Controller():
    def __init__(self, port_index, init_msgs=None):
        self.midi_port = rtmidi.MidiIn()
        self.midi_port.open_port(port_index)

        midi_port_out = rtmidi.MidiOut()
        midi_port_out.open_port(port_index)

        if init_msgs:
            for msg in init_msgs:
                midi_port_out.send_message(msg)

    def set_callback(self, call_back_fn, data):
        self.midi_port.set_callback(call_back_fn, data)


class MidiUtil():
    @staticmethod
    def get_midi_devs():
        # FIXME: hardcoded midi devices we wanted
        controller_data = [
            # Controller 1
            {'port_str': 'reface CS:reface CS MIDI 1 24',
             'init_seq': [[0xF0, 0x43, 0x10, 0x7F, 0x1C, 0x03, 0x00, 0x00, 0x06, 0x00, 0xF7]]}
        ]
        module_data = [
            {'port_str': 'microKORG XL:microKORG XL MIDI 2',
             'init_seq': None},
            {'port_str': 'reface CS:reface CS MIDI 1 24',
             'init_seq': None}
        ]

        controllers = []
        modules = []

        def get_dev_index(name):
            # used just read ports, not used afterwards
            rtmidi_devs = rtmidi.MidiOut()
            for index, dev in enumerate(rtmidi_devs.get_ports()):
                if name in dev:
                    return index


        for dev in controller_data:
            new_controller = Controller(get_dev_index(dev['port_str']),
                                        dev['init_seq'])
            controllers.append(new_controller)

        for dev in module_data:
            new_module = SoundModule(get_dev_index(dev['port_str']),
                                     dev['init_seq'])
            modules.append(new_module)

        # Disable omni mode on reface CS, channel 16
        return controllers, modules
