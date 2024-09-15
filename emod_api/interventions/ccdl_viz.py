"""
Early draft of a very handy utility that takes a CCDL file (Concise Campaign Definition Language)
and creates a graph(viz) visualization of it.

"""
import sys
import graphviz # This makes emod-api dependent on graphviz. Might be nice if this was optional?
from emod_api.interventions.ccdl import *

debug = False

def get_nickname_from_event( event_num, pieces ):
    """
    Allow nodes to get briefer and potentially more helpful nicknames. Default will probably remain a
    the nasty autogen above. Users can override this function with a callback of their own.
    """
    # If user has manually added an optional 5th 'column', use that, but turns certain characters into newlines.
    if len(pieces)==5:
        event_name = pieces[4].strip().replace( " ", "\n" ).replace("->","%%%").replace( "-", "\n" ).replace( "%%%", "->" )
    else:
        event_name = f"[{event_num}]{pieces[WHEN_IDX]}*{pieces[WHERE_IDX]}*{pieces[WHO_IDX]}"
    return event_name 


def get_colour_from_event( tokens ): 
    """
    Allow nodes to get a content-dependent colour. Default to just white. Users can override this function with 
    a callback of their own. Have been using colour to capture IP categories. 
    """
    return "white" 

def get_shape_from_event( tokens ):
    """
    Allow nodes to get a content-dependent shape. Default to circle. Users can override this function with 
    a callback of their own. Have been using shape to capture 'epoch' categories. Possible shapes include ellipse, circle, square, and diamond.  Full list can be found at: https://www.graphviz.org/doc/info/shapes.html
    """
    return "circle" 


def set_beautifiers( name_cb=None, colour_cb=None, shape_cb=None ):
    """
    Override default no-op callbacks for setting nicknames, colours, and shapes of campaign nodes
    """
    global get_nickname_from_event, get_colour_from_event, get_shape_from_event
    if name_cb:
        get_nickname_from_event = name_cb
    if colour_cb:
        get_colour_from_event = colour_cb
    if shape_cb:
        get_shape_from_event = shape_cb
    return

