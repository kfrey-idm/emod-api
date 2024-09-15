"""
argparse for command-line usage
-s schema file
-m model name
-c config file

Sample code:
    from emod_api.config import schema_to_config as s2c
    builder = s2c.SchemaConfigBuilder()
    builder.enumerate_params()
    builder.validate_dependent_params()
    builder.write_config_file()

That will look for a local file called schema.json and produce a file called config.json that should work with an Eradication binary that produced the schema.json.

To build a default config for MALARIA_SIM, do:
    builder = s2c.SchemaConfigBuilder( model="MALARIA_SIM" ) 

To generate a schema.json file from a binary, see help text for emod_api.schema.
"""

import json
from emod_api.schema import get_schema as gs

class SchemaConfigBuilder:
    def __init__(self, schema_name="schema.json",
                 model="GENERIC_SIM",
                 config_out="config.json",
                 debug=False):
        self.schemaname=schema_name
        with open(self.schemaname) as infile:
            self.schema = json.load(infile) 
        self.model=model
        self.configout=config_out
        self.debug=debug
        self.dependent_params = None
        self.root_params = None
        self.validated_dependencies = {}
        self._enumerate_params()
        self._validate_dependent_params()
        self._write_config_file()

    def _enumerate_params(self):
        dependent_params = {}
        independent_params = {}
        config_schema = self.schema['config']
        for root in config_schema.keys():
            root_node = config_schema[root]
            for param in root_node.keys():
                param_node = root_node[param]
                if param.endswith('_Params') and len(param_node) == 1: # Keys-as-nodes type parameter
                    param_node['default'] = {}
                    independent_params[param] = param_node
                if 'default' in param_node: #This is probably a parameter
                    if 'depends-on' in param_node:
                        if not 'required-simtypes' in param_node:
                            dependencies = []
                            dependency_dict = param_node['depends-on']
                            for d_key in dependency_dict:
                            # if len(dependency_dict) == 1:
                            #    d_key = list(dependency_dict.keys())[0]
                                my_dependency = {}
                                my_dependency['dependent_param'] = d_key
                                my_dependency['dependent_value'] = dependency_dict[d_key]
                                my_dependency['default'] = param_node['default']
                                dependencies.append(my_dependency)
                            dependent_params[param] = dependencies
                        else:
                            if self.model in param_node['required-simtypes']:
                                independent_params[param] = param_node
                                independent_params[param]['default'] = param_node['required-simtypes'][self.model]
                    else:
                        independent_params[param] = param_node
        if self.debug:
            with open('DEBUG_dependent_params.json','w') as outfile:
                json.dump(dependent_params, outfile, indent=4, sort_keys=True)
            with open('DEBUG_root_params.json','w') as outfile:
                json.dump(independent_params, outfile, indent=4, sort_keys=True)
        self.dependent_params = dependent_params
        self.root_params = independent_params


    def _validate_dependent_params(self):
        for d in self.dependent_params:
            dependency_list = self.dependent_params[d]
            looking_good = True
            for d_item in dependency_list:
                param = d_item['dependent_param']
                requirement = d_item['dependent_value']
                if not self._check_single_param(d, param, requirement):
                    looking_good = False
            if looking_good:
                validated = {}
                validated['default'] = self.dependent_params[d][0]['default']
                dependencies = []
                for d_item in dependency_list:
                    dep = {}
                    dep['param'] = d_item['dependent_param']
                    dep['requirement'] = d_item['dependent_value']
                    dependencies.append(dep)
                validated['dependencies'] = dependencies
                self.validated_dependencies[d] = validated
        if self.debug:
            with open('DEBUG_validated_requirements.json','w') as outfile:
                json.dump(self.validated_dependencies, outfile, indent=4, sort_keys=True)

    def _requirement_is_met(self, param, param_requirement, param_default):
        if self.debug:
            print(f'requirement check param: {param} param_requirement: {param_requirement} param_default: {param_default}')
        if param_requirement == param_default:
            return True
        elif isinstance(param_requirement, str) and  ',' in param_requirement: # Lists of things, including Simulation_Type
            valid_options = param_requirement.split(',')
            if self.debug:
                print(f'Splitting a list. Valid options: {valid_options}')
            if param_default in valid_options:
                return True
        else:
            return False

    def _check_single_param(self, parent_param, dependency_param, requirement):
        if self.debug:
            print (f'check_single_param Param: {parent_param} Dependency: {dependency_param} Requirement: {requirement}')
        if dependency_param in self.root_params:
            root_default = self.root_params[dependency_param]['default']
            return self._requirement_is_met(dependency_param, requirement, root_default)
        elif dependency_param in self.validated_dependencies:
            dependency_default = self.validated_dependencies[dependency_param]['default']
            return self._requirement_is_met(dependency_param, requirement, dependency_default)
        elif dependency_param in self.dependent_params:
            # First, get the dependency's values
            dependency_list = self.dependent_params[dependency_param]
            looking_good = True
            for dependency in dependency_list:
                dependency_default = dependency['default']
                # Next, see if this local requirement is met
                if looking_good and self._requirement_is_met(param=dependency_param, param_requirement=requirement, param_default=dependency_default):
                    next_param = dependency['dependent_param']
                    next_requirement = dependency['dependent_value']
                    return self._check_single_param(dependency_param, next_param, next_requirement) # Now see if the dependency's requirement is met
                else:
                    looking_good = False # In this dependency, the requirement is unmet
                if not looking_good:
                    return False
        raise ValueError(f'Dependency {dependency_param} of parameter {parent_param} not found in root or dependent params.')# The dependency is neither in root params or dependent params

    def _write_config_file(self):
        config_params = self.root_params
        for v in self.validated_dependencies:
            if v not in config_params:
                config_params[v] = self.validated_dependencies[v]
        # config_params.update(self.validated_dependencies)
        parameters = {}
        for p in config_params:
            if self.debug:
                print(f'Attempting to write parameter: {p}\t config_params[p]: {config_params[p]}')
            if p == "Simulation_Type":
                parameters[p] = self.model
            else:
                value = config_params[p]['default']
                if value == "UNINITIALIZED STRING":
                    # This is not a debug message. Any 'patching' in code we do to the default config that's not actually in the schema defaults is given to user.
                    print( "Schema had default value of 'UNINITIALIZED STRING'; setting to ''." )
                    value = ""
                if self.debug:
                    print( f"Using default value of {value} for {p}." )
                parameters[p] = value 
        self.config = {'parameters':parameters}
        with open(self.configout,'w') as config_file:
            json.dump(self.config, config_file, indent=4, sort_keys=True)

def _do_main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--binary', help="Path to Eradication executable/binary")
    parser.add_argument('-s', '--schema', default="schema.json", help="Path to existing schema file")
    parser.add_argument('-m', '--modelname', default="GENERIC_SIM", help="model to configure (GENERIC_SIM)")
    parser.add_argument('-c', '--config', default="config.json", help="Config name to generate (config.json)")
    parser.add_argument('-d', '--debug', action='store_true', help="Turns on debugging")
    args = parser.parse_args()
    if args.binary:
        gs.dtk_to_schema( args.binary )
    builder = SchemaConfigBuilder(schema_name=args.schema, model=args.modelname,
                                  config_out=args.config, debug=args.debug)

    # # Uncomment when running in debugger
    # builder = SchemaConfigBuilder(schema_name='schema-generic-raw_fixed.json', model='GENERIC_SIM',
    #                              config_out='config-generic.json', debug=True)



if __name__ == "__main__":
    _do_main()
