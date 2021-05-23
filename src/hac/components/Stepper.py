import RPi.GPIO as GPIO
import time


class Stepper(object):
    def __init__(self, enable_pin, step_pin, dir_pin, stop_pin, delay=100, reversesteps=100):
        self.enable_pin = enable_pin
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.stop_pin = stop_pin
        self.delay = delay
        self.reversesteps = reversesteps
        self.sleeptimer = delay * 0.000001
        self._setup()

    def _setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.enable_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.stop_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def _enable(self):
        GPIO.output(self.enable_pin, GPIO.LOW)

    def _disable(self):
        GPIO.output(self.enable_pin, GPIO.HIGH)

    def _set_direction(self):
        GPIO.output(self.dir_pin, self.direction)

    def _step(self):
        GPIO.output(self.step_pin, GPIO.HIGH)
        time.sleep(self.sleeptimer / 2)
        GPIO.output(self.step_pin, GPIO.LOW)
        time.sleep(self.sleeptimer / 2)

    def _reverse(self):
        self.direction = not self.direction
        self._set_direction()
        for i in range(0, self.reversesteps):
            self._step()

    def run(self, steps, direction='forward'):
        self.direction = False if direction == 'forward' else True
        self._set_direction()
        self._enable()

        for i in range(0, steps):
            if not GPIO.input(self.stop_pin):
                print("Endstop triggered !!!")
                self._reverse()
                break
            self._step()
        self._disable()
