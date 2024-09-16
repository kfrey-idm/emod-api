from tracemalloc import start
import emod_api.interventions.utils as utils
from emod_api.utils import Distributions
from emod_api import schema_to_class as s2c
from enum import Enum
import copy
from typing import List

schema_path = None
old_adhoc_trigger_style = True

cached_be = None
cached_mid = None
cached_sec = None
cached_ce = None
_MAX_AGE = 365 * 125

###
### Generic
###


class TargetGender(Enum):
    Male = "Male"
    Female = "Female"
    All = "All"

def BroadcastEvent(
        camp,
        Event_Trigger: str = 'Births'
):
    """
        Wrapper function to create and return a BroadcastEvent intervention.

        Args:
            camp: emod_api.campaign object with schema_path set.
            Event_Trigger: A valid trigger/event/signal.

        Returns:
            ReadOnlyDict: Schema-based smart dictionary representing a new 
            BroadastEvent intervention ready to be added to a campaign.
    """

    if Event_Trigger is None or Event_Trigger == "":
        raise ValueError("BroadcastEvent called with an empty Event_Trigger. Please specify a string.")

    global cached_be
    if cached_be is None:
        global schema_path
        schema_path = (camp.schema_path if camp is not None else schema_path)
        cached_be = s2c.get_class_with_defaults("BroadcastEvent", schema_path)
    intervention = copy.deepcopy(cached_be)
    try:
        intervention.Broadcast_Event = camp.get_send_trigger(Event_Trigger, old=old_adhoc_trigger_style)
    except ValueError as ex:
        raise ValueError(str(ex) + "\n\nMaybe you need to set 'old_adhoc_trigger_style' to false in this module?\n")
    return intervention


def broadcast_node_event(campaign,
                         broadcast_event: str,
                         cost_to_consumer: float = 0.0,
                         disqualifying_properties: List[str] = None,
                         dont_allow_duplicates: bool = False,
                         intervention_name: str = "BroadcastNodeEvent",
                         new_property_value: str = ""):
    """
    Wrapper function to create and return a BroadcastNodeEvent intervention.

    Args:
        campaign: emod_api.campaign object with schema_path set
        broadcast_event: String that will be broadcast as Node-level event
        cost_to_consumer: The unit cost of the intervention campaign that will be assigned to the specified nodes.
        disqualifying_properties: A list of NodeProperty key:value pairs that cause an intervention to be aborted.
            Generally used to control the flow of health care access. For example, to prevent the same individual
            from accessing health care via two different routes at the same time.
        dont_allow_duplicates: If a node's container has the same intervention, set to True to prevent them from
            receiving another copy of the intervention. Supported by all intervention classes.
        intervention_name: The optional name used to refer to this intervention as a means to differentiate it
            from others that use the same class.
        new_property_value: An optional NodeProperty key:value pair that will be assigned when the intervention is
            distributed. Generally used to indicate the broad category of health care cascade to which an intervention
            belongs to prevent individuals from accessing care through multiple pathways.

    Returns:
        ReadOnlyDict: BroadcastNodeEvent intervention ready to be added to a campaign.
    """
    if not broadcast_event:
        raise ValueError("BroadcastNodeEvent called with an empty broadcast_event. Please specify a "
                         "non-empty string.\n")
    global schema_path
    schema_path = campaign.schema_path if campaign is not None else schema_path
    if not disqualifying_properties:
        disqualifying_properties = []

    intervention = s2c.get_class_with_defaults("BroadcastNodeEvent", schema_path)
    intervention.Broadcast_Event = broadcast_event
    campaign.custom_node_events.append(broadcast_event)
    intervention.Cost_To_Consumer = cost_to_consumer
    intervention.Disqualifying_Properties = disqualifying_properties
    intervention.Dont_Allow_Duplicates = 1 if dont_allow_duplicates else 0
    intervention.Intervention_Name = intervention_name
    intervention.New_Property_Value = new_property_value
    return intervention


def BroadcastEventToOtherNodes(
        camp,
        Event_Trigger,
        Node_Selection_Type="DISTANCE_ONLY",
        Max_Distance_To_Other_Nodes_Km=-1,
        Include_My_Node=1
):
    """
        Wrapper function to create and return a BroadcastEventToOtherNodes intervention. 

        Args:
            camp: emod_api.campaign object with schema_path set.
            Event_Trigger: A valid trigger/event/signal.
            Node_Selection_Type: TBD.
            Max_Distance_To_Other_Nodes_Km: TBD.
            Include_My_Node: TBD.

        Returns:
            ReadOnlyDict: Schema-based smart dictionary representing a new 
            BroadastEvent intervention ready to be added to a campaign.
    """
    if Event_Trigger is None or Event_Trigger == "":
        raise ValueError("BroadcastEventToOtherNodes called with an empty Event_Trigger. "
                         "Please specify a non-empty string.")

    global schema_path
    schema_path = camp.schema_path if camp is not None else schema_path
    intervention = s2c.get_class_with_defaults("BroadcastEventToOtherNodes", schema_path)
    intervention.Event_Trigger = camp.get_send_trigger(Event_Trigger, old=old_adhoc_trigger_style)
    intervention.Node_Selection_Type = Node_Selection_Type
    if Max_Distance_To_Other_Nodes_Km != -1:
        intervention.Max_Distance_To_Other_Nodes_Km = Max_Distance_To_Other_Nodes_Km
    intervention.Include_My_Node = Include_My_Node
    return intervention


def add_broadcast_coordinator_event(
        campaign,
        broadcast_event: str,
        start_day: int = 0,
        cost_to_consumer: float = None,
        coordinator_name: str = "BroadcastCoordinatorEvent"):
    """
        Creates and adds BroadcastCoordinatorEvent intervention to the campaign

        Args:
            campaign: emod_api.campaign object with schema_path set.
            broadcast_event: String that will be broadcast as Coordinator-level event.
            start_day: The day in the simulation on which to send out this event.
            cost_to_consumer: The unit cost of broadcasting the event.
            coordinator_name: The unique identifying coordinator name, which is useful with the output report,
                ReportCoordinatorEventRecorder.csv

        Returns:
            Nothing
    """
    if not broadcast_event:
        raise ValueError("BroadcastCoordinatorEvent called with an empty broadcast_event. "
                         "Please specify a non-empty string.\n")

    global schema_path
    schema_path = campaign.schema_path if campaign is not None else schema_path
    b_c_e = s2c.get_class_with_defaults("BroadcastCoordinatorEvent", schema_path)
    b_c_e.Broadcast_Event = broadcast_event
    campaign.custom_coordinator_events.append(broadcast_event)
    b_c_e.Cost_To_Consumer = cost_to_consumer
    b_c_e.Coordinator_Name = coordinator_name

    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    event.Start_Day = start_day
    event.Event_Coordinator_Config = b_c_e
    campaign.add(event)


