#!/usr/bin/env python3
import json
from parse import parse 

from emod_api.interventions.ccdl import *
presets = {}
trigger_map = {}

def decorate_actual_iv( iv, signal=None ):
    return decorate_actual_iv_impl( iv, signal )

def decorate_actual_iv_impl( iv, signal=None ):
    """
        This function converts json interventions to their CCDL versions. This relies on a lot of special-casing.
    """
    orig_iv_name = iv["class"]
    iv_name = orig_iv_name

    if signal:
        iv_name = f"{signal}->{iv_name}"

    if orig_iv_name == "PropertyValueChanger":
        key = iv["Target_Property_Key"]
        value = iv["Target_Property_Value"]
        iv_name += f"({key}:{value})"
    elif orig_iv_name == "MigrateIndividuals":
        dest = iv["NodeID_To_Migrate_To"]
        iv_name += f"({dest})"
    elif orig_iv_name.endswith( "DelayedIntervention" ): # handle more than 1 kind of DelayedIntervention
        key = "Delay_Period_Distribution" if "Delay_Period_Distribution" in iv else "Delay_Distribution"
        dist = iv[key].replace("_DURATION","")
        if dist == "FIXED" or dist == "EXPONENTIAL":
            dist += f"/{iv['Delay_Period']}"
        elif dist == "UNIFORM":
            if 'Delay_Period_Min' in iv:
                the_min = iv['Delay_Period_Min']
            else:
                the_min = 0
            dist += f"/{the_min}/{iv['Delay_Period_Max']}"
        elif dist == "GAUSSIAN":
            dist += f"/{iv['Delay_Period_Mean']}/{iv['Delay_Period_Std_Dev']}"
        elif dist == "WEIBULL":
            dist += f"/{iv['Delay_Period_Scale']}/{iv['Delay_Period_Shape']}"
        iv_name += f"({dist})"
        if "Broadcast_Event" in iv:
            actual = iv["Broadcast_Event"]
            be = f"=>BroadcastEvent({actual})" 
            iv_name += be
    elif orig_iv_name == "BroadcastEvent":
        signal = iv["Broadcast_Event"]
        if signal in trigger_map:
            signal = trigger_map[signal]
        iv_name += f"({signal})"
    elif orig_iv_name == "SimpleHealthSeekingBehavior":
        # special case for HIV/rakai
        # if "Intervention_Name" in iv:
        #    iv_name += iv["Intervention_Name"]
        # goal = iv["New_Property_Value"] 
        goal = iv["Actual_IndividualIntervention_Event"]
        if goal in trigger_map:
            goal = trigger_map[goal]
        tendency = iv["Tendency"]
        name = iv["Intervention_Name"]
        if name != "HSB":
            iv_name += f"({goal}/{tendency}/{name})"
        else:
            iv_name += f"({goal}/{tendency})"
    elif "Diagnostic" in orig_iv_name or "DrawBlood" in orig_iv_name:
        try:
            pos = iv["Positive_Diagnosis_Event"]
            if pos in trigger_map:
                pos = trigger_map[pos]
            if "Negative_Diagnosis_Event" in iv:
                neg = iv["Negative_Diagnosis_Event"]
                if neg in trigger_map:
                    neg = trigger_map[neg]
            else:
                neg = "null" # this is ugly; do better.
            iv_name += f"({pos}/{neg})"
        except Exception as ex:
            print( f"Exception {ex} assuming key in {iv_name}." )

    ### THESE WILL BE MOVED INTO A DISEASE-SPECIFIC EXTENSION OF THIS FILL THAT CALLS
    ### INTO THE BASE EMOD_API FILE

    ### HIV
    elif orig_iv_name == "HIVMuxer":
        signal = iv["Broadcast_Event"]
        if colorize:
            iv_name += f"({console.highlight(signal, textColor=textColor.RED)})"
        else:
            iv_name += f"({signal})"
    #elif orig_iv_name == "HIVDelayedIntervention":
        #signal = iv["Broadcast_Event"]
        #iv_name += f"({console.highlight(signal, textColor=textColor.RED)})"
    elif orig_iv_name == "HIVRandomChoice":
        choices = iv["Choices"]
        iv_name += f"({choices})"
    elif orig_iv_name == "PMTCT":
        eff = iv["Efficacy"]
        iv_name += f"({eff})"
    #elif orig_iv_name == "HIVRapidHIVDiagnostic":
    #elif orig_iv_name in [ "HIVRapidHIVDiagnostic", "DiagnosticTreatNeg", "" ]:

    ### MALARIA
    elif orig_iv_name == "AntimalarialDrug":
        drug = iv["Drug_Type"]
        iv_name += f"({drug})"
    return iv_name

