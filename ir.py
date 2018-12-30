import RPi.GPIO as GPIO
from time import time
import logging

# IR reading logic based on:
# https://apps.fishandwhistle.net/archives/1115

class Infrared:

    def __init__(self, pin_number=11, callback=None):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin_number, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.pin_number = pin_number
        self.callback = callback


    def listen(self):
        logging.info('ir.Infrared started listening')
        GPIO.add_event_detect(self.pin_number, GPIO.FALLING)
        GPIO.add_event_callback(self.pin_number, self._on_edge_detected)
        while True:
            time.sleep(0.1)


    def _on_edge_detected(self):
        logging.debug('ir.Infrared edge event detected')
        code = self._read_pulses()
        if code:
            logging.debug('ir.Infrared received code %s', hex(code))
            if self.callback is not None:
                self.callback(code)
        else:
            logging.debug('ir.Infrared received invalid code')


    def _read_pulses(self, bouncetime=150):
        # when edge detect is called (which requires less CPU than constant
        # data acquisition), we acquire data as quickly as possible
        data = binary_aquire(self.pin_number, bouncetime/1000.0)
        if len(data) < bouncetime:
            return
        rate = len(data) / (bouncetime / 1000.0)
        pulses = []
        i_break = 0
        # detect run lengths using the acquisition rate to turn the times in to microseconds
        for i in range(1, len(data)):
            if (data[i] != data[i-1]) or (i == len(data)-1):
                pulses.append((data[i-1], int((i-i_break)/rate*1e6)))
                i_break = i
        # decode ( < 1 ms "1" pulse is a 1, > 1 ms "1" pulse is a 1, longer than 2 ms pulse is something else)
        # does not decode channel, which may be a piece of the information after the long 1 pulse in the middle
        outbin = ""
        for val, us in pulses:
            if val != 1:
                continue
            if outbin and us > 2000:
                break
            elif us < 1000:
                outbin += "0"
            elif 1000 < us < 2000:
                outbin += "1"
        try:
            return int(outbin, 2)
        except ValueError:
            # probably an empty code
            return None


    def _binary_aquire(self, duration):
        # aquires data as quickly as possible
        t0 = time()
        results = []
        while (time() - t0) < duration:
            results.append(GPIO.input(self.pin_number))
        return results


    def __del__(self):
        logging.debug('ir.Infrared object destructor called')
        GPIO.cleanup()
