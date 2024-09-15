#!/usr/bin/python3

import emod_api.config.from_poi_and_binary as s2c

config = s2c.schema_to_config("schema.json")
config.parameters.Enable_Vital_Dynamics = True
config.parameters.Base_Infectivity_Constant = 2.6
config.parameters.to_file("my_awesome_config.json")
