import os
import json
import unittest
import emod_api.demographics.Demographics as Demographics
import emod_api.demographics.Node as Node
import emod_api.demographics.DemographicsTemplates as DT
import manifest
import math
from datetime import date
import getpass
import pandas as pd
import numpy as np
import pathlib
from emod_api.demographics.PropertiesAndAttributes import IndividualAttributes, IndividualProperty, IndividualProperties, NodeAttributes
import emod_api.demographics.PreDefinedDistributions as Distributions

# from pathlib import Path
# import sys
# parent = Path(__file__).resolve().parent
# sys.path.append(str(parent))


class DemoTest(unittest.TestCase):
    def setUp(self) -> None:
        print(f"\n{self._testMethodName} started...")
        self.out_folder = manifest.demo_folder

    def test_demo_basic_node(self):
        out_filename = os.path.join(self.out_folder, "demographics_basic_node.json")
        demog = Demographics.from_template_node()
        print(f"Writing out file: {out_filename}.")
        demog.generate_file(out_filename)
        self.assertTrue(os.path.isfile(out_filename), msg=f'{out_filename} is not generated.')
        with open(out_filename, 'r') as demo_file:
            demog_json = json.load(demo_file)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['Latitude'], 0)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['Longitude'], 0)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['InitialPopulation'], 1e6)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['FacilityName'], "Erewhon")
        self.assertEqual(demog_json['Nodes'][0]['NodeID'], 1)

    def test_demo_basic_node_2(self):
        out_filename = os.path.join(self.out_folder, "demographics_basic_node_2.json")
        lat = 1111
        lon = 999
        pop = 888
        name = 'test_name'
        forced_id = 777
        demog = Demographics.from_template_node(lat=lat, lon=lon, pop=pop, name=name, forced_id=forced_id)
        print(f"Writing out file: {out_filename}.")
        demog.generate_file(out_filename)
        self.assertTrue(os.path.isfile(out_filename), msg=f'{out_filename} is not generated.')
        with open(out_filename, 'r') as demo_file:
            demog_json = json.load(demo_file)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['Latitude'], lat)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['Longitude'], lon)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['InitialPopulation'], pop)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['FacilityName'], name)
        self.assertEqual(demog_json['Nodes'][0]['NodeID'], forced_id)
        self.assertEqual(len(demog.implicits), 1)

    def test_demo_node(self):
        out_filename = os.path.join(self.out_folder, "demographics_node.json")
        lat = 22
        lon = 33
        pop = 99
        area = 2.0
        name = 'test_node'
        forced_id = 1
        the_nodes = [Node.Node(lat, lon, pop, name=name, area=area, forced_id=forced_id)]
        demog = Demographics.Demographics(nodes=the_nodes)
        print(f"Writing out file: {out_filename}.")
        demog.generate_file(out_filename)
        self.assertTrue(os.path.isfile(out_filename), msg=f'{out_filename} is not generated.')
        with open(out_filename, 'r') as demo_file:
            demog_json = json.load(demo_file)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['Latitude'], lat)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['Longitude'], lon)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['InitialPopulation'], pop)
        self.assertEqual(demog_json['Nodes'][0]['NodeAttributes']['FacilityName'], name)
        self.assertEqual(demog_json['Nodes'][0]['NodeID'], forced_id)
        self.assertEqual(len(demog.implicits), 1)

        metadata = demog_json['Metadata']
        today = date.today()
        self.assertEqual(metadata['DateCreated'], today.strftime("%m/%d/%Y"))
        self.assertEqual(metadata['Tool'], "emod-api")
        self.assertEqual(metadata['NodeCount'], 1)
        self.assertEqual(metadata['Author'], getpass.getuser())
        # todo: test area and density when they are ready

    def test_set_default_properties(self):
        demog = Demographics.from_template_node()
        demog.SetDefaultProperties()
        self.assertIn('BirthRate', demog.raw['Defaults']['NodeAttributes'])
        self.assertIn('AgeDistribution', demog.raw['Defaults']['IndividualAttributes'])
        self.assertIn('MortalityDistribution', demog.raw['Defaults']['IndividualAttributes'])
        self.assertIn('SusceptibilityDistribution', demog.raw['Defaults']['IndividualAttributes'])
        self.assertIn('IndividualProperties', demog.raw['Defaults'])
        self.assertEqual(len(demog.implicits), 5)

    def test_add_age_dependent_transmission(self):
        demog = Demographics.from_template_node()
        demog.SetDefaultProperties()
        age_bin_edges_in_years = [0, 1, 2, -1]
        transmission_matrix = [[0.2, 0.4, 1.0], [0.2, 0.4, 1.0], [0.2, 0.4, 1.0]]
        demog.AddAgeDependentTransmission(Age_Bin_Edges_In_Years=age_bin_edges_in_years,
                                          TransmissionMatrix=transmission_matrix)

        self.assertEqual('Age_Bin', demog.raw['Defaults']['IndividualProperties'][0]['Property'])
        self.assertEqual(age_bin_edges_in_years, demog.raw['Defaults']['IndividualProperties'][0][
            'Age_Bin_Edges_In_Years'])
        self.assertEqual(transmission_matrix, demog.raw['Defaults']['IndividualProperties'][0]['TransmissionMatrix'][
            'Matrix'])
        self.assertEqual(len(demog.implicits), 7)

    def test_add_ip_and_hint(self):
        implicit_config_fns = []
        demog = Demographics.from_template_node()
        demog.SetDefaultProperties()
        property = 'Risk'
        values = ['high', 'low']
        initial_distribution = [0.1, 0.9]
        demog.AddIndividualPropertyAndHINT(Property=property, Values=values, InitialDistribution=initial_distribution)

        self.assertEqual(property, demog.raw['Defaults']['IndividualProperties'][0]['Property'])
        self.assertEqual(values, demog.raw['Defaults']['IndividualProperties'][0][
            'Values'])
        self.assertEqual(initial_distribution,
                         demog.raw['Defaults']['IndividualProperties'][0]['Initial_Distribution'])
        self.assertEqual(len(demog.implicits), 5)

        # Error handling

        demog.raw['Defaults'].pop('IndividualProperties', None)
        demog.AddIndividualPropertyAndHINT(Property=property, Values=values, InitialDistribution=initial_distribution)
        self.assertEqual(len(demog.raw['Defaults']['IndividualProperties']), 1)

        with self.assertRaises(ValueError) as context:
            demog.AddIndividualPropertyAndHINT(Property=property, Values=values, InitialDistribution=initial_distribution)        

    def test_add_ip_and_hint_disable_whitelist(self):
        """
        test property not in whitelist for auto-set Disable_IP_Whitelist in config, #94

        """
        demog = Demographics.from_template_node()
        demog.SetDefaultProperties()
        property = 'my_propertry'
        values = ['1', '2']
        initial_distribution = [0.2, 0.8]
        demog.AddIndividualPropertyAndHINT(Property=property, Values=values, InitialDistribution=initial_distribution)

        self.assertEqual(property, demog.raw['Defaults']['IndividualProperties'][0]['Property'])
        self.assertEqual(values, demog.raw['Defaults']['IndividualProperties'][0][
            'Values'])
        self.assertEqual(initial_distribution,
                         demog.raw['Defaults']['IndividualProperties'][0]['Initial_Distribution'])
        self.assertEqual(len(demog.implicits), 6)

    def test_add_ip_and_hint_agebin(self):
        demog = Demographics.from_template_node()
        demog.SetDefaultProperties()
        property = 'Age_Bin'
        values = ['50+', '50-']
        initial_distribution = [0.5, 0.5]
        transmission_matrix = [[0, 1], [1, 0]]
        demog.AddIndividualPropertyAndHINT(Property=property, Values=values, InitialDistribution=initial_distribution,
                                           TransmissionMatrix=transmission_matrix)

        self.assertEqual(property, demog.raw['Defaults']['IndividualProperties'][0]['Property'])
        self.assertEqual(values, demog.raw['Defaults']['IndividualProperties'][0][
            'Age_Bin_Edges_In_Years'])
        self.assertEqual(transmission_matrix,
                         demog.raw['Defaults']['IndividualProperties'][0]['TransmissionMatrix']['Matrix'])
        self.assertEqual(len(demog.implicits), 6)

    def test_add_ip_and_hint_transmission_matrix(self):
        demog = Demographics.from_template_node()
        demog.SetDefaultProperties()
        property = 'QualityOfCare'
        values = ['High', 'Low']
        initial_distribution = [0.3, 0.7]
        transmission_matrix = [[1, 0], [0, 1]]
        demog.AddIndividualPropertyAndHINT(Property=property, Values=values, InitialDistribution=initial_distribution,
                                           TransmissionMatrix=transmission_matrix)

        self.assertEqual(property, demog.raw['Defaults']['IndividualProperties'][0]['Property'])
        self.assertEqual(values, demog.raw['Defaults']['IndividualProperties'][0][
            'Values'])
        self.assertEqual(initial_distribution,
                         demog.raw['Defaults']['IndividualProperties'][0]['Initial_Distribution'])
        self.assertEqual(transmission_matrix,
                         demog.raw['Defaults']['IndividualProperties'][0]['TransmissionMatrix']['Matrix'])
        self.assertEqual(len(demog.implicits), 6)

    def test_add_ip_and_hint_defaults(self):
        demog = Demographics.from_template_node()
        demog.SetDefaultProperties()
        property = 'QualityOfCare'
        values = ['High', 'Low']
        demog.AddIndividualPropertyAndHINT(property, values)

        self.assertEqual(property, demog.raw['Defaults']['IndividualProperties'][0]['Property'])
        self.assertEqual(values, demog.raw['Defaults']['IndividualProperties'][0]['Values'])
        self.assertIsNone(demog.raw['Defaults']['IndividualProperties'][0].get('Initial_Distribution'))
        self.assertIsNone(demog.raw['Defaults']['IndividualProperties'][0].get('TransmissionMatrix'))


    def test_set_individual_attributtes_with_fert_mort(self):
        demog = Demographics.from_template_node()
        birth_rate = 50/1000
        mort_rate = 25/1000
        demog.SetIndividualAttributesWithFertMort(CrudeBirthRate=birth_rate, CrudeMortRate=mort_rate)
        self.assertIn('AgeDistribution', demog.raw['Defaults']['IndividualAttributes']) # Template should add an age distribution
        self.assertIn('MortalityDistribution', demog.raw['Defaults']['IndividualAttributes'])
        true_mort_rate = -1 * (math.log(1 - mort_rate) / 365)
        self.assertEqual(demog.raw['Defaults']['IndividualAttributes']['MortalityDistribution']['ResultValues'], [[true_mort_rate], [true_mort_rate]])

    def test_set_default_properties_fert_mort(self):
        demog = Demographics.from_template_node()
        c_birth_rate = 20/1000
        c_mort_rate = 30/1000
        default_susc = {"DistributionValues": [[i * 365 for i in range(100)]], "ResultScaleFactor": 1, "ResultValues": [[1.0, 1.0] + [0.025 + 0.975 * math.exp(-(i - 1) / (2.5 / math.log(2))) for i in range(2, 100, 1)]]}

        demog.SetDefaultPropertiesFertMort(CrudeBirthRate=c_birth_rate, CrudeMortRate=c_mort_rate)
        self.assertEqual(demog.raw['Defaults']['NodeAttributes']['BirthRate'], c_birth_rate ) # Currently this is some default in the code
        self.assertEqual(demog.raw['Defaults']['IndividualAttributes']['SusceptibilityDistribution'], default_susc) 

    def test_set_overdispersion(self):
        demog = Demographics.from_template_node()
        new_overdispersion_value = 0.3
        demog.SetOverdispersion(new_overdispersion_value=new_overdispersion_value)

        self.assertEqual(new_overdispersion_value, demog.raw['Defaults']['NodeAttributes']['InfectivityOverdispersion'])
        self.assertEqual(len(demog.implicits), 2)
        # TODO: add a test to set different InfectivityOverdispersion values for specific nodes when feature is
        #  implemented.

    @staticmethod
    def demog_template_test(template, **kwargs):
        demog = Demographics.from_template_node()
        template(demog, **kwargs)
        return demog

    def test_template_simple_susceptibility_dist(self):
        mean_age_at_infection = 10
        template = DT.SimpleSusceptibilityDistribution
        demog= self.demog_template_test(template, meanAgeAtInfection=mean_age_at_infection)
        self.assertIn('SusceptibilityDistribution', demog.raw['Defaults']['IndividualAttributes'])
        # todo: assert the key:value pairs in the distribution and mean_age_at_infection

        # make sure mean age is in the description
        self.assertIn('SusceptibilityDist_Description', demog.raw['Defaults']['IndividualAttributes'])
        self.assertIn(str(mean_age_at_infection), demog.raw['Defaults']['IndividualAttributes']['SusceptibilityDist_Description'])
        self.assertEqual(len(demog.implicits), 2)

    def test_template_susceptibility_default(self):
        template = DT.DefaultSusceptibilityDistribution
        demog = self.demog_template_test(template)
        self.assertIn('SusceptibilityDistribution', demog.raw['Defaults']['IndividualAttributes'])
        self.assertEqual(len(demog.implicits), 2)
        # todo: assert default mean_age_at_infection

    def test_template_init_suscept_constant(self):
        template = DT.InitSusceptConstant
        demog = self.demog_template_test(template=template)
        self.assertEqual(0, demog.raw['Defaults']['IndividualAttributes']['SusceptibilityDistributionFlag'])
        self.assertEqual(len(demog.implicits), 2)

    def test_template_everyone_initially_susceptible(self):
        template = DT.EveryoneInitiallySusceptible
        demog = self.demog_template_test(template=template)
        expect_susceptibility_distribution = {
            "DistributionValues": [
                [0, 36500]
            ],
            "ResultScaleFactor": 1,
            "ResultValues": [
                [1.0, 1.0]
            ]
        }
        self.assertEqual(expect_susceptibility_distribution, demog.raw['Defaults']['IndividualAttributes'][
            'SusceptibilityDistribution'])
        self.assertEqual(len(demog.implicits), 2)

    def test_template_no_initial_prevalence(self):
        template = DT.NoInitialPrevalence
        demog = self.demog_template_test(template=template)
        self.assertEqual(0, demog.raw['Defaults']['IndividualAttributes']['InitialPrevalence'])
        self.assertEqual(len(demog.implicits), 1)

    def test_template_init_age_uniform(self):
        template = DT.InitAgeUniform
        demog = self.demog_template_test(template=template)
        self.assertEqual(1, demog.raw['Defaults']['IndividualAttributes']['AgeDistributionFlag'])
        self.assertEqual(len(demog.implicits), 2)

    def test_template_age_structure_UNWPP(self):
        template = DT.AgeStructureUNWPP
        demog = self.demog_template_test(template=template)
        self.assertIn('AgeDistribution', demog.raw['Defaults']['IndividualAttributes'])
        self.assertEqual(len(demog.implicits), 2)

    def test_template_equilibrium_age_dist_from_birth_and_mort_rates(self):
        demog = Demographics.from_template_node()
        demog.SetEquilibriumAgeDistFromBirthAndMortRates(CrudeBirthRate=20/1000, CrudeMortRate=10/1000)
        self.assertIn('AgeDistribution', demog.raw['Defaults']['IndividualAttributes'])
        self.assertEqual(len(demog.implicits), 2)
        print(demog.raw)

    def set_default_from_template_test(self, template):
        demog = Demographics.from_template_node()
        demog.SetDefaultFromTemplate(template=template)
        for key, value in template.items():
            self.assertEqual(value, demog.raw['Defaults']['IndividualAttributes'][key])
        return demog

    def test_set_default_from_template_full_risk(self):
        demog = Demographics.from_template_node()
        DT.FullRisk(demog)
        template_setting = {"RiskDist_Description": "Full risk",
                            "RiskDistributionFlag": 0,
                            "RiskDistribution1": 1,
                            "RiskDistribution2": 0}
        for key, value in template_setting.items():
            self.assertEqual(value, demog.raw['Defaults']['IndividualAttributes'][key])
        self.assertEqual(len(demog.implicits), 2)

    def test_set_default_from_template_init_risk_uniform(self):
        min_risk = 0.1
        max_risk = 0.9
        demog = Demographics.from_template_node()
        demog.SetHeteroRiskUniformDist( min_risk, max_risk )
        template_setting = {"RiskDistributionFlag": 1,
                            "RiskDistribution1": min_risk,
                            "RiskDistribution2": max_risk}
        for key, value in template_setting.items():
            self.assertEqual(value, demog.raw['Defaults']['IndividualAttributes'][key])

        self.assertEqual(1, demog.raw['Defaults']['IndividualAttributes']['RiskDistributionFlag'])
        self.assertEqual(min_risk, demog.raw['Defaults']['IndividualAttributes']['RiskDistribution1'])
        self.assertEqual(max_risk, demog.raw['Defaults']['IndividualAttributes']['RiskDistribution2'])
        self.assertEqual(len(demog.implicits), 2)

    def test_set_default_from_template_init_risk_lognormal(self):
        mean = 0.1
        sigma = 0.9
        demog = Demographics.from_template_node()
        demog.SetHeteroRiskLognormalDist( mean, sigma )
        template_setting = {"RiskDistributionFlag": 5,
                            "RiskDistribution1": mean,
                            "RiskDistribution2": sigma}
        for key, value in template_setting.items():
            self.assertEqual(value, demog.raw['Defaults']['IndividualAttributes'][key])

        self.assertEqual(5, demog.raw['Defaults']['IndividualAttributes']['RiskDistributionFlag'])
        self.assertEqual(mean, demog.raw['Defaults']['IndividualAttributes']['RiskDistribution1'])
        self.assertEqual(sigma, demog.raw['Defaults']['IndividualAttributes']['RiskDistribution2'])
        self.assertEqual(len(demog.implicits), 2)

    def test_set_default_from_template_init_risk_expon(self):
        mean = 0.1
        demog = Demographics.from_template_node()
        demog.SetHeteroRiskExponDist( mean )
        template_setting = {"RiskDistributionFlag": 3,
                            "RiskDistribution1": mean,
                            "RiskDistribution2": 0}
        for key, value in template_setting.items():
            self.assertEqual(value, demog.raw['Defaults']['IndividualAttributes'][key])

        self.assertEqual(3, demog.raw['Defaults']['IndividualAttributes']['RiskDistributionFlag'])
        self.assertEqual(mean, demog.raw['Defaults']['IndividualAttributes']['RiskDistribution1'])
        self.assertEqual(0, demog.raw['Defaults']['IndividualAttributes']['RiskDistribution2'])
        self.assertEqual(len(demog.implicits), 2)

    def test_set_default_from_template_mortality_rate_by_age(self):
        age_bin = [0, 10, 80]
        mort_rate = [0.00005, 0.00001, 0.0004]
        demog = Demographics.from_template_node()
        DT.MortalityRateByAge(demog=demog, age_bins=age_bin, mort_rates=mort_rate)
        mort_dist = demog.raw["Defaults"]["IndividualAttributes"]["MortalityDistribution"]
        self.assertEqual( 2, len(mort_dist['PopulationGroups'][0]) ) # number of sexes
        self.assertEqual( len(mort_rate), len(mort_dist['PopulationGroups'][1]) )
        self.assertIn('MortalityDistribution', demog.raw['Defaults']['IndividualAttributes']) # Can't use set_default_from_template_test since template is implicit

    def test_set_default_from_template_constant_mortality(self):
        demog = Demographics.from_template_node()
        demog.implicits = []
        mortality_rate = 0.0001
        demog.SetMortalityRate(mortality_rate=mortality_rate) # ca
        self.assertIn('MortalityDistribution', demog.raw['Defaults']['IndividualAttributes']) # Can't use set_default_from_template_test since template is implicit
        expected_rate = [[-1 * (math.log(1 - mortality_rate) / 365)]] * 2
        demog_rate = demog.raw['Defaults']['IndividualAttributes']['MortalityDistribution']['ResultValues']
        self.assertListEqual(expected_rate, demog_rate)

    def test_set_default_from_template_constant_mortality_list(self):
        demog = Demographics.from_template_node()
        mortality_rate = [[0.1, 0.2], [0.3, 0.4]]
        demog.SetMortalityRate(mortality_rate)
        expected_rate = -1 * (np.log(1 - np.array(mortality_rate))) / 365
        temp_result = demog.raw['Defaults']['IndividualAttributes']['MortalityDistribution']['ResultValues']
        np.testing.assert_almost_equal(expected_rate, np.array(temp_result))

    def test_generate_from_file_compatibility(self):
        input_filename = os.path.join(self.out_folder, "demographics_from_params.json")
        output_filename = os.path.join(self.out_folder, "demographics_from_params_comparison.json")

        self.pass_through_test(input_filename, output_filename)

    def test_generate_from_file_compatibility_Prashanth_single_node(self):
        input_filename = os.path.join(self.out_folder, "single_node_demographics.json")
        output_filename = os.path.join(self.out_folder, "single_node_demographics_comparison.json")

        self.pass_through_test(input_filename, output_filename)

    def test_generate_from_file_compatibility_Prashanth_4_nodes(self):
        input_filename = os.path.join(self.out_folder, "Namawala_four_node_demographics_for_Thomas.json")
        output_filename = os.path.join(self.out_folder, "Namawala_four_node_demographics_for_Thomas_comparison.json")

        self.pass_through_test(input_filename, output_filename)

    def pass_through_test(self, input_filename, output_filename):
        demog = Demographics.from_file(input_filename)
        demog.generate_file(output_filename)
        with open(input_filename, 'r') as demo_file:
            demog_json_original = json.load(demo_file)
        with open(output_filename, 'r') as demo_file2:
            demog_json_after_passthrough = json.load(demo_file2)
        for demog_json in [demog_json_original, demog_json_after_passthrough]:
            demog_json["Metadata"].pop("DateCreated")
            demog_json["Metadata"].pop("Author")
            demog_json["Metadata"].pop("Tool")

        self.maxDiff = None

        if "NodeAttributes" in demog_json_original['Defaults']:
            FacilityName = demog_json_original['Defaults']["NodeAttributes"].pop("FacilityName", None)
            self.assertEqual(FacilityName, demog_json_after_passthrough['Defaults']["NodeAttributes"].pop("FacilityName", None))

        for node_original, node_new in zip(demog_json_original['Nodes'], demog_json_after_passthrough['Nodes']):
            if "NodeAttributes" in node_original:
                FacilityName = node_original["NodeAttributes"].pop("FacilityName", None)

                if FacilityName:
                    self.assertEqual(FacilityName, node_new["NodeAttributes"].pop("FacilityName", None))
                else:
                    NodeID = node_original['NodeID']
                    self.assertEqual(NodeID, node_new["NodeAttributes"].pop("FacilityName", None))

                self.assertEqual(node_original.pop("NodeID"), node_new.pop("NodeID"))   # NodeID must exist, return no default

        self.assertDictEqual(demog_json_original, demog_json_after_passthrough)

    def test_from_csv(self):
        out_filename = os.path.join(self.out_folder, "demographics_from_csv.json")
        manifest.delete_existing_file(out_filename)
        id_ref = "from_csv_test"

        input_file = os.path.join(manifest.current_directory, 'data', 'demographics', 'demog_in.csv')
        demog = Demographics.from_csv(input_file, res=25/ 3600, id_ref=id_ref)
        self.assertEqual(demog.idref, id_ref)
        demog.SetDefaultProperties()
        demog.generate_file(out_filename)
        sorted_nodes = Demographics.get_node_ids_from_file(out_filename)

        self.assertEqual(demog.idref, id_ref)
        self.assertGreater(len(sorted_nodes), 0)

        self.assertTrue(os.path.isfile(out_filename), msg=f'{out_filename} is not generated.')
        with open(out_filename, 'r') as demo_file:
            demog_json = json.load(demo_file)

        # Checking we can grab a node
        inspect_node = demog.get_node(demog.nodes[15].id)
        self.assertEqual(inspect_node.id, demog.nodes[15].id, msg=f"This node should have an id of {demog.nodes[15].id} but instead it is {inspect_node.id}")

        with self.assertRaises(ValueError) as context:
            bad_node = demog.get_node(161839)

        self.assertEqual(demog_json['Metadata']['IdReference'], id_ref)

        self.assertDictEqual(demog_json, demog.raw)

        import pandas as pd
        csv_df = pd.read_csv(input_file, encoding='iso-8859-1')

        pop_threshold = 25000  # hardcoded value
        csv_df = csv_df[(6*csv_df['under5_pop']) >= pop_threshold]
        self.assertEqual(len(csv_df), len(demog_json['Nodes']))

        self.assertTrue(self.check_for_unique_node_id(demog.raw['Nodes']))

        # Produces error due to not assigning name to each node issue #221
        if False:
            location = pd.Series(["Seattle"]*4357)
        
            csv_df['loc'] = location

            self.assertFalse(any([name != "Seattle" for name in csv_df['loc']]))
            csv_df.to_csv("demographics_places_from_csv.csv")

            demog = Demographics.from_csv("demographics_places_from_csv.csv", res=25/ 3600)
            nodes = demog.nodes

            for index, node in enumerate(nodes):
                self.assertEqual(node.name, "Seattle", msg=f"Bad node found: {node} on line {index+2}")

    def test_from_csv_2(self):
        out_filename = os.path.join(self.out_folder, "demographics_from_csv_2.json")
        manifest.delete_existing_file(out_filename)

        input_file = os.path.join(manifest.current_directory, 'data', 'demographics', 'nodes.csv')
        demog = Demographics.from_csv(input_file, res=25 / 3600)
        demog.SetDefaultProperties()
        demog.generate_file(out_filename)
        sorted_nodes = Demographics.get_node_ids_from_file(out_filename)

        self.assertGreater(len(sorted_nodes), 0)

        self.assertTrue(os.path.isfile(out_filename), msg=f'{out_filename} is not generated.')

        with open(out_filename, 'r') as demo_file:
            demog_json = json.load(demo_file)

        # Checking we can grab a node
        inspect_node = demog.get_node(demog.nodes[0].id)
        self.assertEqual(inspect_node.id, demog.nodes[0].id, msg=f"This node should have an id of {demog.nodes[0].id} "
                                                                 f"but instead it is {inspect_node.id}")

        id_reference = 'from_csv' # hardcoded value
        self.assertEqual(demog_json['Metadata']['IdReference'], id_reference)

        self.assertDictEqual(demog_json, demog.raw)

        import pandas as pd
        csv_df = pd.read_csv(input_file, encoding='iso-8859-1')

        # checking if we have the same number of nodes and the number of rows in csv file
        self.assertEqual(len(csv_df), len(demog_json['Nodes']))

        self.assertTrue(self.check_for_unique_node_id(demog.raw['Nodes']))
        for index, row in csv_df.iterrows():
            pop = int(row['pop'])
            lat = float(row['lat'])
            lon = float(row['lon'])
            node_id = int(row['node_id'])
            self.assertEqual(pop, demog.nodes[index].node_attributes.initial_population)
            self.assertEqual(lat, demog.nodes[index].node_attributes.latitude)
            self.assertEqual(lon, demog.nodes[index].node_attributes.longitude)
            self.assertEqual(node_id, demog.nodes[index].forced_id)

    def test_from_csv_bad_id(self):
        input_file = os.path.join(manifest.current_directory, 'data', 'demographics', 'demog_in_faulty.csv')

        with self.assertRaises(ValueError):
            Demographics.from_csv(input_file, res=25 / 3600)

    def test_from_pop_csv(self):
        out_filename = os.path.join(self.out_folder, "demographics_from_pop_csv.json")
        manifest.delete_existing_file(out_filename)

        input_file = os.path.join(manifest.current_directory, 'data', 'demographics', 'nodes.csv')
        demog = Demographics.from_pop_csv(input_file)
        demog.SetDefaultProperties()
        demog.generate_file(out_filename)
        sorted_nodes = Demographics.get_node_ids_from_file(out_filename)

        self.assertGreater(len(sorted_nodes), 0)

        self.assertTrue(os.path.isfile(out_filename), msg=f'{out_filename} is not generated.')
        with open(out_filename, 'r') as demo_file:
            demog_json = json.load(demo_file)

        # Checking we can grab a node
        inspect_node = demog.get_node(demog.nodes[0].id)
        self.assertEqual(inspect_node.id, demog.nodes[0].id,
                         msg=f"This node should have an id of {demog.nodes[0].id} but instead it is {inspect_node.id}")

        with self.assertRaises(ValueError) as context:
            bad_node = demog.get_node(161839)

        id_reference = 'from_csv'  # hardcoded value
        self.assertEqual(demog_json['Metadata']['IdReference'], id_reference)

        self.assertDictEqual(demog_json, demog.raw)

        import pandas as pd
        csv_df = pd.read_csv(input_file, encoding='iso-8859-1')

        # the following assertion fails, logged as https://github.com/InstituteforDiseaseModeling/emod-api/issues/367
        # self.assertEqual(len(csv_df), len(demog_json['Nodes']))

        self.assertTrue(self.check_for_unique_node_id(demog.raw['Nodes']))

    def test_from_csv_birthrate(self):
        input_file = os.path.join(manifest.current_directory, 'data', 'demographics', 'nodes_with_birthrate.csv')
        demog = Demographics.from_csv(input_file)
        data = pd.read_csv(input_file)
        node_ids = list(data["node_id"])
        for node_id in node_ids:
            birth_rate = data[data["node_id"] == node_id]["birth_rate"].iloc[0]
            self.assertAlmostEqual(demog.get_node(node_id).birth_rate, birth_rate)

        bad_input = os.path.join(manifest.current_directory, 'data', 'demographics', 'bad_nodes_with_birthrate.csv')
        with self.assertRaises(ValueError):
            demog = Demographics.from_csv(bad_input)

    def test_from_params(self):
        out_filename = os.path.join(self.out_folder, "demographics_from_params.json")
        manifest.delete_existing_file(out_filename)

        totpop = 1e5
        num_nodes = 250
        frac_rural = 0.1
        implicit_config_fns = []
        demog = Demographics.from_params(tot_pop=totpop, num_nodes=num_nodes, frac_rural=frac_rural)
        demog.SetDefaultProperties()
        demog.generate_file(out_filename)

        self.assertTrue(os.path.isfile(out_filename), msg=f'{out_filename} is not generated.')
        with open(out_filename, 'r') as demo_file:
            demog_json = json.load(demo_file)

        id_reference = 'from_params'  # hardcoded value
        self.assertEqual(demog_json['Metadata']['IdReference'], id_reference)

        self.assertDictEqual(demog_json, demog.raw)

        self.assertEqual(num_nodes, len(demog_json['Nodes']))

        sum_pop = 0
        for node in demog_json['Nodes']:
            sum_pop += node['NodeAttributes']['InitialPopulation']
        # Todo: add this assertion back when #112 is fixed.
        # self.assertEqual(sum_pop, totpop)
        if sum_pop != totpop:
            print(f"Something went wrong, expected totpop is {totpop}, got {sum_pop} total population.")

        self.assertTrue(self.check_for_unique_node_id(demog.raw['Nodes']))

        # Todo: assert frac_rural after we figure out the definition of this parameter

    def test_overlay_node_attributes(self):
        # create simple demographics
        temp = {'node_id': [1, 2, 5, 10],
                'loc': ["loc1", "loc2", "loc3", "loc4"],
                'pop': [123, 234, 345, 678],
                'lon': [10, 11, 12, 13],
                'lat': [21, 22, 23, 24]}
        csv_file = pathlib.Path("test_overlay_population.csv")
        pd.DataFrame.from_dict(temp).to_csv(csv_file)
        demo = Demographics.from_csv(csv_file)

        airport_dont_override = 123
        demo.nodes[1].node_attributes.airport = airport_dont_override  # Change one item, it should not change after override
        node_attr_before_override = demo.nodes[3].node_attributes.to_dict()
        csv_file.unlink()

        # create overlay and update
        overlay_nodes = []
        new_population = 999
        new_name = "Test NodeAttributes"
        new_node_attributes = NodeAttributes(name=new_name, initial_population=new_population)
        empty_node_attributes = NodeAttributes()

        overlay_nodes.append(Node.OverlayNode(node_id=1, node_attributes=new_node_attributes))
        overlay_nodes.append(Node.OverlayNode(node_id=2, node_attributes=new_node_attributes))
        overlay_nodes.append(Node.OverlayNode(node_id=10, node_attributes=empty_node_attributes))
        demo.apply_overlay(overlay_nodes)

        # test if new values are used
        self.assertEqual(demo.nodes[0].node_attributes.initial_population, new_population)
        self.assertEqual(demo.nodes[0].node_attributes.name, new_name)

        # overriding with empty object does not change attributes
        temp1 = demo.nodes[3].node_attributes.to_dict()
        self.assertDictEqual(demo.nodes[3].node_attributes.to_dict(), node_attr_before_override)

    def test_all_members_to_dict(self):
        node_attributes = NodeAttributes(airport=1,
                                         altitude=12,
                                         area=0.5,
                                         birth_rate=123,
                                         country="country",
                                         growth_rate=0.123,
                                         name="name",
                                         latitude=1.0,
                                         longitude=2.0,
                                         metadata={"Meta": 123},
                                         initial_population=1234,
                                         region=45,
                                         seaport=56,
                                         larval_habitat_multiplier=[{"Larval": 123}],
                                         initial_vectors_per_species=123,
                                         infectivity_multiplier=0.5,
                                         extra_attributes={"Test_Parameter_1": 123})

        node_attributes.add_parameter("Test_Parameter_2", 123)
        number_vars = len(vars(node_attributes).items())
        number_vars_dict = len(node_attributes.to_dict())
        self.assertEqual(number_vars, number_vars_dict)

        # check conversion from and to dict
        node_attributes_from_dict = node_attributes.from_dict(node_attributes.to_dict())
        self.assertDictEqual(node_attributes_from_dict.to_dict(), node_attributes.to_dict())

    def test_overlay_list_of_nodes(self):
        # create simple demographics
        temp = {'node_id': [1, 2, 5, 10],
                'loc': ["loc1", "loc2", "loc3", "loc4"],
                'pop': [123, 234, 345, 678],
                'lon': [10, 11, 12, 13],
                'lat': [21, 22, 23, 24]}
        csv_file = pathlib.Path("test_overlay_population.csv")
        pd.DataFrame.from_dict(temp).to_csv(csv_file)
        demo = Demographics.from_csv(csv_file)
        csv_file.unlink()

        overlay_nodes = []  # list of all overlay nodes
        overlay_nodes_id_1 = [1, 2]  # Change susceptibility of nodes with ids 1 and 2
        for node_id in overlay_nodes_id_1:
            new_susceptibility_distribution_1 = IndividualAttributes.SusceptibilityDistribution(distribution_values=[0.1, 0.2],
                                                                                                          result_scale_factor=1,
                                                                                                          result_values=[0.1, 0.2])

            new_individual_attributes_1 = IndividualAttributes(susceptibility_distribution=new_susceptibility_distribution_1)
            overlay_nodes.append(Node.OverlayNode(node_id=node_id, individual_attributes=new_individual_attributes_1))

        overlay_nodes_id_2 = [5, 10]    # Change susceptibility of nodes with ids 5 and 10
        for node_id in overlay_nodes_id_2:
            new_susceptibility_distribution_2 = IndividualAttributes.SusceptibilityDistribution(distribution_values=[0.8, 0.9],
                                                                                                          result_scale_factor=1,
                                                                                                          result_values=[0.8, 0.9])

            new_individual_attributes_2 = IndividualAttributes(susceptibility_distribution=new_susceptibility_distribution_2)
            overlay_nodes.append(Node.OverlayNode(node_id=node_id, individual_attributes=new_individual_attributes_2))

        demo.apply_overlay(overlay_nodes)
        demo.generate_file("test_overlay_list_of_nodes.json")

        self.assertDictEqual(demo.nodes[0].individual_attributes.to_dict(), new_individual_attributes_1.to_dict())
        self.assertDictEqual(demo.nodes[1].individual_attributes.to_dict(), new_individual_attributes_1.to_dict())
        self.assertDictEqual(demo.nodes[2].individual_attributes.to_dict(), new_individual_attributes_2.to_dict())
        self.assertDictEqual(demo.nodes[3].individual_attributes.to_dict(), new_individual_attributes_2.to_dict())

    def test_add_individual_properties(self):
        # create simple demographics
        temp = {'NodeID': [1, 2, 5],
                'loc': ["loc1", "loc2", "loc3"],
                'pop': [123, 234, 345],
                'lon': [10, 11, 12],
                'lat': [21, 22, 23]}
        csv_file = pathlib.Path("test_overlay_population.csv")
        pd.DataFrame.from_dict(temp).to_csv(csv_file)
        demo = Demographics.from_csv(csv_file)
        csv_file.unlink()

        initial_distribution = [0.1, 0.3, 0.6]
        property = "Property"
        values = ["1", "2", "3"]
        transitions = [3, 4, 5]
        transmission_matrix = [[0.0, 0.0, 0.2],
                               [0.0, 0.0, 1.2],
                               [0.0, 0.0, 0.0]]
        node = demo.nodes[0]
        node.individual_properties.add(IndividualProperty(initial_distribution=initial_distribution,
                                                          property=property,
                                                          values=values,
                                                          transitions=transitions,
                                                          transmission_matrix=transmission_matrix
                                                          ))
        node = demo.nodes[2]
        node.individual_properties.add(IndividualProperty())
        node.individual_properties[0].initial_distribution = initial_distribution
        node.individual_properties[0].property = property
        node.individual_properties[0].values = values
        node.individual_properties[0].transitions = transitions
        node.individual_properties[0].transmission_matrix = transmission_matrix

        individual_properties_reference = {
            "Initial_Distribution": initial_distribution,
            "Property": property,
            "Values": values,
            "Transitions": transitions,
            "TransmissionMatrix": transmission_matrix}

        self.assertDictEqual(demo.nodes[0].individual_properties[0].to_dict(), individual_properties_reference)
        self.assertDictEqual(demo.nodes[2].individual_properties[0].to_dict(), individual_properties_reference)

    def test_default_individual_property_parameters_to_dict(self):
        individual_property = IndividualProperty()
        self.assertDictEqual(individual_property.to_dict(), {})  # empty, no keys/values added

    def test_overlay_individual_properties(self):
        # create simple demographics
        temp = {'NodeID': [1, 2, 5],
                'loc': ["loc1", "loc2", "loc3"],
                'pop': [123, 234, 345],
                'lon': [10, 11, 12],
                'lat': [21, 22, 23]}
        csv_file = pathlib.Path("test_overlay_population.csv")
        pd.DataFrame.from_dict(temp).to_csv(csv_file)
        demo = Demographics.from_csv(csv_file)
        csv_file.unlink()

        initial_distribution = 999
        property = "Property"
        values = [1, 2, 3]
        transitions = [3, 4, 5]
        transmission_matrix = [[1, 2], [3, 4]]

        node = demo.nodes[0]
        node.individual_properties.add(IndividualProperty(initial_distribution=initial_distribution,
                                                                    property=property,
                                                                    values=values,
                                                                    transitions=transitions,
                                                                    transmission_matrix=transmission_matrix
                                                                    ))
        # create overlay and update
        new_population = 999
        new_property = "Test_Property"

        ip_overlay = IndividualProperty()
        ip_overlay.initial_distribution = new_population
        ip_overlay.property = new_property
        node.individual_properties[0].update(ip_overlay)

        self.assertEqual(demo.nodes[0].individual_properties[0].initial_distribution, new_population)
        self.assertEqual(demo.nodes[0].individual_properties[0].property, new_property)
        self.assertEqual(demo.nodes[0].individual_properties[0].values, values)
        self.assertEqual(demo.nodes[0].individual_properties[0].transitions, transitions)

    def test_add_individual_attributes(self):
        # create simple demographics
        temp = {'NodeID': [1, 2, 5],
                'loc': ["loc1", "loc2", "loc3"],
                'pop': [123, 234, 345],
                'lon': [10, 11, 12],
                'lat': [21, 22, 23]}
        csv_file = pathlib.Path("test_overlay_population.csv")
        pd.DataFrame.from_dict(temp).to_csv(csv_file)
        demo = Demographics.from_csv(csv_file)
        csv_file.unlink()

        node = demo.nodes[0]
        node._set_individual_attributes(IndividualAttributes(age_distribution_flag=3,
                                                                      age_distribution1=0.1,
                                                                      age_distribution2=0.2
                                                                      ))

        node = demo.nodes[2]
        node._set_individual_attributes(IndividualAttributes())
        node.individual_attributes.age_distribution_flag = 3
        node.individual_attributes.age_distribution1 = 0.1
        node.individual_attributes.age_distribution2 = 0.2

        individual_attributes = {
            "AgeDistributionFlag": 3,
            "AgeDistribution1": 0.1,
            "AgeDistribution2": 0.2
        }

        self.assertDictEqual(demo.nodes[0].individual_attributes.to_dict(), individual_attributes)
        self.assertDictEqual(demo.nodes[2].individual_attributes.to_dict(), individual_attributes)

    def test_applyoverlay_individual_properties(self):
        node_attributes_1 = NodeAttributes(name="test_demo")
        node_attributes_2 = NodeAttributes(name="test_demo")
        nodes = [Node.Node(1, 0, 1001, node_attributes=node_attributes_1, forced_id=1),
                 Node.Node(0, 1, 1002, node_attributes=node_attributes_2, forced_id=2)]
        demog = Demographics.Demographics(nodes=nodes)
        demog.SetDefaultProperties()

        overlay_nodes = []

        initial_distribution = [0.1, 0.9]
        property = "QualityOfCare"
        values = ["High", "Low"]
        transmission_matrix = {
            "Matrix": [
                [0.5, 0.0],
                [0.0, 1]],
            "Route": "Contact"}
        new_individual_properties = IndividualProperties()
        new_individual_properties.add(IndividualProperty(initial_distribution,
                                                                   property=property,
                                                                   values=values,
                                                                   transmission_matrix=transmission_matrix))

        overlay_nodes.append(Node.OverlayNode(node_id=1, individual_properties=new_individual_properties))
        overlay_nodes.append(Node.OverlayNode(node_id=2, individual_properties=new_individual_properties))
        demog.apply_overlay(overlay_nodes)
        out_filename = os.path.join(self.out_folder, "demographics_applyoverlay_individual_properties.json")
        demog.generate_file(out_filename)
        with open(out_filename, 'r') as out_file:
            demographics = json.load(out_file)
        self.assertEqual(demographics['Nodes'][0]["IndividualProperties"][0]['Initial_Distribution'],
                         initial_distribution)
        self.assertEqual(demographics['Nodes'][1]["IndividualProperties"][0]['Initial_Distribution'],
                         initial_distribution)

        self.assertEqual(demographics['Nodes'][0]["IndividualProperties"][0]['Property'],
                         property)
        self.assertEqual(demographics['Nodes'][1]["IndividualProperties"][0]['Property'],
                         property)

        self.assertEqual(demographics['Nodes'][0]["IndividualProperties"][0]['Values'],
                         values)
        self.assertEqual(demographics['Nodes'][1]["IndividualProperties"][0]['Values'],
                         values)

        self.assertEqual(demographics['Nodes'][0]["IndividualProperties"][0]['TransmissionMatrix'],
                         transmission_matrix)
        self.assertEqual(demographics['Nodes'][1]["IndividualProperties"][0]['TransmissionMatrix'],
                         transmission_matrix)

    def test_applyoverlay_individual_attributes(self):
        individual_attributes_1 = IndividualAttributes(age_distribution_flag=1,
                                                                 age_distribution1=730,
                                                                 age_distribution2=7300)
        individual_attributes_2 = IndividualAttributes(age_distribution_flag=1,
                                                                 age_distribution1=365,
                                                                 age_distribution2=3650)
        nodes = [Node.Node(0, 0, 0, individual_attributes=individual_attributes_1, forced_id=1),
                 Node.Node(0, 0, 0, individual_attributes=individual_attributes_2, forced_id=2)]
        demog = Demographics.Demographics(nodes=nodes)
        demog.SetDefaultProperties()

        overlay_nodes = []
        new_individual_attributes = IndividualAttributes(age_distribution_flag=0,
                                                                   age_distribution1=300,
                                                                   age_distribution2=600)

        overlay_nodes.append(Node.OverlayNode(node_id=1, individual_attributes=new_individual_attributes))
        overlay_nodes.append(Node.OverlayNode(node_id=2, individual_attributes=new_individual_attributes))
        demog.apply_overlay(overlay_nodes)
        out_filename = os.path.join(self.out_folder, "demographics_applyoverlay_individual_attributes.json")
        demog.generate_file(out_filename)
        with open(out_filename, 'r') as out_file:
            demographics = json.load(out_file)
        self.assertEqual(demographics['Nodes'][0]["IndividualAttributes"]['AgeDistributionFlag'], 0)
        self.assertEqual(demographics['Nodes'][1]["IndividualAttributes"]['AgeDistributionFlag'], 0)

        self.assertEqual(demographics['Nodes'][0]["IndividualAttributes"]['AgeDistribution1'], 300)
        self.assertEqual(demographics['Nodes'][1]["IndividualAttributes"]['AgeDistribution1'], 300)

        self.assertEqual(demographics['Nodes'][0]["IndividualAttributes"]['AgeDistribution2'], 600)
        self.assertEqual(demographics['Nodes'][1]["IndividualAttributes"]['AgeDistribution2'], 600)


    @staticmethod
    def check_for_unique_node_id(nodes):
        node_ids = list()
        for node in nodes:
            node_id = node['NodeID']
            if node_id not in node_ids:
                node_ids.append(node_id)
            else:
                return False
        return True

    def test_infer_natural_mortality(self):
        demog = Demographics.from_template_node(lat=0, lon=0, pop=100000, name=1, forced_id=1)
        male_input_file = os.path.join(self.out_folder, "Malawi_male_mortality.csv")
        female_input_file = os.path.join(self.out_folder, "Malawi_female_mortality.csv")
        predict_horizon = 2060
        results_scale_factor = 1.0 / 340.0
        demog.infer_natural_mortality(male_input_file, female_input_file, predict_horizon=predict_horizon,
                                      results_scale_factor=results_scale_factor, csv_out=True)
        male_input = pd.read_csv(male_input_file)
        female_input = pd.read_csv(female_input_file)
        output = demog.raw['Defaults']

        # Check population group consistency
        male_distribution = output['IndividualAttributes']['MortalityDistributionMale']
        female_distribution = output['IndividualAttributes']['MortalityDistributionFemale']

        # Check age group
        male_age_groups = male_distribution['NumPopulationGroups'][0]
        self.assertEqual(len(male_distribution['PopulationGroups'][0]), male_age_groups)
        # Get age groups information male from csv file
        expected_male_age_group = np.append(male_input['Age (x)'].unique(), 100).tolist()
        self.assertListEqual(expected_male_age_group[1:], male_distribution['PopulationGroups'][0])

        female_age_groups = female_distribution['NumPopulationGroups'][0]
        self.assertEqual(len(female_distribution['PopulationGroups'][0]), female_age_groups)
        # Get age groups information from female csv file
        expected_female_age_group = np.append(female_input['Age (x)'].unique(), 100).tolist()
        self.assertListEqual(expected_female_age_group[1:], female_distribution['PopulationGroups'][0])

        # Check Year
        male_year_groups = male_distribution['NumPopulationGroups'][1]
        self.assertEqual(len(male_distribution['PopulationGroups'][1]), male_year_groups)
        # Get year groups information male from csv file
        expected_male_year_group = male_input['Ave_Year'].unique().tolist()
        # Up to year = predict_horizon
        expected_male_year_group = [x for x in expected_male_year_group if x < predict_horizon]
        self.assertListEqual(expected_male_year_group, male_distribution['PopulationGroups'][1])

        female_year_groups = female_distribution['NumPopulationGroups'][1]
        self.assertEqual(len(female_distribution['PopulationGroups'][1]), female_year_groups)
        expected_female_year_group = expected_male_year_group
        self.assertListEqual(expected_female_year_group, female_distribution['PopulationGroups'][1])

        # Check prediction horizon is honored
        self.assertLessEqual(max(male_distribution['PopulationGroups'][1]), 2060)
        self.assertLessEqual(max(female_distribution['PopulationGroups'][1]), 2060)

        # Check results scale factor is consistent with parameters
        self.assertEqual(male_distribution['ResultScaleFactor'], results_scale_factor)
        self.assertEqual(female_distribution['ResultScaleFactor'], results_scale_factor)

        # Check result values array length
        self.assertEqual(len(male_distribution['ResultValues']), male_age_groups)
        for m_y in male_distribution['ResultValues']:
            self.assertEqual(len(m_y), male_year_groups)
        self.assertEqual(len(female_distribution['ResultValues']), female_age_groups)
        for f_y in female_distribution['ResultValues']:
            self.assertEqual(len(f_y), female_year_groups)

        # Check result values consistency with reference files
        male_reference = pd.read_csv(os.path.join(self.out_folder, "MaleTrue"))
        female_reference = pd.read_csv(os.path.join(self.out_folder, "FemaleTrue"))
        for i in range(male_age_groups):
            for j in range(male_year_groups):
                male_mortality_rate = male_distribution['ResultValues'][i][j]
                expected_male_mortality_rate = male_reference[male_reference['Age'] == expected_male_age_group[i + 1]][
                    str(expected_male_year_group[j])].iloc[0]
                self.assertAlmostEqual(expected_male_mortality_rate, male_mortality_rate, delta=1e-5,
                                       msg=f"at year {expected_male_year_group[j]} age {expected_male_age_group[i + 1]}"
                                           f", male mortality rate is set to {male_mortality_rate} (please see "
                                           f"male_distribution['ResultValues'][{i}][{j}]), while it's "
                                           f"{expected_male_mortality_rate} in male csv file.\n")

                female_mortality_rate = female_distribution['ResultValues'][i][j]
                expected_female_mortality_rate = female_reference[female_reference['Age'] ==
                                                                  expected_female_age_group[i + 1]][
                    str(expected_female_year_group[j])].iloc[0]
                self.assertAlmostEqual(expected_female_mortality_rate, female_mortality_rate, delta=1e-5,
                                       msg=f"at year {expected_female_year_group[j]} age "
                                           f"{expected_female_age_group[i + 1]},"
                                           f" female mortality rate is set to {female_mortality_rate} (please see "
                                           f"female_distribution['ResultValues'][{i}][{j}]), while it's "
                                           f"{expected_female_mortality_rate} in female csv file.\n")

    def test_set_initial_age_exponential(self):
        demog = Demographics.from_template_node()
        rate = 0.0001
        demog.SetInitialAgeExponential(rate)
        self.assertEqual(3, demog.raw['Defaults']['IndividualAttributes']['AgeDistributionFlag'])
        self.assertEqual(rate, demog.raw['Defaults']['IndividualAttributes']['AgeDistribution1'])
        self.assertEqual(0, demog.raw['Defaults']['IndividualAttributes']['AgeDistribution2'])
        self.assertIn("exponential", demog.raw['Defaults']['IndividualAttributes']['AgeDistribution_Description'])
        self.assertEqual(len(demog.implicits), 2)

    def test_set_initial_age_like_SubSaharanAfrica(self):
        demog = Demographics.from_template_node()
        rate = 0.0001068
        demog.SetInitialAgeLikeSubSaharanAfrica()
        self.assertEqual(3, demog.raw['Defaults']['IndividualAttributes']['AgeDistributionFlag'])
        self.assertEqual(rate, demog.raw['Defaults']['IndividualAttributes']['AgeDistribution1'])
        self.assertEqual(0, demog.raw['Defaults']['IndividualAttributes']['AgeDistribution2'])
        self.assertIn("exponential", demog.raw['Defaults']['IndividualAttributes']['AgeDistribution_Description'])
        self.assertEqual(len(demog.implicits), 2)

    def test_set_initial_prev_from_uniform(self):
        demog = Demographics.from_template_node()
        min_init_prev = 0.05
        max_init_prev = 0.2
        demog.SetInitPrevFromUniformDraw(min_init_prev=min_init_prev, max_init_prev=max_init_prev)
        self.assertEqual(1, demog.raw['Defaults']['IndividualAttributes']['PrevalenceDistributionFlag'])
        self.assertEqual(min_init_prev, demog.raw['Defaults']['IndividualAttributes']['PrevalenceDistribution1'])
        self.assertEqual(max_init_prev, demog.raw['Defaults']['IndividualAttributes']['PrevalenceDistribution2'])
        self.assertIn("uniform", demog.raw['Defaults']['IndividualAttributes']['PrevalenceDistribution_Description'])
        self.assertEqual(len(demog.implicits), 2)

    def test_set_constant_risk(self):
        demog = Demographics.from_template_node()
        risk = 0.1
        demog.SetConstantRisk(risk)
        self.assertEqual(1, demog.raw['Defaults']['IndividualAttributes']['RiskDistributionFlag'])
        self.assertEqual(risk, demog.raw['Defaults']['IndividualAttributes']['RiskDistribution1'])
        self.assertEqual(risk, demog.raw['Defaults']['IndividualAttributes']['RiskDistribution2'])
        self.assertIn("constant", demog.raw['Defaults']['IndividualAttributes']['RiskDistribution_Description'])
        self.assertEqual(len(demog.implicits), 2)

    def test_set_full_risk(self):
        demog = Demographics.from_template_node()
        demog.SetConstantRisk()
        self.assertEqual(0, demog.raw['Defaults']['IndividualAttributes']['RiskDistributionFlag'])
        self.assertEqual(1, demog.raw['Defaults']['IndividualAttributes']['RiskDistribution1'])
        self.assertEqual(0, demog.raw['Defaults']['IndividualAttributes']['RiskDistribution2'])
        self.assertIn("constant", demog.raw['Defaults']['IndividualAttributes']['RiskDistribution_Description'])
        self.assertEqual(len(demog.implicits), 2)

    def test_set_predefined_mortality_distribution(self):
        demog = Demographics.from_template_node()
        mortality_distribution = Distributions.SEAsia_Diag
        demog.SetMortalityDistribution(mortality_distribution)
        self.assertDictEqual(demog.raw['Defaults']['IndividualAttributes']['MortalityDistribution'],
                             mortality_distribution.to_dict())

    def test_mortality_rate_with_node_ids(self):
        input_file = os.path.join(manifest.current_directory, 'data', 'demographics', 'nodes.csv')
        demog = Demographics.from_csv(input_file)
        mortality_rate = 0.1234
        node_ids = [97, 99]
        demog.SetMortalityRate(mortality_rate, node_ids)

        set_mortality_dist_97 = demog.get_node(97).individual_attributes.mortality_distribution.to_dict()
        set_mortality_dist_99 = demog.get_node(99).individual_attributes.mortality_distribution.to_dict()
        expected_mortality_dist = DT._ConstantMortality(mortality_rate).to_dict()
        self.assertDictEqual(set_mortality_dist_99, expected_mortality_dist)
        self.assertDictEqual(set_mortality_dist_97, expected_mortality_dist)
        self.assertIsNone(demog.get_node(96).individual_attributes.mortality_distribution)

    def test_set_predefined_age_distribution(self):
        demog = Demographics.from_template_node()
        age_distribution = Distributions.SEAsia_Diag
        demog.SetAgeDistribution(age_distribution)
        self.assertDictEqual(demog.raw['Defaults']['IndividualAttributes']['AgeDistribution'],
                             age_distribution.to_dict())

    def test_set_predefined_age_distribution_SEAsia(self):
        demog = Demographics.from_template_node()
        demog.SetAgeDistribution(Distributions.AgeDistribution_SEAsia)
        self.assertDictEqual(demog.raw['Defaults']['IndividualAttributes']['AgeDistribution'],
                             Distributions.AgeDistribution_SEAsia.to_dict())

    def test_set_predefined_age_distribution_Americas(self):
        demog = Demographics.from_template_node()
        demog.SetAgeDistribution(Distributions.AgeDistribution_Americas)
        self.assertDictEqual(demog.raw['Defaults']['IndividualAttributes']['AgeDistribution'],
                             Distributions.AgeDistribution_Americas.to_dict())

    def test_set_predefined_age_distribution_Amelia_with_node_ids(self):
        demog = Demographics.from_template_node()
        demog.SetAgeDistribution(Distributions.AgeDistribution_SSAfrica, node_ids=[1])
        self.assertDictEqual(demog.to_dict()['Nodes'][0]['IndividualAttributes']['AgeDistribution'],
                             Distributions.AgeDistribution_SSAfrica.to_dict())

    def test_set_predefined_mortality_distribution_with_node_ids(self):
        demog = Demographics.from_template_node()
        demog.SetMortalityDistribution(Distributions.Constant_Mortality, node_ids=[1])
        self.assertDictEqual(demog.to_dict()['Nodes'][0]['IndividualAttributes']['MortalityDistribution'],
                             Distributions.Constant_Mortality.to_dict())

    def test_get_node_and_set_property(self):
        demog = Demographics.from_template_node(lat=0, lon=0, pop=100000, name=1, forced_id=1)
        demog.get_node(1).birth_rate = 0.123
        self.assertEqual(demog.to_dict()['Nodes'][0]['NodeAttributes']['BirthRate'], 0.123)

    def test_setting_value_throws_exception_distribution_const(self):
        # Trying to set/change a value of a predefined distribution raises an Exception
        distribution = Distributions.Constant_Mortality
        with self.assertRaises(Exception):
            distribution.result_values = [[0.1], [0.1]]

    def test_wrap_distribution_const(self):
        # Test if wrapper ConstantDistribution changes distribution
        distribution = Distributions.Constant_Mortality
        predefined_mort_dist = IndividualAttributes.MortalityDistribution(num_population_axes=2,
                                                                          axis_names=["gender", "age"],
                                                                          axis_units=["male=0,female=1", "years"],
                                                                          axis_scale_factors=[1, 365],
                                                                          population_groups=[[0, 1], [0]],
                                                                          result_scale_factor=1,
                                                                          result_units="daily probability of dying",
                                                                          result_values=[[0.5], [0.5]])
        self.assertDictEqual(distribution.to_dict(), predefined_mort_dist.to_dict())

    def test_change_copied_distribution_const(self):
        # Test if changing a copy of a predefined distribution changes predefined distribution
        distribution_copy = Distributions.AgeDistribution_SEAsia.copy()
        distribution_copy.distribution_values = 123
        self.assertNotEqual(Distributions.AgeDistribution_SEAsia.distribution_values, 123)
        self.assertEqual(distribution_copy.distribution_values, 123)

    def test_copy_distribution_const(self):
        # test copy() function
        distribution_copy = Distributions.Constant_Mortality.copy()
        self.assertDictEqual(distribution_copy.to_dict(), Distributions.Constant_Mortality.to_dict())


