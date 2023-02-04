import toml
from utils import BetterMqttClient
from shifter import Shifter
from protocol.gamepad_node_messages import *
from protocol.motor_messages import *
import time
import queue
from poweredup_motor import PoweredupMotor
global battery_status

def wait_for_hub_online(client):
    def battery_status_cb(topic, message_dict):
        msg = BatteryStatus.from_dict(message_dict)
        global battery_status
        battery_status = msg.charging_state

    client.register_callback(BatteryStatus.get_topic_static(), battery_status_cb)
    global battery_status
    battery_status = -1
    while battery_status < 0:
        client.publish_message(RequestBatteryStatus())
        time.sleep(0.5)

    time.sleep(1)
    print("HUB is online")

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
        self.events = queue.Queue()
        self.gamepad_handler_map = {}
        self.client.register_callback(DiscreteGamepadButton.get_topic_static(), self.discrete_gamepad_button_cb)
        self.shifter_available = False

        if "shifter" in self.config_dict:
            self.shifter_available = True
            shifter_config = self.config_dict["shifter"]
            for port in shifter_config["motor_ports"]:
                motor = PoweredupMotor(Port[port], self.client, False)
                motor.register(self.client)
                motor.run_at_speed(self.client, 0, 100)
                self.motors[Port[port]] = motor
            self.shifter = Shifter(Port[shifter_config["shifter_port"]], self.client)
            self.gamepad_handler_map[get_key_from_gamepad_discrete("r1", "pressed")]        = GamepadInputHandle(self.shifter.shift_up, True)
            self.gamepad_handler_map[get_key_from_gamepad_discrete("l1", "pressed")]        = GamepadInputHandle(self.shifter.shift_down, True)


            wait_for_hub_online(self.client)
            self.shifter.calibrate(self.client)

            for (gear,gear_config) in shifter_config["gears"].items():
                for (port, motor_config) in gear_config.items():
                    self.register_motor(port, motor_config, gear)

        if "direct_motors" in self.config_dict:
            direct_config = self.config_dict["direct_motors"]
            for port in direct_config["motor_ports"]:
                motor = PoweredupMotor(Port[port], self.client, False)
                motor.register(self.client)
                motor.run_at_speed(self.client, 0, 100)
                self.motors[Port[port]] = motor
            
            for (port, motor_config) in direct_config["motors"].items():
                self.register_motor(port, motor_config)
            
    def register_motor(self, port, config, gear=None):
        if config["type"] == "independent":
            self.register_independent_motor_cb(gear, Port[port], config)

        elif config["type"] == "tank":
            self.register_tank_motor_pair(gear, Port[port], config)
        

    def register_tank_motor_pair(self, gear, port, motor_config):                
        other_port = Port[motor_config["partner"]]
        side       = motor_config["side"]
        
        if gear is not None:
            key_pressed_forward                     = f'{get_key_from_gamepad_discrete("axis_top_bottom", "top")}:{gear}'
            key_pressed_backward                    = f'{get_key_from_gamepad_discrete("axis_top_bottom", "bottom")}:{gear}'
            key_pressed_forward_backward_stop       = f'{get_key_from_gamepad_discrete("axis_top_bottom", "released")}:{gear}'
            key_pressed_left                        = f'{get_key_from_gamepad_discrete("axis_left_right", "left")}:{gear}'
            key_pressed_right                       = f'{get_key_from_gamepad_discrete("axis_left_right", "right")}:{gear}'
            key_pressed_right_left_stop             = f'{get_key_from_gamepad_discrete("axis_left_right", "released")}:{gear}'
        else:
            key_pressed_forward                     = f'{get_key_from_gamepad_discrete("axis_top_bottom", "top")}'
            key_pressed_backward                    = f'{get_key_from_gamepad_discrete("axis_top_bottom", "bottom")}'
            key_pressed_forward_backward_stop       = f'{get_key_from_gamepad_discrete("axis_top_bottom", "released")}'
            key_pressed_left                        = f'{get_key_from_gamepad_discrete("axis_left_right", "left")}'
            key_pressed_right                       = f'{get_key_from_gamepad_discrete("axis_left_right", "right")}'
            key_pressed_right_left_stop             = f'{get_key_from_gamepad_discrete("axis_left_right", "released")}'

        def run_tank(client, motor_1_sign, motor_2_sign):
            self.motors[port].run_at_speed(client, motor_1_sign*motor_config["max_speed"]*motor_config["sign"], motor_config["max_power"])
            self.motors[other_port].run_at_speed(client, motor_2_sign*motor_config["max_speed"]*motor_config["partner_sign"], motor_config["max_power"])

        self.gamepad_handler_map[key_pressed_forward] = GamepadInputHandle(lambda client: run_tank(client, 1, 1), False)
        self.gamepad_handler_map[key_pressed_backward] = GamepadInputHandle(lambda client: run_tank(client, -1, -1), False)
        self.gamepad_handler_map[key_pressed_forward_backward_stop] = GamepadInputHandle(lambda client: run_tank(client, 0, 0), False)


        left_sign   = 1
        right_sign  = -1
        if side == "left": # If first motor is the left one, it needs to run backwards to turn left
            left_sign = -left_sign
            right_sign = -right_sign
        self.gamepad_handler_map[key_pressed_left] = GamepadInputHandle(lambda client: run_tank(client, left_sign, right_sign), False)
        self.gamepad_handler_map[key_pressed_right] = GamepadInputHandle(lambda client: run_tank(client, -left_sign, -right_sign), False)
        self.gamepad_handler_map[key_pressed_right_left_stop] = GamepadInputHandle(lambda client: run_tank(client, 0, 0), False)

    def register_independent_motor_cb(self, gear, port, motor_config):
        forward_button = motor_config["forward"]
        backward_button = motor_config["backward"]

        if gear is not None:
            key_pressed_forward     = f'{get_key_from_gamepad_discrete(forward_button, "pressed")}:{gear}'
            key_released_forward    = f'{get_key_from_gamepad_discrete(forward_button, "released")}:{gear}'
            key_pressed_backward    = f'{get_key_from_gamepad_discrete(backward_button, "pressed")}:{gear}'
            key_released_backward   = f'{get_key_from_gamepad_discrete(backward_button, "released")}:{gear}'
        else:
            key_pressed_forward     = f'{get_key_from_gamepad_discrete(forward_button, "pressed")}'
            key_released_forward    = f'{get_key_from_gamepad_discrete(forward_button, "released")}'
            key_pressed_backward    = f'{get_key_from_gamepad_discrete(backward_button, "pressed")}'
            key_released_backward   = f'{get_key_from_gamepad_discrete(backward_button, "released")}'

        self.gamepad_handler_map[key_pressed_forward]    = GamepadInputHandle(lambda client: self.motors[port].run_at_speed(client, motor_config["max_speed"]*motor_config["sign"], motor_config["max_power"]), False)
        self.gamepad_handler_map[key_released_forward]   = GamepadInputHandle(lambda client: self.motors[port].run_at_speed(client, 0, motor_config["max_power"]), False)
        self.gamepad_handler_map[key_pressed_backward]   = GamepadInputHandle(lambda client: self.motors[port].run_at_speed(client, -motor_config["max_speed"]*motor_config["sign"], motor_config["max_power"]), False)
        self.gamepad_handler_map[key_released_backward]  = GamepadInputHandle(lambda client: self.motors[port].run_at_speed(client, 0, motor_config["max_power"]), False)


    def discrete_gamepad_button_cb(self, topic, payload):
        message = DiscreteGamepadButton.from_dict(payload)
        self.events.put(message)

    def run(self):
        print("Running")
        for key in self.gamepad_handler_map:
            print(key)
        while True:
            e = self.events.get(block=True)
            key = get_key_from_gamepad_discrete(e.button_name, e.value)
            if key in self.gamepad_handler_map:
                self.gamepad_handler_map[key].cb(self.client)
                if self.gamepad_handler_map[key].clear_events:
                    self.events.queue.clear()
            if self.shifter_available:
                gear = self.shifter.gear
                if gear < 0:
                    print("WTF")
                    continue

                full_key = f"{key}:{gear}"
                if full_key in self.gamepad_handler_map:
                    self.gamepad_handler_map[full_key].cb(self.client)
                    if self.gamepad_handler_map[full_key].clear_events:
                        self.events.queue.clear()




nd = ShifterNode("shifter_config_gamepad.toml", "localhost")
nd.run()