def MultiInterventionDistributor(
        camp,
        Intervention_List
):
    """
        Wrapper function to create and return a MultiInterventionDistributor intervention. 

        Args:
            camp: emod_api.campaign object with schema_path set.
            Intervention_List: List of 1 or more valid intervention dictionaries to be
            distributed together. 

        Returns:
            ReadOnlyDict: Schema-based smart dictionary representing a new 
            MultiInterventionDistributor intervention ready to be added to a campaign.
    """

    global schema_path
    schema_path = camp.schema_path if camp is not None else schema_path
    if Intervention_List is None or type(Intervention_List) is not list or len(Intervention_List) == 0:
        raise ValueError("Intervention_List is empty or None or not a list.")
    global cached_mid
    if cached_mid is None:
        cached_mid = s2c.get_class_with_defaults("MultiInterventionDistributor", schema_path)
    intervention = copy.deepcopy(cached_mid)
    intervention.Intervention_List = copy.deepcopy(Intervention_List)
    if "Intervention_Name" in Intervention_List[0]:
        intervention.Intervention_Name = Intervention_List[0].Intervention_Name
    else:
        intervention.Intervention_Name = "MultiInterventionDistributor"
    return intervention


def DelayedIntervention(
        camp,
        Configs: List[dict],
        Delay_Dict: dict):
    """
        Wrapper function to create and return a DelayedIntervention containing a list of individual-level interventions.

        Args:
            camp: emod_api.campaign object with schema_path set.  
            Configs: A list of individual-level interventions
            Delay_Dict: Dictionary with delay parameters, please use emod_api.utils.Distributions
                to generate the delay parameters.

        Returns:
            ReadOnlyDict: Schema-based smart dictionary representing a new 
            DelayedIntervention intervention ready to be added to a campaign.
    """
    global schema_path
    schema_path = camp.schema_path if camp is not None else schema_path
    if not Configs or not isinstance(Configs, list):
        raise ValueError("Configs needs to be a list of interventions.\n")

    intervention = s2c.get_class_with_defaults("DelayedIntervention", schema_path)
    intervention.Actual_IndividualIntervention_Configs = copy.deepcopy(Configs)
    # Set the delay parameters
    Distributions.set_distribution_parameters(distribution_containing_obj=intervention, distribution=Delay_Dict,
                                              prefix="Delay_Period_")
    return intervention


def HSB(
        camp,
        Event_Or_Config="Event",
        Config=None,
        Event="NoTrigger",
        Tendency=1.0,
        Single_Use=True,
        Name="HSB"
):
    """
        Wrapper function to create and return a HealthSeekingBehaviour intervention. 

        Args:
            camp: emod_api.campaign object with schema_path set.
            Event_Or_Config: "Event" or "Config".
            Config: Complete, valid intervention configuration to be distributed.
            Event: Event/Trigger/Signal to be broadcast, alternative to an intervention.
            Tendency: Daily probability of 'seeking care' aka distributing payload intervention.
            Single_Use: One-and-done, or continuous?
            Name: Intervention Name. Useful if you want to provide uniqueness and not worry about 
            duplicate intervention management.

        Returns:
            ReadOnlyDict: Schema-based smart dictionary representing a new 
            HSB intervention ready to be added to a campaign.
    """
    global schema_path
    schema_path = camp.schema_path if camp is not None else schema_path

    intervention = s2c.get_class_with_defaults("SimpleHealthSeekingBehavior", schema_path)
    intervention.Event_Or_Config = Event_Or_Config
    if intervention.Event_Or_Config == "Event":
        intervention.Actual_IndividualIntervention_Event = camp.get_send_trigger(Event, old=old_adhoc_trigger_style)
    else:
        if Config is None:
            raise ValueError("You specified 'Config' but no actual Config.")
        intervention.Actual_IndividualIntervention_Config = Config
    intervention.Tendency = Tendency
    intervention.Intervention_Name = Name
    intervention.Single_Use = Single_Use
    return intervention


def NLHTI(
        camp,
        Triggers: List[str],
        Interventions: List[dict],
        Property_Restrictions=None,
        Demographic_Coverage=1.0,
        Target_Age_Min: float = 0,
        Target_Age_Max: float = _MAX_AGE,
        Target_Gender="All",
        Target_Residents_Only=False,
        Duration: float = -1,
        Blackout_Event_Trigger=None,
        Blackout_Period=None,
        Blackout_On_First_Occurrence=None,
        Disqualifying_Properties=None,
):
    """
        Wrapper function to create and return a NodeLevelHealthTriggeredIntervention intervention. 

        Args:
            camp: emod_api.campaign object with schema_path set.
            Triggers: List of Triggers/Events/Signals
            Interventions: List of interventions to distrbute when signal is heard.
            Property_Restrictions: Individual Properties that an agent must have to qualify for intervention.
            Demographic_Coverage: Percentage of individuals to receive intervention.
            Target_Age_Min: Minimum age (in years).
            Target_Age_Max: Maximum age (in years).
            Target_Gender: All, Male, or Female.
            Target_Residents_Only: Not used.
            Duration: How long this listen-and-distribute should last.
            Blackout_Event_Trigger: Not used.
            Blackout_Period: Not used.
            Blackout_On_First_Occurrence: Not used.
            Disqualifying_Properties: Not used.

        Returns:
            ReadOnlyDict: Schema-based smart dictionary representing a new 
            NLHTI intervention ready to be added to a campaign.
    """
    global schema_path
    schema_path = camp.schema_path if camp is not None else schema_path

    intervention = s2c.get_class_with_defaults("NodeLevelHealthTriggeredIV", schema_path)
    intervention.Trigger_Condition_List = [camp.get_recv_trigger(trigger, old=old_adhoc_trigger_style) for trigger in
                                           Triggers]
    if Target_Age_Min > 0 or Target_Age_Max < _MAX_AGE:
        intervention.Target_Age_Min = Target_Age_Min
        intervention.Target_Age_Max = Target_Age_Max
    if Target_Gender != "All":
        intervention.Target_Gender = Target_Gender
        intervention.Target_Demographic = "ExplicitAgeRangesAndGender"
    intervention.Target_Residents_Only = Target_Residents_Only
    intervention.Demographic_Coverage = Demographic_Coverage
    intervention.Duration = Duration
    intervention.Blackout_Event_Trigger = Blackout_Event_Trigger
    intervention.Blackout_Period = Blackout_Period
    intervention.Blackout_On_First_Occurrence = Blackout_On_First_Occurrence
    prs = utils._convert_prs(Property_Restrictions)
    if len(prs) > 0 and type(prs[0]) is dict:
        intervention.Property_Restrictions_Within_Node = prs
        intervention.pop("Property_Restrictions")
    else:
        intervention.Property_Restrictions = prs
        if "Property_Restrictions_Within_Node" in intervention:
            intervention.pop("Property_Restrictions_Within_Node")
    if len(Interventions) == 1:
        intervention.Actual_IndividualIntervention_Config = Interventions[0]
    else:
        intervention.Actual_IndividualIntervention_Config = MultiInterventionDistributor(camp, Interventions)

    return intervention