class DemographicsOverlayTest(unittest.TestCase):
    def setUp(self) -> None:
        print(f"\n{self._testMethodName} started...")

    def test_create_overlay_file(self):
        # reference from Kurt's demographics_is000.json
        reference = {
            "Defaults": {
                "IndividualAttributes": {
                    "SusceptibilityDistribution": {
                        "DistributionValues": [
                            0.0,
                            3650.0
                        ],
                        "ResultScaleFactor": 1,
                        "ResultValues": [
                            1.0,
                            0.0
                        ]
                    }
                },
                #                    "NodeAttributes": {}
            },
            "Metadata": {
                "IdReference": "polio-custom"
            },
            "Nodes": [
                {
                    "NodeID": 1
                }
            ]
        }

        individual_attributes = IndividualAttributes()
        individual_attributes.susceptibility_distribution = IndividualAttributes.SusceptibilityDistribution(distribution_values=[0.0, 3650],
                                                                                                                      result_scale_factor=1,
                                                                                                                      result_values=[1.0, 0.0])

        overlay = Demographics.DemographicsOverlay(nodes=[1],
                                                   individual_attributes=individual_attributes,
                                                   meta_data={"IdReference": "polio-custom"})

        self.assertDictEqual(reference, overlay.to_dict())

    def test_create_overlay_file_2(self):
        # reference from Kurt's demographics_vd000.json
        reference = {
            "Defaults": {
                "IndividualAttributes": {
                    "AgeDistribution": {
                        "DistributionValues": [
                            [
                                0.0,
                                1.0
                            ]
                        ],
                        "ResultScaleFactor": 1,
                        "ResultValues": [
                            [
                                0,
                                43769
                            ]
                        ]
                    },
                    "MortalityDistribution": {
                        "AxisNames": [
                            "gender",
                            "age"
                        ],
                        "AxisScaleFactors": [
                            1,
                            1
                        ],
                        "NumDistributionAxes": 2,
                        "NumPopulationGroups": [
                            2,
                            54
                        ],
                        "PopulationGroups": [
                            [
                                0,
                                1
                            ],
                            [
                                0.6,
                                43829.5
                            ]
                        ],
                        "ResultScaleFactor": 1,
                        "ResultValues": [
                            [
                                0.0013,
                                1.0
                            ],
                            [
                                0.0013,
                                1.0
                            ]
                        ]
                    }
                },
                "NodeAttributes": {
                    "BirthRate": 0.1,
                    "GrowthRate": 1.01
                }
            },
            "Metadata": {
                "IdReference": "polio-custom"
            },
            "Nodes": [
                {
                    "NodeID": 1
                },
                {
                    "NodeID": 2
                }
            ]
        }

        individual_attributes = IndividualAttributes()
        individual_attributes.age_distribution = IndividualAttributes.AgeDistribution(distribution_values=[[0.0, 1.0]],
                                                                                                result_scale_factor=1,
                                                                                                result_values=[[0, 43769]])

        individual_attributes.mortality_distribution = IndividualAttributes.MortalityDistribution(axis_names=["gender", "age"],
                                                                                                            axis_scale_factors=[1, 1],
                                                                                                            num_distribution_axes=2,
                                                                                                            num_population_groups=[2, 54],
                                                                                                            population_groups=[[0, 1], [0.6, 43829.5]],
                                                                                                            result_scale_factor=1,
                                                                                                            result_values=[[0.0013, 1.0], [0.0013, 1.0]])

        node_attributes = NodeAttributes(birth_rate=0.1, growth_rate=1.01)
        meta_data = {"IdReference": "polio-custom"}
        nodes = [1, 2]

        overlay = Demographics.DemographicsOverlay(nodes=nodes,
                                                   individual_attributes=individual_attributes,
                                                   node_attributes=node_attributes,
                                                   meta_data=meta_data)

        self.assertDictEqual(reference, overlay.to_dict())


if __name__ == '__main__':
    unittest.main()
