from emod_api import schema_to_class as s2c
import json
import copy

cached_NSA = None
cached_NSNL = None


def do_nodes(schema_path, node_ids: list = None):
    """
        Create and return a NodeSetConfig based on node_ids list.

    Args:
        schema_path: Path to schema.json file.
        node_ids: a list of NodeIDs, defaults to None, which is NodeSetAll

    Returns:
        Well-configured NodeSetConfig
    """
    if node_ids and len(node_ids) > 0:
        global cached_NSNL
        if cached_NSNL is None:
            cached_NSNL = s2c.get_class_with_defaults("NodeSetNodeList", schema_path)
        nodelist = copy.deepcopy(cached_NSNL)
        nodelist.Node_List = node_ids
    else:
        global cached_NSA
        if cached_NSA is None:
            cached_NSA = s2c.get_class_with_defaults("NodeSetAll", schema_path)
        nodelist = copy.deepcopy(cached_NSA)
    return nodelist


def get_waning_from_params(schema_path, initial=1.0, box_duration=365, decay_rate=0, decay_time_constant=None):
    """
        Get well-configured waning structure. Default is 1-year full efficacy box.
        Note that an infinite decay rate (0 or even -1) is same as WaningEffectBox.
        Note that an infinite box duration (-1) is same as WaningEffectConstant.
        Note that a zero box duration is same as WaningEffectExponential.

    Args:
        schema_path: Path to schema.json file.
        initial: Initial_Effect value, defaults to 1.0.
        box_duration: Number of timesteps efficacy remains at Initial_Effect before decay. Defaults to 365.
        decay_rate: Rate at which Initial_Effect decays after box_duration. Defaults to 0.
        decay_time_constant: 1/decay_rate. Defaults to None. Use this or decay_rate, not both.
            If this is specified, decay_rate is ignored.

    Returns:
        A well-configured WaningEffect structure

      .. deprecated:: 2.x
       Please use function get_waning_from_parameters() or get_waning_from_points().
    """
    waning = get_waning_from_parameters(schema_path, initial, box_duration, decay_rate, decay_time_constant)
    return waning


def get_waning_from_points(schema_path, initial: float = 1.0, times_values=None, expire_at_end: bool = False):
    """
        Get well-configured waning structure.

    Args:
        schema_path: Path to schema.json file.
        initial: Initial_Effect value, defaults to 1.0.
        times_values: A list of tuples with days and values. The values match the defined linear values that modify the
            Initial_Effect, e.g. [(day_0, value_0), (day_5, value_5)].
        expire_at_end: Set to 1 to have efficacy go to zero and let the intervention expire when the end of
            the map is reached.  Only vaccines and bednet usage currently support this expiration feature.
            defaults to 0.

    Returns:
        A well-configured WaningEffectMapLinear structure
    """
    if times_values is None:
        raise ValueError(f"ERROR: No points to create a waning function given.")

    if s2c.uses_old_waning(schema_path):
        waning = s2c.get_class_with_defaults("WaningEffectMapLinear", schema_path)
        waning.Expire_At_Durability_Map_End = int(expire_at_end)
    else:
        waning = s2c.get_class_with_defaults("WaningEffect", schema_path)
    times, values = zip(*times_values)
    waning.Durability_Map.Times = list(times)
    waning.Durability_Map.Values = list(values)
    waning.Initial_Effect = initial
    return waning


