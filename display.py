# -*- coding: utf-8 -*-

import platform
from ctypes.test import usage
if platform.system() == 'Windows':
    pass
else:
    import GPIO
import threading
import time


class Display:
    """uses delegation to windows- or raspberry-Implementation """
    def __init__(self):
        if platform.system() == 'Windows':
            self.delegate = DisplayWindows()
        else:
            self.delegate = DisplayRaspberry()

    def stop(self):
        self.delegate.stop()
    
    def displayState(self, text):
        self.delegate.displayState(text)
     
    def setPressure(self, pressure):
        self.delegate.setPressure(pressure)
                      

class DisplayWindows:
    # member variables for data being set from the application
    state = None
    pressure = None
    
    def __init__(self):
        
        self._stop = threading.Event()
        self.thread = threading.Thread(target=self.run)
        self.thread.setName("DisplayWindows")
        self._stop.clear()
        self.thread.start()

    def run(self):
        lastLine1 = None
        lastLine2 = None
        
        while not self._stop.isSet():
            line1 = self.state
            if self.pressure == None:
                line2 = 'hello'
            else:
                line2 = 'pressure:' + str(self.pressure)
                
            if line1 != lastLine1 or line2 != lastLine2:
                lastLine1 = line1
                lastLine2 = line2
                 
                print('-' * 36)
                print ( line1 )
                print ( line2 )
                print('-' * 36)
            
            time.sleep(0.5) # small delay to prevent excessive CPU usage
                            
    def stop(self):
        self._stop.set()
            
    def displayState(self, text):
        self.state = text

    def setPressure(self, pressure):
        self.pressure = pressure
                
class DisplayRaspberry:
    # define Pins here
    LCD_RS = 18
    LCD_E = 23
    LCD_D4 = 12
    LCD_D5 = 16
    LCD_D6 = 20
    LCD_D7 = 21
    
    # Define some device constants
    LCD_WIDTH = 16  # Maximum characters per line
    LCD_CHR = True
    LCD_CMD = False
    
    LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

    # member variables for data being set from the application
    state = None
    pressure = None
    
    def __init__(self):
    
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.LCD_E, GPIO.OUT)   # E
        GPIO.setup(self.LCD_RS, GPIO.OUT)  # RS
        GPIO.setup(self.LCD_D4, GPIO.OUT)  # DB4
        GPIO.setup(self.LCD_D5, GPIO.OUT)  # DB5
        GPIO.setup(self.LCD_D6, GPIO.OUT)  # DB6
        GPIO.setup(self.LCD_D7, GPIO.OUT)  # DB7

        self._stop = threading.Event()
        self.thread = threading.Thread(target=self.run)
        self.thread.setName("DisplayRaspberry")
        self._stop.clear()
        self.thread.start()

    def run(self):
        #
      
        while not self._stop.isSet():
            def lcd_init():
                # Initialise display
                lcd_byte(0x33, LCD_CMD)
                lcd_byte(0x32, LCD_CMD)
                lcd_byte(0x28, LCD_CMD)
                lcd_byte(0x0C, LCD_CMD)
                lcd_byte(0x06, LCD_CMD)
                lcd_byte(0x01, LCD_CMD)
                time.sleep(E_DELAY)
                print("LCD init")

            def lcd_string_fix(message, line):
                # Send string to display
                message = message.ljust(LCD_WIDTH, " ")
                lcd_byte(line, LCD_CMD)
                for i in range(LCD_WIDTH):
                    lcd_byte(ord(message[i]), LCD_CHR)

            def lcd_string_scroll(message,style):
                # Send string to display
                # style=1 Left justified
                # style=2 Centred
                # style=3 Right justified
                if style == 1:
                    message = message.ljust(LCD_WIDTH, " ")
                elif style == 2:
                    message = message.center(LCD_WIDTH, " ")
                elif style == 3:
                    message = message.rjust(LCD_WIDTH, " ")

                for i in range(LCD_WIDTH):
                    lcd_byte(ord(message[i]), LCD_CHR)

            def lcd_byte(bits, mode):
                # Send byte to data pins
                # bits = data
                # mode = True  for character
                #        False for command
                GPIO.output(LCD_RS, mode)  # RS

                # High bits
                GPIO.output(LCD_D4, False)
                GPIO.output(LCD_D5, False)
                GPIO.output(LCD_D6, False)
                GPIO.output(LCD_D7, False)
                if bits & 0x10 == 0x10:
                    GPIO.output(LCD_D4, True)
                if bits & 0x20 == 0x20:
                    GPIO.output(LCD_D5, True)
                if bits & 0x40 == 0x40:
                    GPIO.output(LCD_D6, True)
                if bits & 0x80 == 0x80:
                    GPIO.output(LCD_D7, True)

                # Toggle 'Enable' pin
                lcd_toggle_enable()

                # Low bits
                GPIO.output(LCD_D4, False)
                GPIO.output(LCD_D5, False)
                GPIO.output(LCD_D6, False)
                GPIO.output(LCD_D7, False)
                if bits & 0x01 == 0x01:
                    GPIO.output(LCD_D4, True)
                if bits & 0x02 == 0x02:
                    GPIO.output(LCD_D5, True)
                if bits & 0x04 == 0x04:
                    GPIO.output(LCD_D6, True)
                if bits & 0x08 == 0x08:
                    GPIO.output(LCD_D7, True)

                # Toggle 'Enable' pin
                lcd_toggle_enable()


            def lcd_toggle_enable():
                # Toggle enable
                time.sleep(E_DELAY)
                GPIO.output(LCD_E, True)
                time.sleep(E_PULSE)
                GPIO.output(LCD_E, False)
                time.sleep(E_DELAY)            
            lcd_init()

            str_pad = " " * 16

            # DISPLAY
            print ("LCD " + state)
            lcd_string_fix(line1, LCD_LINE_1)
            time.sleep(2)
            lcd_string_fix(line2, LCD_LINE_1)
            my_long_string = str_pad + '; '.join('p{}: {}'.format(i, s) for i, s in enumerate(sensors))
            for i in range(0, len(my_long_string)):
                lcd_byte(LCD_LINE_2, LCD_CMD)
                lcd_text = my_long_string[i:(i+15)]
                lcd_string_scroll(lcd_text, 1)
                time.sleep(0.4)
            lcd_byte(LCD_LINE_2, LCD_CMD)
            lcd_string_scroll(str_pad, 1)

            time.sleep(0.05)
            
    def stop(self):
        self._stop.set()
            
    def displayState(self, text):
        self.state = text
    
    def setPressure(self, pressure):    
        self.pressure = pressure
        