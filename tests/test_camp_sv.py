#!/usr/bin/env python
import os
import unittest
import shutil
import json

from emod_api.interventions import simple_vaccine as sv
from emod_api import campaign as camp

from camp_test import CampaignTest, delete_existing_file

current_directory = os.path.dirname(os.path.realpath(__file__))


class VaccineTest(CampaignTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        sv.schema_path = os.path.join(current_directory, 'data', 'config', 'input_generic_schema.json')
        camp.set_schema(sv.schema_path)

    def test_as_file(self):
        vaccine_type = 'Acquire'
        iv_name = 'simple_vaccine'
        initial_effect = 0.9
        box_duration = 99
        sv.vaccine_type = vaccine_type
        sv.iv_name = iv_name
        sv.initial_effect = initial_effect
        sv.box_duration = box_duration

        camp_filename = 'simple_vaccine_as_file.json'
        delete_existing_file(camp_filename)
        timestep = 1
        sv.new_intervention_as_file(timestep, camp_filename)
        print(f"Check for valid campaign file at: {camp_filename}.")
        self.assertTrue(os.path.isfile(camp_filename))
        with open(camp_filename, 'r') as file:
            camp_event = json.load(file)['Events']
        self.assertEqual(len(camp_event), 1)
        event = camp_event[0]
        self.assertEqual(event['Start_Day'], timestep)
        ic = event['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(ic['Intervention_Name'], iv_name)

        self.assertIn("Initial_Effect", ic['Acquire_Config']) # Want this to fail before checking rest
        self.assertEqual(ic['Acquire_Config']['Initial_Effect'], initial_effect)
        self.assertEqual(ic['Acquire_Config']['Box_Duration'], box_duration)
        self.assertEqual(ic['Acquire_Config']['class'], "WaningEffectBox")
        self.assertEqual(ic['class'], 'Vaccine')
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))
        
    def test_as_event(self):
        camp_filename = "simple_vaccine_as_event.json"
        delete_existing_file(camp_filename)

        timestep_1 = 1
        v_type_1 = "Generic"
        efficacy_1 = 1
        sv_name_1 = "Generic_Vaccine"
        box_duration_1 = 88
        event = sv.new_intervention(timestep_1, v_type=v_type_1, efficacy=efficacy_1, sv_name=sv_name_1,
                                    waning_duration=box_duration_1)
        camp.add(event, first=True)

        timestep_2 = 30
        v_type_2 = "Acquire"
        efficacy_2 = 0
        sv_name_2 = "No_Acq_Vacc"
        box_duration_2 = 77
        camp.add(sv.new_intervention(timestep_2, v_type=v_type_2, efficacy=efficacy_2, sv_name=sv_name_2,
                                     waning_duration=box_duration_2), first=False)

        timestep_3 = 60
        v_type_3 = "Transmit"
        efficacy_3 = 0.8
        sv_name_3 = "No_Trans_Vacc"
        box_duration_3 = 66
        camp.add(sv.new_intervention(timestep_3, v_type=v_type_3, efficacy=efficacy_3, sv_name=sv_name_3,
                                     waning_duration=box_duration_3), first=False)

        timestep_4 = 90
        v_type_4 = "Mortality"
        efficacy_4 = 0.3
        sv_name_4 = "No_Die_Vacc"
        box_duration_4 = 55
        camp.add(sv.new_intervention(timestep_4, v_type=v_type_4, efficacy=efficacy_4, sv_name=sv_name_4,
                                     waning_duration=box_duration_4), first=False)

        camp.save(camp_filename)
        print(f"Check for valid campaign file at: {camp_filename}.")
        self.assertTrue(os.path.isfile(camp_filename))

        with open(camp_filename, 'r') as file:
            campaign = json.load(file)
            camp_event = campaign['Events']

        self.assertEqual(len(camp_event), 4)
        event_1, event_2, event_3, event_4 = camp_event

        # Generic, default is mortality
        self.assertEqual(event_1['Start_Day'], timestep_1)
        ic_1 = event_1['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(ic_1['Intervention_Name'], sv_name_1)
        self.assertIn("Initial_Effect", ic_1['Mortality_Config']) # Want this to fail before checking rest
        self.assertEqual(ic_1['Mortality_Config']['Initial_Effect'], efficacy_1)
        self.assertEqual(ic_1['Mortality_Config']['Box_Duration'], box_duration_1)
        self.assertEqual(ic_1['Mortality_Config']['class'], "WaningEffectBox")
        self.assertEqual(ic_1['class'], 'Vaccine')

        # Acquire vaccine
        self.assertEqual(event_2['Start_Day'], timestep_2)
        ic_2 = event_2['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(ic_2['Intervention_Name'], sv_name_2)
        self.assertIn("Initial_Effect", ic_2['Acquire_Config']) # Want this to fail before checking rest
        self.assertEqual(ic_2['Acquire_Config']['Initial_Effect'], efficacy_2)
        self.assertEqual(ic_2['Acquire_Config']['Box_Duration'], box_duration_2)
        self.assertEqual(ic_2['Acquire_Config']['class'], "WaningEffectBox")
        self.assertEqual(ic_2['class'], 'Vaccine')

        # Transmission vaccine
        self.assertEqual(event_3['Start_Day'], timestep_3)
        ic_3 = event_3['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(ic_3['Intervention_Name'], sv_name_3)
        self.assertIn("Initial_Effect", ic_3['Transmit_Config']) # Want this to fail before checking rest
        self.assertEqual(ic_3['Transmit_Config']['Initial_Effect'], efficacy_3)
        self.assertEqual(ic_3['Transmit_Config']['Box_Duration'], box_duration_3)
        self.assertEqual(ic_3['Transmit_Config']['class'], "WaningEffectBox")
        self.assertEqual(ic_3['class'], 'Vaccine')

        # Mortality vaccine
        self.assertEqual(event_4['Start_Day'], timestep_4)
        ic_4 = event_4['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(ic_4['Intervention_Name'], sv_name_4)

        self.assertIn("Initial_Effect", ic_1['Mortality_Config']) # Want this to fail before checking rest
        self.assertEqual(ic_4['Mortality_Config']['Initial_Effect'], efficacy_4)
        self.assertEqual(ic_4['Mortality_Config']['Box_Duration'], box_duration_4)
        self.assertEqual(ic_4['Mortality_Config']['class'], "WaningEffectBox")
        self.assertEqual(ic_4['class'], 'Vaccine')

        self.assertTrue(self.rec_check_camp(campaign) is None)

        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_as_event_2(self):  # skip this test until we fix https://github.com/InstituteforDiseaseModeling/emod-api/issues/141
        camp_filename = "simple_vaccine_as_event_2.json"
        delete_existing_file(camp_filename)

        timestep_1 = 1
        sv.vaccine_type = vaccine_type_1 = "Acquire"
        sv.initial_effect = initial_effect_1 = 0.9
        sv.iv_name = iv_name_1 = "No_Acq_Vacc"
        sv.box_duration = box_duration_1 = 11
        event = sv.new_intervention2(timestep_1)
        camp.add(event, first=True)

        timestep_2 = 30
        sv.vaccine_type = vaccine_type_2 = "Transmit"
        sv.initial_effect = initial_effect_2 = 0.8
        sv.iv_name = iv_name_2 = "No_Trans_Vacc"
        sv.box_duration = box_duration_2 = 22
        camp.add(sv.new_intervention2(timestep_2), first=False)

        timestep_3 = 60
        sv.vaccine_type = vaccine_type_3 = "MortalityBlocking"
        sv.initial_effect = initial_effect_3 = 0.7
        sv.iv_name = iv_name_3 = "No_Die_Vacc"
        sv.box_duration = box_duration_3 = 33
        camp.add(sv.new_intervention2(timestep_3), first=False)

        camp.save(camp_filename)
        print(f"Check for valid campaign file at: {camp_filename}.")
        self.assertTrue(os.path.isfile(camp_filename))

        with open(camp_filename, 'r') as file:
            campaign = json.load(file)
            camp_event = campaign['Events']

        self.assertEqual(len(camp_event), 3)
        event_1, event_2, event_3 = camp_event

        self.assertEqual(event_1['Start_Day'], timestep_1)
        ic_1 = event_1['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(ic_1['Intervention_Name'], iv_name_1)
        self.assertIn("Initial_Effect", ic_1['Acquire_Config'], msg="Acquire Config not set properly") # Want this to fail before checking rest
        self.assertEqual(ic_1['Acquire_Config']['Initial_Effect'], initial_effect_1)
        self.assertEqual(ic_1['Acquire_Config']['Box_Duration'], box_duration_1)
        self.assertEqual(ic_1['Acquire_Config']['class'], "WaningEffectBox")
        self.assertEqual(ic_1['class'], 'Vaccine')

        self.assertEqual(event_2['Start_Day'], timestep_2)
        ic_2 = event_2['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(ic_2['Intervention_Name'], iv_name_2)
        self.assertIn("Initial_Effect", ic_2['Transmit_Config'], msg="Transmit Config not set properly") # Want this to fail before checking rest
        self.assertEqual(ic_2['Transmit_Config']['Initial_Effect'], initial_effect_2)
        self.assertEqual(ic_2['Transmit_Config']['Box_Duration'], box_duration_2)
        self.assertEqual(ic_2['Transmit_Config']['class'], "WaningEffectBox")
        self.assertEqual(ic_2['class'], 'Vaccine')

        self.assertEqual(event_3['Start_Day'], timestep_3)
        ic_3 = event_3['Event_Coordinator_Config']['Intervention_Config']
        self.assertEqual(ic_3['Intervention_Name'], iv_name_3)
        self.assertIn("Initial_Effect", ic_3['Mortality_Config'], msg="Mortality Config not set properly") # Want this to fail before checking rest
        self.assertEqual(ic_3['Mortality_Config']['Initial_Effect'], initial_effect_3)
        self.assertEqual(ic_3['Mortality_Config']['Box_Duration'], box_duration_3)
        self.assertEqual(ic_3['Mortality_Config']['class'], "WaningEffectBox")
        self.assertEqual(ic_3['class'], 'Vaccine')
        
        self.assertTrue(self.rec_check_camp(campaign) is None)
        

        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_intervention_parameter(self):
        timestep = 10
        sv_event = sv.new_intervention(timestep=timestep)
        sv_file = 'simple_vaccine_intervention_parameter.json'
        name = "simple_vaccine_intervention"
        camp.add(sv_event, name=name, first=True)

        delete_existing_file(sv_file)
        camp.save(sv_file)

        with open(sv_file, 'r') as file:
            campaign = json.load(file)
            sv_dict = campaign["Events"][0]['Event_Coordinator_Config']['Intervention_Config']
            sv_default = campaign["Use_Defaults"]

        intervention_only = sv.new_intervention(timestep=timestep, intervention_only=True)
        intervention_only_file = "sv_intervention_only.json"
        camp.add(intervention_only, name=name, first=True)
        delete_existing_file(intervention_only_file)
        camp.save(intervention_only_file)

        with open(intervention_only_file, 'r') as file:
            campaign = json.load(file)
            intervention_only_dict = campaign['Events'][0]
            intervention_only_defaults = campaign["Use_Defaults"]

        for key in sv_dict:
            self.assertEqual(sv_dict[key], intervention_only_dict[key])
        
        for key in intervention_only_dict:
            if key != "Event_Name":
                self.assertEqual(sv_dict[key], intervention_only_dict[key])
        
        self.assertEqual(sv_default, intervention_only_defaults)
        shutil.move(sv_file, os.path.join(self.output_folder, intervention_only_file))
        shutil.move(intervention_only_file, os.path.join(self.output_folder, intervention_only_file))

    def rec_check_camp(self, camp):
        if "schema" in camp: 
            return 1
        for key, value in camp.items():
            if isinstance(value,dict):
                item = self.rec_check_camp(value)
                if item is not None:
                    return item

    def test_recursion(self):
        dictionary = {"bing": {"bang": {"schema": 50}}}
        print(self.rec_check_camp(dictionary))


if __name__ == '__main__':
    unittest.main()