def PropertyValueChanger(
        camp,
        Target_Property_Key,
        Target_Property_Value,
        Daily_Probability=1.0,
        Maximum_Duration=1,
        Revert=-1,
        Intervention_Name="",
        Event_Trigger_Distributed="",
        Event_Trigger_Expired=""
):
    """
        Wrapper function to create and return a PropertyValueChanger intervention. 

        Args:
            camp: emod_api.campaign object with schema_path set. 
            Target_Property_Key. The key part of the new key-value pair of the IP.
            Target_Property_Key. The key part of the new key-value pair of the IP.
            Target_Property_Value. The value part of the new key-value pair of the IP.
            New_Property_Value.. Optional IP key:value part to be set, common to all interventions.
            Daily_Probability. The daily probability that an individual will move to the Target_Property_Value.
            Maximum_Duration. The maximum amount of time individuals have to move to a new group. This timing works
                in conjunction with Daily_Probability.
            Revert.  The number of days before an individual moves back to their original group.
            Intervention_Name. Optional Intervention_Name. Useful if managing a replacement policy.
            Event_Trigger_Distributed. Optional broadcast trigger to be published when PVC is distributed.
            Event_Trigger_Expired. Optional broadcast trigger to be published when PVC is expired.

        Returns:
            ReadOnlyDict: Schema-based smart dictionary representing a new 
            PropertyValueChanger intervention ready to be added to a campaign.
    """
    global schema_path
    schema_path = camp.schema_path if camp is not None else schema_path

    intervention = s2c.get_class_with_defaults("PropertyValueChanger", schema_path)
    intervention.Target_Property_Key = Target_Property_Key
    intervention.Target_Property_Value = Target_Property_Value
    intervention.Daily_Probability = Daily_Probability
    intervention.Maximum_Duration = Maximum_Duration
    if Revert != -1:
        intervention.Revert = Revert
    if len(Intervention_Name) > 0:
        intervention.Intervention_Name = Intervention_Name
    if len(Event_Trigger_Distributed) > 0:
        intervention.Event_Trigger_Distributed = Event_Trigger_Distributed
    if len(Event_Trigger_Expired) > 0:
        intervention.Event_Trigger_Expired = Event_Trigger_Expired

    return intervention


def ScheduledCampaignEvent(
        camp,
        Start_Day: int,
        Node_Ids=None,
        Nodeset_Config=None,
        Number_Repetitions: int = 1,
        Timesteps_Between_Repetitions: int = -1,
        Event_Name: str = "Scheduled_Campaign_Event",  # not set, doesn't exist in schema
        Property_Restrictions=None,
        Demographic_Coverage: float = 1.0,
        Target_Age_Min=0,
        Target_Age_Max=_MAX_AGE,
        Target_Gender: str = "All",
        Target_Residents_Only: bool = False,
        Intervention_List=None):
    """
        Wrapper function to create and return a ScheduledCampaignEvent intervention. 
        The alternative to a ScheduledCampaignEvent is a TriggeredCampaignEvent.

        Args:
            camp: emod_api.campaign object with schema_path set.
            Start_Day: When to start.
            Event_Name: Name for overall campaign event, of no functional meaning. Not in schema and not yet used.
            Node_Ids: Nodes to target with this intervenion
            Nodeset_Config: Nodes to target with this intervenion, return from utils.do_nodes().

                .. deprecated:: 2.x
                   Use parameter Node_Ids instead

            Property_Restrictions: Individual Properties a person must have to receive the intervention(s).
            Number_Repetitions: N/A 
            Timesteps_Between_Repetitions: N/A 
            Demographic_Coverage: Percentage of individuals to receive intervention.
            Target_Age_Min: Minimum age (in years).
            Target_Age_Max: Maximum age (in years).
            Target_Gender: All, Male, or Female.
            Intervention_List: List of 1 or more valid intervention dictionaries to be
            distributed together. 

        Returns:
            ReadOnlyDict: Schema-based smart dictionary representing a new 
            ScheduledCampaignEvent intervention ready to be added to a campaign.
    """
    global schema_path
    schema_path = camp.schema_path if camp is not None else schema_path

    # Not checking Intervention_list because MultiInterventionDistributor checks

    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    global cached_sec
    if cached_sec is None:
        cached_sec = s2c.get_class_with_defaults("StandardEventCoordinator", schema_path)

    coordinator = copy.deepcopy(cached_sec)
    coordinator.Demographic_Coverage = Demographic_Coverage
    coordinator.Number_Repetitions = Number_Repetitions
    coordinator.Timesteps_Between_Repetitions = Timesteps_Between_Repetitions

    # Second, hook them up
    event.Event_Coordinator_Config = coordinator
    event.Start_Day = float(Start_Day)

    if Nodeset_Config is not None and Node_Ids is not None:
        raise AssertionError("Node_Ids and Nodeset_Config are set. Please set only one.")

    if Nodeset_Config is not None:
        event.Nodeset_Config = Nodeset_Config
    else:
        # The real default is an empty list
        if Node_Ids is None:
            Node_Ids = []
        node_ids = Node_Ids
        event.Nodeset_Config = utils.do_nodes(camp.schema_path, node_ids)

    if len(Intervention_List) > 1:
        coordinator.Intervention_Config = MultiInterventionDistributor(camp, Intervention_List)
    else:
        coordinator.Intervention_Config = Intervention_List[0]
    prs = utils._convert_prs(Property_Restrictions)
    if len(prs) > 0 and type(prs[0]) is dict:
        coordinator.Property_Restrictions_Within_Node = prs
        coordinator.pop("Property_Restrictions")
    else:
        coordinator.Property_Restrictions = prs
        coordinator.pop("Property_Restrictions_Within_Node")

    coordinator.Demographic_Coverage = Demographic_Coverage

    if Target_Age_Min > 0 or Target_Age_Max < _MAX_AGE:
        coordinator.Target_Age_Min = Target_Age_Min

    if Target_Age_Max is not None and Target_Age_Max < _MAX_AGE:  # overwrite default from schema
        coordinator.Target_Age_Max = Target_Age_Max

    if Target_Gender != "All":
        coordinator.Target_Gender = Target_Gender
        coordinator.Target_Demographic = "ExplicitAgeRangesAndGender"

    coordinator.Target_Residents_Only = Target_Residents_Only

    return event


