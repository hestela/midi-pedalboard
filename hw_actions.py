import RPi.GPIO as GPIO

class Hardware():
    def __init__(self):
        pass
    def poll(self):
        pass
    def set_led_on(self, led):
        pass


class Bohara_one(Hardware):
    def __init__(self):
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
            print("setup led", led)
            GPIO.setup(led, GPIO.OUT, initial=GPIO.LOW)
            print("=======")

    def poll(self):
        pass

    def set_led_on(self, led):

        # Setup row
        if led > 4:
            on_row, off_row = (self.__led_rows[0], self.__led_rows[1])
        else:
            on_row, off_row = (self.__led_rows[1], self.__led_rows[0])
        GPIO.setup(on_row, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(off_row, GPIO.OUT, initial=GPIO.HIGH)

        # Setup col
        GPIO.setup(self.__led_cols[self.__curr_led % 5], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.__led_cols[led % 5], GPIO.OUT, initial=GPIO.HIGH)

        self.__curr_led = led
