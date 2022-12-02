import toml
from utils import BetterMqttClient
from shifter import Shifter
from protocol.gamepad_node_messages import *
from protocol.motor_messages import *
import time
import queue
from poweredup_motor import PoweredupMotor

def get_key_from_gamepad_discrete(button_name, value):
    return f"{button_name}:{value}"

class GamepadInputHandle():
    def __init__(self, cb, clear_events):
        self.cb = cb
        self.clear_events = clear_events

class ShifterNode():
    def __init__(self, config_path, host):
        with open(config_path) as fh:
            self.config_dict = toml.load(fh)
        print(self.config_dict)
        self.client  = BetterMqttClient(host)
        self.motors = {}
        for port in self.config_dict["motor_ports"]:
            motor = PoweredupMotor(Port[port], self.client, False)
            motor.run_at_speed(self.client, 0, 100)
            self.motors[Port[port]] = motor


        self.shifter = Shifter(Port[self.config_dict["shifter_port"]], self.client)
        self.shifter.calibrate(self.client)
        if self.config_dict["control_type"] == "gamepad_direct":
            self.client.register_callback(DiscreteGamepadButton.get_topic_static(), self.discrete_gamepad_button_cb)
            self.gamepad_handler_map = {}
            self.gamepad_handler_map[get_key_from_gamepad_discrete("r1", "pressed")]        = GamepadInputHandle(self.shifter.shift_up, True)
            self.gamepad_handler_map[get_key_from_gamepad_discrete("l1", "pressed")]        = GamepadInputHandle(self.shifter.shift_down, True)
            self.gamepad_handler_map_by_gear = {}
        self.events = queue.Queue()

        for gear in self.config_dict["gears"]:
            gear_config = self.config_dict["gears"][gear]

            
            for port in self.config_dict["motor_ports"]:
                if port in gear_config:
                    motor_config = gear_config[port]
                    if motor_config["type"] == "independent":
                        self.register_independent_motor_cb(gear, Port[port], motor_config)

                    elif motor_config["type"] == "tank":
                        self.register_tank_motor_pair(gear, Port[port], motor_config)

    def register_tank_motor_pair(self, gear, port, motor_config):                
        other_port = Port[motor_config["partner"]]
        side       = motor_config["side"]
        key_pressed_forward                     = f'{get_key_from_gamepad_discrete("axis_top_bottom", "top")}:{gear}'
        key_pressed_backward                    = f'{get_key_from_gamepad_discrete("axis_top_bottom", "bottom")}:{gear}'
        key_pressed_forward_backward_stop       = f'{get_key_from_gamepad_discrete("axis_top_bottom", "released")}:{gear}'

        def run_tank(client, motor_1_sign, motor_2_sign):
            self.motors[port].run_at_speed(client, motor_1_sign*motor_config["max_speed"]*motor_config["sign"], motor_config["max_power"])
            self.motors[other_port].run_at_speed(client, motor_2_sign*motor_config["max_speed"]*motor_config["partner_sign"], motor_config["max_power"])

        self.gamepad_handler_map_by_gear[key_pressed_forward] = lambda client: run_tank(client, 1, 1)
        self.gamepad_handler_map_by_gear[key_pressed_backward] = lambda client: run_tank(client, -1, -1)
        self.gamepad_handler_map_by_gear[key_pressed_forward_backward_stop] = lambda client: run_tank(client, 0, 0)

        key_pressed_left                    = f'{get_key_from_gamepad_discrete("axis_left_right", "left")}:{gear}'
        key_pressed_right                   = f'{get_key_from_gamepad_discrete("axis_left_right", "right")}:{gear}'
        key_pressed_right_left_stop       = f'{get_key_from_gamepad_discrete("axis_left_right", "released")}:{gear}'


        left_sign   = 1
        right_sign  = -1
        if side == "left": # If first motor is the left one, it needs to run backwards to turn left
            left_sign = -left_sign
            right_sign = -right_sign
        self.gamepad_handler_map_by_gear[key_pressed_left] = lambda client: run_tank(client, left_sign, right_sign)
        self.gamepad_handler_map_by_gear[key_pressed_right] = lambda client: run_tank(client, -left_sign, -right_sign)
        self.gamepad_handler_map_by_gear[key_pressed_right_left_stop] = lambda client: run_tank(client, 0, 0)

    def register_independent_motor_cb(self, gear, port, motor_config):
        forward_button = motor_config["forward"]
        backward_button = motor_config["backward"]

        key_pressed_forward     = f'{get_key_from_gamepad_discrete(forward_button, "pressed")}:{gear}'
        key_released_forward    = f'{get_key_from_gamepad_discrete(forward_button, "released")}:{gear}'
        key_pressed_backward    = f'{get_key_from_gamepad_discrete(backward_button, "pressed")}:{gear}'
        key_released_backward   = f'{get_key_from_gamepad_discrete(backward_button, "released")}:{gear}'
        
        self.gamepad_handler_map_by_gear[key_pressed_forward]    = lambda client: self.motors[port].run_at_speed(client, motor_config["max_speed"]*motor_config["sign"], motor_config["max_power"])
        self.gamepad_handler_map_by_gear[key_released_forward]   = lambda client: self.motors[port].run_at_speed(client, 0, motor_config["max_power"])
        self.gamepad_handler_map_by_gear[key_pressed_backward]   = lambda client: self.motors[port].run_at_speed(client, -motor_config["max_speed"]*motor_config["sign"], motor_config["max_power"])
        self.gamepad_handler_map_by_gear[key_released_backward]  = lambda client: self.motors[port].run_at_speed(client, 0, motor_config["max_power"])


    def discrete_gamepad_button_cb(self, topic, payload):
        message = DiscreteGamepadButton.from_dict(payload)
        self.events.put(message)

    def run(self):
        while True:
            e = self.events.get(block=True)
            key = get_key_from_gamepad_discrete(e.button_name, e.value)

            if key in self.gamepad_handler_map:
                self.gamepad_handler_map[key].cb(self.client)
                if self.gamepad_handler_map[key].clear_events:
                    self.events.queue.clear()
            else:
                gear = self.shifter.gear

                if gear < 0:
                    continue

                full_key = f"{key}:{gear}"
                if full_key in self.gamepad_handler_map_by_gear:
                    self.gamepad_handler_map_by_gear[full_key](self.client)


nd = ShifterNode("shifter_config_gamepad.toml", "localhost")
nd.run()



