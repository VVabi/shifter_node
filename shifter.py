import paho.mqtt.client as mqtt
import json
from motor_node_messages import *
import time
import numpy as np
from poweredup_motor import PoweredupMotor
from utils import BetterMqttClient

class Shifter():
    def __init__(self, motor_port, client):
        self.busy = False
        self.motor = PoweredupMotor(motor_port, client, True)
        self.shift_start_angle  = 0
        self.calibrated         = False
        self.gear               = -1
        self.locked             = False

    def calibrate(self, client):
        self.motor.go_to_position_blocking(client, 30, 60, 1000)
        self.motor.go_to_position_blocking(client, 30, 60, -1000)

        time.sleep(1) # necessary because current angle may not be up to date
        self.shift_start_angle = self.motor.ticks
        self.gear = 0
        self.calibrated = True

    def set_gear(self, new_gear, client):
        self.gear = int(np.clip(new_gear, 0, 3))
        new_gear_angle = self.shift_start_angle+self.gear*90
        
        if np.abs(new_gear_angle-self.motor.ticks) > 10:
            self.motor.go_to_position_blocking(client, 10, 60, new_gear_angle)

    def shift_up(self, client):
        self.set_gear(self.gear+1, client)

    def shift_down(self, client):
        self.set_gear(self.gear-1, client)

"""shifter = Shifter(Port.B, "localhost")
shifter.calibrate()
shifter.set_gear(0)
shifter.set_gear(1)
shifter.set_gear(2)
shifter.set_gear(3)
shifter.set_gear(1)
shifter.set_gear(0)
shifter.set_gear(3)
shifter.set_gear(2)
shifter.set_gear(1)
shifter.set_gear(0)"""