def TriggeredCampaignEvent(
        camp,
        Start_Day: int,
        Event_Name: str,
        Triggers: List[str],
        Intervention_List: List[dict],
        Node_Ids: List[int] = None,
        Nodeset_Config: dict = None,
        Node_Property_Restrictions: List[dict] = None,
        Property_Restrictions: List[dict] = None,
        Number_Repetitions: int = 1,
        Timesteps_Between_Repetitions: int = -1,
        Demographic_Coverage: float = 1.0,
        Target_Age_Min: float = 0,
        Target_Age_Max: float = _MAX_AGE,
        Target_Gender: str = "All",
        Target_Residents_Only: bool = False,
        Duration: float = -1,
        Blackout_Event_Trigger: str = None,
        Blackout_Period: float = 0,
        Blackout_On_First_Occurrence=0,
        Disqualifying_Properties: List[str] = None,
        Delay: dict = None
):
    """
        Wrapper function to create and return a TriggeredCampaignEvent intervention. 
        The alternative to a TriggeredCampaignEvent is a ScheduledCampaignEvent.

        Args:
            camp: emod_api.campaign object with schema_path set.
            Start_Day: When to start.
            Event_Name: Name for overall campaign event, of no functional meaning. Not in schema and not yet used.
            Node_Ids: Nodes to target with this intervenion
            Nodeset_Config: Nodes to target with this intervenion, return from utils.do_nodes().

                .. deprecated:: 2.x
                   Use parameter Node_Ids instead

            Triggers: List of triggers/events/signals to listen to in order to trigger distribution.
            Intervention_List: List of 1 or more valid individual-level intervention dictionaries to be
            distributed together. 
            Node_Property_Restrictions: N/A.
            Property_Restrictions: Individual Properties a person must have to receive the intervention(s).
            Demographic_Coverage: Percentage of individuals to receive intervention.
            Target_Age_Min: Minimum age (in years).
            Target_Age_Max: Maximum age (in years).
            Target_Gender: All, Male, or Female.
            Target_Residents_Only: TBD.
            Duration: How long this listen-and-distribute should last.
            Blackout_Event_Trigger: Not used.
            Blackout_Period: Not used.
            Blackout_On_First_Occurrence: Not used.
            Disqualifying_Properties: Not used.
            Delay: Optional delay between trigger and actual distribution, a distribution dictionary generated by
                emod_api.utils.Distributions class.

        Returns:
            ReadOnlyDict: Schema-based smart dictionary representing a new 
            TriggeredCampaignEvent intervention ready to be added to a campaign.
    """
    global schema_path
    schema_path = camp.schema_path if camp is not None else schema_path

    if Node_Property_Restrictions is None:
        Node_Property_Restrictions = []
    if Property_Restrictions is None:
        Property_Restrictions = []

    global cached_ce
    if cached_ce is None:
        cached_ce = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    event = copy.deepcopy(cached_ce)
    event.Start_Day = float(Start_Day)

    if Nodeset_Config is not None and Node_Ids is not None:
        raise AssertionError("Node_Ids and Nodeset_Config are set. Please use only one.")

    if Nodeset_Config is not None:
        event.Nodeset_Config = Nodeset_Config
    else:
        # The real default is an empty list.
        if Node_Ids is None:
            Node_Ids = []
        node_ids = Node_Ids
        event.Nodeset_Config = utils.do_nodes(camp.schema_path, node_ids)

    global cached_sec
    if cached_sec is None:
        cached_sec = s2c.get_class_with_defaults("StandardEventCoordinator", schema_path)
    coordinator = copy.deepcopy(cached_sec)
    coordinator.Number_Repetitions = Number_Repetitions
    coordinator.Timesteps_Between_Repetitions = Timesteps_Between_Repetitions

    if Delay:
        if isinstance(Delay, dict):
            Intervention_List = [DelayedIntervention(camp, Intervention_List, Delay_Dict=Delay)]
        elif isinstance(Delay, int) or isinstance(Delay, float):
            Intervention_List = [DelayedIntervention(camp, Intervention_List, Delay_Dict=Distributions.constant(Delay))]
        else:
            raise AssertionError(f"Delay must be a dictionary or a number. It is {type(Delay)}.\n")

    intervention = NLHTI(
        camp,
        Triggers,
        Intervention_List,
        Duration=Duration,
        Property_Restrictions=Property_Restrictions,
        Demographic_Coverage=Demographic_Coverage,
        Target_Age_Min=Target_Age_Min,
        Target_Age_Max=Target_Age_Max,
        Target_Gender=Target_Gender,
        Target_Residents_Only=Target_Residents_Only,
        Blackout_Event_Trigger=Blackout_Event_Trigger,
        Blackout_Period=Blackout_Period,
        Blackout_On_First_Occurrence=Blackout_On_First_Occurrence
    )

    event.Event_Coordinator_Config = coordinator
    coordinator.Intervention_Config = intervention
    return event


