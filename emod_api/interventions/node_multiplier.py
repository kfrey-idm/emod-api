from .. import schema_to_class as s2c
import json
import emod_api.campaign as camp
import emod_api.interventions.utils as utils

"""
    if(camp_obj['Nodeset_Config']['Node_List'][0] == 3):
      xval = np.arange(0,365)
      yval = 1.0+0.2*np.sin(8.0*2*np.pi*xval/365)
      camp_obj['Start_Day'] = 180
      camp_obj[ECC][IC][MBD]['Times']  = xval.tolist()
      camp_obj[ECC][IC][MBD]['Values'] = yval.tolist()

    if(camp_obj['Nodeset_Config']['Node_List'][0] == 2):
      xval = np.array([ 0.0, 50.0, 100.0, 149.5, 150.0, 200.0])
      yval = np.array([ 1.0,  1.3,   1.0,   1.0,   0.7,   0.7])
      camp_obj['Start_Day'] = 10
      camp_obj[ECC][IC][MBD]['Times']  = xval.tolist()
      camp_obj[ECC][IC][MBD]['Values'] = yval.tolist()

    if(camp_obj['Nodeset_Config']['Node_List'][0] == 1):
      xval = np.arange(0,365)
      yval = 1.0-0.8*np.exp(-5.0*xval/365)
      camp_obj['Start_Day'] = 0
      camp_obj[ECC][IC][MBD]['Times']  = xval.tolist()
      camp_obj[ECC][IC][MBD]['Values'] = yval.tolist()
"""
def new_intervention( camp, new_infectivity=1.0, profile="CONST", **kwargs ):
    """
        Create new NodeInfectivityModifying intervention.

        Args:
            profile: multiplier options include:

                - CONST(ANT)
                    - new_infectivity lasts forever (or until replaced). 
                - TRAP(EZOID)
                    - rise_dur(ation)
                    - peak_dur(ation)
                    - fall_dur(ation)
                - EXP(ONENTIAL) (not implemented yet)
                    - rise duration
                    - rise rate
                - SIN(USOIDAL) (not implemented yet)
                    - period

            To do boxcar, specify 0 rise and fall durations (or omit). To do sawtooth, specify 0 peak duration (or omit).

        Returns: 
            new NodeInfectivityMult intervention dictionary.
    """
    intervention = s2c.get_class_with_defaults( "NodeInfectivityMult", camp.schema_path )
    if profile.startswith("CONST"):
        intervention.Multiplier_By_Duration.Times=[0, 365000] # I'm preferring 1000 years to FLT_MAX
        intervention.Multiplier_By_Duration.Values=[new_infectivity,new_infectivity]
    elif profile.startswith("TRAP"):
        rise_dur = 0
        if "rise_dur" in kwargs:
            rise_dur = float(kwargs["rise_dur"])
        peak_dur = 0
        if "peak_dur" in kwargs:
            peak_dur = float(kwargs["peak_dur"])
        fall_dur = 0
        if "fall_dur" in kwargs:
            fall_dur = float(kwargs["fall_dur"])
        total_durs = rise_dur + peak_dur + fall_dur
        if total_durs == 0:
            raise ValueError( "Didn't find any durations." )
        elif total_durs >365:
            raise ValueError( "Total of durations needs to be less than a year." )
        rise_dur = max(rise_dur,1)
        peak_dur = max(peak_dur,1)
        fall_dur = max(fall_dur,1)
        total_durs = rise_dur + peak_dur + fall_dur
        intervention.Multiplier_By_Duration.Times=[0, rise_dur, rise_dur+peak_dur, rise_dur+peak_dur+fall_dur]
        intervention.Multiplier_By_Duration.Values=[1.0, new_infectivity, new_infectivity, 1.0]
    else:
        raise ValueError( f"profile {profile} not supported at this time. Valid profiles are: 'CONST', 'TRAP'." )
    return intervention

def new_scheduled_event( camp, start_day=1, new_infectivity=1.0, profile="CONST", node_ids=None, recurring=True, **kwargs ):
    """
        Create new NodeInfectivityModifying intervention as scheduled campaign event.
    """
    #new_iv = new_intervention( camp=camp, new_infectivity=new_infectivity, profile=profile, kwargs=**kwargs )
    new_iv = new_intervention( camp, new_infectivity, profile, **kwargs )

    coordinator = s2c.get_class_with_defaults( "StandardEventCoordinator", camp.schema_path )
    coordinator.Intervention_Config = new_iv
    if recurring == False:
        coordinator.Number_Repetitions = 1
    else:
        coordinator.Number_Repetitions = -1
        coordinator.Timesteps_Between_Repetitions=365

    event = s2c.get_class_with_defaults( "CampaignEvent", camp.schema_path )
    event.Nodeset_Config = utils.do_nodes( camp.schema_path, node_ids )
    event.Event_Coordinator_Config = coordinator
    event.Start_Day = start_day

    return event

def new_intervention_as_file( camp, timestep, filename=None ):
    """
    Create new NodeInfectivityModifying intervention as sole scheduled campaign event inside working campaign json file.
    """
    camp.add( new_scheduled_event( camp, profile="CONSTANT", start_day=timestep, node_ids=[] ), first=True )
    if filename is None:
        filename = "node_infectivity.json"
    camp.save( filename )
    return filename