def viz( in_name = "campaign.ccdl", out_name = "camp.sv", display = True, whitelist = None ): 
    ccdl = open( in_name ).readlines()
    dot = graphviz.Digraph(out_name, comment='Patient Pathway Design')

    producers = {}
    consumers = {}
    # Don't see how to avoid a specific list here. Not complete, needs more diagnostics.
    broadcasters = ["BroadcastEvent", "SimpleHealthSeekingBehavior", "DiagnosticTreatNeg" ]

    event_names = {}
    event_num = 0
    for camp_event in ccdl:
        if debug:        
            print( f"Processing line {camp_event}." )

        # We're going to do a brute force purge of DelayedInterventions for now.
        pieces = camp_event.strip().split( main_sep )
        if len(pieces)<2:
            event_num += 1
            continue

        if "Outbreak" in pieces[-1]:
            # It is useful to 'hack' a few lines so that major infection lifecycle events get tied into
            # our visualization.
            camp_event = camp_event.replace( pieces[-1], pieces[-1]+"+BroadcastEvent(TBActivation)" )
            pieces = camp_event.strip().split( main_sep )

        # Color represents IP
        # Shape represents Epoch
        node_name = get_nickname_from_event( event_num, pieces )
        event_names[event_num] = node_name
        node_color = get_colour_from_event(pieces)
        node_shape = get_shape_from_event(pieces)

        if debug:
            print( f"Creating node with name {event_names[event_num]}." )
        dot.node( name=event_names[event_num], style='filled', fillcolor = node_color, shape=node_shape )
        triggered = pieces[WHAT_IDX].split( post_trigger_sep )
        if len(triggered)>1:
            triggers = triggered[0].strip()
            for trigger in triggers.split( multi_trigger_sep ):
                if trigger not in consumers:
                    consumers[trigger] = set() 
                consumers[trigger].add( event_num )

        triggeree = triggered[-1].split( post_delay_sep )[-1].strip()
        for broadcaster in broadcasters:
            sender = (triggeree.split( multi_iv_sep )[-1]).strip()
            if broadcaster in sender:
                from parse import parse
                regex = broadcaster + "({})"
                #print( f"Looking for {regex} in {sender}" )
                tokens = parse( regex, sender )
                signals = tokens[0]
                for signal in signals.split( multi_signal_sep ):
                    #print( f"Found an event broadcasting {signal}" )
                    if signal not in producers:
                        producers[signal] = set()
                    producers[signal].add( event_num )
        event_num += 1

    if debug:
        print( "PRODUCERS\n" )
        print( producers )
        print( "\nCONSUMERS\n" )
        print( consumers )

    # This is a list so we can do more than 1 eventually but for now lets just do 1.
    event_whitelist = []
    if whitelist:
        event_whitelist.append( whitelist )

    for event in producers:
        if event_whitelist and event not in event_whitelist:
            continue
        senders = producers[event]
        if event in consumers:
            receivers = consumers[event]
            for from_event in senders:
                for to_event in receivers:
                    # Reject edges where IPs don't "overlap"
                    ip_from = ccdl[from_event].split( main_sep )[2].split("/")[1] if "/" in ccdl[from_event].split( main_sep )[2] else "*"
                    ip_to = ccdl[to_event].split( main_sep )[2].split("/")[1] if "/" in ccdl[to_event].split( main_sep )[2] else "*"
                    #if ip_to != "*" and ip_from != "*" and ip_from.split(":")[0] == ip_to.split(":")[0] and ip_from.split(":")[1] != ip_to.split(":")[1]:
                    if ip_to != "*" and ip_from != "*":
                        ip_from_key = ip_from.split("=")[0]
                        ip_from_value = ip_from.split("=")[1]
                        ip_to_key = ip_to.split("=")[0]
                        ip_to_value = ip_to.split("=")[1]
                        if ip_from_key == ip_to_key and ip_from_value != ip_to_value:
                            continue # aka do not continue

                    # Reject edges where Times don't "overlap"
                    time_from = ccdl[from_event].split( main_sep )[0]
                    if "(" in time_from:
                        time_from = time_from.split( "(" )[0]
                    time_to = ccdl[to_event].split( main_sep )[0]
                    time_from_start = time_from
                    time_to_start = time_to
                    time_from_end = 1e9
                    time_to_end = 1e9
                    if "-" in time_from:
                        time_from_start = float(time_from.split("-")[0])
                        time_from_end = float(time_from.split("-")[1])
                    if "-" in time_to:
                        time_to_start = float(time_to.split("-")[0])
                        time_to_end = float(time_to.split("-")[1])
                    time_from_start = float(time_from_start)
                    time_to_start = float(time_to_start)
                    if time_from_end <= time_to_start or time_from_start >= time_to_end:
                        if debug:
                            print( f"Discarding edge from {from_event} to {to_event} because not overlapping in time." )
                            print( time_from_start, time_from_end, time_to_start, time_to_end )
                        continue
                    if debug:
                        #print( f"Creating edge from {from_event} to {to_event} for {event}." )
                        #print( f"{from_event} ---{event} ---> {to_event}" )
                        print( f"{event_names[from_event]} ---{event} ---> {event_names[to_event]}" )
                    #dot.edge( from_event, to_event, name=event )
                    dot.edge( str(event_names[from_event]), str(event_names[to_event]), label=event )

    # Honestly not sure what the most general-purpose display solution is for graphviz
    # This seems to generate a pdf and open the registered pdf viewer if there is one.
    dot.render( view=True )
    

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--ccdl', help='Path to existing campaign in CCDL format.', default= "campaign.ccdl" )
    parser.add_argument('-w', '--whitelist', help='Optional trigger to limit visualization to.', default=None )

    args = parser.parse_args()
    viz( args.ccdl, args.whitelist )