def add_triggered_coordinator_event(campaign,
                                    start_day: int = 0,
                                    listening_duration: float = -1,
                                    start_trigger_condition_list: list = None,
                                    stop_trigger_condition_list: list = None,
                                    demographic_coverage: float = None,
                                    target_num_individuals: int = None,
                                    node_ids: list = None,
                                    repetitions: int = None,
                                    timesteps_between_repetitions: int = None,
                                    ind_property_restrictions: list = None,
                                    node_property_restrictions: list = None,
                                    target_age_min: float = None,
                                    target_age_max: float = None,
                                    target_gender: TargetGender = TargetGender.All,
                                    target_residents_only: bool = False,
                                    completion_event: str = "",
                                    coordinator_name: str = "TriggeredEventCoordinator",
                                    node_interventions: any = None,
                                    individual_interventions: any = None):
    """
        Wrapper function to create and adds a TriggeredCoordinatorEvent. The intervention is triggered by
        COORDINATOR-level event, and sends out a COORDINATOR-level event when done.
    
    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        start_day: The day the intervention is given out.
        listening_duration: The number of time steps that the coordinator will monitor for triggers before expiring.
            Default is -1, which is indefinitely.
        start_trigger_condition_list:  A list of the COORDINATOR-level events that will trigger intervention distribution.
        stop_trigger_condition_list: A list of the COORDINATOR-level events that will stop intervention from happening
            if the intervention is repeating.
        demographic_coverage: This value is the probability that each individual in the target population will
            receive the intervention. It does not guarantee that the exact fraction of the target population set by
            Demographic_Coverage receives the intervention.
        target_num_individuals: The exact number of people to select out of the targeted group. If this value is set,
            demographic_coverage parameter is ignored
        node_ids: List of nodes to which to distribute the intervention. [] or None, indicates all nodes
            will get the intervention
        repetitions: The number of times an intervention is given, used with timesteps_between_repetitions. -1 means
            the intervention repeats forever. Sets **Number_Repetitions**
        timesteps_between_repetitions: The interval, in timesteps, between repetitions. Ignored if repetitions = 1.
            Sets **Timesteps_Between_Repetitions**
        ind_property_restrictions: A list of dictionaries of IndividualProperties, which are needed for the individual
            to receive the intervention. Sets the **Property_Restrictions_Within_Node**
        node_property_restrictions: "A list of the NodeProperty key:value pairs, as defined in the demographics file,
            that nodes must have to be targeted by the intervention.
        target_age_min: The lower end of ages targeted for an intervention, in years. Sets **Target_Age_Min**
        target_age_max: The upper end of ages targeted for an intervention, in years. Sets **Target_Age_Max**
        target_gender: The gender targeted for an intervention: All, Male, or Female.
        target_residents_only: When set to True, the intervention is only distributed to individuals that began
            the simulation in the node (i.e. those that claim the node as their residence)
        completion_event: A COORDINATOR-level event to send out when the coordinator has expired.
        coordinator_name: The unique identifying coordinator name used to identify the different coordinators in
            reports.
        node_interventions: A node-level intervention or a list of node-level interventions that will be distributed
            when one of the triggers from start_trigger_condition_list is heard.
        individual_interventions: A individual-level intervention or a list of individual-level interventions that
            will be distributed when one of the triggers from start_trigger_condition_list is heard.

    Returns:
        None
    """
    if not start_trigger_condition_list:
        raise ValueError("Please define triggers for start_trigger_condition_list. Cannot be empty or None.\n")
    if bool(node_interventions) == bool(individual_interventions):
        raise ValueError("Please define either node_interventions or individual_interventions. "
                         "They are mutually exclusive.\n")
    if node_interventions and (demographic_coverage or target_num_individuals or target_gender != TargetGender.All
                               or target_age_min or
                               target_age_max or target_residents_only or ind_property_restrictions):
        raise ValueError("demographic_coverage, target_num_individuals, target_gender, target_age_min, target_age_max, "
                         "target_residents_only, and ind_property_restrictions are not used when passing in "
                         "node_interventions\n")
    if individual_interventions and (bool(demographic_coverage) == bool(target_num_individuals)):
        raise ValueError("Please define either demographic_coverage or target_num_individuals, but not both, "
                         "when passing in individual_interventions\n")

    schema_path = campaign.schema_path
    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    event.Start_Day = start_day
    event.Nodeset_Config = utils.do_nodes(schema_path, node_ids)

    if node_interventions:
        if isinstance(node_interventions, list) and len(node_interventions) > 1:
            multi_intervention_distributor = s2c.get_class_with_defaults("MultiNodeInterventionDistributor",
                                                                         schema_path)
            multi_intervention_distributor.Node_Intervention_List = node_interventions
            intervention = multi_intervention_distributor
        elif isinstance(node_interventions, list) and len(node_interventions) == 1:
            intervention = node_interventions[0]  # if only one intervention, just use that
        elif isinstance(node_interventions, dict):
            intervention = node_interventions
        else:
            raise ValueError("Invalid type for node_interventions: " + str(type(node_interventions)))
    else:
        if isinstance(individual_interventions, list) and len(individual_interventions) > 1:
            multi_intervention_distributor = s2c.get_class_with_defaults("MultiInterventionDistributor", schema_path)
            multi_intervention_distributor.Intervention_List = individual_interventions
            intervention = multi_intervention_distributor
        elif isinstance(individual_interventions, list) and len(individual_interventions) == 1:
            intervention = individual_interventions[0]  # if only one intervention, just use that
        elif isinstance(individual_interventions, dict):
            intervention = individual_interventions
        else:
            raise ValueError("Invalid type for individual_interventions: " + str(type(individual_interventions)))

    # configuring the coordinator
    coordinator = s2c.get_class_with_defaults("TriggeredEventCoordinator", schema_path)
    coordinator.Intervention_Config = intervention
    if target_num_individuals is not None:  # so they can set it to 0 for some reason
        coordinator.Target_Num_Individuals = target_num_individuals
    elif demographic_coverage is not None:  # so they can set it to 0 for some reason
        coordinator.Demographic_Coverage = demographic_coverage
    coordinator.Target_Residents_Only = target_residents_only
    if repetitions and timesteps_between_repetitions:
        coordinator.Number_Repetitions = repetitions
        coordinator.Timesteps_Between_Repetitions = timesteps_between_repetitions
    elif bool(repetitions) != bool(timesteps_between_repetitions):
        raise ValueError("Please define both repetitions and timesteps_between_repetitions. "
                         "Cannot define one without the other.\n")
    if ind_property_restrictions:
        coordinator.Property_Restrictions_Within_Node = ind_property_restrictions
    if node_property_restrictions:
        coordinator.Node_Property_Restrictions = node_property_restrictions

    if target_age_min:  # 0 is the default, we don't have to set it explicitly
        coordinator.Target_Age_Min = target_age_min
    if target_age_max is not None and target_age_max <= coordinator.Target_Age_Min:
        raise ValueError(f"target_age_max ({target_age_max}) must be greater than or equal to "
                         f"target_age_min ({target_age_min}).\n")
    else:
        coordinator.Target_Age_Max = target_age_max
    if target_gender != TargetGender.All:
        coordinator.Target_Gender = target_gender.name
        coordinator.Target_Demographic = "ExplicitAgeRangesAndGender"

    coordinator.Duration = listening_duration
    coordinator.Coordinator_Name = coordinator_name
    coordinator.Start_Trigger_Condition_List = start_trigger_condition_list
    campaign.custom_coordinator_events.extend(start_trigger_condition_list)
    if stop_trigger_condition_list:
        coordinator.Stop_Trigger_Condition_List = stop_trigger_condition_list
        campaign.custom_coordinator_events.extend(stop_trigger_condition_list)
    if completion_event:
        coordinator.Completion_Event = completion_event
        campaign.custom_coordinator_events.append(completion_event)
    event.Event_Coordinator_Config = coordinator
    campaign.add(event)


