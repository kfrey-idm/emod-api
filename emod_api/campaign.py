#!/usr/bin/env python
"""
You use this simple campaign builder by importing it, adding valid events via "add", and writing it out with "save".
"""

import json

schema_path = None
campaign_dict = {}
campaign_dict["Events"] = []
campaign_dict["Use_Defaults"] = 1
pubsub_signals_subbing = []
pubsub_signals_pubbing = []
adhocs = []
event_map = {}
use_old_adhoc_handling = False

def reset():
    del( campaign_dict["Events"][:] )
    global pubsub_signals_subbing
    global pubsub_signals_pubbing
    global adhocs
    global event_map
    del( pubsub_signals_subbing[:] )
    del( pubsub_signals_pubbing[:] )
    del( adhocs[:] )
    event_map = {}
    from emod_api import schema_to_class as s2c
    s2c.schema_cache = None

def set_schema( schema_path_in ):
    """
    Set the (path to) the schema file. And reset all campaign variables. This is essentially a "start_building_campaign" function.
    Args:
        schema_path_in. The path to a schema.json.
    Returns:
        N/A.
    """
    reset()
    global schema_path 
    schema_path = schema_path_in


def add( event, name=None, first=False ):
    """
    Add a complete campaign event to the campaign builder. The new event is assumed to be a Python dict, and a 
    valid event. The new event is not validated here. 
    Set the first flag to True if this is the first event in a campaign because it functions as an
    accumulator and in some situations like sweeps it might have been used recently.
    """
    event.finalize()
    if first:
        print( "Use of first flag is deprecated. Use set_schema to start build a new, empty campaign." )
        global campaign_dict
        campaign_dict["Events"] = []

    if "Event_Name" not in event and name is not None:
        event["Event_Name"] = name
    if "Listening" in event:
        pubsub_signals_subbing.extend( event["Listening"] )
        event.pop( "Listening" )
    if "Broadcasting" in event:
        pubsub_signals_pubbing.extend( event["Broadcasting"] )
        event.pop( "Broadcasting" )
    campaign_dict["Events"].append( event )


trigger_list = None
def get_trigger_list():
    global trigger_list
    if get_schema():
        # This needs to be fixed in the schema post-processor: maybe create a new idmTime:EventEnum and replace all the occurrences with a reference to that.
        try:
            trigger_list = get_schema()["idmTypes"]["idmAbstractType:EventCoordinator"]["BroadcastCoordinatorEvent"]["Broadcast_Event"]["enum"]
        except Exception as ex:
            trigger_list = get_schema()["idmTypes"]["idmType:IncidenceCounter"]["Trigger_Condition_List"]["Built-in"]
    return trigger_list

def save( filename="campaign.json" ):
    """
    Save 'camapign_dict' as 'filename'.
    """
    #campaign_dict["ADHOCS"] = event_map

    with open( filename, "w" ) as camp_file:
        json.dump( campaign_dict, camp_file, sort_keys=True, indent=4 )

    # For now we just print to screen the events discovered for human inspection.
    # TBD: 1) Check for any published-but-not-listened events.
    # TBD: 2) Check for any listened-but-not-published events -- but many events come from model, not campaign.
    # TBD: 3) Discover ad-hoc events (those not in schema) and map to GP_EVENTS.

    import copy
    ignored_events = copy.deepcopy(set(pubsub_signals_pubbing))
    non_camp_events = set()
    if len( pubsub_signals_pubbing ) > 0:
        print( "Campaign is publishing the following events:" )
        for event in set( pubsub_signals_pubbing ):
            print( event )
    if len( pubsub_signals_subbing ) > 0:
        print( "Campaign is listening to the following events:" )
        for event in set(pubsub_signals_subbing):
            if event in ignored_events:
                ignored_events.remove( event )
            else:
                non_camp_events.add( event )
            print( event )
    if len( ignored_events ) > 0:
        print( "Campaign is IGNORING the following events:" )
        for event in set( ignored_events ):
            print( event )
    if len( non_camp_events ) > 0:
        print( "WARNING: Campaign or Report is configured to LISTEN to the following non-campaign events:" )
        for event in set( non_camp_events ):
            print( event )
            if event in get_adhocs():
                print( "\nERROR: Report is configured to LISTEN to the following non-existent 'trigger':" )
                raise RuntimeError( "Please fix above error." ) 
    return filename

def get_adhocs():
    return event_map

def get_schema():
    schema = None
    if schema_path and not schema:
        with open( schema_path ) as schema_file:
            schema = json.load( schema_file )
    return schema

def get_recv_trigger( trigger, old=use_old_adhoc_handling ):
    """
    Get the correct representation of a trigger (also called signal or even event) that is being listened to.
    """
    pubsub_signals_subbing.append( trigger )
    return get_event( trigger, old )

def get_send_trigger( trigger, old=use_old_adhoc_handling ):
    """
    Get the correct representation of a trigger (also called signal or even event) that is being broadcast.
    """
    pubsub_signals_pubbing.append( trigger )
    return get_event( trigger, old )

def get_event( event, old=False ):
    """
    Basic placeholder functionality for now. This will map new ad-hoc events to GP_EVENTs and manage that 'cache'
    If event in built-ins, return event, else if in adhoc map, return mapped event, else add to adhoc_map and return mapped event.
    """
    if event is None or event == "":
        raise ValueError( "campaign.get_event() called with an empty event. Please specify a string." )

    return_event = None
    global trigger_list
    if trigger_list is None:
        trigger_list = get_trigger_list()

    if event in trigger_list:
        return_event = event
    elif event in event_map:
        return_event = event_map[event] 
    else:
        # get next entry in GP_EVENT_xxx
        new_event_name = event if old else 'GP_EVENT_{:03d}'.format(len(event_map))
        event_map[event] = new_event_name 
        return_event = event_map[event]
    return return_event