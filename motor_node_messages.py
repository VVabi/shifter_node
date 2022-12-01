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

    def from_dict(input_dict):
        return SetMotorPwm(
            input_dict['pwm'],
            Port[input_dict['port']],
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

    def from_dict(input_dict):
        return SetMotorSpeed(
            input_dict['pwm'],
            Port[input_dict['port']],
            input_dict['max_power'],
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

    def from_dict(input_dict):
        return MotorGoToPosition(
            input_dict['pwm'],
            Port[input_dict['port']],
            input_dict['max_power'],
            input_dict['target_angle'],
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

    def from_dict(input_dict):
        return MotorCommandFeedback(
            Port[input_dict['port']],
            input_dict['flags'],
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

    def from_dict(input_dict):
        return EnableModeUpdates(
            Port[input_dict['port']],
            input_dict['mode'],
            input_dict['notifications_enabled'],
            input_dict['delta'],
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

    def from_dict(input_dict):
        return MotorPositionUpdate(
            input_dict['position'],
            Port[input_dict['port']],
        )

class RequestBatteryStatus:
    def __init__(self):
        pass

    def to_dict(self):
        ret = dict()
        return ret

    def get_topic(self):
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

    def from_dict(input_dict):
        return BatteryStatus(
            input_dict['charging_state'],
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

    def from_dict(input_dict):
        return AttachmentInfo(
            input_dict['type_id'],
            input_dict['hw_rev'],
            input_dict['sw_rev'],
        )

class AttachedIo:
    def __init__(self, port_id, event, info):
        self.port_id = port_id #uint8
        self.event = event #uint8
        self.info = info #struct:AttachmentInfo

    def to_dict(self):
        ret = dict()
        ret['port_id'] = self.port_id
        ret['event'] = self.event
        ret['info'] = self.info.to_dict()
        return ret

    def get_topic(self):
        return 'brickcontrol/io/connection_update'

    def from_dict(input_dict):
        return AttachedIo(
            input_dict['port_id'],
            input_dict['event'],
            AttachmentInfo.from_dict(input_dict['info']),
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

    def from_dict(input_dict):
        return PortInformationRequest(
            input_dict['port_id'],
        )