def StandardDiagnostic(
        camp,
        Base_Sensitivity: float = 1.0,
        Base_Specificity: float = 1.0,
        Days_To_Diagnosis: float = 0.0,
        Event_Trigger_Distributed: str = None,
        Event_Trigger_Expired: str = None,
        Positive_Diagnosis_Intervention=None,
        Positive_Diagnosis_Event: str = "PositiveResult",
        Negative_Diagnosis_Intervention=None,
        Negative_Diagnosis_Event: str = "NegativeResult",
        Treatment_Fraction: float = 1.0
):
    """
        Wrapper function to create and return a StandardDiagnostic intervention. 

        Args:
            camp: emod_api.campaign object with schema_path set.
            Base_Sensitivity: base sensitivity [0..1]
            Base_Specificity: base specificity [0..1]
            Days_To_Diagnosis: days to diagnosis
            Event_Trigger_Distributed: A trigger that is fired when intervention was distributed
            Event_Trigger_Expired: A trigger that is fired when intervention has expired
            Positive_Diagnosis_Intervention: Intervention that is distributed in case of a positive diagnosis.
                If set, no events may be configured.
            Positive_Diagnosis_Event: A trigger that is fired in case of a positive diagnosis
            Negative_Diagnosis_Intervention: Intervention that is distributed in case of a Negative diagnosis.
                If set, no events may be configured.  Not used outside of Malaria-Ongoing yet.
            Negative_Diagnosis_Event: A trigger that is fired in case of a Negative diagnosis. Not used outside of
                Malaria-Ongoing yet.
            Treatment_Fraction: treatment fraction [0..1]

        Returns:
            ReadOnlyDict: Schema-based smart dictionary representing a new 
            MultiInterventionDistributor intervention ready to be added to a campaign.
    """

    global schema_path
    schema_path = camp.schema_path if camp is not None else schema_path

    if Positive_Diagnosis_Intervention is not None and (
            Event_Trigger_Distributed is not None or Event_Trigger_Expired is not None):
        raise Exception(
            "Events and intervention are configured. Configuration of events and intervention are mutually exclusive.")

    # First, get the objects
    # Only in Malaria-Ongoing the class is called StandardDiagnostic
    try:
        intervention = s2c.get_class_with_defaults("StandardDiagnostic", schema_path)
        if Positive_Diagnosis_Intervention is None:
            intervention.Positive_Diagnosis_Config = BroadcastEvent(camp, Positive_Diagnosis_Event)
        else:
            intervention.Positive_Diagnosis_Config = Positive_Diagnosis_Intervention

        if Negative_Diagnosis_Intervention is None:
            intervention.Negative_Diagnosis_Config = BroadcastEvent(camp, Negative_Diagnosis_Event)
        else:
            intervention.Negative_Diagnosis_Config = Negative_Diagnosis_Intervention
    except ValueError:
        # Non Malaria, use SimpleDiagnostic
        intervention = s2c.get_class_with_defaults("SimpleDiagnostic", schema_path)

        if Positive_Diagnosis_Intervention is None:
            intervention.Positive_Diagnosis_Config = BroadcastEvent(camp, Positive_Diagnosis_Event)
            if Event_Trigger_Distributed:
                intervention.Event_Trigger_Distributed = Event_Trigger_Distributed
            if Event_Trigger_Expired:
                intervention.Event_Trigger_Expired = Event_Trigger_Expired
        else:
            intervention.Positive_Diagnosis_Config = Positive_Diagnosis_Intervention

    intervention.Base_Sensitivity = Base_Sensitivity
    intervention.Base_Specificity = Base_Specificity
    intervention.Days_To_Diagnosis = Days_To_Diagnosis
    intervention.Treatment_Fraction = Treatment_Fraction

    return intervention


def triggered_campaign_delay_event(camp, start_day, trigger, delay, intervention, ip_targeting=None, coverage=1.0):
    """
        Create and return a campaign event that responds to a trigger after a delay with an intervention.

        Args:
            camp: emod_api.campaign object with schema_path set.
            start_day: Day the event will start.
            delay: Dictionary with delay parameters, please use emod_api.utils.Distributions
                to generate the delay parameters.
            trigger: E.g., "NewInfection".
            intervention: List of 1 or more valid intervention dictionaries to be distributed together. 
            ip_targeting: Optional Individual Properties required for someone to receive the intervention(s).
            coverage: Fraction of the population that will receive the intervention.

        Returns:
            Campaign event.

    """
    if not ip_targeting:
        ip_targeting = []
    delay_iv = DelayedIntervention(camp, Configs=[intervention], Delay_Dict=delay)
    event = TriggeredCampaignEvent(camp, Start_Day=start_day, Event_Name="triggered_delayed_intervention",
                                   Triggers=[camp.get_recv_trigger(trigger, old=True)],
                                   Intervention_List=[delay_iv], Property_Restrictions=ip_targeting,
                                   Demographic_Coverage=coverage)
    return event


#
# The following function is intended to replace triggered_campaign_delay_event.
# There's a bit of a structure here:
# change_individual_property() -> 
#     change_individual_property_scheduled() -> 
#         ScheduledCampaignEvent()
#     OR
#     change_individual_property_triggered ->
#         triggered_campaign_event_with_optional_delay
#             TriggeredCampaignEvent()

