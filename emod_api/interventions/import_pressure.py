from .. import schema_to_class as s2c
import emod_api.campaign as camp
import json

schema_path = None

def new_intervention(timestep, durs=None, dips=None,
                     nods=None):  # These are NOT the module variables
    event = s2c.get_class_with_defaults("CampaignEvent", schema_path)
    coordinator = s2c.get_class_with_defaults("StandardEventCoordinator", schema_path)
    if coordinator is None:
        print("s2c.get_class_with_defaults returned None. Maybe no schema.json was provided.")
        return ""

    event.Event_Coordinator_Config = coordinator
    intervention = s2c.get_class_with_defaults("ImportPressure", schema_path)
    coordinator.Intervention_Config = intervention
    event.Start_Day = float(timestep)

    if not durs:
        raise ValueError(f"Please set durations -> 'durs'")
    if not dips:
        raise ValueError(f"Please set daily import pressures -> 'dips'")
    if len(dips) != len(durs):
        raise ValueError(f"durations (durs) and daily_import_pressures (dips) need to have same number of entries.\n"
                         f"len(durs) = {len(durs)} and len(dips) = {len(dips)}.\n")
    intervention.Durations = durs
    intervention.Daily_Import_Pressures = dips

    if nods:
        nodelist = s2c.get_class_with_defaults("NodeSetNodeList", schema_path)
        nodelist.Node_List = nods
        event.Nodeset_Config = nodelist

    return event


def new_intervention_as_file(timestep, filename=None):
    camp.set_schema("schema.json")
    camp.add(new_intervention(timestep, durs, dips, nods))

    if filename is None:
        filename = "import_pressure.json"
    camp.save(filename)
    return filename