def handle_di( iv ):
    new_iv_name = "=>"
    if "Actual_IndividualIntervention_Configs" in iv: # DelayedIntervention
        for act_iv in iv["Actual_IndividualIntervention_Configs"]:
            new_iv_name += decorate_actual_iv( act_iv )
            new_iv_name += multi_iv_sep 
    elif "Actual_IndividualIntervention_Config" in iv: # HIVDelayedIntervention
        new_iv_name += decorate_actual_iv( iv )
        new_iv_name += multi_iv_sep 
    elif "Broadcast_Event" in iv: # HIVDelayedIntervention
        new_iv_name += f"Broadcast_Event({iv['Broadcast_Event']})"
    return new_iv_name.strip( multi_iv_sep )

def get_ip( coord ):
    ip = None
    if "Property_Restrictions" in coord:
        ip = coord["Property_Restrictions"]
        if len(ip)==0:
            ip = ""
        else:
            ip = str(ip).strip("[").strip("]").strip("'").replace(":","=")
    elif "Property_Restrictions_Within_Node" in coord:
        ips = coord["Property_Restrictions_Within_Node"][0]
        if len(ips)>0:
            ip = ""
            for ip_key, ip_value in ips.items():
                ip += f"{ip_key}={ip_value}"
                ip += ","
            ip = ip.strip(",")
    return ip

def get_ages( coord ):
    min_age = 0
    max_age = 120*365
    try:
        if "Target_Age_Min" in coord and float(coord["Target_Age_Min"]) > 0:
            min_age = coord["Target_Age_Min"]
        if "Target_Age_Max" in coord and float(coord["Target_Age_Max"]) < 120*365:
            max_age = coord["Target_Age_Max"]
    except Exception as ex:
        print( "Exception extracting ages." )
        print( str( ex ) )
    return min_age, max_age

