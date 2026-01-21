#!/usr/bin/env python
import os
import unittest
import shutil
import json
import pprint
from emod_api.interventions import outbreak as ob
from emod_api import campaign as camp

from tests.data.campaign import outbreak_arguments as testcase
from tests import manifest
class OutbreakTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        camp.set_schema(manifest.malaria_schema_path)
        cls.output_folder = os.path.join(manifest.output_folder, 'outbreak')

    def tearDown(self) -> None:
        camp.set_schema(manifest.malaria_schema_path)
        
    def test_seed_simple(self):
        testcase.Property_Restrictions = [{"Place": "Rural"}]
        testcase.Filename = "outbreak_individual_seed_simple"
        event = self.outbreak_seed(testcase)
        self.assertEqual(event['Event_Coordinator_Config']['Property_Restrictions'], ["Place:Rural"] )

    def test_seed_complex(self):
        testcase.Property_Restrictions = [{"Place": "Rural"}, {"Risk": "Medium"} ]
        testcase.Filename = "outbreak_individual_seed_complex"
        event = self.outbreak_seed(testcase)
        self.assertEqual(event['Event_Coordinator_Config']['Property_Restrictions_Within_Node'], testcase.Property_Restrictions )

    def outbreak_seed(self, case):
        event = ob.seed(camp=camp, 
                        Start_Day= case.Start_Day, 
                        Coverage= case.Demographic_Coverage, 
                        Target_Props= case.Property_Restrictions, 
                        Node_Ids= case.Node_Ids, 
                        Tot_Rep= case.Number_Repetitions, 
                        Rep_Interval= case.Timesteps_Between_Repetitions, 
                        Target_Age_Min= case.Target_Age_Min,
                        Target_Age_Max= case.Target_Age_Max,
                        Target_Gender= case.Target_Gender,
                        Honor_Immunity= case.Honor_Immunity
                        )

        #camp.add() Handled inside the funtion.
        camp_filename = case.Filename
        camp_filename = os.path.join(self.output_folder, camp_filename + '.json')
        manifest.delete_existing_file(camp_filename)
        camp.save(camp_filename)
        self.assertTrue(os.path.isfile(camp_filename))
        with open(camp_filename, 'r') as file:
            campaign = json.load(file)
            camp_event = campaign["Events"]
        
        self.assertEqual(len(camp_event), 1)
        event = camp_event[0]
        self.assertEqual(event['Start_Day'], case.Start_Day)
        self.assertEqual(event['Event_Coordinator_Config']['Demographic_Coverage'], case.Demographic_Coverage)
        self.assertEqual(event['Event_Coordinator_Config']['Target_Age_Max'], case.Target_Age_Max)
        self.assertEqual(event['Event_Coordinator_Config']['Target_Age_Min'], case.Target_Age_Min)
        self.assertTrue(self.rec_check_camp(campaign) is None)
        ic = event['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(ic['class'], 'OutbreakIndividual')
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))
        camp.reset()
        return event

    def test_as_file(self):
        camp_filename = 'outbreak_as_file.json'
        camp_filename = os.path.join(self.output_folder, camp_filename + '.json')
        manifest.delete_existing_file(camp_filename)
        timestep = 10
        cases = 44
        ob.new_intervention_as_file(camp, timestep, cases=cases, filename=camp_filename)
        print(f"Check for valid campaign file at: {camp_filename}.")
        self.assertTrue(os.path.isfile(camp_filename))
        with open(camp_filename, 'r') as file:
            camp_event = json.load(file)['Events']
        self.assertEqual(len(camp_event), 1)
        event = camp_event[0]
        self.assertEqual(event['Start_Day'], timestep)
        ic = event['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(ic['class'], 'Outbreak')
        self.assertEqual(ic['Number_Cases_Per_Node'], cases)
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))
        camp.reset()

    def test_as_event(self):
        timestep = 30
        cases = 5
        event = ob.new_intervention(camp, timestep, cases=cases)
        camp.add(event, name='outbreak_1')
        camp.add(ob.new_intervention(camp, timestep * 2, cases=cases * 2), name='outbreak_2')
        camp.add(ob.new_intervention(camp, timestep * 3, cases=cases * 3), name='outbreak_3')
        camp.add(ob.new_intervention(camp, timestep * 4, cases=cases * 4), name='outbreak_4')
        camp_filename = 'outbreak_as_event.json'
        camp_filename = os.path.join(self.output_folder, camp_filename + '.json')
        manifest.delete_existing_file(camp_filename)
        camp.save(camp_filename)
        self.assertTrue(os.path.isfile(camp_filename))
        with open(camp_filename, 'r') as file:
            campaign = json.load(file)
            camp_event = campaign["Events"]
        self.assertEqual(len(camp_event), 4)
        event_index = 0
        for event in camp_event:
            event_index += 1
            self.assertEqual(event['Start_Day'], timestep * event_index)
            self.assertEqual(event['Event_Name'], f'outbreak_{event_index}')

            ic = event['Event_Coordinator_Config']['Intervention_Config']
            self.assertEqual(ic['class'], 'Outbreak')
            self.assertEqual(ic['Number_Cases_Per_Node'], cases * event_index)

        self.assertTrue(self.rec_check_camp(campaign) is None)
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))
        camp.reset()

    def test_seed_by_coverage(self):
        timestep = 10
        coverage = 0.05
        event = ob.seed_by_coverage(campaign_builder=camp, timestep=timestep, coverage=coverage)
        event_name = 'individual_outbreak'
        camp.add(event, name=event_name)
        camp_filename = 'outbreak_individual.json'
        camp_filename = os.path.join(self.output_folder, camp_filename + '.json')
        manifest.delete_existing_file(camp_filename)
        camp.save(camp_filename)
        self.assertTrue(os.path.isfile(camp_filename))
        with open(camp_filename, 'r') as file:
            campaign = json.load(file)
            camp_event = campaign["Events"]
        self.assertEqual(len(camp_event), 1)
        event = camp_event[0]
        self.assertEqual(event['Start_Day'], timestep )
        self.assertEqual(event['Event_Name'], event_name)
        self.assertEqual(event['Event_Coordinator_Config']['Demographic_Coverage'], coverage)
        self.assertTrue(self.rec_check_camp(campaign) is None)

        ic = event['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(ic['class'], 'OutbreakIndividual')
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))
        camp.reset()

    def test_seed(self):
        camp.set_schema( camp.schema_path )
        timestep = 10
        coverage = 0.05
        ob.seed(camp=camp, Start_Day=timestep, Coverage=coverage)
        event_name = 'individual_outbreak'
        camp_filename = 'outbreak_individual.json'
        camp_filename = os.path.join(self.output_folder, camp_filename + '.json')
        manifest.delete_existing_file(camp_filename)
        camp.save(camp_filename)
        self.assertTrue(os.path.isfile(camp_filename))
        with open(camp_filename, 'r') as file:
            campaign = json.load(file)
            camp_event = campaign["Events"]
        self.assertEqual(len(camp_event), 1)
        event = camp_event[0]
        self.assertEqual(event['Start_Day'], timestep )
        self.assertEqual(event['Event_Coordinator_Config']['Demographic_Coverage'], coverage)
        self.assertTrue(self.rec_check_camp(campaign) is None)

        ic = event['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(ic['class'], 'OutbreakIndividual')
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_seed(self):
        camp.set_schema( camp.schema_path )
        timestep = 10
        coverage = 0.05
        ob.seed(camp=camp, Start_Day=timestep, Coverage=coverage)
        event_name = 'individual_outbreak'
        camp_filename = 'outbreak_individual.json'
        camp_filename = os.path.join(self.output_folder, camp_filename + '.json')
        manifest.delete_existing_file(camp_filename)
        camp.save(camp_filename)
        self.assertTrue(os.path.isfile(camp_filename))
        with open(camp_filename, 'r') as file:
            campaign = json.load(file)
            camp_event = campaign["Events"]
        self.assertEqual(len(camp_event), 1)
        event = camp_event[0]
        self.assertEqual(event['Start_Day'], timestep )
        self.assertEqual(event['Event_Coordinator_Config']['Demographic_Coverage'], coverage)
        self.assertTrue(self.rec_check_camp(campaign) is None)

        ic = event['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(ic['class'], 'OutbreakIndividual')
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def rec_check_camp(self, camp):
        if "schema" in camp: 
            return 1
        for key, value in camp.items():
            if isinstance(value, dict):
                item = self.rec_check_camp(value)
                if item is not None:
                    return 1

    def test_intervention_parameter(self):
        timestep = 10
        coverage = 0.05
        event = ob.seed_by_coverage(campaign_builder=camp, timestep=timestep, coverage=coverage)
        event_name = 'individual_outbreak'
        camp.add(event, name=event_name)

        outbreak_file = 'outbreak.json'
        outbreak_file = os.path.join(self.output_folder, outbreak_file)
        manifest.delete_existing_file(outbreak_file)
        camp.save(outbreak_file)

        with open(outbreak_file, 'r') as file:
            campaign = json.load(file)
            outbreak_dict = campaign["Events"][0]['Event_Coordinator_Config']['Intervention_Config']
            outbreak_default = campaign["Use_Defaults"]

        intervention_only = ob.seed_by_coverage(campaign_builder=camp, timestep=timestep, coverage=coverage, intervention_only=True)
        intervention_only_file = "outbreak_intervention_only.json"
        camp.add(intervention_only, name=event_name)
        intervention_only_file = os.path.join(self.output_folder, intervention_only_file)
        manifest.delete_existing_file(intervention_only_file)
        camp.save(intervention_only_file)

        with open(intervention_only_file, 'r') as file:
            campaign = json.load(file)
            intervention_only_dict = campaign['Events'][0]['Event_Coordinator_Config']['Intervention_Config']
            intervention_only_defaults = campaign["Use_Defaults"]

        for key in outbreak_dict:
            self.assertEqual(outbreak_dict[key], intervention_only_dict[key])

        for key in intervention_only_dict:
            if key != "Event_Name":
                self.assertEqual(outbreak_dict[key], intervention_only_dict[key])
        
        self.assertEqual(outbreak_default, intervention_only_defaults)
        shutil.move(outbreak_file, os.path.join(self.output_folder, intervention_only_file))
        shutil.move(intervention_only_file, os.path.join(self.output_folder, intervention_only_file))
        camp.reset()


if __name__ == '__main__':
    unittest.main()
