from motor_node_messages import *
import time

class PoweredupMotor():
    def __init__(self, port, client, enable_position_updates):
        self.ticks = 0
        self.port = port
        self.flags = []
        client.register_callback(MotorCommandFeedback(0, 0).get_topic(), self.on_motor_flags_update) #TODO

        if enable_position_updates:
            enable_mode_update = EnableModeUpdates(self.port, 2, 1, 5)
            client.publish_message(enable_mode_update)
            client.register_callback(MotorPositionUpdate(0, 0).get_topic(), self.on_angle_delta_update)

    def on_angle_delta_update(self, topic, payload):
        message = MotorPositionUpdate.from_dict(payload)

        if message.port == self.port:
            self.ticks = message.position

    def on_motor_flags_update(self, topic, payload):
        message = MotorCommandFeedback.from_dict(payload)

        if message.port == self.port:
            self.flags.append(message.flags)
    
    def go_to_position_blocking(self, client, speed, max_power, target):
        self.flags = []
        move = MotorGoToPosition(speed, self.port, max_power, target)
        client.publish_message(move)

        done = False
        while not done:
            time.sleep(0.1)
            for flag in self.flags:
                if flag & 8 != 0:
                    done = True
                    break

        self.flags = []

    def run_at_speed(self, client, speed, max_power):
        message = SetMotorSpeed(pwm=speed, port = self.port, max_power=max_power)
        client.publish_message(message)