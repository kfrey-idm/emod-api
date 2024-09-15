# Config

This submodule provides scripts for creating what we have historically referred to as 'config.json' input files that can be directly ingested by the DTK (EMOD) for configuring the model itself, specifically turning features on or off and parameterizing those features.

- **default_from_schema_no_validation** is a very simple script that produces a default_config.json file from a DTK schema. Note that other people have done a lot more work on doing this properly. This is a 10-line version. There are bugs filed against DTK because there are some defaults that don't actually work with the DTK. Nothing here attempts to fix that.

  `    > python -m emod_api.config.default_from_schema_no_validation schema.json`

- **from_schema** is a more complete solution. In the sequence below we assume you have an Eradication, preferably a disease-specific build, and then the -m <sim_type> should match that. Generic is where most of the testing has been done.

```
      > python -m emod_api.config.from_schema -e /path/to/Eradication -m GENERIC_SIM -c generic_config.json
```
  Now you should have a config.json that can be used by Eradication.

  Note that if you already have a schema file you can use that directly, but then it's up to you to be sure the schema you're using matches the binary.

```
      > python -m emod_api.config.from_schema -s /path/to/schema.json -m GENERIC_SIM -c generic_config.json
```
  Again you should have a config.json that can be used by Eradication.

## Config Utilities

### Param Overrides -> Config.json (Method 1)

- Note that the conversion of a param_overrides.json (or parameter-of-interest.json if you prefer) can be done by the DTK through embedded Python pre-processing or you can do it manually and then just use the config.json after that if that's your preferred workflow. If you want to do the latter:

      > python -m emod_api.config.from_overrides param_overrides.json

Now you should have a config.json that can be used by Eradication.

- Note that the poi.json needs to have a "Default_Config_Path" in there that points to the defaults or base config.

### Param Overrides -> Config.json (Method 2)

Sample code:
```
import config.config_from_poi_and_binary as conf
import sys

def set_params( config ):
    config.parameters.Enable_Termination_On_Zero_Total_Infectivity = 1
    config.parameters.Minimum_End_Time = 100
    config.parameters.Simulation_Duration = 365
    config.parameters.Enable_Demographics_Builtin = 0
    config.parameters.Enable_Vital_Dynamics = 0
    return config

conf.make_config_from_poi( sys.argv[1], set_params )
```

### W5ML -> campaign.json

- W5ML is a prototype campaign file format based on YAML that lets you just say When, Who, What, Where -- and maybe Why your intervention should go to, without worrying about event coordinators and nesting levels. It is most useful for simple intervention distributions where you don't want to worry about Event Coordinators and Node Sets. To convert a campaign.w5ml file into campaign.json, your Python code would be something like:

```
      > from emod_api.config import dtk_pre_process_w5ml as easy_camps
      > import json 
      > 
      > def application( config_path ):
      >    config_json = json.loads( open( config_name ).read() )
      >    camp_filename = config_json["parameters"]["Campaign_Filename"] 
      >    easy_camps.application( camp_filename )
      >    # Hmm, might be that you have to change 'campaign.w5ml' to 'campaign.json' in the config.
      >    return config_path 
```
- The W5ML schema is best captured by example:
```
  >   Events:
  >   - Who: <Coverage as 0-100%>, <Target Demographic, e.g., 'AllAges', or '0-5'>, <Target Sex, e.g., 'BothSexes'>
  >     When: <Start Day, e.g., 5. Can also do repeats -- details TBD>
  >     Where: <Nodes Targeted, e.g., 'Everywhere'>
  >     What: <The intervention itself, has to use actual params, but defaults can be omitted.>
  >       class: OutbreakIndividual
  >       Ignore_Immunity: 0
```


### Custom Events

- You can use custom events in campaign files and they will get automagically understood if you use the config.dtk_p*_adhocevents scripts. There are no more Custom_XXX_Event params.
- In the dtk_pre_process.py script:
```
      > import emod_api.config.dtk_pre_process_adhocevents as adhoc
      > 
      > def application( json_config_path ):
      >     return adhoc.application( json_config_path )

```

- And then in the dtk_post_process.py script:
```
      > import emod_api.config.dtk_post_process_adhocevents as adhoc
      > 
      > def application( output_path ):
      >     return adhoc.application( output_path )
```
