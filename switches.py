# -*- coding: utf-8 -*-

import platform
from ctypes.test import usage
if platform.system() == 'Windows':
    pass
else:
    import GPIO
import threading
import time

class Switches:
    """uses delegation to windows- or raspberry-Implementation """
    
    def __init__(self, queue):
        if platform.system() == 'Windows':
            self.delegate = SwitchesWindows(queue)
        else:
            self.delegate = SwitchesRaspberry(queue)

    def stop(self):
        self.delegate.stop()
                
class SwitchesWindows:
    def __init__(self, queue):
        self.queue = queue
        
        self._stop = threading.Event()
        self.thread = threading.Thread(target=self.run)
        self.thread.setName("SwitchesWindows")
        self._stop.clear()
        self.thread.start()

    def run(self):
        while not self._stop.isSet():
            time.sleep(0.05)  # small delay to prevent excessive CPU usage
            print("give action : pp_on, pp_off, tmp_on, tmp_off, hvgv_on, hvgv_off, vv_on, vv_off, VC_vacuum, VC_vent, local")
            s = raw_input("your action ")
            if s == 'pp_on':
                self.queue.put("pp_on")
            elif s == 'pp_off':
                self.queue.put("pp_off")
            elif s == 'tmp_on':
                self.queue.put("tmp_on")
            elif s == 'tmp_off':
                self.queue.put("tmp_off")
            elif s == 'hvgv_on':
                self.queue.put("hvgv_on")
            elif s == 'hvgv_off':
                self.queue.put("hvgv_off")
            elif s == 'vv_on':
                self.queue.put("vv_on")
            elif s == 'vv_off':
                self.queue.put("vv_off")
            elif s == 'VC_vent':
                self.queue.put("VC_vent")
            elif s == 'VC_vacuum':
                self.queue.put("VC_vacuum")
            elif s == 'local':
                self.queue.put("local")
            # needed for simulating shutdown
            elif s == 'stop':
                self.queue.put("stop")
            else:
                print ("unknown input")
                            
    def stop(self):
        self._stop.set()
            
        
class SwitchesRaspberry:

    sw_pp_pin = 5  # RPi.GPIO - Real RPi pin #29
    sw_tmp_pin = 6  # RPi.GPIO - Real RPi pin #31
    sw_hvgv_pin = 13  # RPi.GPIO - Real RPi pin #33
    sw_vv_pin = 19  # RPi.GPIO - Real RPi pin #35

    def __init__(self, queue):
        self.queue = queue
    
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.sw_pp_pin, GPIO.IN)
        GPIO.setup(self.sw_tmp_pin, GPIO.IN)
        GPIO.setup(self.sw_hvgv_pin, GPIO.IN)
        GPIO.setup(self.sw_vv_pin, GPIO.IN)
        GPIO.setwarnings(False)

        self._stop = threading.Event()
        self.thread = threading.Thread(target=self.run)
        self.thread.setName("SwitchesRaspberry")
        self._stop.clear()
        self.thread.start()

    def run(self):
        pp_last = None
        tmp_last = None
        hvgv_last = None
        vv_last = None
        while not self._stop.isSet():  # endless loop to read buttons
            if GPIO.input(self.sw_pp_pin) != pp_last:
                pp_last = GPIO.input(self.sw_pp_pin)
                if pp_last:
                    self.queue.put("pp_on")
                else:
                    self.queue.put("pp_off")
            if GPIO.input(self.sw_tmp_pin) != tmp_last:
                tmp_last = GPIO.input(self.sw_tmp_pin)
                if tmp_last:
                    self.queue.put("tmp_on")
                else:
                    self.queue.put("tmp_off")
            if GPIO.input(self.sw_hvgv_pin) != hvgv_last:
                hvgv_last = GPIO.input(self.sw_hvgv_pin)
                if hvgv_last:
                    self.queue.put("hvgv_on")
                else:
                    self.queue.put("hvgv_off")
            if GPIO.input(self.sw_vv_pin) != vv_last:
                vv_last = GPIO.input(self.sw_vv_pin)
                if vv_last:
                    self.queue.put("vv_on")
                else:
                    self.queue.put("vv_off")
            time.sleep(0.05)  # small delay to prevent excessive CPU usage
            
    def stop(self):
        self._stop.set()