import enum
class ContinuousGamepadButton:
    def __init__(self, button_name, value):
        self.button_name = button_name #string
        self.value = value #int32

    def to_dict(self):
        ret = dict()
        ret['button_name'] = self.button_name
        ret['value'] = self.value
        return ret

    def get_topic(self):
        return 'gamepad/continuous'

    def get_topic_static():
        return 'gamepad/continuous'

    def from_dict(input_dict):
        button_name = input_dict['button_name']
        value = input_dict['value']
        return ContinuousGamepadButton(
            button_name,
            value,
        )

class DiscreteGamepadButton:
    def __init__(self, button_name, value):
        self.button_name = button_name #string
        self.value = value #string

    def to_dict(self):
        ret = dict()
        ret['button_name'] = self.button_name
        ret['value'] = self.value
        return ret

    def get_topic(self):
        return 'gamepad/discrete'

    def get_topic_static():
        return 'gamepad/discrete'

    def from_dict(input_dict):
        button_name = input_dict['button_name']
        value = input_dict['value']
        return DiscreteGamepadButton(
            button_name,
            value,
        )

