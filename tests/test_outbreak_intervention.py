import unittest
import json
import pathlib
import os

from emod_api import campaign
from emod_api.interventions import outbreak

class TestBasicInterventions(unittest.TestCase):
    # region helper methods
    def setUp(self) -> None:
        self.is_debugging = False
        self.tmp_intervention = None
        self.start_day = None

        self._nodeset = None
        self.nodeset_class = None
        self.nodelist = None

        # event coordinator parts
        self.event_coordinator = None
        self.ec_demographic_coverage = None
        self.ec_target_gender = None
        self.ec_number_repetitions = None
        self.ec_repetition_interval = None
        self.ec_target_demographic = None
        self.ec_target_age_max = None
        self.ec_target_age_min = None
        self.ec_property_restrictions = None

        # intervention config parts
        self.intervention_config = None
        self.ic_clade = None
        self.ic_genome = None
        self.ic_import_age = None
        self.ic_import_female_prob = None
        self.ic_number_cases_per_node = None
        self.ic_ignore_immunity = None
        self.ic_incubation_period_override = None
        self.schema_path = pathlib.Path(str(pathlib.Path.cwd()), 'data', 'config', 'input_generic_schema.json')
        campaign.set_schema(self.schema_path)
        self.assertEqual(len(campaign.campaign_dict["Events"]), 0)
        self.debug_files = []
        return

    def write_debug_files(self):
        debug_filename = f'DEBUG_{self._testMethodName}.json'
        with open(debug_filename, 'w') as outfile:
            self.debug_files.append(debug_filename)
            if self.tmp_intervention:
                json.dump(self.tmp_intervention, outfile, indent=4, sort_keys=True)
            else:
                campaign.save(debug_filename)
        return

    def parse_intervention_parts(self):
        if self.tmp_intervention == None:
            self.assertEqual(len(campaign.campaign_dict["Events"]), 1,
                             msg="There is more than one event, and the temp intervention is None.")
            self.tmp_intervention = campaign.campaign_dict["Events"][0]
        self._nodeset = self.tmp_intervention['Nodeset_Config']
        self.nodeset_class = self._nodeset['class']
        if self.nodeset_class == "NodeSetNodeList":
            self.nodelist = self._nodeset['Node_List']

        self.start_day = self.tmp_intervention['Start_Day']
        self.event_coordinator = self.tmp_intervention['Event_Coordinator_Config']
        self.ec_number_repetitions = self.event_coordinator['Number_Repetitions']
        if self.ec_number_repetitions > 1:
            self.ec_repetition_interval = self.event_coordinator['Timesteps_Between_Repetitions']
        self.ec_target_gender = self.event_coordinator['Target_Gender']
        self.ec_demographic_coverage = self.event_coordinator['Demographic_Coverage']
        self.ec_target_demographic = self.event_coordinator['Target_Demographic']
        if self.ec_target_demographic != "Everyone":
            self.ec_target_age_max = self.event_coordinator['Target_Age_Max']
            self.ec_target_age_min = self.event_coordinator['Target_Age_Min']
        self.ec_property_restrictions = self.event_coordinator['Property_Restrictions']

        self.intervention_config = self.event_coordinator['Intervention_Config']
        self.ic_clade = self.intervention_config['Clade']
        self.ic_genome = self.intervention_config['Genome']
        if self.intervention_config['class'] == 'Outbreak':
            self.ic_import_age = self.intervention_config['Import_Age']
            self.ic_import_female_prob = self.intervention_config['Import_Female_Prob']
            self.ic_number_cases_per_node = self.intervention_config['Number_Cases_Per_Node']
        elif self.intervention_config['class'] == 'OutbreakIndividual':
            self.ic_ignore_immunity = self.intervention_config['Ignore_Immunity']
            self.ic_incubation_period_override = self.intervention_config['Incubation_Period_Override']

    def tearDown(self) -> None:
        if self.is_debugging:
            self.write_debug_files()
        else:
            for f in self.debug_files:
                os.remove(f)
        return

    # endregion

    def test_write_default_outbreak(self):
        self.is_debugging = False
        expected_filename = "outbreak.json"
        expected_cases = 5
        expected_timestep = 5
        self.tmp_intervention = outbreak.new_intervention_as_file(
            camp=campaign,
            timestep=5,
            cases=5
        )
        self.debug_files.append(expected_filename)
        self.assertTrue(pathlib.Path(expected_filename).is_file(),
                        msg=f"{expected_filename} should be written.")

        with open (expected_filename) as infile:
            self.tmp_intervention = json.load(infile)["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.ic_clade, 0)
        self.assertEqual(self.ic_genome, 0)
        self.assertEqual(self.ic_import_age, 365)
        self.assertEqual(self.ic_import_female_prob, 0.5)
        self.assertEqual(self.ic_number_cases_per_node, expected_cases)
        self.assertEqual(self.start_day, expected_timestep)

    def test_write_custom_outbreak(self):
        self.is_debugging = False
        expected_filename = "DEBUG_outbreak_haha.json"
        expected_cases = 5
        expected_timestep = 5
        self.tmp_intervention = outbreak.new_intervention_as_file(
            camp=campaign,
            timestep=5,
            cases=5,
            filename=expected_filename
        )
        self.debug_files.append(expected_filename)
        self.assertTrue(pathlib.Path(expected_filename).is_file(),
                        msg=f"{expected_filename} should be written.")

        with open (expected_filename) as infile:
            self.tmp_intervention = json.load(infile)["Events"][0]
        self.parse_intervention_parts()
        self.assertEqual(self.ic_clade, 0)
        self.assertEqual(self.ic_genome, 0)
        self.assertEqual(self.ic_import_age, 365)
        self.assertEqual(self.ic_import_female_prob, 0.5)
        self.assertEqual(self.ic_number_cases_per_node, expected_cases)
        self.assertEqual(self.start_day, expected_timestep)

    def test_default_seed(self):
        self.is_debugging = False
        expected_start_day = 5
        expected_coverage = 0.03
        outbreak.seed(
            camp=campaign,
            Coverage=expected_coverage,
            Start_Day=expected_start_day
        )
        self.parse_intervention_parts()
        self.assertEqual(self.start_day, expected_start_day)
        self.assertEqual(self.ec_demographic_coverage, expected_coverage)
        self.assertEqual(self.ic_ignore_immunity, 1)
        self.assertEqual(self.ic_incubation_period_override, -1)
        self.assertEqual(self.ec_target_gender, "All")
        self.assertEqual(self.ec_target_age_max, 125)
        self.assertEqual(self.ec_target_age_min, 0)
        self.assertEqual(self.ec_property_restrictions, [])
        self.assertEqual(self.ec_number_repetitions, 1)

    def test_seed_excessive_coverage(self):
        self.is_debugging = False
        expected_start_day = 5
        low_start_day = -1

        high_coverage = 1.01
        expected_coverage = 0.05
        low_coverage = -0.01
        with self.assertRaises(ValueError) as context:
            outbreak.seed(
                camp=campaign,
                Coverage=high_coverage,
                Start_Day=expected_start_day
            )
        self.assertIn("Demographic_Coverage", str(context.exception))
        self.assertIn("above", str(context.exception))
        with self.assertRaises(ValueError) as context:
            outbreak.seed(
                camp=campaign,
                Coverage=low_coverage,
                Start_Day=expected_start_day
            )
        self.assertIn("Demographic_Coverage", str(context.exception))
        self.assertIn("below", str(context.exception))
        with self.assertRaises(ValueError) as context:
            outbreak.seed(
                camp=campaign,
                Coverage=expected_coverage,
                Start_Day=low_start_day
            )
        self.assertIn("Start_Day", str(context.exception))
        self.assertIn("below", str(context.exception))

    def test_custom_seed(self):
        self.is_debugging = False
        expected_start_day = 13
        expected_coverage = 1.0
        expected_target_properties =["Risk:seed", "Place:rural"]
        expected_target_demographic = "ExplicitAgeRanges"
        expected_age_max = 15
        expected_age_min = 12
        expected_nodes = [2, 3, 5, 8, 13, 21]
        expected_repetitions = 3
        expected_rep_interval = 730
        expected_ignore_immunity = 0

        outbreak.seed(
            camp=campaign,
            Start_Day=expected_start_day,
            Coverage=expected_coverage,
            Target_Props=expected_target_properties,
            Target_Age_Min=expected_age_min,
            Target_Age_Max=expected_age_max,
            Node_Ids=expected_nodes,
            Tot_Rep=expected_repetitions,
            Rep_Interval=expected_rep_interval,
            Honor_Immunity=(not expected_ignore_immunity)
        )
        self.parse_intervention_parts()
        self.assertEqual(self.start_day, expected_start_day)
        self.assertEqual(self.ec_demographic_coverage, expected_coverage)
        self.assertEqual(self.ec_property_restrictions, expected_target_properties)
        self.assertEqual(self.ec_target_demographic, expected_target_demographic)
        self.assertEqual(self.ec_target_age_min, expected_age_min)
        self.assertEqual(self.ec_target_age_max, expected_age_max)
        self.assertEqual(self.nodeset_class, "NodeSetNodeList")
        self.assertEqual(self.nodelist, expected_nodes)
        self.assertEqual(self.ec_number_repetitions, expected_repetitions)
        self.assertEqual(self.ec_repetition_interval, expected_rep_interval)
        self.assertEqual(self.ic_ignore_immunity, expected_ignore_immunity)

    def test_seed_young_men_monthly(self):
        self.is_debugging = False
        expected_target_gender = "Male"
        expected_age_max = 18
        expected_age_min = 0
        expected_start_day = 1
        expected_repetitions = 12
        expected_rep_interval = 28
        expected_ignore_immunity = 1
        expected_coverage = 1.0
        expected_target_properties =[]
        expected_target_demographic = "ExplicitAgeRangesAndGender"

        outbreak.seed(
            camp=campaign,
            Start_Day=expected_start_day,
            Coverage=1.0,
            Tot_Rep=expected_repetitions,
            Rep_Interval=expected_rep_interval,
            Target_Gender=expected_target_gender,
            Target_Age_Max=expected_age_max,
            Honor_Immunity=(not expected_ignore_immunity)
        )
        self.parse_intervention_parts()
        self.assertEqual(self.start_day, expected_start_day)
        self.assertEqual(self.ec_property_restrictions, expected_target_properties)
        self.assertEqual(self.ec_target_demographic, expected_target_demographic)
        self.assertEqual(self.ec_target_age_min, expected_age_min)
        self.assertEqual(self.ec_target_age_max, expected_age_max)
        self.assertEqual(self.nodeset_class, "NodeSetAll")
        self.assertEqual(self.ec_number_repetitions, expected_repetitions)
        self.assertEqual(self.ec_repetition_interval, expected_rep_interval)
        self.assertEqual(self.ic_ignore_immunity, expected_ignore_immunity)
        self.assertEqual(self.ec_demographic_coverage, expected_coverage)

