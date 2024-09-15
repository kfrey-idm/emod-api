
class Updateable():
    """
    (Base) class that provides update() method for each class that inherits from this class.
    """
    def __init__(self):
        self.parameter_dict = {}

    def to_dict(self) -> dict:
        raise NotImplementedError

    def update(self, overlay_object):
        """
        Updates an object with the values from overlay_object.
        :param overlay_object: Object that is used to update self
        :return: None
        """
        # loop over all member variables and try to call update() method, if object does not have update() method just assign new value.
        for v_node, v_overlay_node in zip(vars(self).items(), vars(overlay_object).items()):
            if v_overlay_node[1] is not None:     # only update if object contains something (e.g. non empty list or dict) and is not None
                try:
                    # Try to call update() method
                    vars(self)[v_node[0]].update(v_overlay_node[1])
                except AttributeError:
                    # print("Object does not have update() method.")
                    vars(self)[v_node[0]] = v_overlay_node[1]
                except Exception as e:
                    print("Neither update() method could be called, nor simple value assignment was possible.")
                    print(e)
                    exit(-1)

    def add_parameter(self, key, value):
        """
        Adds a user defined key-value pair to demographics.
        :param key: Key
        :param value: Value
        :return: None
        """
        self.parameter_dict[key] = value