from .. import schema_to_class as s2c
import emod_api.campaign as camp
import json

schema_path = None
durations = []
daily_import_pressures = []
nodes = []

def new_intervention( timestep, durs=durations, dips=daily_import_pressures, nods=nodes ): # These are NOT the module variables
    event = s2c.get_class_with_defaults( "CampaignEvent", schema_path )
    coordinator = s2c.get_class_with_defaults( "StandardEventCoordinator", schema_path )
    if coordinator is None:
        print( "s2c.get_class_with_defaults returned None. Maybe no schema.json was provided." )
        return ""

    event.Event_Coordinator_Config = coordinator
    intervention = s2c.get_class_with_defaults( "ImportPressure", schema_path )
    coordinator.Intervention_Config = intervention
    event.Start_Day = float(timestep)

    if len( durs ) == 0:
        Ex = ValueError()
        Ex.strerror = "durations not set."
        raise Ex
    if len( dips  ) == 0:
        Ex = ValueError()
        Ex.strerror = "daily_import_pressures not set."
        raise Ex
    if len( dips ) != len( durs ):
        Ex = ValueError()
        Ex.strerror = "durations and daily_import_pressures neeed to have same number of entries." 
        raise Ex
    intervention.Durations = durs
    intervention.Daily_Import_Pressures = dips

    if len(nods) > 0:
        nodelist = s2c.get_class_with_defaults( "NodeSetNodeList", schema_path )
        nodelist.Node_List = nods
        event.Nodeset_Config = nodelist

    return event

def new_intervention_as_file( timestep, filename=None ): 
    camp.schema_path = "schema.json"
    camp.add( new_intervention( timestep, durations, daily_import_pressures, nodes ), first=True )

    if filename is None:
        filename = "import_pressure.json"
    camp.save( filename )
    return filename
