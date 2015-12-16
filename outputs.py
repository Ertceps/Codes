# -*- coding: utf-8 -*-

import platform
from ctypes.test import usage
if platform.system() == 'Windows':
    pass
else:
    import GPIO
import threading
import time


class Outputs:
    """uses delegation to windows- or raspberry-Implementation """
    
    def __init__(self):
        if platform.system() == 'Windows':
            self.delegate = OutputsWindows()
        else:
            self.delegate = OutputsRaspberry()


class OutputsWindows:
    def __init__(self):
        pass

    def pp_on(self):
        self.delegate.pp_on()
        print ("action : pp on")

    def pp_off(self):
        self.delegate.pp_off()
        print ("action : pp off")

    def tmp_on(self):
        self.delegate.tmp_on()
        print ("action : tmp on")

    def tmp_off(self):
        self.delegate.tmp_off()
        print ("action : tmp off")

    def hvgv_on(self):
        self.delegate.hvgv_on()
        print ("action : hvgv on")

    def hvgv_off(self):
        self.delegate.hvgv_off()
        print ("action : hvgv off")

    def vv_on(self):
        self.delegate.vv_on()
        print ("action : vv on")

    def vv_off(self):
        self.delegate.vv_off()
        print ("action : vv off")
        
        
class OutputsRaspberry:
    # Relays
    pp_pin = 4  # RPi.GPIO - Real RPi pin #7
    tmp_pin = 17  # RPi.GPIO - Real RPi pin #11
    hvgv_pin = 2  # RPi.GPIO - Real RPi pin #13
    vv_pin = 3  # RPi.GPIO - Real RPi pin #15

    def __init__(self):
    
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pp_pin, GPIO.OUT)
        GPIO.setup(self.tmp_pin, GPIO.OUT)
        GPIO.setup(self.hvgv_pin, GPIO.OUT)
        GPIO.setup(self.vv_pin, GPIO.OUT)

    # --- PRIMARY PUMP ---
    def pp_on(self):  # Switch ON Primary Pump
        GPIO.output(self.pp_pin, 1)
        print "pp on"

    def pp_off(self):  # Switch OFF Primary Pump
        GPIO.output(self.pp_pin, 0)
        print "pp off"

    # --- TURBO MOLECULAR PUMP ---
    def tmp_on(self):  # Switch ON Turbo Molecular Pump
        GPIO.output(self.tmp_pin, 1)
        print "tmp on"

    def tmp_off(self):  # Switch OFF Turbo Molecular Pump
        GPIO.output(self.tmp_pin, 0)
        print "tmp off"

    # --- HIGH-VACUUM VENTING VALVE ---
    def hvgv_on(self):  # Open High Vacuum Gate Valve
        GPIO.output(self.hvgv_pin, 1)
        print "hvgv open"

    def hvgv_off(self):  # Close High Vacuum Gate Valve
        GPIO.output(self.hvgv_pin, 0)
        print "hvgv closed"

    # --- VENTING VALVE ---
    def vv_on(self):  # Open Venting Valve
        GPIO.output(self.vv_pin, 1)
        print "vv open"

    def vv_off(self):  # Close Venting Valve
        GPIO.output(self.vv_pin, 0)
        print "vv closed"