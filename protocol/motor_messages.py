import enum
class BleMessageType(enum.Enum):
    HubProperties = 0x01
    PortInformationRequest = 0x21
    PortInputFormatSetup = 0x41
    PortOutputCommand = 0x81
    PortOutputCommandFeedback = 0x82
    PortValue = 0x45
    HubAttached = 0x04

class Port(enum.Enum):
    A = 0
    B = 1
    C = 2
    D = 3

class SetMotorPwm:
    def __init__(self, pwm, port):
        self.pwm = pwm #int8
        self.port = port #enum:Port

    def to_dict(self):
        ret = dict()
        ret['pwm'] = self.pwm
        ret['port'] = self.port.name
        return ret

    def get_topic(self):
        return 'brickcontrol/motor/pwm'

    def get_topic_static():
        return 'brickcontrol/motor/pwm'

    def from_dict(input_dict):
        pwm = input_dict['pwm']
        port = Port[input_dict['port']]
        return SetMotorPwm(
            pwm,
            port,
        )

class SetMotorSpeed:
    def __init__(self, pwm, port, max_power):
        self.pwm = pwm #int8
        self.port = port #enum:Port
        self.max_power = max_power #uint8

    def to_dict(self):
        ret = dict()
        ret['pwm'] = self.pwm
        ret['port'] = self.port.name
        ret['max_power'] = self.max_power
        return ret

    def get_topic(self):
        return 'brickcontrol/motor/set_speed'

    def get_topic_static():
        return 'brickcontrol/motor/set_speed'

    def from_dict(input_dict):
        pwm = input_dict['pwm']
        port = Port[input_dict['port']]
        max_power = input_dict['max_power']
        return SetMotorSpeed(
            pwm,
            port,
            max_power,
        )

class MotorGoToPosition:
    def __init__(self, pwm, port, max_power, target_angle):
        self.pwm = pwm #int8
        self.port = port #enum:Port
        self.max_power = max_power #uint8
        self.target_angle = target_angle #int32

    def to_dict(self):
        ret = dict()
        ret['pwm'] = self.pwm
        ret['port'] = self.port.name
        ret['max_power'] = self.max_power
        ret['target_angle'] = self.target_angle
        return ret

    def get_topic(self):
        return 'brickcontrol/motor/go_to_position'

    def get_topic_static():
        return 'brickcontrol/motor/go_to_position'

    def from_dict(input_dict):
        pwm = input_dict['pwm']
        port = Port[input_dict['port']]
        max_power = input_dict['max_power']
        target_angle = input_dict['target_angle']
        return MotorGoToPosition(
            pwm,
            port,
            max_power,
            target_angle,
        )

class MotorCommandFeedback:
    def __init__(self, port, flags):
        self.port = port #enum:Port
        self.flags = flags #uint8

    def to_dict(self):
        ret = dict()
        ret['port'] = self.port.name
        ret['flags'] = self.flags
        return ret

    def get_topic(self):
        return 'brickcontrol/motor/output/command_feedback'

    def get_topic_static():
        return 'brickcontrol/motor/output/command_feedback'

    def from_dict(input_dict):
        port = Port[input_dict['port']]
        flags = input_dict['flags']
        return MotorCommandFeedback(
            port,
            flags,
        )

class EnableModeUpdates:
    def __init__(self, port, mode, notifications_enabled, delta):
        self.port = port #enum:Port
        self.mode = mode #uint8
        self.notifications_enabled = notifications_enabled #uint8
        self.delta = delta #uint32

    def to_dict(self):
        ret = dict()
        ret['port'] = self.port.name
        ret['mode'] = self.mode
        ret['notifications_enabled'] = self.notifications_enabled
        ret['delta'] = self.delta
        return ret

    def get_topic(self):
        return 'brickcontrol/generic/set_mode_update'

    def get_topic_static():
        return 'brickcontrol/generic/set_mode_update'

    def from_dict(input_dict):
        port = Port[input_dict['port']]
        mode = input_dict['mode']
        notifications_enabled = input_dict['notifications_enabled']
        delta = input_dict['delta']
        return EnableModeUpdates(
            port,
            mode,
            notifications_enabled,
            delta,
        )

class MotorPositionUpdate:
    def __init__(self, position, port):
        self.position = position #int32
        self.port = port #enum:Port

    def to_dict(self):
        ret = dict()
        ret['position'] = self.position
        ret['port'] = self.port.name
        return ret

    def get_topic(self):
        return 'brickcontrol/motor/output/position_update'

    def get_topic_static():
        return 'brickcontrol/motor/output/position_update'

    def from_dict(input_dict):
        position = input_dict['position']
        port = Port[input_dict['port']]
        return MotorPositionUpdate(
            position,
            port,
        )

class RequestBatteryStatus:
    def __init__(self):
        pass

    def to_dict(self):
        ret = dict()
        return ret

    def get_topic(self):
        return 'brickcontrol/battery/request_status'

    def get_topic_static():
        return 'brickcontrol/battery/request_status'

    def from_dict(input_dict):
        return RequestBatteryStatus(
        )

class BatteryStatus:
    def __init__(self, charging_state):
        self.charging_state = charging_state #uint8

    def to_dict(self):
        ret = dict()
        ret['charging_state'] = self.charging_state
        return ret

    def get_topic(self):
        return 'brickcontrol/battery/status'

    def get_topic_static():
        return 'brickcontrol/battery/status'

    def from_dict(input_dict):
        charging_state = input_dict['charging_state']
        return BatteryStatus(
            charging_state,
        )

class AttachmentInfo:
    def __init__(self, type_id, hw_rev, sw_rev):
        self.type_id = type_id #uint32
        self.hw_rev = hw_rev #int32
        self.sw_rev = sw_rev #int32

    def to_dict(self):
        ret = dict()
        ret['type_id'] = self.type_id
        ret['hw_rev'] = self.hw_rev
        ret['sw_rev'] = self.sw_rev
        return ret

    def get_topic(self):
        return 'unused'

    def get_topic_static():
        return 'unused'

    def from_dict(input_dict):
        type_id = input_dict['type_id']
        hw_rev = input_dict['hw_rev']
        sw_rev = input_dict['sw_rev']
        return AttachmentInfo(
            type_id,
            hw_rev,
            sw_rev,
        )

class AttachedIo:
    def __init__(self, port_id, event, info):
        self.port_id = port_id #uint8
        self.event = event #uint8
        self.info = info #list:struct:AttachmentInfo

    def to_dict(self):
        ret = dict()
        ret['port_id'] = self.port_id
        ret['event'] = self.event
        ret['info'] = self.info.to_dict()
        return ret

    def get_topic(self):
        return 'brickcontrol/io/connection_update'

    def get_topic_static():
        return 'brickcontrol/io/connection_update'

    def from_dict(input_dict):
        port_id = input_dict['port_id']
        event = input_dict['event']
        info = AttachmentInfo.from_dict(input_dict['info'])
        return AttachedIo(
            port_id,
            event,
            info,
        )

class PortInformationRequest:
    def __init__(self, port_id):
        self.port_id = port_id #uint8

    def to_dict(self):
        ret = dict()
        ret['port_id'] = self.port_id
        return ret

    def get_topic(self):
        return 'brickcontrol/generic/read_port'

    def get_topic_static():
        return 'brickcontrol/generic/read_port'

    def from_dict(input_dict):
        port_id = input_dict['port_id']
        return PortInformationRequest(
            port_id,
        )

