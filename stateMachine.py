# -*- coding: utf-8 -*-

import threading
import Queue


class StateMachine:
    debug = True
    # --------------------------------------
    # DEFINED STATES
    # --------------------------------------
    START_ENTRY = 'START_ENTRY'
    START = 'START'
    START_EXIT = 'START_EXIT'
    
    LAST_ENTRY = 'LAST_ENTRY'
    LAST = 'LAST'
    
    # --------------------------------------
    # VACUUM CHAMBER STATES
    # --------------------------------------
    # STATE 0 : CHAMBER VENTED
    STATE_0_ENTRY = 'STATE_0_ENTRY'
    STATE_0 = 'STATE 0'
    STATE_0_EXIT = 'STATE_0_EXIT'

    # STATE 1 : ESTABLISH VACUUM
    STATE_1_PP_ENTRY = 'STATE_1_PP_ENTRY'
    STATE_1_PP = 'STATE 1 PP'
    STATE_1_PP_EXIT = 'STATE_1_PP_EXIT'

    STATE_1_HVGV_ENTRY = 'STATE_1_HVGV_ENTRY'
    STATE_1_HVGV = 'STATE 1 HVGV'
    STATE_1_HVGV_EXIT = 'STATE_1_HVGV_EXIT'

    STATE_1_TMP_ENTRY = 'STATE_1_TMP_ENTRY'
    STATE_1_TMP = 'STATE 1 TMP'
    STATE_1_TMP_EXIT = 'STATE_1_TMP_EXIT'

    # STATE 2 : MAINTAIN VACUUM
    STATE_2_ENTRY = 'STATE_2_ENTRY'
    STATE_2 = 'STATE 2'
    STATE_2_EXIT = 'STATE_2_EXIT'

    # STATE 3 : VENTING CHAMBER
    STATE_3_ENTRY = 'STATE_3_ENTRY'
    STATE_3 = 'STATE 3'
    STATE_3_EXIT = 'STATE_3_EXIT'

    # STATE 4 : SAFE STATE
    STATE_4_ENTRY = 'STATE_4_ENTRY'
    STATE_4 = 'STATE 4'
    STATE_4_EXIT = 'STATE_4_EXIT'
    
    def __init__(self, queue, app):
        self.app = app
        self.queue = queue
        self.state = None
        self.changeState(self.START)

        self._stop = threading.Event()
        self.thread = threading.Thread(target=self.run)
        self.thread.setName('StateMachine')
        self._stop.clear()
        self.thread.start()

    def run(self):
        # 
        lastState = None
        while True:

            state = self.nextState()
            if self.debug:
                if state != lastState:
                    print("State: " + state)
                    lastState = state
                    
            if state == None:
                pass
            # --------------------------------------
            # START
            # --------------------------------------
            elif state == self.START_ENTRY:
                print("START")
                self.app.callback_Sample('application started')
                pass
            
            elif self.state == self.START:
                try:
                    command = self.queue.get(True, 0.1)
                    if self.debug:
                        print ("Command " + command)
                except Queue.Empty:
                    continue
                self.changeState(self.STATE_0)
            
            elif self.state == self.START_EXIT:
                pass

            # --------------------------------------
            # STATE 0
            # --------------------------------------
            elif state == self.STATE_0_ENTRY:
                print("STATE 0")
                self.app.callback_displayState(self.STATE_0)  # Display State 0 on LCD screen
                self.app.callback_log_command(self.STATE_0)
                pass
            
            elif self.state == self.STATE_0:
                try:
                    command = self.queue.get(True, 0.1)
                    if self.debug:
                        print ("Command " + command)
                except Queue.Empty:
                    continue

                if command == 'VC_vacuum':
                    self.changeState(self.STATE_1_PP)  # Go to STATE 1 PP
                
                if command == 'local':
                    self.changeState(self.LOCAL)  # Go to LOCAL mode
                else:
                    self.add.

                # stop is mandatory in each state
                if command == 'stop':
                    self.changeState(self.LAST)
                    
            elif self.state == self.STATE_0_EXIT:
                pass

            # --------------------------------------
            # STATE 1 - ESTABLISH VACUUM
            # --------------------------------------

            #STATE 1 PP
            elif state == self.STATE_1_PP_ENTRY:
                print("STATE 1 PP")
                self.app.callback_displayState(self.STATE_1_PP)
                self.app.callback_pp_on()
                start_time = time.time()
                pass

            elif self.state == self.STATE_1_PP:
                try:
                    command = self.queue.get(True, 0.1)
                    if self.debug:
                        print ("Command " + command)
                except Queue.Empty:
                    continue

                if command == 'tick':
                    if time.time() - start_time > 3600*5:
                        # log in error log
                        self.changeState(self.STATE_4)  # Go to STATE 4 - SAFE MODE
                    elif self.app.check_p3_sup_p1():  # Check if P3 > P1
                        self.changeState(self.STATE_1_HVGV)  # Go to STATE 1 HVGV

                if command == 'stop':
                    self.changeState(self.LAST)

            elif self.state == self.STATE_1_PP_EXIT:
                pass

            #STATE 1 HVGV
            elif state == self.STATE_1_HVGV_ENTRY:
                print("STATE 1 HVGV")
                self.app.callback_displayState(self.STATE_1_HVGV)
                self.app.callback_hvgv_on()
                start_time = time.time()
                pass

            elif self.state == self.STATE_1_HVGV:
                try:
                    command = self.queue.get(True, 0.1)
                    if self.debug:
                        print ("Command " + command)
                except Queue.Empty:
                    continue

                if command == 'tick':
                    if self.app.check_pressure_reached():
                        if time.time() - start_time > 3600*5:
                            # log in error log
                            self.changeState(self.STATE_4)  # Go to STATE 4 - SAFE MODE
                        elif self.app.check_p1_inf_10pwmin1mbar():  # Check if P1 > 10^(-1)
                            self.changeState(self.STATE_1_TMP)  # Go to STATE 1 TMP

                if command == 'stop':
                    self.changeState(self.LAST)

            elif self.state == self.STATE_1_HVGV_EXIT:
                pass

            # STATE 1 TMP
            elif state == self.STATE_1_TMP_ENTRY:
                print("STATE 1 TMP")
                self.app.callback_displayState(self.STATE_1_TMP)
                self.app.callback_tmp_on()
                start_time = time.time()
                pass

            elif self.state == self.STATE_1_TMP:
                try:
                    command = self.queue.get(True, 0.1)
                    if self.debug:
                        print ("Command " + command)
                except Queue.Empty:
                    continue

                if command == 'tick':
                    if self.app.check_pressure_reached():
                        if time.time() - start_time > 3600*60:
                            # log in error log
                            self.changeState(self.STATE_4)  # Go to STATE 4 - SAFE MODE
                        elif self.app.check_p2_inf_10pwmin4mbar():  # Check if P2 < 10^(-4)
                            if self.app.check_p2_inf_10pwmin5mbar():
                                self.changeState(self.STATE_2)  # Go to STATE 2 - MAINTAIN VACUUM

                if command == 'stop':
                    self.changeState(self.LAST)

            elif self.state == self.STATE_1_TMP_EXIT:
                pass

            # --------------------------------------
            # STATE 2 - MAINTAIN VACUUM
            # --------------------------------------
            elif state == self.STATE_2_ENTRY:
                print("STATE 2")
                self.app.callback_displayState(self.STATE_2)
                pass

            elif self.state == self.STATE_2:
                try:
                    command = self.queue.get(True, 0.1)
                    if self.debug:
                        print ("Command " + command)
                except Queue.Empty:
                    continue

                if command == '':  # Check if HVGV open
                    # log in error log
                    self.changeState(self.STATE_4)  # Go to STATE 4 - SAFE MODE
                    if self.app.check_p3_sup_5x10pwmin2mbar():
                        # log in error log
                        self.changeState(self.STATE_4)
                    elif self.app.check_p2_sup_10pwmin5mbar():
                        self.app.callback_displayState('WARNING')
                        if self.app.check_p2_sup_10pwmin2mbar():
                            # log in error log
                            self.changeState(self.STATE_4)
                        elif command == 'VC_vent':
                            self.changeState(self.STATE_3)  # Go to STATE 3 - VENTING CHAMBER
                    elif command == 'VC_vent':
                        self.changeState(self.STATE_3)  # Go to STATE 3 - VENTING CHAMBER

                if command == 'stop':
                    self.changeState(self.LAST)

            elif self.state == self.STATE_2_EXIT:
                pass

            # --------------------------------------
            # STATE 3 - VENTING CHAMBER
            # --------------------------------------
            elif state == self.STATE_3_ENTRY:
                print("STATE 3")
                self.app.callback_displayState(self.STATE_3)
                self.app.callback_hvgv_off()  # Close HVGV
                self.app.callback_tmp_off()  # Switch OFF TMP
                pass

            elif self.state == self.STATE_3:
                try:
                    command = self.queue.get(True, 0.1)
                    if self.debug:
                        print ("Command " + command)
                except Queue.Empty:
                    continue

                if command == 'pp_on':
                    self.changeState(self.P0)

                if command == 'stop':
                    error = "Error 5502"  # Send error 5502
                    self.app.read_error_txt(error)
                    self.changeState(self.STATE_4)
                elif mode == 'local':
                    error = "Error 5521"  # Send error 5502 to chamber control
                    self.app.read_error_txt(error)
                    self.changeState(self.STATE_1_LOCAL)
                else:
                    self.app.callback_pp_off()  # Switch OFF PP
                    self.app.callback_vv_on()  # Open Venting Valve
                    start_time = time.time()
                    time.sleep(10)  # Wait 10 sec

                    counter = 0
                    while self.app.get_dp_dt_p1() < 0 and self.app.get_dp_dt_p2() < 0:
                        counter += 1
                        if counter < 3:
                            self.app.callback_vv_on()
                            time.sleep(10)
                        else:
                            # log error
                            self.changeState(self.STATE_4)
                    time.sleep(30)
                    # log error
                    while time.time() - start_time < 100:  # Value TBD to vent the chamber
                        time.sleep(30)
                    self.app.callback_vv_off()
                    self.changeState(self.STATE_0)

            elif self.state == self.STATE_3_EXIT:
                pass

            # --------------------------------------
            # STATE 4
            # --------------------------------------
            elif state == self.STATE_4_ENTRY:
                print("STATE 4")
                self.app.callback_displayState(self.STATE_4)
                # log command
                # log error
                self.app.callback_hvgv_off()  # Close HVGV
                pass

            elif self.state == self.STATE_4:
                try:
                    command = self.queue.get(True, 0.1)
                    if self.debug:
                        print ("Command " + command)
                except Queue.Empty:
                    continue

                if self.app.check_hvgv_off():
                    self.app.callback_vv_off()
                    if self.app.check_vv_off():
                        self.app.callback_tmp_off()
                        if self.app.check_tmp_off():
                            # log error
                            if command == "VC_vent":
                                self.changeState(self.STATE_3)
                            elif command == "VC_vacuum":
                                self.changeState(self.STATE_1_PP)
                            elif command == "local":
                                error = "Error 5521"  # Send error 5502
                                self.app.read_error_txt(error)
                                self.changeState(self.LOCAL)

                if command == 'stop':
                    self.changeState(self.LAST)

            elif self.state == self.STATE_4_EXIT:
                pass

            # --------------------------------------
            # LAST
            # --------------------------------------
            elif state == self.LAST_ENTRY:
                pass
            elif self.state == self.LAST:
                return
            #
            # ===========================================
            #
            else:
                print("fatal: unknown state " + self.state)
                
    def changeState(self, newState):
        if self.state == None:
            self.transition = [newState+'_ENTRY', newState]
        else:
            self.transition = [self.state+'_EXIT', newState+'_ENTRY', newState]
        self.state = newState
        
    def nextState(self):
        if len(self.transition) > 0:
            n = self.transition[0]
            self.transition = self.transition[1:]
            return n
        return self.state 

    def stop(self):
        # allow the state machine to gracefully stop
        self.queue.put("stop")           
        