def decode( camp_path, config_path=None ):
    def get_when( event ):
        if 'Start_Day' in event:
            day = int(event['Start_Day'])
        else:
            day = 1
        coord = event['Event_Coordinator_Config']
        if coord["class"] != "StandardInterventionDistributionEventCoordinator":
            #print( f"DEBUG: {coord['class']} not fully supported yet." )
            frac = "???"
            #continue
        if 'Number_Repetitions' in coord and coord['Number_Repetitions'] != 1:
            reps = coord['Number_Repetitions']
            gap = None
            if coord['Timesteps_Between_Repetitions'] != -1:
                gap = coord['Timesteps_Between_Repetitions']
            day = f"{day}(x{reps}/_{gap})"
        return day

    def get_where( event ):
        nc = event['Nodeset_Config']
        if nc["class"] == "NodeSetAll":
            nodes = "AllPlaces"
        else:
            nodes = nc["Node_List"]
        return nodes

    def get_who( coord, frac, sex, ip, min_age, max_age ):
        if "Demographic_Coverage" in coord and frac == 1:
            frac = coord["Demographic_Coverage"]
        if "Target_Gender" in coord and sex == "Both":
            sex = coord["Target_Gender"]
        min_age, max_age = get_ages( coord )
        tmp_ip = get_ip( coord )
        if tmp_ip:
            ip = tmp_ip

        who = "STEERED" if type(frac) is str else f"{float(frac)*100}%"
        if "ale" in sex:
            who += f"/{sex}"
        if min_age > 0:
            who += f"/>{min_age}"
        if max_age < 120*365.:
            who += f"/<{max_age}"
        if ip and ip != "" and ip != "None":
            who += f"/{ip}"
        return who

    def get_what( event, day ):
        iv = event['Event_Coordinator_Config']['Intervention_Config']
        iv_name = decorate_actual_iv( iv )
        sex = "Both"
        ip = None
        min_age = None
        max_age = None
        duration = None
        frac = 1
        if event['Event_Coordinator_Config']["class"] != "StandardInterventionDistributionEventCoordinator":
            frac = "???"
        if iv_name == "NodeLevelHealthTriggeredIV":
            signals = iv["Trigger_Condition_List"]
            new_signals = []
            for signal in signals:
                if signal in trigger_map:
                    signal = trigger_map[signal]
                new_signals.append( signal )
            signal = multi_iv_sep.join( new_signals )
            if "Demographic_Coverage" in iv:
                frac = iv["Demographic_Coverage"]
            if "Target_Gender" in iv:
                sex = iv["Target_Gender"]
            ip = get_ip( iv )
            min_age, max_age = get_ages( iv )
            duration = iv["Duration"]
            if duration != -1:
                day = f"{day}-{day+duration}"
            iv = iv["Actual_IndividualIntervention_Config"]
            iv_name = decorate_actual_iv( iv, signal )
        if iv_name.startswith( "MultiInterventionDistributor" ) or iv_name.split(post_trigger_sep)[-1].startswith( "MultiInterventionDistributor" ):
            iv_name = iv_name.strip( "MultiInterventionDistributor" ) # not sure about this yet
            new_iv_name = ""
            for act_iv in iv["Intervention_List"]:
                new_iv_name += decorate_actual_iv( act_iv )
                new_iv_name += multi_iv_sep
            iv_name += new_iv_name.strip( multi_iv_sep )
            if iv_name.split(multi_iv_sep)[-1].startswith( "DelayedIntervention" ): # ugly copy-paste
                iv_name += handle_di( act_iv )
        if iv_name.split(post_trigger_sep)[-1].startswith( "DelayedIntervention" ): # we should have a heuristic, or a list
            iv_name += handle_di( iv )

        return iv_name, frac, sex, ip, min_age, max_age, day

    if config_path is not None:
        global trigger_map
        with open( config_path ) as conf:
            params = json.load( conf )["parameters"]
            if "Event_Map" in params:
                trigger_map = params["Event_Map"]
        #print( f"DEBUG: Found {trigger_map.keys()} in config." )
    with open( camp_path ) as camp:
        cj = json.load( camp )
    print( f"{ len( cj['Events'] ) }" )

    for event in cj['Events']:
        ip = ""
        try:
            # when
            day = get_when( event )

            # where
            nodes = get_where( event )

            # what
            iv_name, frac, sex, ip, min_age, max_age, day = get_what( event, day )

            # who
            who = get_who( event['Event_Coordinator_Config'], frac, sex, ip, min_age, max_age  )

            print( f"{day} :: {nodes} :: {who} :: {iv_name}" )

        except Exception as ex:
            print( "Exception..." )
            print( str( ex ) )
            print( str( event ) )

def params_to_dict( start_day, reps=None, gap=None, nodes=None, frac=None, sex=None, minage=None, maxage=None, ips=None, signal=None, iv_name=None, payload=None, delay=None ):
    """
    Take all the CCDL params (When? Where? Who? What? Why?) and create a dictionary from them.
    """
    new_dict = {}
    new_dict[ "start_day" ] = start_day
    if reps:
        new_dict[ "reps" ] = reps
        new_dict[ "gap" ] = gap
    new_dict[ "nodes" ] = nodes
    new_dict[ "frac" ] = frac
    if sex:
        new_dict[ "sex" ] = sex
    if minage:
        new_dict[ "minage" ] = minage
    if maxage:
        new_dict[ "maxage" ] = maxage
    if ips:
        new_dict[ "ips" ] = ips

    if signal:
        new_dict[ "signal" ] = signal
    if delay:
        new_dict[ "delay" ] = delay
    new_dict[ "iv_name" ] = iv_name
    if payload:
        new_dict[ "payload" ] = payload
    return new_dict