def get_waning_from_parameters(schema_path, initial: float = 1.0, box_duration: float = 365,
                               decay_rate: float = 0, decay_time_constant: float = None):
    """
        Get well-configured waning structure. Default is 1-year full efficacy box.
        Note that an infinite decay rate (0 or even -1) is same as WaningEffectBox.
        Note that an infinite box duration (-1) is same as WaningEffectConstant.
        Note that a zero box duration is same as WaningEffectExponential.

    Args:
        schema_path: Path to schema.json file.
        initial: Initial_Effect value, defaults to 1.0.
        box_duration: Number of timesteps efficacy remains at Initial_Effect before decay. Defaults to 365.
        decay_rate: Rate at which Initial_Effect decays after box_duration. Defaults to 0.
        decay_time_constant: 1/decay_rate. Defaults to None. Use this or decay_rate, not both.
            If this is specified, decay_rate is ignored.

    Returns:
        A well-configured WaningEffect structure
    """
    if s2c.uses_old_waning(schema_path):
        if box_duration == -1:
            waning = s2c.get_class_with_defaults("WaningEffectConstant", schema_path)
        else:
            if decay_time_constant is None:
                decay_time_constant = 1.0/decay_rate if decay_rate > 0 else 0

            if box_duration == 0 and decay_time_constant > 0:
                waning = s2c.get_class_with_defaults("WaningEffectExponential", schema_path)
                waning.Decay_Time_Constant = decay_time_constant
            elif box_duration > 0 and decay_time_constant == 0:
                waning = s2c.get_class_with_defaults("WaningEffectBox", schema_path)
                waning.Box_Duration = box_duration
            elif box_duration > 0 and decay_time_constant > 0:
                waning = s2c.get_class_with_defaults("WaningEffectBoxExponential", schema_path)
                waning.Decay_Time_Constant = decay_time_constant
                waning.Box_Duration = box_duration
            else:
                raise ValueError(f"ERROR: Cannot create a valid waning structure with box_duration={box_duration} and decay_time_constant={decay_time_constant}.")

        waning.Initial_Effect = initial
    else:
        waning = s2c.get_class_with_defaults("WaningEffect", schema_path)
        waning.Initial_Effect = initial

        if decay_time_constant is None:
            decay_time_constant = 1.0 / decay_rate if decay_rate > 0 else 0
        waning.Decay_Time_Constant = decay_time_constant

        if box_duration != -1:
            waning.Box_Duration = box_duration
    return waning


def _convert_prs(kvps):
    """
    This function is not intended to be called directly by users but rather by emod_api.interventions.common
    API functions. It is intended to allow users to target interventions to individuals with specific 
    individual properties without having to worry about the particular data structures that the DTK uses.
    The permissible structures do need to be documented in the relevant API functions.
    kvps needs to be one of:
    - "key:value"
    - "key=value"
    - "key1:value1,key2:value2"
    - "key1=value1,key2=value2"
    - { "key": "value" }
    - { "key1": "value1", "key2": "value2" }
    - [  { "key1": "value1", "key2": "value2" }, { "key3": "value3", "key4": "value4" } ]
    - [ "key:value" ]
    - [ "key1:value1", "key2:value2" ]
    Note that the key-value-pairs _values_ are not currently validated against the selected demographics file.
    In the current implementation, the return value is prepped as a value for Property_Restrictions_Within_Nodes

    Args:
        kvps: any of the above
        
    Returns:
        list of dictionaries of key-value-pairs where each dict can only contain a given key once.
        E.g., [ { "Risk": "High" } ]
    """

    def parse_list_of_strings(entries):
        ret_kvps = []
        prs_as_dict = dict()
        for entry in entries:
            if ":" in entry:
                key, value = entry.split(':')
                prs_as_dict[key.strip()] = value.strip()
            elif "=" in entry:
                key, value = entry.split('=')
                prs_as_dict[key.strip()] = value.strip()
            else:
                raise ValueError(
                    f"ERROR: malformed property targets: {kvps}. "
                    f"Can't figure out where the keys and values are in at least one of the list entries.")
        ret_kvps = [prs_as_dict]
        return ret_kvps

    ret_kvps = []
    if kvps is None or kvps == "":
        ret_kvps = list()  # just happen to know default is empty list, not getting from schema
    elif type(kvps) is str and len(kvps) > 0:
        entries = kvps.split(',')
        ret_kvps = parse_list_of_strings(entries)
    elif type(kvps) is dict:
        ret_kvps = [kvps]
    elif type(kvps) is list:
        if len(kvps) > 0:
            if type(kvps[0]) in [dict, set]:
                ret_kvps = kvps  # could check the contents of the list...
            elif type(kvps[0]) is str:
                ret_kvps = parse_list_of_strings(kvps)
            else:
                raise ValueError(
                    f"ERROR: malformed property targets: {kvps}. The input is a list but not of strings or dicts.")
    else:
        raise ValueError(f"ERROR: malformed property targets: {kvps}.")

    # TBD: Let's keep simple things simple and leave complex solutions for complex cases.
    # Do not return list of dicts unless complex case.
    if len(ret_kvps) == 1:
        string_list = []
        for key, value in dict(ret_kvps[0]).items():
            string_list.append(f"{key}:{value}")
        ret_kvps = string_list
    return ret_kvps