def triggered_campaign_event_with_optional_delay(camp,
                                                 start_day,
                                                 triggers,
                                                 intervention,
                                                 delay=None,
                                                 duration=-1,
                                                 ip_targeting=None,
                                                 coverage=1.0,
                                                 target_age_min=0,
                                                 target_age_max=_MAX_AGE,
                                                 target_sex="All",
                                                 target_residents_only=False,
                                                 blackout=True,
                                                 check_at_trigger=False
                                                 ):
    """
        Create and return a campaign event that responds to a trigger after a delay with an intervention.

        Args:
            camp: emod_api.campaign object with schema_path set.
            start_day: When to start.
            triggers: List of signals to listen for/trigger on. E.g., "NewInfection".
            intervention: List of 1 or more valid intervention dictionaries to be distributed together. 
            delay: Optional dictionary of 1 or 2 params that are the literal Delay_Distribution parameters, 
            but without the distribution, which is inferred. E.g., { "Delay_Period_Exponential": 5 }. If omitted,
            intervention is immediate.
            duration: How long to listen.
            ip_targeting: Optional Individual Properties required for someone to receive the intervntion(s).
            coverage: Fraction of target population to reach.
            target_age_min: Minimum age to target.
            target_age_max: Maximum age to target.
            target_sex: Optional target just "MALE" or "FEMALE" individuals.
            target_residents_only: Set to True to target only the individuals who
                started the simulation in this node and are still in the node.
            blackout: Set to True if you don't want the triggered intervention
                to be distributed to the same person more than once a day.
            check_at_trigger: if triggered event is delayed, you have an
                option to check individual/node's eligibility at the initial trigger
                or when the event is actually distributed after delay.

        Returns:
            Campaign event.

    """
    if delay:
        # If delay is just a number, convert to dict.
        delay_iv = DelayedIntervention(camp, Configs=[intervention], Delay_Dict=delay)
        event = TriggeredCampaignEvent(camp, Start_Day=start_day, Event_Name="Delayed Triggered Intervention",
                                       Triggers=triggers, Intervention_List=[delay_iv],
                                       Property_Restrictions=ip_targeting, Demographic_Coverage=coverage,
                                       Target_Age_Min=target_age_min, Target_Age_Max=target_age_max,
                                       Target_Gender=target_sex, Target_Residents_Only=target_residents_only,
                                       Duration=duration)
    else:
        event = TriggeredCampaignEvent(camp, Start_Day=start_day, Event_Name="Immediate Triggered Intervention",
                                       Triggers=triggers, Intervention_List=[intervention],
                                       Property_Restrictions=ip_targeting, Demographic_Coverage=coverage,
                                       Target_Age_Min=target_age_min, Target_Age_Max=target_age_max,
                                       Target_Gender=target_sex, Target_Residents_Only=target_residents_only,
                                       Duration=duration)

    return event


def change_individual_property_at_age(camp, new_ip_key, new_ip_value, change_age_in_days, revert_in_days,
                                      ip_targeting_key, ip_targeting_value, coverage=1.0):
    """
        Create and return a campaign event that changes a person's Individual Properties once they turns a certain age. 
        e.g., change_individual_property_at_age(cb, 'ForestGoing', 'LovesForest', coverage=0.6,
        change_age_in_days=15*365, revert=20*365)

        Args:
            camp: emod_api.campaign object with schema_path set.
            new_ip_key: The new IP key.
            new_ip_value: The new IP value.
            change_age_in_days: The age at which the individual transitions (in units of days).
            revert_in_days: How many days they remain with the new property.
            ip_targeting_key: The IP key a person must have to receive this.
            ip_targeting_value: The IP value a person must have to receive this.
            coverage: Optional fraction to limit this to a subset of the target population.

        Returns:
            Campaign event.

    """
    iv = PropertyValueChanger(camp, Target_Property_Key=new_ip_key, Target_Property_Value=new_ip_value,
                              Revert=revert_in_days)
    # TBD: migrate this to use triggered_campaign_event_with_optional_delay
    return triggered_campaign_delay_event(camp, start_day=1, trigger="Births", coverage=coverage,
                                          delay={"Delay_Period_Constant": change_age_in_days}, intervention=iv,
                                          ip_targeting={ip_targeting_key: ip_targeting_value})


def change_individual_property_triggered(camp,
                                         triggers: list,
                                         new_ip_key: str,
                                         new_ip_value: str,
                                         start_day: int = 0,
                                         daily_prob: float = 1,
                                         max_duration: int = 9.3228e+35,
                                         revert_in_days: int = -1,

                                         node_ids: list = None,  # where

                                         ip_restrictions: list = None,
                                         coverage: float = 1.0,
                                         target_age_min: float = 0,
                                         target_age_max: float = _MAX_AGE,
                                         target_sex: str = "All",
                                         target_residents_only: bool = False,

                                         delay=None,
                                         listening_duration: int = -1,
                                         blackout: bool = True,
                                         check_at_trigger: bool = False
                                         ):
    """
        Change Individual Properties when a certain trigger is observed.

    Args: 
        camp: The instance containing the campaign builder and accumulator.
        triggers: A list of the events that will trigger the intervention. 
        new_ip_key: The individual property key to assign to the
            individual. For example, InterventionStatus.
        new_ip_value: The individual property value to assign to the
            individual. For example, RecentDrug.
        start_day: The day on which to start distributing the intervention
            (**Start_Day** parameter).
        node_ids: The list of nodes to apply this intervention to. If not provided, defaults to all nodes.
        daily_prob: The daily probability that an individual's property value
            will be updated (**Daily_Probability** parameter).
        max_duration: The maximum amount of time individuals have to move to a new
            **daily_prob**; individuals not moved to the new value by the end of
            **max_duration** keep the same value.
        revert_in_days: The number of days before a node reverts to its original
            property value. Default of 0 means the new value is kept forever.
        ip_restrictions: The IndividualProperty key:value pairs to target.
        coverage: The proportion of the population that will receive the
            intervention (**Demographic_Coverage** parameter).
        target_age_min: Minimum age to target.
        target_age_max: Maximum age to target.
        target_sex: Optional target just "MALE" or "FEMALE" individuals.
        target_residents_only: Set to True to target only the individuals who
            started the simulation in this node and are still in the node.

        delay: The number of days the campaign is delayed after being triggered.
        listening_duration: The number of time steps that the
            triggered campaign will be active for. Default is -1, which is
            indefinitely.

        blackout (advanced): Set to True if you don't want the triggered intervention
            to be distributed to the same person more than once a day.
        check_at_trigger (advanced): if triggered event is delayed, you have an
            option to check individual/node's eligibility at the initial trigger
            or when the event is actually distributed after delay.

        Returns:
            N/A.
    """

    iv = PropertyValueChanger(camp, Target_Property_Key=new_ip_key, Target_Property_Value=new_ip_value,
                              Daily_Probability=daily_prob, Maximum_Duration=max_duration, Revert=revert_in_days)
    tce = triggered_campaign_event_with_optional_delay(camp, start_day=start_day, intervention=iv, triggers=triggers,
                                                       delay=delay, ip_targeting=ip_restrictions, coverage=coverage,
                                                       target_age_min=target_age_min, target_age_max=target_age_max,
                                                       target_sex=target_sex,
                                                       target_residents_only=target_residents_only,
                                                       duration=listening_duration, blackout=blackout,
                                                       check_at_trigger=check_at_trigger)
    camp.add(tce)


