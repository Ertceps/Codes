########################################################################################################################

#  VACUUM CHAMBER CONTROL  #

########################################################################################################################

# -+- IMPORT -+-
import Queue
import time
import stateMachine
import switches
import outputs
import display
import logging
import sensors
import TCPCommunicatorClient

import testing
#
# set to true for automated test
test = False


class Application:
    _eventQueue = None
    last_time = 0
    p1_last_value = None
    p2_last_value = None
    p3_last_value = None
    
    def __init__(self):
        self._eventQueue = Queue.Queue()
        # Create Outputs
        self.di = display.Display() 
        self.ou = outputs.Outputs()
        self.tcp = TCPCommunicatorClient.TCPIP()
         # Create State Machine
        self.sm = stateMachine.StateMachine(self._eventQueue, self)
        # Create Inputs
        self.sw = switches.Switches(self._eventQueue) 
        # Create Sensors
        self.se = sensors.Sensors(self._eventQueue)
        
        if test:
            self.te = testing.Test(self._eventQueue, self)
        pass
    
    def stop(self):
        self.sw.stop()
        self.sm.stop()
        self.di.stop()
        self.se.stop()
        if test:
            self.te.stop()

    #-------------------------
    # DEFINE CALLBACK HANDLERS
    #-------------------------
    def callback_Sample(self, text):
        print (text)

    # PUMPS AND VALVES

    def callback_pp_on(self):
        self.ou.pp_on()
        self.pp = True
    def check_pp_on(self):
        if self.pp:
            return True
        else:
            return False
        
    def callback_pp_off(self):
        self.ou.pp_off()
        self.pp = False
    def check_pp_off(self):
        if self.pp:
            return False
        else:
            return True

    def callback_tmp_on(self):
        self.ou.tmp_on()
        self.tmp = True
    def check_tmp_on(self):
        if self.tmp:
            return True
        else:
            return False

    def callback_tmp_off(self):
        self.ou.tmp_off()
        self.tmp = False
    def check_tmp_off(self):
        if self.tmp:
            return False
        else:
            return True

    def callback_hvgv_on(self):
        self.ou.hvgv_on()
        self.hvgv = True
    def check_hvgv_on(self):
        if self.hvgv:
            return True
        else:
            return False

    def callback_hvgv_off(self):
        self.ou.hvgv_off()
        self.hvgv = False
    def check_hvgv_off(self):
        if self.hvgv:
            return False
        else:
            return True

    def callback_vv_on(self):
        self.ou.vv_on()
        self.vv = True
    def check_vv_on(self):
        if self.vv:
            return True
        else:
            return False

    def callback_vv_off(self):
        self.ou.vv_off()
        self.vv = False
    def check_vv_off(self):
        if self.vv:
            return False
        else:
            return True

    # LCD
    def callback_displayState(self, stateText):
        self.di.displayState(stateText)    

    # SENSORS
    def check_p3_sup_p1(self, sensors):
        if sensors[1] < sensors[3]:
            return True

    def check_p1_inf_10pwmin1mbar(self, sensors):
        if sensors[1] < 10^(-1):
            return True

    def check_p2_inf_10pwmin4mbar(self, sensors):
        if sensors[2] < 10^(-4):
            return True

    def check_p2_inf_10pwmin5mbar(self, sensors):
        if sensors[2] < 10^(-5):
            return True

    def setPressure(self, sensors):
        self.sensors = sensors
        self.di.setPressure(sensors)
        time = times.time()

        # Sensors 1 and 2 (Pirani 1 and Cold Cathod 2) take the pressure in the VC
        # Sensor 3 (Pirani 3) take the pressure in the pipe between the PP and TMP
        if self.p1_last_value != None:
            self.dp_dt_p1 = (sensors[1] - self.p1_last_value) / (time - self.last_time)
        if self.p2_last_value != None:
            self.dp_dt_p2 = (sensors[1] - self.p2_last_value) / (time - self.last_time)
        if self.p3_last_value != None:
            self.dp_dt_p3 = (sensors[1] - self.p3_last_value) / (time - self.last_time)

        self.last_time = time
        self.p1_last_value = sensors[1]
        self.p2_last_value = sensors[2]
        self.p3_last_value = sensors[3]

    def get_dp_dt_p1(self):
        return self.dp_dt_p1  # Positive if pressure increase - Negative otherwise

    def get_dp_dt_p2(self):
        return self.dp_dt_p2  # Positive if pressure increase - Negative otherwise

    def get_dp_dt_p3(self):
        return self.dp_dt_p3  # Positive if pressure increase - Negative otherwise


    # LOGGING
    def setup_logger(logger_name, log_file, level=logging.INFO):
        l = logging.getLogger(logger_name)
        formatter = logging.Formatter('%(asctime)s : %(message)s')
        fileHandler = logging.FileHandler(log_file, mode='w')
        fileHandler.setFormatter(formatter)
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)

        l.setLevel(level)
        l.addHandler(fileHandler)
        l.addHandler(streamHandler)

    def callback_read_error_txt(self, error_num):
        global contents
        global send_error
        f = open(error_num + ".txt", "r")
        contents = f.readlines()
        if 'Critical' in contents:
            send_error = True
        f.close()
        log_error = logging.getLogger('error')
        name = contents[1]
        message = contents[2]
        cause = contents[3]
        solution = contents[4]
        log_error.error('Name: ' + name + ' Message: ' + message + ' Cause: ' + cause + ' Solution: ' + solution)

    def callback_log_command(self, name):
        command = logging.getLogger('command')
        command.info(name)



if test:
    print("TEST TEST TEST")  
          
app = Application()
try:
    while True:
        time.sleep(0.1)
       
except KeyboardInterrupt:
    app.stop()
    