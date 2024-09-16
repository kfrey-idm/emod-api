#!/usr/bin/env python
import os
import unittest
import shutil
import json

from emod_api.interventions import node_multiplier as nm
from emod_api import campaign as camp

from camp_test import CampaignTest, delete_existing_file

current_directory = os.path.dirname(os.path.realpath(__file__))
schema_path = os.path.join(current_directory, 'data', 'config', 'input_generic_schema.json')
_sim_max_time = 365000
class NodeMultiplierTest(CampaignTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        camp.set_schema(schema_path)

    def tearDown(self) -> None:
        camp.set_schema(schema_path)

    def test_as_file(self):
        camp_filename = 'node_multiplier_as_file.json'
        delete_existing_file(camp_filename)
        timestep = 10
        nm.new_intervention_as_file(camp, timestep, filename=camp_filename)
        print(f"Check for valid campaign file at: {camp_filename}.")
        self.assertTrue(os.path.isfile(camp_filename))
        with open(camp_filename, 'r') as file:
            camp_event = json.load(file)['Events']
        self.assertEqual(len(camp_event), 1)
        event = camp_event[0]
        self.assertEqual(event['Start_Day'], timestep)
        self.assertEqual(event['Nodeset_Config'], {"class": "NodeSetAll"})

        ecc = event['Event_Coordinator_Config']
        self.assertEqual(ecc['Number_Repetitions'], -1)
        self.assertEqual(ecc['Timesteps_Between_Repetitions'], 365)

        ic = ecc['Intervention_Config']
        self.assertEqual(ic['class'], 'NodeInfectivityMult')
        self.assertEqual(ic['Multiplier_By_Duration'], {"Times": [0, _sim_max_time ],
                                                        "Values": [1, 1]})

        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_as_event_default(self):
        event = nm.new_scheduled_event(camp)
        name = 'node_multiplier_as_event_default'
        camp.add(event, name=name)
        camp_filename = 'node_multiplier_as_event_default.json'
        delete_existing_file(camp_filename)
        camp.save(camp_filename)
        self.assertTrue(os.path.isfile(camp_filename))
        with open(camp_filename, 'r') as file:
            campaign = json.load(file)
            camp_event = campaign["Events"]
        self.assertEqual(len(camp_event), 1)
        self.assertEqual(event['Start_Day'], 1)
        self.assertEqual(event['Event_Name'], name)
        self.assertEqual(event['Nodeset_Config'], {"class": "NodeSetAll"})

        ecc = event['Event_Coordinator_Config']
        self.assertEqual(ecc['Number_Repetitions'], -1)
        self.assertEqual(ecc['Timesteps_Between_Repetitions'], 365)

        ic = ecc['Intervention_Config']
        self.assertEqual(ic['class'], 'NodeInfectivityMult')
        self.assertEqual(ic['Multiplier_By_Duration'], {"Times": [0, _sim_max_time ],
                                                        "Values": [1, 1]})

        self.assertTrue(self.rec_check_camp(campaign) is None)
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_as_event_constant(self):
        start_day = 2
        new_infectivity = 3
        profile = "CONST"
        node_ids = [1, 2]
        name = 'node_multiplier_as_event_constant'
        event = nm.new_scheduled_event(camp, start_day=start_day, new_infectivity=new_infectivity, profile=profile,
                                       node_ids=node_ids, recurring=False)
        camp.add(event, name=name)
        camp_filename = 'node_multiplier_as_event_constant.json'
        delete_existing_file(camp_filename)
        camp.save(camp_filename)
        self.assertTrue(os.path.isfile(camp_filename))
        with open(camp_filename, 'r') as file:
            campaign = json.load(file)
            camp_event = campaign["Events"]
        self.assertEqual(len(camp_event), 1)
        self.assertEqual(event['Start_Day'], start_day)
        self.assertEqual(event['Event_Name'], name)
        self.assertEqual(event['Nodeset_Config'], {"Node_List": node_ids, "class": "NodeSetNodeList"})

        ecc = event['Event_Coordinator_Config']
        self.assertEqual(ecc['Number_Repetitions'], 1)

        ic = ecc['Intervention_Config']
        self.assertEqual(ic['class'], 'NodeInfectivityMult')
        self.assertEqual(ic['Multiplier_By_Duration'], {"Times": [0, _sim_max_time ],
                                                        "Values": [new_infectivity, new_infectivity]})

        self.assertTrue(self.rec_check_camp(campaign) is None)
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_as_event_sawtooth_rise_dur(self):
        start_day = 3
        new_infectivity = 4
        rise_dur = 10
        profile = "TRAP"
        name = 'node_multiplier_as_event_sawtooth_rise_dur'
        event = nm.new_scheduled_event(camp, start_day=start_day, new_infectivity=new_infectivity, profile=profile,
                                       rise_dur=rise_dur)
        camp.add(event, name=name)
        camp_filename = name + '.json'
        delete_existing_file(camp_filename)
        camp.save(camp_filename)
        self.assertTrue(os.path.isfile(camp_filename))
        with open(camp_filename, 'r') as file:
            campaign = json.load(file)
            camp_event = campaign["Events"]
        self.assertEqual(len(camp_event), 1)
        self.assertEqual(event['Start_Day'], start_day)
        self.assertEqual(event['Event_Name'], name)

        ecc = event['Event_Coordinator_Config']
        ic = ecc['Intervention_Config']
        self.assertEqual(ic['class'], 'NodeInfectivityMult')
        self.assertEqual(ic['Multiplier_By_Duration'], {'Times': [0, rise_dur, rise_dur + 1, rise_dur + 2],
                                                        'Values': [1.0, new_infectivity, new_infectivity, 1.0]})

        self.assertTrue(self.rec_check_camp(campaign) is None)
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_as_event_boxcar(self):
        start_day = 4
        new_infectivity = 0.6
        peak_dur = 20
        profile = "TRAP"
        name = 'node_multiplier_as_event_boxcar'
        event = nm.new_scheduled_event(camp, start_day=start_day, new_infectivity=new_infectivity, profile=profile,
                                       peak_dur=peak_dur)
        camp.add(event, name=name)
        camp_filename = name + '.json'
        delete_existing_file(camp_filename)
        camp.save(camp_filename)
        self.assertTrue(os.path.isfile(camp_filename))
        with open(camp_filename, 'r') as file:
            campaign = json.load(file)
            camp_event = campaign["Events"]
        self.assertEqual(len(camp_event), 1)
        self.assertEqual(event['Start_Day'], start_day)
        self.assertEqual(event['Event_Name'], name)

        ecc = event['Event_Coordinator_Config']
        ic = ecc['Intervention_Config']
        self.assertEqual(ic['class'], 'NodeInfectivityMult')
        self.assertEqual(ic['Multiplier_By_Duration'], {'Times': [0, 1, peak_dur + 1, peak_dur + 2],
                                                        'Values': [1.0, new_infectivity, new_infectivity, 1.0]})

        self.assertTrue(self.rec_check_camp(campaign) is None)
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_as_event_sawtooth_fall_dur(self):
        start_day = 366
        new_infectivity = 0.9
        fall_dur = 30
        profile = "TRAP"
        name = 'node_multiplier_as_event_sawtooth_fall_dur'
        event = nm.new_scheduled_event(camp, start_day=start_day, new_infectivity=new_infectivity, profile=profile,
                                       fall_dur=fall_dur)
        camp.add(event, name=name)
        camp_filename = name + '.json'
        delete_existing_file(camp_filename)
        camp.save(camp_filename)
        self.assertTrue(os.path.isfile(camp_filename))
        with open(camp_filename, 'r') as file:
            campaign = json.load(file)
            camp_event = campaign["Events"]
        self.assertEqual(len(camp_event), 1)
        self.assertEqual(event['Start_Day'], start_day)
        self.assertEqual(event['Event_Name'], name)

        ecc = event['Event_Coordinator_Config']
        ic = ecc['Intervention_Config']
        self.assertEqual(ic['class'], 'NodeInfectivityMult')
        self.assertEqual(ic['Multiplier_By_Duration'], {'Times': [0, 1, 2, fall_dur + 2],
                                                        'Values': [1.0, new_infectivity, new_infectivity, 1.0]})

        self.assertTrue(self.rec_check_camp(campaign) is None)
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_as_event_trapezoid(self):
        start_day = 376
        new_infectivity = 1.2
        rise_dur = 60
        peak_dur = 100
        fall_dur = 90
        profile = "TRAP"
        name = 'node_multiplier_as_event_trapezoid'
        event = nm.new_scheduled_event(camp, start_day=start_day, new_infectivity=new_infectivity, profile=profile,
                                       rise_dur=rise_dur, peak_dur=peak_dur, fall_dur=fall_dur)
        camp.add(event, name=name)
        camp_filename = name + '.json'
        delete_existing_file(camp_filename)
        camp.save(camp_filename)
        self.assertTrue(os.path.isfile(camp_filename))
        with open(camp_filename, 'r') as file:
            campaign = json.load(file)
            camp_event = campaign["Events"]
        self.assertEqual(len(camp_event), 1)
        self.assertEqual(event['Start_Day'], start_day)
        self.assertEqual(event['Event_Name'], name)

        ecc = event['Event_Coordinator_Config']
        ic = ecc['Intervention_Config']
        self.assertEqual(ic['class'], 'NodeInfectivityMult')
        self.assertEqual(ic['Multiplier_By_Duration'],
                         {'Times': [0, rise_dur, rise_dur + peak_dur, rise_dur + peak_dur + fall_dur],
                          'Values': [1.0, new_infectivity, new_infectivity, 1.0]})

        self.assertTrue(self.rec_check_camp(campaign) is None)
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_as_event_trapezoid_longer_duration(self):
        start_day = 376
        new_infectivity = 1.2
        rise_dur = 60
        peak_dur = 100
        fall_dur = 206
        profile = "TRAP"
        with self.assertRaises(ValueError) as error:
            nm.new_scheduled_event(camp, start_day=start_day, new_infectivity=new_infectivity, profile=profile,
                                   rise_dur=rise_dur, peak_dur=peak_dur, fall_dur=fall_dur)
        self.assertIn("less than a year", str(error.exception))


if __name__ == '__main__':
    unittest.main()
