import RPi.GPIO as GPIO
from callbacks import State

class Hardware():
    def __init__(self):
        pass
    def poll_buttons(self):
        pass
    def set_led(self, led):
        pass


class Bohara_one(Hardware):
    def __init__(self):
        # Disables pin in use warning
        GPIO.setwarnings(False)

        GPIO.setmode(GPIO.BCM)
        self.__curr_led = 0

        # GPIO setup for LED
        self.__led_rows = [
                16, # Row0
                26, # Row1
                ]
        self.__led_cols = [
                25, # Col0
                24, # Col1
                23, # Col2
                22, # Col3
                27  # Col4
                ]
        for led in self.__led_rows + self.__led_cols:
            GPIO.setup(led, GPIO.OUT, initial=GPIO.LOW)


        # GPIO setup for buttons
        self.__but_rows = [
                21, # Row0
                20, # Row1
                ]
        self.__but_cols = [
                19, # Col0
                6, # Col1
                5, # Col2
                7, # Col3
                8  # Col4
                ]
        for but in self.__but_rows:
            GPIO.setup(but, GPIO.OUT, initial=GPIO.HIGH)

        for but in self.__but_cols:
            GPIO.setup(but, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def poll_buttons(self):
        GPIO.output(self.__but_rows[0], GPIO.LOW)

        def check_cols(but_cols, row):
            for col in but_cols:
                # read col
                # if col is low then return corresponding button index
                but_ind = self.__but_cols.index(col)
                if GPIO.input(col) == 0:
                    if but_ind == 0:
                        if row is 0:
                            return (State.bank_down, 0)
                        return (State.bank_up, 0)
                    else:
                        return (State.update_button, but_ind - 1)
            return (None, None)

        state, ind = check_cols(self.__but_cols, 0)
        if state:
            GPIO.output(self.__but_rows[0], GPIO.HIGH)
            return (state, ind)

        GPIO.output(self.__but_rows[0], GPIO.HIGH)
        GPIO.output(self.__but_rows[1], GPIO.LOW)

        state, ind = check_cols(self.__but_cols, 1)
        if state:
            GPIO.output(self.__but_rows[1], GPIO.HIGH)
            return (state, ind + 5)

        GPIO.output(self.__but_rows[1], GPIO.HIGH)
        return (State.idle, 0)


    def set_led(self, led):

        # Setup row
        if led > 4:
            on_row, off_row = (self.__led_rows[0], self.__led_rows[1])
        else:
            on_row, off_row = (self.__led_rows[1], self.__led_rows[0])
        # move to init
        GPIO.output(on_row, GPIO.LOW)
        GPIO.output(off_row, GPIO.HIGH)

        # Setup col
        GPIO.output(self.__led_cols[self.__curr_led % 5], GPIO.LOW)
        GPIO.output(self.__led_cols[led % 5], GPIO.HIGH)

        self.__curr_led = led
