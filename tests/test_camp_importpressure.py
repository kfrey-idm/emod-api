#!/usr/bin/env python
import os
import unittest
import shutil
import json
from copy import deepcopy

from emod_api.interventions import import_pressure as ip
from emod_api import campaign as camp

from camp_test import CampaignTest, delete_existing_file

current_directory = os.path.dirname(os.path.realpath(__file__))
schema_path = os.path.join(current_directory, 'data', 'config', 'input_generic_schema.json')

class ImportPressureTest(CampaignTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        camp.set_schema(schema_path)
        ip.schema_path = camp.schema_path

    def tearDown(self) -> None:
        camp.set_schema(schema_path)
        
    def test_as_file(self):
        durations = [10, 10, 10, 10]
        ip.durations = deepcopy(durations)
        daily_import_pressures = [0.0, 0.25, 0.5, 1.0]
        ip.daily_import_pressures = deepcopy(daily_import_pressures)
        nodes = [0, 1, 2, 3, 4]
        ip.nodes = deepcopy(nodes)
        camp_filename = 'import_pressure_as_file.json'
        delete_existing_file(camp_filename)
        timestep = 10
        ip.new_intervention_as_file(timestep, camp_filename)
        print(f"Check for valid campaign file at: {camp_filename}.")
        self.assertTrue(os.path.isfile(camp_filename))
        with open(camp_filename, 'r') as file:
            camp_event = json.load(file)['Events']
        self.assertEqual(len(camp_event), 1)
        event = camp_event[0]
        self.assertEqual(event['Start_Day'], timestep)
        self.assertEqual(event['Nodeset_Config']['Node_List'], nodes)

        ic = event['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(ic['Daily_Import_Pressures'], daily_import_pressures)
        self.assertEqual(ic['Durations'], durations)
        self.assertEqual(ic['class'], 'ImportPressure')
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_as_event(self):
        camp_filename = "import_pressure_as_event.json"
        delete_existing_file(camp_filename)

        durations_1 = [10, 10, 10, 10]
        daily_import_pressures_1 = [0.0, 0.25, 0.5, 1.0]
        nodes_1 = [0, 1, 2, 3, 4]
        timestep_1 = 1
        event = ip.new_intervention(timestep_1, deepcopy(durations_1), deepcopy(daily_import_pressures_1),
                                    deepcopy(nodes_1))
        camp.add(event)

        durations_2 = [20, 20, 20, 20]
        daily_import_pressures_2 = [1.0, 0.75, 0.25, 0.1]
        nodes_2 = [1, 2, 3, 4, 5]
        timestep_2 = 365
        camp.add(ip.new_intervention(timestep_2, deepcopy(durations_2), deepcopy(daily_import_pressures_2),
                                     deepcopy(nodes_2)))

        durations_3 = [55, 55, 55, 55]
        daily_import_pressures_3 = [0.1, 0.01, 0.001, 0.0]
        nodes_3 = [i for i in range(10)]
        timestep_3 = 730
        camp.add(ip.new_intervention(timestep_3, deepcopy(durations_3), deepcopy(daily_import_pressures_3),
                                     deepcopy(nodes_3)))
        camp.save(camp_filename)
        print(f"Check for valid campaign file at: {camp_filename}.")
        self.assertTrue(os.path.isfile(camp_filename))

        with open(camp_filename, 'r') as file:
            campaign = json.load(file)
            camp_event = campaign['Events']
        self.assertEqual(len(camp_event), 3)
        event_1, event_2, event_3 = camp_event

        self.assertEqual(event_1['Start_Day'], timestep_1)
        self.assertEqual(event_1['Nodeset_Config']['Node_List'], nodes_1)
        ic_1 = event_1['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(ic_1['Daily_Import_Pressures'], daily_import_pressures_1)
        self.assertEqual(ic_1['Durations'], durations_1)
        self.assertEqual(ic_1['class'], 'ImportPressure')

        self.assertEqual(event_2['Start_Day'], timestep_2)
        self.assertEqual(event_2['Nodeset_Config']['Node_List'], nodes_2)
        ic_2 = event_2['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(ic_2['Daily_Import_Pressures'], daily_import_pressures_2)
        self.assertEqual(ic_2['Durations'], durations_2)
        self.assertEqual(ic_2['class'], 'ImportPressure')

        self.assertEqual(event_3['Start_Day'], timestep_3)
        self.assertEqual(event_3['Nodeset_Config']['Node_List'], nodes_3)
        ic_3 = event_3['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(ic_3['Daily_Import_Pressures'], daily_import_pressures_3)
        self.assertEqual(ic_3['Durations'], durations_3)
        self.assertEqual(ic_3['class'], 'ImportPressure')

        self.assertTrue(self.rec_check_camp(campaign) is None)

        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def rec_check_camp(self, camp):
        if "schema" in camp: 
            return 1
        for key, value in camp.items():
            if isinstance(value,dict):
                item = self.rec_check_camp(value)
                if item is not None:
                    return 1


class MalariaImportPressureTest(ImportPressureTest):
    @classmethod
    def setUpClass(cls) -> None:
        cls.output_folder = os.path.join(current_directory, 'data', 'campaign')
        if not os.path.isdir(cls.output_folder):
            print(f"\t{cls.output_folder} doesn't exist, creating {cls.output_folder}.")
            os.mkdir(cls.output_folder)
        camp.schema_path = os.path.join(current_directory, 'data', 'config', 'input_malaria_schema.json')


if __name__ == '__main__':
    unittest.main()

