from .. import schema_to_class as s2c
import emod_api.campaign as camp
import json


def seed_by_coverage(campaign_builder, timestep, coverage=0.01, ignore_immunity=None, intervention_only=False):
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
        print(str(ex))
        print("Using 'Outbreak' intervention instead of OutbreakIndividual and Max_Case_Per_Node.")
        iv_name = "Outbreak"

    event.Event_Coordinator_Config = coordinator
    intervention = s2c.get_class_with_defaults(iv_name, schema_path)
    if iv_name == "Outbreak":
        intervention.Number_Cases_Per_Node = cases
    coordinator.Intervention_Config = intervention
    event.Start_Day = float(timestep)

    return event


def new_intervention_as_file(camp, timestep, cases=1, filename=None):
    camp.add(new_intervention(camp, timestep, cases), first=True)
    if filename is None:
        filename = "outbreak.json"
    camp.save(filename)
    return filename
