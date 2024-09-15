#!/usr/bin/env python

from emod_api.interventions import outbreak as ob
from emod_api import campaign as camp

camp.schema_path = "schema.json" # we should do this earlier but the default is schema.json
camp.add( ob.new_intervention( camp, 30, cases = 44  ) )
camp.save( "campaign_outbreaks.json" )