def encode( encoded_path ):
    """
    The encode function takes a CCDL files as input and returns a list of campaign events as dictionaries that can be used to create a campaign json from it using emod-api/emodpy functions.
    This is early code, use at your own risk, or contribute to its improvement. :)
    """
    output_list = []
    from parse import parse
    # TBD: Check that encoded_path exists and is the right format.
    with open( encoded_path ) as ccdl:
        encoded = ccdl.readlines()
    for line in encoded:
        data = line.split( main_sep )
        if len(data)==1:
        # might be a map preset
            tokens = line.split("=")
            if "=" in line and "map" in tokens[0].lower():
                presets[tokens[0]]=eval(tokens[1].strip())
            continue
        # print( data )

        # extract start_day, and optional repetition number and intervale
        when = data[WHEN_IDX]
        if "(" in when:
            result = parse( "{}(x{}/_{})", when )
            start_day = result[0]
            reps = result[1]
            gap = result[2]
        else:
            start_day = float(when)
            reps = None
            gap = None
        #print( f"{start_day}" )
        #print( f"{reps}" )
        #print( f"{gap}" )

        # extract node list, usually All
        where = data[WHERE_IDX]
        nodes = []
        if "All" not in where:
            nodelist = parse( "[{}]", where )
            nodes.extend( [int(x.strip(',')) for x in nodelist[0].split()] )

        # extract coverage, and optional min age, max age, sex, and IPs.
        who = data[WHO_IDX]
        whos = who.split("/")
        if whos[0] == "STEERED":
            print( "DEBUG: Reference Tracking not supported yet." )
            continue
        frac = float(whos[0].strip("%"))/100
        sex = None
        minage = None
        maxage = None
        ips = None
        if len(whos)>1 and "ale" in whos[1]:
            sex = whos[1]
        if len(whos)>1:
            for who_elem in whos[1:]:
                if who_elem.startswith(">"):
                    minage = float(who_elem.strip(">"))
                elif who_elem.startswith("<"):
                    maxage = float(who_elem.strip("<"))
                elif "=" in who_elem: # IP has to include a=b
                    ips = who_elem
        # format: coverage/minage/maxage/sex/IPs
        #print( f"{frac}" )

        # extract interventions; this is where we'll do most of our work.
        what = data[WHAT_IDX]
        signal = None
        if post_trigger_sep in what:
            splits = what.split(post_trigger_sep)
            signal = splits[0] # We're going to be calling TriggeredCampaignEvent(...)
            what = splits[1]
        #interventions = what.split(".")
        interventions = what.split("=>")
        print( f"DEBUG: interventions = {interventions}" )
        delay = None
        payload = None
        for iv in interventions:
            # check for multiintervention first.
            if multi_iv_sep in iv: # multi-iv
                # ladies & gentlemen, we have ourselves a multiintervention...
                iv_name = []
                payload = []
                for iv in iv.split(multi_iv_sep):
                    result = parse( "{}({})", iv.strip() )
                    try:
                        iv_name.append( result[0] )
                        payload.append( result[1] )
                    except Exception as ex:
                        print( f"DEBUG: Failed to parse {iv} using standard intervention format." )
                        iv_name.append( iv )
                        payload.append( "" )
            elif "(" in iv: # payload
                result = parse( "{}({})", iv.strip() )
                try:
                    iv_name = result[0]
                    payload = result[1]
                    if iv_name == "DelayedIntervention":
                        delay=payload # handle delay as its own thing
                except Exception as ex:
                    print( f"Had trouble parsing {iv}" )
            else:
                iv_name = iv.strip()
            print( f"DEBUG: {iv_name}" )
        new_dict = params_to_dict( start_day, reps, gap, nodes, frac, sex, minage, maxage, ips, signal, iv_name, payload, delay )
        output_list.append( new_dict )
    return output_list

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--campaign', 
                help='Existing campaign.json file path.'
            )
    parser.add_argument('-e', '--encode', help='encode')
    parser.add_argument('-f', '--config', default=None, help='Existing config file path.'
            )
    args = parser.parse_args()
    if args.encode:
        encode( args.campaign )
    else:
        decode( args.campaign, args.config )
