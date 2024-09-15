from emod_api import schema_to_class as s2c
import json
import copy

cached_NSA = None
cached_NSNL = None
def do_nodes( schema_path, node_ids ):
    """
        Create and return a NodeSetConfig based on node_ids list.
    """
    if node_ids and len(node_ids) > 0:
        global cached_NSNL
        if cached_NSNL is None:
            cached_NSNL  = s2c.get_class_with_defaults( "NodeSetNodeList", schema_path )
        nodelist = copy.deepcopy(cached_NSNL)
        nodelist.Node_List = node_ids
    else:
        global cached_NSA
        if cached_NSA is None:
            cached_NSA  = s2c.get_class_with_defaults( "NodeSetAll", schema_path )
        nodelist = copy.deepcopy( cached_NSA )
    return nodelist


def get_waning_from_params( schema_path, initial=1.0, box_duration=365, decay_rate=0, decay_time_constant=None ):
    """
        Get well configured waning structure. Default is 1-year full efficacy box.
        Note that an infinite decay rate (0 or even -1) is same as Box.
        Note that an infinite box duration (-1) is same as constant.
        Note that a zero box duration is same as Exponential.
        
    Args:
        schema_path: Path to schema.json file.
        initial: Initial efficacy value, defaults to 1.0.
        box_duration: Number of timesteps efficacy remains at initial before decay. Defaults to 365.
        decay_rate: Rate at which efficacy decays after box_duration. Defaults to 0.
        decay_time_constant: 1/decay_rate. Defaults to None. Use this or decay_rate, not both. If this is specified, decay_rate is ignored.

    """

    waning = None
    if box_duration == -1:
        waning = s2c.get_class_with_defaults( "WaningEffectConstant", schema_path )
    else:
        waning = s2c.get_class_with_defaults( "WaningEffectBoxExponential", schema_path )
        waning.Box_Duration = box_duration
        if decay_time_constant:
            waning.Decay_Time_Constant = decay_time_constant
        else:
            if decay_rate > 0: # -1 really
                waning.Decay_Time_Constant = 1.0/decay_rate
            else:
                waning.Decay_Time_Constant = 0

    waning.Initial_Effect = initial
    return waning


def _convert_prs( kvps ):
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
        list of dictionaries of key-value-pairs where each dict can only contain a given key once. E.g., [ { "Risk": "High" } ]
    """
    def parse_list_of_strings( entries ):
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
                raise ValueError( f"ERROR: malformed property targets: {kvps}. Can't figure out where the keys and values are in at least one of the list entries." )
        ret_kvps = [ prs_as_dict ]
        return ret_kvps 

    ret_kvps = []
    if kvps is None or kvps == "":
        ret_kvps = list() # just happen to know default is empty list, not getting from schema
    elif type(kvps) is str and len(kvps)>0:
        entries = kvps.split(',')
        ret_kvps = parse_list_of_strings( entries )
    elif type(kvps) is dict:
        ret_kvps = [kvps]
    elif type(kvps) is list:
        if len(kvps)>0:
            if type(kvps[0]) in [ dict, set ]:
                ret_kvps = kvps # could check the contents of the list...
            elif type(kvps[0]) is str:
                ret_kvps = parse_list_of_strings( kvps )
            else:
                raise ValueError( f"ERROR: malformed property targets: {kvps}. The input is a list but not of strings or dicts." )
    else:
        raise ValueError( f"ERROR: malformed property targets: {kvps}." )

    # TBD: Let's keep simple things simple and leave complex solutions for complex cases.
    # Do not return list of dicts unless complex case.
    if len(ret_kvps) == 1:
        string_list = []
        for key, value in dict(ret_kvps[0]).items():
            string_list.append( f"{key}:{value}" )
        ret_kvps = string_list
    return ret_kvps 