def change_individual_property_scheduled(camp,
                                         new_ip_key,
                                         new_ip_value,
                                         start_day: int = 0,
                                         number_repetitions: int = 1,
                                         timesteps_between_reps: int = -1,
                                         node_ids: list = None,  # where
                                         daily_prob: float = 1,
                                         max_duration: int = 9.3228e+35,
                                         revert_in_days: int = -1,
                                         ip_restrictions: list = None,
                                         coverage: float = 1.0,
                                         target_age_min: float = 0,
                                         target_age_max: float = _MAX_AGE,
                                         target_sex: str = "All",
                                         target_residents_only: bool = False
                                         ):
    """
        Change Individual Properties at a given time.

    Args: 
        camp: The instance containing the campaign builder and accumulator.
        new_ip_key: The individual property key to assign to the
            individual. For example, InterventionStatus.
        new_ip_value: The individual property value to assign to the
            individual. For example, RecentDrug.
        start_day: The day on which to start distributing the intervention
            (**Start_Day** parameter).
        node_ids: The list of nodes to apply this intervention to. If not provided, defaults to all nodes.
        daily_prob: The daily probability that an individual's property value
            will be updated (**Daily_Probability** parameter).
        max_duration: The maximum amount of time individuals have to move to a new
            **daily_prob**; individuals not moved to the new value by the end of
            **max_duration** keep the same value.
        revert_in_days: The number of days before an individual reverts to its original
            property value. Default of -1 means the new value is kept forever.
        ip_restrictions: The IndividualProperty key:value pairs to target.
        coverage: The proportion of the population that will receive the
            intervention (**Demographic_Coverage** parameter).
        target_age_min: Minimum age to target.
        target_age_max: Maximum age to target.
        target_sex: Optional target just "MALE" or "FEMALE" individuals.
        target_residents_only: Set to True to target only the individuals who
            started the simulation in this node and are still in the node.

        Returns:
            N/A.

    """

    iv = PropertyValueChanger(camp, Target_Property_Key=new_ip_key, Target_Property_Value=new_ip_value,
                              Daily_Probability=daily_prob, Maximum_Duration=max_duration, Revert=revert_in_days)
    sce = ScheduledCampaignEvent(camp, Intervention_List=[iv], Start_Day=start_day, Node_Ids=node_ids,
                                 Number_Repetitions=number_repetitions,
                                 Timesteps_Between_Repetitions=timesteps_between_reps,
                                 Property_Restrictions=ip_restrictions, Demographic_Coverage=coverage,
                                 Target_Age_Min=target_age_min, Target_Age_Max=target_age_max, Target_Gender=target_sex,
                                 Target_Residents_Only=target_residents_only)
    camp.add(sce)


def change_individual_property(camp,
                               target_property_name: str,  # what...
                               target_property_value: str,
                               start_day: int = 0,  # when
                               number_repetitions: int = 1,
                               timesteps_between_reps: int = -1,
                               node_ids: list = None,  # where
                               daily_prob: float = 1,
                               max_duration: int = 9.3228e+35,
                               revert: int = -1,
                               coverage: float = 1,  # who
                               ip_restrictions: list = None,
                               target_age_min: float = 0,
                               target_age_max: float = _MAX_AGE,
                               target_sex: str = "All",
                               target_residents_only: bool = False,
                               trigger_condition_list: list = None,  # the why...
                               triggered_campaign_delay: int = 0,  # (well, kind of when again)
                               listening_duration: int = -1,
                               blackout_flag: bool = True,  # advanced trigger stuff
                               check_eligibility_at_trigger: bool = False):
    """
        Add an intervention that changes the individual property value to another on a
        particular day OR after a triggering event using the
        **PropertyValueChanger** class. Deprecated. Prefer change_individual_property_scheduled
        or change_individual_property_triggered depending on the use case.
        
    Args:
        camp: emod_api.campaign object with schema_path set.

        target_property_name: The individual property key to assign to the
            individual. For example, Risk.
        target_property_value: The individual property value to assign to the
            individual. For example, High.

        start_day: The day on which to start distributing the intervention. 
        number_repetitions: Optional repeater value. Does not work with triggers.
        timesteps_between_reps: Gap between repetitions, optional. Does not work with triggers.

        node_ids: The list of nodes to apply this intervention to.  Defaults to all.

        daily_prob: The daily probability that an individual's property value
            will be updated (**Daily_Probability** parameter).
        max_duration: The number of days to continue the intervention after
            **start_day**.
        revert: The number of days before an individual reverts to its original
            property value. Default of -1 means the new value is kept forever.

        coverage: The proportion of the population that will receive the
            intervention (**Demographic_Coverage** parameter).
        ip_restrictions: The IndividualProperty key:value pairs to target. 
            Usually this will be the same key but different from the 
            target_property_xxx entries.
        target_residents_only: Set to True to target only the individuals who
            started the simulation in this node and are still in the node.
        target_age_min: Optional minimum age, defaults to 0.
        target_age_max: Optional maximum age, defaults to inf.
        target_sex: Optional target sex, defaults to both.

        triggered_campaign_delay: The number of days the campaign is delayed
            after being triggered.
        trigger_condition_list: A list of the events that will
            trigger the intervention. If included, **start_day** is the day
            when monitoring for triggers begins.
        listening_duration: The number of time steps that the
            triggered campaign will be active for. Default is -1, which is
            indefinitely.
        blackout_flag: Set to True if you don't want the triggered intervention
            to be distributed to the same person more than once a day.
        check_eligibility_at_trigger: if triggered event is delayed, you have an
            option to check individual/node's eligibility at the initial trigger
            or when the event is actually distributed after delay.

    Returns:
        None

    """

    if trigger_condition_list:
        return change_individual_property_triggered(camp,
                                                    start_day=start_day,
                                                    coverage=coverage,
                                                    max_duration=max_duration,
                                                    daily_prob=daily_prob,
                                                    triggers=trigger_condition_list,
                                                    new_ip_key=target_property_name,
                                                    new_ip_value=target_property_value,
                                                    revert_in_days=revert,
                                                    ip_restrictions=ip_restrictions,
                                                    target_age_min=target_age_min,
                                                    target_age_max=target_age_max,
                                                    target_sex=target_sex,
                                                    target_residents_only=target_residents_only,
                                                    delay=triggered_campaign_delay,
                                                    listening_duration=listening_duration,
                                                    blackout=blackout_flag,
                                                    check_at_trigger=check_eligibility_at_trigger,
                                                    node_ids=node_ids)
    else:
        return change_individual_property_scheduled(camp,
                                                    start_day=start_day,
                                                    coverage=coverage,
                                                    max_duration=max_duration,
                                                    daily_prob=daily_prob,
                                                    number_repetitions=number_repetitions,
                                                    timesteps_between_reps=timesteps_between_reps,
                                                    new_ip_key=target_property_name,
                                                    new_ip_value=target_property_value,
                                                    revert_in_days=revert,
                                                    ip_restrictions=ip_restrictions,
                                                    target_residents_only=target_residents_only,
                                                    target_age_min=target_age_min,
                                                    target_age_max=target_age_max,
                                                    target_sex=target_sex,
                                                    node_ids=node_ids
                                                    )
