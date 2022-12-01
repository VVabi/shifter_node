import toml
from utils import BetterMqttClient
from shifter import Shifter
from gamepad_messages import *
from motor_node_messages import *
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
        self.shifter = Shifter(Port[self.config_dict["shifter_port"]], self.client)
        self.shifter.calibrate(self.client)
        if self.config_dict["control_type"] == "gamepad_direct":
            self.client.register_callback(DiscreteGamepadButton.get_topic_static(), self.discrete_gamepad_button_cb)
            self.gamepad_handler_map = {}
            self.gamepad_handler_map[get_key_from_gamepad_discrete("r1", "pressed")]        = GamepadInputHandle(self.shifter.shift_up, True)
            self.gamepad_handler_map[get_key_from_gamepad_discrete("l1", "pressed")]        = GamepadInputHandle(self.shifter.shift_down, True)
            self.gamepad_handler_map_by_gear = {}
        self.events = queue.Queue()

        self.motors = {}
        for port in self.config_dict["motor_ports"]:
            self.motors[Port[port]] = PoweredupMotor(Port[port], self.client, False)

        self.gamepad_config_by_gear = []
        for gear in self.config_dict["gears"]:
            gear_config = self.config_dict["gears"][gear]

            if gear_config["type"] == "independent":
                for port in self.config_dict["motor_ports"]:
                    if port in gear_config:
                        motor_config = gear_config[port]
                        self.register_independent_motor_cb(gear, Port[port], motor_config)

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



