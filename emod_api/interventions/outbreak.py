from .. import schema_to_class as s2c
import emod_api.campaign as camp
import emod_api.interventions.common as comm
import json


def seed( camp,
    Start_Day: int,
    Coverage: float,
    Target_Props = None,
    Node_Ids = None,
    Tot_Rep: int = 1,
    Rep_Interval: int = -1,
    Target_Age_Min:float =0,
    Target_Age_Max:float =125,
    Target_Gender:str = "All",
    Honor_Immunity:bool =False
):
    """
    Distribute an outbreak (via prevalence increase of existing agents) to individuals based on inclusion criteria.

    Parameters:
        camp: Central campaign builder object.
        Start_Day: Simulation timestep when outbreak should occur. Required.
        Coverage: Fraction of population to reach. No default.
        Target_Props: Individual Properties to limit the seeding to.
        Node_Ids: Nodes to target. Optional. Defaults to all.
        Tot_Rep: Number of times to "re-seed". Optional. Defaults to just once.
        Rep_Interval: Number of timesteps between re-seeding events. Optional. Use with Rep_Num.
        Target_Age_Min: Minimum age in years. Optional. Defaults to 0.
        Target_Age_Max: Maximum age in years. Optional. Defaults to AGE_MAX.
        Target_Gender: Optional sex-targeting param (Male or Female if you don't want "All").
        Honor_Immunity: Set to True if you want to infect people regardless of their immunity.

    """
    intervention = s2c.get_class_with_defaults("OutbreakIndividual", camp.schema_path)
    if Honor_Immunity is True:
        intervention.Ignore_Immunity = False
    event = comm.ScheduledCampaignEvent( camp, Start_Day=Start_Day, Node_Ids=Node_Ids, Number_Repetitions=Tot_Rep, Timesteps_Between_Repetitions=Rep_Interval, Property_Restrictions=Target_Props, Demographic_Coverage=Coverage, Target_Age_Min=Target_Age_Min, Target_Age_Max=Target_Age_Max, Target_Gender= Target_Gender, Intervention_List=[ intervention ] )
    if "Node_Property_Restrictions" in event.Event_Coordinator_Config:
        event.Event_Coordinator_Config.pop( "Node_Property_Restrictions" )
    if Target_Age_Max <= Target_Age_Min:
        raise ValueError( f"Max age {Target_Age_Max} must be greater than Min Age {Target_Age_Min}." )
    if Target_Age_Max > 150:
        raise ValueError( f"It seems that your value of Target_Age_Max ({Target_Age_Max}) might be in units of days instead of years." )
    if Target_Age_Min > 150:
        raise ValueError( f"It seems that your value of Target_Age_Min ({Target_Age_Min}) might be in units of days instead of years." )
    camp.add( event )

        
def seed_by_coverage(campaign_builder, timestep, coverage=0.01, node_ids=[], properties=None, ignore_immunity=None, intervention_only=False):
    """
    This simple function provides a very common piece of functionality to seed an infection. A future version 
    will support targeted nodesets.
    """
    schema_path = campaign_builder.schema_path
    iv_name = "OutbreakIndividual"
    intervention = s2c.get_class_with_defaults(iv_name, schema_path)
    if ignore_immunity is not None:  # use default value if not defined.
        intervention.Ignore_Immunity = ignore_immunity
    if intervention_only:
        return intervention

    # Coordinator
    coordinator = s2c.get_class_with_defaults("StandardEventCoordinator", schema_path)
    coordinator.Demographic_Coverage = coverage
    coordinator.Intervention_Config = intervention

    # Event
    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    event.Event_Coordinator_Config = coordinator
    event.Start_Day = float(timestep)

    return event


def new_intervention(campaign_builder, timestep, cases=1):
    """
    Create EMOD-ready Outbreak intervention.

    Parameters:
        timestep (float): timestep at which outbreak should occur.
        cases (integer): new parmamter that specifies maximum number of cases. May not be supported.

    Returns: 
        event (json): event as dict (json)
    """
    iv_name = "OutbreakIndividual"
    schema_path = campaign_builder.schema_path
    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    coordinator = s2c.get_class_with_defaults("StandardEventCoordinator", schema_path)
    if coordinator is None:
        print("s2c.get_class_with_defaults returned None. Maybe no schema.json was provided.")
        return ""
    try:
        coordinator.Max_Cases_Per_Node = cases
    except Exception as ex:
        # This can be fine because this is a new parameter only in some branches.
        # Obviously this question is more general and needs a better general solution
        # if at all possible. Max_Cases_Per_Node is an event coordinator optional param.
        #print(str(ex))
        #print("Using 'Outbreak' intervention instead of OutbreakIndividual and Max_Case_Per_Node.")
        iv_name = "Outbreak"

    event.Event_Coordinator_Config = coordinator
    intervention = s2c.get_class_with_defaults(iv_name, schema_path)
    if iv_name == "Outbreak":
        intervention.Number_Cases_Per_Node = cases
    coordinator.Intervention_Config = intervention
    event.Start_Day = float(timestep)

    return event


def new_intervention_as_file(camp, timestep, cases=1, filename=None):
    camp.add(new_intervention(camp, timestep, cases))
    if filename is None:
        filename = "outbreak.json"
    camp.save(filename)
    return filename
