#!/usr/bin/env python
import os
import unittest
import shutil
import json

from emod_api.interventions.common import *
from emod_api.interventions import common, migration
from emod_api import campaign as camp
from emod_api.interventions import utils as ut

from camp_test import CampaignTest, delete_existing_file

current_directory = os.path.dirname(os.path.realpath(__file__))
schema_path = os.path.join(current_directory, 'data', 'config', 'input_generic_schema.json')
schema_path_malaria = os.path.join(current_directory, 'data', 'config', 'input_malaria_schema.json')


class CommonInterventionTest(CampaignTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        camp.reset()
        camp.schema_path = schema_path

    def save_campaignfile_and_load_event(self, intervention, camp_filename):
        camp.add(intervention, first=True)
        camp.save(camp_filename)
        print(f"Check for valid campaign file at: {camp_filename}.")
        self.assertTrue(os.path.isfile(camp_filename))

        with open(camp_filename, 'r') as file:
            camp_event = json.load(file)['Events']
        self.assertEqual(len(camp_event), 1)
        event = camp_event[0]
        return event

    @unittest.skip
    def test_common_schema_path(self):
        from emod_api.interventions import common
        common.schema_path = schema_path
        broadcast_event = 'Blackout'
        BroadcastEvent(None, Event_Trigger=broadcast_event)
        pass

    def test_broadcast_event(self):
        camp_filename = 'broadcast_event.json'
        delete_existing_file(camp_filename)

        broadcast_event = 'ExitedRelationship'
        intervention = BroadcastEvent(camp, Event_Trigger=broadcast_event)

        event = self.save_campaignfile_and_load_event(intervention, camp_filename)

        self.assertEqual(event['Broadcast_Event'], broadcast_event)
        self.assertEqual(event['class'], "BroadcastEvent")
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_broadcast_event_to_other_node(self):
        camp_filename = 'broadcast_event_to_other_node.json'
        delete_existing_file(camp_filename)

        event_trigger = 'Births'
        node_selection_type = 'MIGRATION_NODES_ONLY'
        max_distance = 100
        my_node = False
        intervention = BroadcastEventToOtherNodes(camp, Event_Trigger=event_trigger,
                                                  Node_Selection_Type=node_selection_type,
                                                  Max_Distance_To_Other_Nodes_Km=max_distance, Include_My_Node=my_node)

        event = self.save_campaignfile_and_load_event(intervention, camp_filename)

        self.assertEqual(event['Event_Trigger'], event_trigger)
        self.assertEqual(event['class'], "BroadcastEventToOtherNodes")
        self.assertEqual(event['Include_My_Node'], my_node)
        self.assertEqual(event['Max_Distance_To_Other_Nodes_Km'], max_distance)
        self.assertEqual(event['Node_Selection_Type'], node_selection_type)
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_multi_intervention_distributor(self):
        camp_filename = 'multi_intervention_distributor.json'
        delete_existing_file(camp_filename)

        intervention_list = [BroadcastEvent(camp, 'GP_EVENT_000'),
                             BroadcastEvent(camp, 'GP_EVENT_001')]
        intervention = MultiInterventionDistributor(camp, Intervention_List=intervention_list)

        event = self.save_campaignfile_and_load_event(intervention, camp_filename)

        for i in range(len(intervention_list)):
            self.assertTrue(event['Intervention_List'][i].items() <= intervention_list[i].items())
        self.assertEqual(event['class'], "MultiInterventionDistributor")
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_multi_intervention_distributor_exception(self):
        with self.assertRaises(Exception) as context:
            intervention_list = 'test'
            MultiInterventionDistributor(camp, Intervention_List=intervention_list)

        self.assertTrue('Intervention_List' in str(context.exception))

    def test_delayed_intervention(self):
        camp_filename = 'delayed_intervention.json'
        delete_existing_file(camp_filename)

        actual_interventions = [BroadcastEvent(camp, 'GP_EVENT_000')]
        intervention = DelayedIntervention(camp, Configs=copy.deepcopy(actual_interventions),
                                           Delay_Dict={"Delay_Period_Exponential": 5})

        event = self.save_campaignfile_and_load_event(intervention, camp_filename)

        self.assertTrue(event['Actual_IndividualIntervention_Configs'][0].items() <= actual_interventions[0].items())
        self.assertEqual(event['class'], "DelayedIntervention")
        self.assertEqual(event['Delay_Period_Distribution'], "EXPONENTIAL_DISTRIBUTION")
        self.assertEqual(event['Delay_Period_Exponential'], 5)

        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    @unittest.skip
    def test_delayed_intervention_exception(self):
        with self.assertRaises(Exception) as context:
            actual_intervention = 'test'
            DelayedIntervention(camp, Configs=actual_intervention)

        self.assertTrue('Configs' in str(context.exception))

    def test_HSB_event(self):
        camp_filename = 'HSB_event.json'
        delete_existing_file(camp_filename)

        actual_event = 'GP_EVENT_000'
        intervention = HSB(camp,
                           Event_Or_Config="Event",
                           Config=None,
                           Event=actual_event,
                           Tendency=0.2,
                           Single_Use=True,
                           Name="HSB")

        event = self.save_campaignfile_and_load_event(intervention, camp_filename)

        self.assertEqual(event['Actual_IndividualIntervention_Event'], actual_event)
        self.assertEqual(event['class'], "SimpleHealthSeekingBehavior")
        self.assertEqual(event['Event_Or_Config'], "Event")
        self.assertEqual(event['Single_Use'], 1)
        self.assertEqual(event['Tendency'], 0.2)
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_HSB_config(self):
        camp_filename = 'HSB_config.json'
        delete_existing_file(camp_filename)

        actual_config = BroadcastEvent(camp, 'GP_EVENT_000')
        import copy
        intervention = HSB(camp,
                           Event_Or_Config="Config",
                           Config=copy.deepcopy(actual_config),
                           Event=None,
                           Tendency=0.7,
                           Single_Use=False,
                           Name="HSB_2")

        event = self.save_campaignfile_and_load_event(intervention, camp_filename)

        self.assertTrue(event['Actual_IndividualIntervention_Config'].items() <= actual_config.items())
        self.assertEqual(event['class'], "SimpleHealthSeekingBehavior")
        self.assertEqual(event['Event_Or_Config'], "Config")
        self.assertEqual(event['Single_Use'], 0)
        self.assertEqual(event['Tendency'], 0.7)
        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_NLHTI(self):
        camp_filename = 'NLHTI.json'
        delete_existing_file(camp_filename)

        triggers = ['GP_EVENT_000', 'GP_EVENT_001']
        intervention_list = [BroadcastEvent(camp)]
        intervention = NLHTI(camp,
                             Triggers=copy.deepcopy(triggers),
                             Interventions=copy.deepcopy(intervention_list),
                             Property_Restrictions=[{'Risk': 'High'}, {'Risk': 'Low'}],
                             Demographic_Coverage=0.6,
                             Target_Age_Min=10,
                             Target_Age_Max=50,
                             Target_Gender="Female",
                             Target_Residents_Only=1,
                             Duration=20)

        event = self.save_campaignfile_and_load_event(intervention, camp_filename)

        self.assertTrue(event['Actual_IndividualIntervention_Config'].items() <=
                        intervention_list[0].items())
        self.assertEqual(event['class'], "NodeLevelHealthTriggeredIV")
        self.assertEqual(event['Duration'], 20)
        self.assertEqual(event['Target_Age_Max'], 50)
        self.assertEqual(event['Target_Age_Min'], 10)
        self.assertEqual(event['Target_Gender'], "Female")
        self.assertEqual(event['Target_Demographic'], "ExplicitAgeRangesAndGender")
        self.assertEqual(event['Trigger_Condition_List'], triggers)
        self.assertEqual(event['Property_Restrictions_Within_Node'], [{'Risk': 'High'}, {'Risk': 'Low'}])

        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_property_value_changer(self):
        camp_filename = 'property_value_changer.json'
        delete_existing_file(camp_filename)

        target_property_key = 'Risk'
        target_property_value = 'High'
        intervention = PropertyValueChanger(camp,
                                            target_property_key,
                                            target_property_value,
                                            Daily_Probability=0.6,
                                            Maximum_Duration=10)

        event = self.save_campaignfile_and_load_event(intervention, camp_filename)

        self.assertEqual(event['class'], "PropertyValueChanger")
        self.assertEqual(event['Maximum_Duration'], 10)
        self.assertEqual(event['Daily_Probability'], 0.6)
        self.assertEqual(event['Target_Property_Key'], target_property_key)
        self.assertEqual(event['Target_Property_Value'], target_property_value)

        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_property_value_changer_defaults(self):
        camp_filename = 'property_value_changer.json'
        delete_existing_file(camp_filename)

        target_property_key = 'Risk'
        target_property_value = 'High'
        daily_probability=1.0
        maximum_dur=1.0
        revert=0
        intervention = PropertyValueChanger(camp,
                                            target_property_key,
                                            target_property_value,
                                            )

        event = self.save_campaignfile_and_load_event(intervention, camp_filename)

        self.assertEqual(event['class'], "PropertyValueChanger")
        self.assertEqual(event['Maximum_Duration'], maximum_dur)
        self.assertEqual(event['Daily_Probability'], daily_probability)
        self.assertIsNone(event['New_Property_Value'])
        self.assertEqual(event['Target_Property_Key'], target_property_key)
        self.assertEqual(event['Target_Property_Value'], target_property_value)
        self.assertEqual(event['Revert'], revert)

        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_scheduled_campaign_event_exception(self):

        with self.assertRaises(AssertionError) as context:
            ScheduledCampaignEvent(camp,
                                   Start_Day=30,
                                   Nodeset_Config=utils.do_nodes(schema_path, [1, 2]),
                                   Node_Ids=[1, 2],
                                   Intervention_List=[BroadcastEvent(camp)])


    def test_scheduled_campaign_event_using_Nodeset_Config(self):
        camp_filename = 'scheduled_campaign_event.json'
        delete_existing_file(camp_filename)

        intervention_list = [BroadcastEvent(camp)]
        intervention = ScheduledCampaignEvent(camp,
                                              Start_Day=30,
                                              Nodeset_Config=utils.do_nodes(schema_path, [1, 2]),
                                              Number_Repetitions=3,
                                              Timesteps_Between_Repetitions=10,
                                              Demographic_Coverage=0.3,
                                              Intervention_List=copy.deepcopy(intervention_list))

        event = self.save_campaignfile_and_load_event(intervention, camp_filename)

        self.assertEqual(event['Start_Day'], 30)
        self.assertEqual(event['Nodeset_Config'], {
            "Node_List": [
                1,
                2
            ],
            "class": "NodeSetNodeList"
        })
        ecc = event['Event_Coordinator_Config']
        self.assertEqual(ecc['Demographic_Coverage'], 0.3)
        self.assertEqual(ecc['Number_Repetitions'], 3)
        self.assertEqual(ecc['Timesteps_Between_Repetitions'], 10)

        ic = ecc['Intervention_Config']
        #self.assertEqual(ic['class'], 'MultiInterventionDistributor')
        self.assertTrue(ic.items() <= intervention_list[0].items())

        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_scheduled_campaign_event(self):
        camp_filename = 'scheduled_campaign_event.json'
        delete_existing_file(camp_filename)

        intervention_list = [BroadcastEvent(camp)]
        intervention = ScheduledCampaignEvent(camp,
                                            Start_Day=30,
                                            Node_Ids=[1, 2],
                                            Number_Repetitions=3,
                                            Timesteps_Between_Repetitions=10,
                                            Demographic_Coverage=0.3,
                                            Intervention_List=copy.deepcopy(intervention_list))

        event = self.save_campaignfile_and_load_event(intervention, camp_filename)

        self.assertEqual(event['Start_Day'], 30)

        self.assertEqual(event['Nodeset_Config'], {
                "Node_List": [
                    1,
                    2
                ],
                "class": "NodeSetNodeList"
            })

        ecc = event['Event_Coordinator_Config']
        self.assertEqual(ecc['Demographic_Coverage'], 0.3)
        self.assertEqual(ecc['Number_Repetitions'], 3)
        self.assertEqual(ecc['Timesteps_Between_Repetitions'], 10)

        ic = ecc['Intervention_Config']
        #self.assertEqual(ic['class'], 'MultiInterventionDistributor')
        self.assertTrue(ic.items() <= intervention_list[0].items())

        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_new_migration_intervention(self):
        mean = 0.123
        std_dev = 0.345
        peak_2_value = 0.456
        mu = 0.567
        sigma = 0.678
        intervention = migration._new_migration_intervention(camp,
                                                             duration_before_leaving_gaussian_mean=mean,
                                                             duration_before_leaving_gaussian_std_dev=std_dev,
                                                             duration_before_leaving_peak_2_value=peak_2_value,
                                                             duration_at_node_peak_2_value=peak_2_value,
                                                             duration_at_node_poisson_mean=mean,
                                                             duration_before_leaving_log_normal_mu=mu,
                                                             duration_before_leaving_log_normal_sigma=sigma)

        self.assertEqual(intervention["Duration_Before_Leaving_Gaussian_Mean"], mean)
        self.assertEqual(intervention["Duration_Before_Leaving_Gaussian_Std_Dev"], std_dev)
        self.assertEqual(intervention["Duration_Before_Leaving_Peak_2_Value"], peak_2_value)
        self.assertEqual(intervention["Duration_At_Node_Poisson_Mean"], mean)
        self.assertEqual(intervention["Duration_At_Node_Peak_2_Value"], peak_2_value)
        self.assertEqual(intervention["Duration_Before_Leaving_Log_Normal_Mu"], mu)
        self.assertEqual(intervention["Duration_Before_Leaving_Log_Normal_Sigma"], sigma)




    def test_ScheduledCampaignEvent_with_migration(self):
        # Property_Restrictions = None,

        start_day = 10
        target_age_max = 12345
        target_age_min = 12
        demographics_coverage = 0.123
        node_list = [1, 2, 3]
        number_repetitions: int = 123
        timesteps_between_repetitions = 1234

        intervention_migration = migration._new_migration_intervention(camp, duration_at_node_mean_1=1, is_moving=True)
        sce_migration = ScheduledCampaignEvent(camp, start_day,
                                               Demographic_Coverage=demographics_coverage,
                                               Node_Ids=node_list,
                                               Number_Repetitions=number_repetitions,
                                               Timesteps_Between_Repetitions=timesteps_between_repetitions,
                                               Target_Age_Max=target_age_max,
                                               Target_Age_Min=target_age_min,
                                               Target_Gender="Male",
                                               Intervention_List=[intervention_migration])

        self.assertEqual(sce_migration["class"], "CampaignEvent")
        self.assertEqual(sce_migration["Start_Day"], start_day)

        event_coordinator_config = sce_migration["Event_Coordinator_Config"]
        self.assertEqual(event_coordinator_config["Demographic_Coverage"], demographics_coverage)
        self.assertEqual(event_coordinator_config["Number_Repetitions"], number_repetitions)
        self.assertEqual(event_coordinator_config["Timesteps_Between_Repetitions"], timesteps_between_repetitions)
        self.assertEqual(event_coordinator_config["Target_Age_Max"], target_age_max)
        self.assertEqual(event_coordinator_config["Target_Age_Min"], target_age_min)
        self.assertEqual(event_coordinator_config["Target_Gender"], "Male")
        self.assertEqual(event_coordinator_config["Target_Demographic"], "ExplicitAgeRangesAndGender")
        self.assertEqual(event_coordinator_config["class"], "StandardInterventionDistributionEventCoordinator")

        self.assertIsNotNone(event_coordinator_config.get("Intervention_Config"))

        nodeset_config = sce_migration["Nodeset_Config"]
        self.assertEqual(nodeset_config["class"], "NodeSetNodeList")
        self.assertEqual(nodeset_config["Node_List"], node_list)

    def test_age_sex_scheduled_campaign_event(self):
        # Testing a few target age range and sex cases

        intervention_list = [BroadcastEvent(camp)]
        test_files = ["ScheduledCE_MinAge.json", "ScheduledCE_MaxAge.json", "ScheduledCE_Gender.json", "ScheduledCE_Everyone.json"]

        # Specific target age min

        intervention = ScheduledCampaignEvent(camp,
                                              Start_Day=30,
                                              Node_Ids=[1, 2],
                                              Number_Repetitions=3,
                                              Timesteps_Between_Repetitions=10,
                                              Demographic_Coverage=0.3,
                                              Intervention_List=copy.deepcopy(intervention_list),
                                              Target_Age_Min=1)

        event = self.save_campaignfile_and_load_event(intervention, "ScheduledCE_MinAge.json")
        ecc = event['Event_Coordinator_Config']
        self.assertEqual(ecc["Target_Demographic"], "ExplicitAgeRanges")
        self.assertEqual(ecc["Target_Age_Min"], 1)

        # Specific age max

        intervention = ScheduledCampaignEvent(camp,
                                              Start_Day=30,
                                              Node_Ids=[1, 2],
                                              Number_Repetitions=3,
                                              Timesteps_Between_Repetitions=10,
                                              Demographic_Coverage=0.3,
                                              Intervention_List=copy.deepcopy(intervention_list),
                                              Target_Age_Max=20)

        event = self.save_campaignfile_and_load_event(intervention, "ScheduledCE_MaxAge.json")
        ecc = event['Event_Coordinator_Config']
        self.assertEqual(ecc["Target_Demographic"], "ExplicitAgeRanges")
        self.assertEqual(ecc["Target_Age_Max"], 20)

        # Specific target gender

        intervention = ScheduledCampaignEvent(camp,
                                              Start_Day=30,
                                              Node_Ids=[1, 2],
                                              Number_Repetitions=3,
                                              Timesteps_Between_Repetitions=10,
                                              Demographic_Coverage=0.3,
                                              Intervention_List=copy.deepcopy(intervention_list),
                                              Target_Gender="Male")

        event = self.save_campaignfile_and_load_event(intervention, "ScheduledCE_Gender.json")
        ecc = event['Event_Coordinator_Config']
        self.assertEqual(ecc["Target_Demographic"], "ExplicitAgeRangesAndGender")
        self.assertEqual(ecc["Target_Gender"], "Male")

        # Everyone targeted

        intervention = ScheduledCampaignEvent(camp,
                                              Start_Day=30,
                                              Node_Ids=[1, 2],
                                              Number_Repetitions=3,
                                              Timesteps_Between_Repetitions=10,
                                              Demographic_Coverage=0.3,
                                              Intervention_List=copy.deepcopy(intervention_list),
                                              Target_Gender="All",
                                              Target_Age_Min=0)

        event = self.save_campaignfile_and_load_event(intervention, "ScheduledCE_Everyone.json")
        ecc = event['Event_Coordinator_Config']
        self.assertEqual(ecc["Target_Demographic"], "Everyone")

        for filename in test_files:
            shutil.move(filename, os.path.join(self.output_folder, filename))

    def test_empty_nodeset(self):
        # Test that empty nodeset returns empty list of target nodes
        camp.reset()
        intervention = ScheduledCampaignEvent(camp,
                                              Start_Day=30,
                                              Number_Repetitions=3,
                                              Timesteps_Between_Repetitions=10,
                                              Demographic_Coverage=0.3,
                                              Intervention_List=[BroadcastEvent(camp)],
                                              Target_Age_Min=1)

        event = self.save_campaignfile_and_load_event(intervention, "EmptyNodesetSCE.json")
        node_config = event['Nodeset_Config']
        prop_restrictions = event['Event_Coordinator_Config']['Property_Restrictions']
        self.assertEqual(node_config, {"class": "NodeSetAll"})
        self.assertEqual(prop_restrictions, [])

        camp.reset()
        intervention2 = TriggeredCampaignEvent(camp,
                                              Start_Day=5,
                                              Event_Name='test_event_name',
                                              Triggers=['ExitedRelationship'],
                                              Intervention_List=[BroadcastEvent(camp)],
                                              Number_Repetitions=6,
                                              Timesteps_Between_Repetitions=30)

        event2 = self.save_campaignfile_and_load_event(intervention2, "EmptyNodesetTCE.json")
        node_config = event2['Nodeset_Config']
        self.assertEqual(node_config, {"class": "NodeSetAll"})
        prop_restrictions = event2['Event_Coordinator_Config']['Property_Restrictions']
        self.assertEqual(prop_restrictions, [])

    def test_triggered_campaign_event_exception(self):
        triggers = ['GP_EVENT_002', 'GP_EVENT_003']
        with self.assertRaises(AssertionError) as context:
            TriggeredCampaignEvent(camp,
                                   Start_Day=5,
                                   Event_Name='test_event_name',
                                   Nodeset_Config=utils.do_nodes(schema_path, [3, 4]),
                                   Node_Ids=[3, 4],
                                   Triggers=copy.deepcopy(triggers),
                                   Intervention_List=[BroadcastEvent(camp)],
                                   Property_Restrictions=[{'Risk': 'High'}],
                                   Number_Repetitions=6,
                                   Timesteps_Between_Repetitions=30)

    def test_triggered_campaign_event_using_Nodeset_Config(self):
        camp_filename = 'triggered_campaign_event.json'
        delete_existing_file(camp_filename)

        triggers = ['GP_EVENT_002', 'GP_EVENT_003']
        intervention_list = [BroadcastEvent(camp)]
        intervention = TriggeredCampaignEvent(camp,
                                              Start_Day=5,
                                              Event_Name='test_event_name',
                                              Nodeset_Config=utils.do_nodes(schema_path, [3, 4]),
                                              Triggers=copy.deepcopy(triggers),
                                              Intervention_List=copy.deepcopy(intervention_list),
                                              Property_Restrictions=[{'Risk': 'High'}],
                                              Number_Repetitions=6,
                                              Timesteps_Between_Repetitions=30)

        event = self.save_campaignfile_and_load_event(intervention, camp_filename)

        self.assertEqual(event['Start_Day'], 5)
        self.assertEqual(event['Nodeset_Config'], {
                "Node_List": [
                    3,
                    4
                ],
                "class": "NodeSetNodeList"
            })
        ecc = event['Event_Coordinator_Config']
        self.assertEqual(ecc['class'], 'StandardInterventionDistributionEventCoordinator')

        ic = ecc['Intervention_Config']
        self.assertEqual(ic['class'], 'NodeLevelHealthTriggeredIV')
        self.assertEqual(ic['Property_Restrictions'], ['Risk:High'])
        self.assertEqual(ic['Trigger_Condition_List'], triggers)

        ac = ic['Actual_IndividualIntervention_Config']
        self.assertTrue(ac.items() <=
                        intervention_list[0].items())
        self.assertEqual(ac['class'], 'BroadcastEvent')

    def test_triggered_campaign_event(self):
        """
        StandardEventCoordinator --> NLHTI --> MultiInterventionDistrib --> List_Of ... Actual Interventions.
        Returns:

        """
        camp_filename = 'triggered_campaign_event.json'
        delete_existing_file(camp_filename)

        triggers = ['GP_EVENT_002', 'GP_EVENT_003']
        intervention_list = [BroadcastEvent(camp)]
        intervention = TriggeredCampaignEvent(camp,
                                              Start_Day=5,
                                              Event_Name='test_event_name',
                                              Node_Ids=[3, 4],
                                              Triggers=copy.deepcopy(triggers),
                                              Intervention_List=copy.deepcopy(intervention_list),
                                              Property_Restrictions=[{'Risk': 'High'}],
                                              Number_Repetitions=6,
                                              Timesteps_Between_Repetitions=30)

        event = self.save_campaignfile_and_load_event(intervention, camp_filename)

        self.assertEqual(event['Start_Day'], 5)
        self.assertEqual(event['Nodeset_Config'], {
                "Node_List": [
                    3,
                    4
                ],
                "class": "NodeSetNodeList"
            })
        ecc = event['Event_Coordinator_Config']
        self.assertEqual(ecc['class'], 'StandardInterventionDistributionEventCoordinator')
        # These two parameters are not used in TriggeredCampaignEvent() yet
        # self.assertEqual(ecc['Number_Repetitions'], 6)
        # self.assertEqual(ecc['Timesteps_Between_Repetitions'], 30)

        ic = ecc['Intervention_Config']
        self.assertEqual(ic['class'], 'NodeLevelHealthTriggeredIV')
        self.assertEqual(ic['Property_Restrictions'], ['Risk:High'])
        self.assertEqual(ic['Trigger_Condition_List'], triggers)

        ac = ic['Actual_IndividualIntervention_Config']
        self.assertTrue(ac.items() <=
                        intervention_list[0].items())
        self.assertEqual(ac['class'], 'BroadcastEvent')

        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

        # Testing a few cases where age range and sex are specified
        test_files = ["TriggeredCE_MinAge.json", "TriggeredCE_MaxAge.json", "TriggeredCE_Gender.json", "TriggeredCE_Everyone.json"]
        # Specific min age:
        intervention = TriggeredCampaignEvent(camp,
                                            Start_Day=5,
                                            Event_Name='test_event_name',
                                            Node_Ids=[3, 4],
                                            Triggers=copy.deepcopy(triggers),
                                            Intervention_List=copy.deepcopy(intervention_list),
                                            Property_Restrictions=[{'Risk': 'High'}],
                                            Number_Repetitions=6,
                                            Timesteps_Between_Repetitions=30,
                                            Target_Age_Min = 1
                                            )

        event = self.save_campaignfile_and_load_event(intervention, "TriggeredCE_MinAge.json")
        ecc = event['Event_Coordinator_Config']
        ic = ecc['Intervention_Config']
        self.assertEqual(ic["Target_Demographic"], "ExplicitAgeRanges")
        self.assertEqual(ic["Target_Age_Min"], 1)

        # Specific max age

        intervention = TriggeredCampaignEvent(camp,
                                            Start_Day=5,
                                            Event_Name='test_event_name',
                                            Node_Ids=[3, 4],
                                            Triggers=copy.deepcopy(triggers),
                                            Intervention_List=copy.deepcopy(intervention_list),
                                            Property_Restrictions=[{'Risk': 'High'}],
                                            Number_Repetitions=6,
                                            Timesteps_Between_Repetitions=30,
                                            Target_Age_Max = 15
                                            )

        event = self.save_campaignfile_and_load_event(intervention, "TriggeredCE_MaxAge.json")
        ecc = event['Event_Coordinator_Config']
        ic = ecc['Intervention_Config']
        self.assertEqual(ic["Target_Demographic"], "ExplicitAgeRanges")
        self.assertEqual(ic["Target_Age_Max"], 15)

        # Specific Gender

        intervention = TriggeredCampaignEvent(camp,
                                            Start_Day=5,
                                            Event_Name='test_event_name',
                                            Node_Ids=[3, 4],
                                            Triggers=copy.deepcopy(triggers),
                                            Intervention_List=copy.deepcopy(intervention_list),
                                            Property_Restrictions=[{'Risk': 'High'}],
                                            Number_Repetitions=6,
                                            Timesteps_Between_Repetitions=30,
                                            Target_Gender="Male"
                                            )

        event = self.save_campaignfile_and_load_event(intervention, "TriggeredCE_Gender.json")
        ecc = event['Event_Coordinator_Config']
        ic = ecc['Intervention_Config']
        self.assertEqual(ic["Target_Demographic"], "ExplicitAgeRangesAndGender")
        self.assertEqual(ic["Target_Gender"], "Male")

        # Everyone

        intervention = TriggeredCampaignEvent(camp,
                                            Start_Day=5,
                                            Event_Name='test_event_name',
                                            Node_Ids=[3, 4],
                                            Triggers=copy.deepcopy(triggers),
                                            Intervention_List=copy.deepcopy(intervention_list),
                                            Property_Restrictions=[{'Risk': 'High'}],
                                            Number_Repetitions=6,
                                            Timesteps_Between_Repetitions=30,
                                            Target_Gender="All",
                                            Target_Age_Min=0
                                            )

        event = self.save_campaignfile_and_load_event(intervention, "TriggeredCE_Everyone.json")
        ecc = event['Event_Coordinator_Config']
        ic = ecc['Intervention_Config']
        self.assertEqual(ic["Target_Demographic"], "Everyone")

        # Blackout_Event Default

        intervention = TriggeredCampaignEvent(camp,
                                              Start_Day=5,
                                              Event_Name='test_event_name',
                                              Node_Ids=[3, 4],
                                              Triggers=copy.deepcopy(triggers),
                                              Intervention_List=copy.deepcopy(intervention_list),
                                              Property_Restrictions=[{'Risk': 'High'}],
                                              Number_Repetitions=6,
                                              Timesteps_Between_Repetitions=30,
                                              Target_Gender="Male"
                                              )

        event = self.save_campaignfile_and_load_event(intervention, "TriggeredCE_Blackout_Event_Default.json")
        ecc = event['Event_Coordinator_Config']
        ic = ecc['Intervention_Config']
        if self.__class__ == CommonInterventionTest:
            self.assertEqual(ic["Blackout_Event_Trigger"], "NoTrigger")  # default for Generic, see schema
        elif self.__class__ == CommonInterventionTestMalaria:
            self.assertEqual(ic["Blackout_Event_Trigger"], "")      # default for Malaria, see schema
        self.assertEqual(ic["Blackout_On_First_Occurrence"], 0)
        self.assertEqual(ic["Blackout_Period"], 0)

        # Blackout_Event

        intervention = TriggeredCampaignEvent(camp,
                                              Start_Day=5,
                                              Event_Name='test_event_name',
                                              Node_Ids=[3, 4],
                                              Triggers=copy.deepcopy(triggers),
                                              Intervention_List=copy.deepcopy(intervention_list),
                                              Property_Restrictions=[{'Risk': 'High'}],
                                              Number_Repetitions=6,
                                              Timesteps_Between_Repetitions=30,
                                              Target_Gender="Male",
                                              Blackout_Event_Trigger="Births",
                                              Blackout_On_First_Occurrence=1,
                                              Blackout_Period=2
                                              )

        event = self.save_campaignfile_and_load_event(intervention, "TriggeredCE_Blackout_Event.json")
        ecc = event['Event_Coordinator_Config']
        ic = ecc['Intervention_Config']
        self.assertEqual(ic["Blackout_Event_Trigger"], "Births")
        self.assertEqual(ic["Blackout_On_First_Occurrence"], 1)
        self.assertEqual(ic["Blackout_Period"], 2)

        #  Number_Repetitions, Timesteps_Between_Repetitions
        num_repetitions = 12
        timestep_between_rep = 34
        intervention = TriggeredCampaignEvent(camp,
                                              Start_Day=5,
                                              Event_Name='test_event_name',
                                              Intervention_List=copy.deepcopy(intervention_list),
                                              Triggers=copy.deepcopy(triggers),
                                              Number_Repetitions=num_repetitions,
                                              Timesteps_Between_Repetitions=timestep_between_rep
                                              )

        event = self.save_campaignfile_and_load_event(intervention, "TriggeredCE_Repetitions_Event.json")
        ecc = event['Event_Coordinator_Config']
        self.assertEqual(ecc["Number_Repetitions"], num_repetitions)
        self.assertEqual(ecc["Timesteps_Between_Repetitions"], timestep_between_rep)

        for filename in test_files:
            shutil.move(filename, os.path.join(self.output_folder, filename))

    def test_triggered_campaign_event_delay(self):
        """
        StandardEventCoordinator --> NLHTI --> MultiInterventionDistrib --> List_Of_ DelayedInterventions --> List_Of ... Actual Interventions.
        Returns:

        """
        camp_filename = 'triggered_campaign_event_delay.json'
        delete_existing_file(camp_filename)
        triggers = ['GP_EVENT_002', 'GP_EVENT_003']

        intervention_list = [BroadcastEvent(camp)]
        intervention = TriggeredCampaignEvent(camp,
                                              Start_Day=50,
                                              Event_Name='test_event_name',
                                              Node_Ids=[3],
                                              Triggers=triggers,
                                              Intervention_List=copy.deepcopy(intervention_list),
                                              Delay=10)

        event = self.save_campaignfile_and_load_event(intervention, camp_filename)

        self.assertEqual(event['Start_Day'], 50)
        self.assertEqual(event['Nodeset_Config'], {
                "Node_List": [
                    3
                ],
                "class": "NodeSetNodeList"
            })
        ecc = event['Event_Coordinator_Config']
        self.assertEqual(ecc['class'], 'StandardInterventionDistributionEventCoordinator')
        # These two parameters are not used in TriggeredCampaignEvent() yet
        # self.assertEqual(ecc['Number_Repetitions'], 6)
        # self.assertEqual(ecc['Timesteps_Between_Repetitions'], 30)

        ic = ecc['Intervention_Config']
        self.assertEqual(ic['class'], 'NodeLevelHealthTriggeredIV')
        ac = ic['Actual_IndividualIntervention_Config']
        self.assertEqual(ac['class'], 'DelayedIntervention')
        delayed_ac = ac['Actual_IndividualIntervention_Configs'][0]
        self.assertTrue(delayed_ac.items() <=
                        intervention_list[0].items())
        self.assertEqual(delayed_ac['class'], 'BroadcastEvent')

        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_StandardDiagnostic_default(self):
        standard_diagnostic = StandardDiagnostic(camp)
        self.assertEqual(standard_diagnostic.Base_Sensitivity, 1)
        self.assertEqual(standard_diagnostic.Base_Specificity, 1)
        self.assertEqual(standard_diagnostic.Days_To_Diagnosis, 0)
        self.assertEqual(standard_diagnostic.Treatment_Fraction, 1)
        #self.assertEqual(standard_diagnostic.Event_Or_Config, "Config")
        self.assertTrue(standard_diagnostic.Intervention_Name == "SimpleDiagnostic" or
                        standard_diagnostic.Intervention_Name == "StandardDiagnostic")

        self.assertTrue(standard_diagnostic.Positive_Diagnosis_Config.Broadcast_Event == "GP_EVENT_005" or 
                        standard_diagnostic.Positive_Diagnosis_Config.Broadcast_Event == "PositiveResult" ) # GP_EVENT_004 for Malaria, PositiveResult elsewhere

        if standard_diagnostic.Intervention_Name == "SimpleDiagnostic":
            self.assertEqual(standard_diagnostic.Event_Trigger_Distributed, "NoTrigger")
            self.assertEqual(standard_diagnostic.Event_Trigger_Expired, "NoTrigger")

    def test_StandardDiagnostic_events(self):
        standard_diagnostic = StandardDiagnostic(camp, Positive_Diagnosis_Event="Births",
                                                 Event_Trigger_Distributed="NewInfection",
                                                 Event_Trigger_Expired="EveryUpdate")
        self.assertEqual(standard_diagnostic.Base_Sensitivity, 1)
        self.assertEqual(standard_diagnostic.Base_Specificity, 1)
        self.assertEqual(standard_diagnostic.Days_To_Diagnosis, 0)
        self.assertEqual(standard_diagnostic.Treatment_Fraction, 1)
        #self.assertEqual(standard_diagnostic.Event_Or_Config, "Config")
        self.assertTrue(standard_diagnostic.Intervention_Name == "SimpleDiagnostic" or
                        standard_diagnostic.Intervention_Name == "StandardDiagnostic")

        if standard_diagnostic.Intervention_Name == "SimpleDiagnostic":
            self.assertEqual(standard_diagnostic.Event_Trigger_Distributed, "NewInfection")
            self.assertEqual(standard_diagnostic.Event_Trigger_Expired, "EveryUpdate")

        self.assertEqual(standard_diagnostic.Positive_Diagnosis_Config.Broadcast_Event, "Births")

    def test_StandardDiagnostic_config(self):
        triggers = ['GP_EVENT_002', 'GP_EVENT_003']
        intervention_list = [BroadcastEvent(camp)]
        intervention = TriggeredCampaignEvent(camp,
                                              Start_Day=50,
                                              Event_Name='test_event_name',
                                              Node_Ids=[3],
                                              Triggers=triggers,
                                              Intervention_List=copy.deepcopy(intervention_list))

        standard_diagnostic = StandardDiagnostic(camp, Positive_Diagnosis_Intervention=intervention)
        self.assertEqual(standard_diagnostic.Base_Sensitivity, 1)
        self.assertEqual(standard_diagnostic.Base_Specificity, 1)
        self.assertEqual(standard_diagnostic.Days_To_Diagnosis, 0)
        self.assertEqual(standard_diagnostic.Treatment_Fraction, 1)
        self.assertEqual(standard_diagnostic.Event_Or_Config, "Config")
        self.assertTrue(standard_diagnostic.Intervention_Name == "SimpleDiagnostic" or
                        standard_diagnostic.Intervention_Name == "StandardDiagnostic")
        self.assertEqual(standard_diagnostic.Positive_Diagnosis_Config.Event_Coordinator_Config["class"], "StandardInterventionDistributionEventCoordinator")

    def test_campaign_delay_event(self):
        camp_filename = 'triggered_campaign_delay_event.json'
        delete_existing_file(camp_filename)
        
        start_day = 3
        trigger = 'NewInfection'
        broadcast_event = 'Blackout'
        intervention_list = [BroadcastEvent(camp, Event_Trigger=broadcast_event)]
        delay = {"Delay_Period_Exponential": 5}
        delay_intervention = triggered_campaign_delay_event(camp, start_day=start_day, trigger=trigger, 
                                                            delay=delay, intervention=intervention_list)
        event = self.save_campaignfile_and_load_event(delay_intervention, camp_filename)
        self.assertEqual(event['Start_Day'], start_day)

        ecc = event['Event_Coordinator_Config']
        self.assertEqual(ecc['class'], 'StandardInterventionDistributionEventCoordinator')

        ac = ecc['Intervention_Config']['Actual_IndividualIntervention_Config']
        self.assertEqual(ecc['Intervention_Config']['Trigger_Condition_List'], [trigger])
        self.assertEqual(ac['class'], 'DelayedIntervention')
        
        delayed_ac = ac['Actual_IndividualIntervention_Configs'][0][0]
        self.assertTrue(delayed_ac.items() <= intervention_list[0].items())
        self.assertEqual(delayed_ac['class'], 'BroadcastEvent')

        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_camp_send_receive(self):
        # Create NLHTI event
        # Create boradcast event
        # Make sure that all triggers of NLHTI event are in listening list
        # Make sure that all triggers of broadcast are in published list
        # Make sure all are formatted properly

        camp_filename = 'send_and_receive_camp.json'
        camp.reset()

        triggers = ['ExitedRelationship', 'EnteredRelationship']

        intervention = BroadcastEvent(camp, Event_Trigger = "ExitedRelationship")
        intervention_list = [BroadcastEvent(camp, Event_Trigger = "EnteredRelationship")]
        
        intervention2 = NLHTI(camp,
                             Triggers=triggers,
                             Interventions=intervention_list,
                             Demographic_Coverage=0.6,
                             Target_Age_Min=10,
                             Target_Age_Max=50,
                             Target_Gender="Female",
                             Target_Residents_Only=1,
                             Duration=20)
        # Publishing exited/entered relationship
        camp.add(intervention)

        # Listening for something1, something2, etc.
        camp.add(intervention2)
        camp.save(camp_filename)

        print(f"Check for valid campaign file at: {camp_filename}.")
        self.assertTrue(os.path.isfile(camp_filename))

        with open(camp_filename, 'r') as file:
            camp_event = json.load(file)['Events']
        self.assertEqual(len(camp_event), 2)
        
        self.assertEqual(camp.pubsub_signals_pubbing, ["ExitedRelationship", "EnteredRelationship"])
        self.assertEqual(camp.pubsub_signals_subbing, triggers)
        os.remove(camp_filename)

    def test_camp_reset(self):
        def save_file(camp):
            camp_filename = "reset_camp.json"
            camp.save(camp_filename)
            with open(camp_filename, 'r') as file:
                campaign = json.load(file)
            return campaign

        target_age_max = 81
        target_age_min = 5
        target_gender = "Male"


        intervention_list = [BroadcastEvent(camp)]

        camp.add(event=ScheduledCampaignEvent(camp, 1, [1, 3, 5], 
                 Target_Age_Min=target_age_min, 
                 Target_Age_Max=target_age_max, 
                 Target_Gender = target_gender, 
                 Intervention_List=intervention_list), 
                 first=True)

        campaign = save_file(camp)

        self.assertEqual(len(campaign['Events']), 1)
        event = campaign['Events'][0]
        event_coordinator = event["Event_Coordinator_Config"]
        self.assertEqual(event_coordinator["Target_Age_Max"], target_age_max)
        self.assertEqual(event_coordinator["Target_Age_Min"], target_age_min)
        self.assertEqual(event_coordinator["Target_Gender"], target_gender)

        camp.reset()

        campaign = save_file(camp)

        # Check that rest gets rid of events
        self.assertEqual(len(campaign['Events']), 0)
        camp.add(event=BroadcastEvent(camp))

        # Check that set schema gets rid of events and changes path name
        if camp.schema_path == "data/config/input_generic_schema.json":
            s2c.schema_cache = None
            camp.set_schema("data/config/input_malaria_schema.json")
            self.assertEqual(len(campaign['Events']), 0)

            self.assertEqual(camp.schema_path, "data/config/input_malaria_schema.json") # will only fail on generic run
            camp.schema_path = "data/config/input_generic_schema.json"
        
        os.remove("reset_camp.json")

    def test_trigger_format(self):
        # Testing that triggers input into SCE or TCE can switch between old and new format
        common.old_adhoc_trigger_style
        camp_filename = "TriggerFormatTest.json"
        triggers = ['EnteredRelationship', 'ExitedRelationship']

        # Checking special case of custom trigger in broadcast event with old format
        common.old_adhoc_trigger_style = True

        def check_value_error_raised():
            intervention = BroadcastEvent(camp, Event_Trigger = "Shazam")
            self.assertIn("Shazam", camp.get_adhocs())

        with self.assertRaises(ValueError) as context:
            check_value_error_raised()

        # Checking for proper formatting of triggers with old style (true) then new (false)
        for style in [True, False]:
            camp.reset()
            common.old_adhoc_trigger_style = style

            intervention = TriggeredCampaignEvent(camp,
                                                    Start_Day=50,
                                                    Event_Name='test_event_name',
                                                    Triggers=triggers,
                                                    Node_Ids=[3],
                                                    Intervention_List=[BroadcastEvent(camp, Event_Trigger = "ReceivedTreatment")],
                                                    Delay=10)

            camp.add(intervention)

            if not style:                
                intervention2 = ScheduledCampaignEvent(camp,
                                                Start_Day=30,
                                                Node_Ids=[1, 2],
                                                Number_Repetitions=3,
                                                Timesteps_Between_Repetitions=10,
                                                Demographic_Coverage=0.3,
                                                Intervention_List=[BroadcastEvent(camp, Event_Trigger = "ReceivedTreatment")])

                camp.add(intervention2)


            camp.save(camp_filename)

            with open(camp_filename, 'r') as file:
                camp_event = json.load(file)['Events']


            event1 = camp_event[0]
            ic1 = event1['Event_Coordinator_Config']['Intervention_Config']

            
            if style:
                self.assertEqual(ic1['Trigger_Condition_List'], triggers)
            else:
                event2 = camp_event[1]
                broadcast_event = event2['Event_Coordinator_Config']['Intervention_Config']['Broadcast_Event']
                self.assertEqual(ic1['Trigger_Condition_List'], triggers)
                self.assertEqual(broadcast_event, "ReceivedTreatment")


        common.old_adhoc_trigger_style = False
        camp.reset()

    def test_triggered_campaign_event_optional_delay(self):
        camp_filename = "optional_delay.json"
        start_day = 4
        triggers = ['GP_EVENT_000', 'GP_EVENT_001']
        iv_list = [BroadcastEvent(camp)]
        delay={"Delay_Period_Exponential": 5}
        duration = 10
        ip_target = {'Risk': 'High'}
        coverage = 0.8
        target_age_min = 0
        target_age_max = 80
        target_sex = "Male"
        target_residents_only = True
        blackout = False

        for delay in [{"Delay_Period_Exponential": 5}, False]:
            print(delay)
            if delay:
                event = common.triggered_campaign_event_with_optional_delay(camp, start_day, triggers, iv_list, delay, duration, ip_target,
                                                                        coverage, target_age_min, target_age_max, target_sex, target_residents_only,
                                                                        blackout)
            else:
                event = common.triggered_campaign_event_with_optional_delay(camp, start_day=start_day, triggers=triggers, intervention=iv_list, duration=duration, 
                                                                        ip_targeting=ip_target, coverage=coverage, target_age_min=target_age_min, target_age_max=target_age_max, 
                                                                        target_sex=target_sex, target_residents_only=target_residents_only, blackout=blackout)

            camp.add(event)
            camp.save(camp_filename)
            with open(camp_filename, 'r') as file:
                camp_event = json.load(file)['Events'][0]
            
            self.assertEqual(event['Start_Day'], start_day)
            ic = event["Event_Coordinator_Config"]["Intervention_Config"]
            self.assertEqual(ic["Demographic_Coverage"], coverage)
            self.assertEqual(ic["Trigger_Condition_List"], triggers)
            if delay:
                self.assertEqual(ic["Actual_IndividualIntervention_Config"]["Actual_IndividualIntervention_Configs"][0][0]["class"], "BroadcastEvent")
                self.assertEqual(ic["Actual_IndividualIntervention_Config"]["Delay_Period_Distribution"], "EXPONENTIAL_DISTRIBUTION")
                self.assertEqual(ic["Actual_IndividualIntervention_Config"]["Delay_Period_Exponential"], 5)

            else:
                self.assertEqual(ic["Actual_IndividualIntervention_Config"][0]["class"], "BroadcastEvent")
            self.assertEqual(ic["Duration"], duration)
            self.assertEqual(ic["Property_Restrictions"], ["Risk:High"])
            self.assertEqual(ic["Target_Age_Max"], target_age_max)
            self.assertEqual(ic["Target_Age_Min"], target_age_min)
            self.assertEqual(ic["Target_Gender"], target_sex)
            self.assertEqual(ic["Target_Residents_Only"], target_residents_only)
        os.remove(camp_filename) # comment out to save camp file
    
    def test_property_restrictions(self):
        camp_filename = 'prop_restrictions.json'
        delete_existing_file(camp_filename)

        intervention_list = [BroadcastEvent(camp)]
        # Ensuring that the property restrictions are properly formatted
        
        properties = [
                {'Risk': 'High'},
                "Risk:High",
                {"Thing": "High", "Thing2": "Low" },
                [  { "Thing": "High"}, { "Thing2": "Low"} ],
                "Risk=High",
                ["Risk=High"],
                ["Risk:High"],
                ["Thing:High", "Thing2:Low"],
                ""]
        triggers = ['GP_EVENT_000', 'GP_EVENT_001']
        
        for index, prop in enumerate(properties):
            camp.reset()
            intervention_list = [BroadcastEvent(camp)]
            intervention = NLHTI(camp,
                             Triggers=copy.deepcopy(triggers),
                             Interventions=copy.deepcopy(intervention_list),
                             Property_Restrictions=prop,
                             Demographic_Coverage=0.6,
                             Target_Age_Min=10,
                             Target_Age_Max=50,
                             Target_Gender="Female",
                             Target_Residents_Only=1,
                             Duration=20)
            event = self.save_campaignfile_and_load_event(intervention, camp_filename)

            
            if index < 2 or index in [4, 5, 6]:
                self.assertEqual(event['Property_Restrictions'], ['Risk:High'],  msg=f"{prop} is being formatted as {event['Property_Restrictions']} and {index}")
            elif index in [2, 7]:
                self.assertEqual(event['Property_Restrictions'], ['Thing:High','Thing2:Low'],  msg=f"{prop} is being formatted as {event['Property_Restrictions']}")
            elif index == 3:
                self.assertEqual(event['Property_Restrictions_Within_Node'], [{'Thing':'High'},{'Thing2':'Low'}],  msg=f"{prop} is being formatted as {event['Property_Restrictions_Within_Node']}")
            else:
                self.assertEqual(len(event['Property_Restrictions']), 0,  msg=f"{prop} is being formatted as {event['Property_Restrictions']}")

        os.remove(camp_filename)

    def test_property_value_changer_defaults(self):
        camp_filename = 'property_value_changer.json'
        delete_existing_file(camp_filename)

        target_property_key = 'Risk'
        target_property_value = 'High'
        daily_probability=1.0
        maximum_dur=1.0
        revert=0
        intervention = PropertyValueChanger(camp,
                                            target_property_key,
                                            target_property_value,
                                            )

        event = self.save_campaignfile_and_load_event(intervention, camp_filename)

        self.assertEqual(event['class'], "PropertyValueChanger")
        self.assertEqual(event['Maximum_Duration'], maximum_dur)
        self.assertEqual(event['Daily_Probability'], daily_probability)
        self.assertEqual(event['New_Property_Value'], "")
        self.assertEqual(event['Target_Property_Key'], target_property_key)
        self.assertEqual(event['Target_Property_Value'], target_property_value)
        self.assertEqual(event['Revert'], revert)

        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_triggered_individual_prop_by_age(self):
        camp_filename = 'change_prop.json'
        delete_existing_file(camp_filename)
        new_ip_key = "Risk"
        new_ip_value = "Low"
        change_age_in_days = 100
        revert_in_days = 10
        ip_targeting_key = "Risk"
        ip_targeting_value = "High"

        intervention = change_individual_property_at_age(camp, new_ip_key=new_ip_key, new_ip_value=new_ip_value, change_age_in_days=change_age_in_days, revert_in_days=revert_in_days, ip_targeting_key=ip_targeting_key, ip_targeting_value=ip_targeting_value)
        event = self.save_campaignfile_and_load_event(intervention, camp_filename)

        ec = event['Event_Coordinator_Config']
        ic = ec["Intervention_Config"]
        aic = ic["Actual_IndividualIntervention_Config"]
        ai_config = aic["Actual_IndividualIntervention_Configs"][0]

        self.assertEqual(ai_config["Target_Property_Key"], new_ip_key)
        self.assertEqual(ai_config["Target_Property_Value"], new_ip_value)
        self.assertEqual(ai_config["New_Property_Value"], "")


        self.assertEqual(ic["Property_Restrictions"], [f"{ip_targeting_key}:{ip_targeting_value}"])
        self.assertEqual(ai_config["Maximum_Duration"], 1)
        self.assertEqual(ai_config["Revert"], revert_in_days)
        self.assertEqual(ai_config["class"], "PropertyValueChanger")
        
        self.assertEqual(aic["Delay_Period_Distribution"], "CONSTANT_DISTRIBUTION")        
        self.assertEqual(aic["Delay_Period_Constant"], change_age_in_days)
        self.assertEqual(aic["class"], "DelayedIntervention")

        shutil.move(camp_filename, os.path.join(self.output_folder, camp_filename))

    def test_change_individual_property_scheduled(self):
        camp_filename = 'change_prop_scheduled.json'
        delete_existing_file(camp_filename)
        new_ip_key = "Risk"
        new_ip_value = "High"
        start_day = 10
        number_repetitions = 2
        timesteps_between_reps = 3
        node_ids = [1,2]
        daily_prob = 0.8
        max_duration = 10
        revert_in_days = 20
        ip_restrictions = {'Risk': 'Low'}
        coverage = 0.7
        target_age_min = 5
        target_age_max = 30
        target_sex = "Male"
        target_residents_only = True

        camp.reset()
        change_individual_property_scheduled(camp, new_ip_key=new_ip_key, new_ip_value=new_ip_value, start_day=start_day, number_repetitions=number_repetitions,
                                                            timesteps_between_reps=timesteps_between_reps, node_ids=node_ids, daily_prob=daily_prob, max_duration=max_duration,
                                                            revert_in_days=revert_in_days, ip_restrictions=ip_restrictions, coverage=coverage, target_age_min=target_age_min,
                                                            target_age_max=target_age_max, target_sex=target_sex, target_residents_only=target_residents_only)
        
        camp.save(camp_filename)
        with open(camp_filename, 'r') as file:
            camp_event = json.load(file)['Events'][0]
        print(camp_event)

        intervention = camp_event["Event_Coordinator_Config"]["Intervention_Config"]
        self.assertEqual(intervention["Daily_Probability"], daily_prob)
        self.assertEqual(intervention["Maximum_Duration"], max_duration)
        self.assertEqual(intervention["Revert"], revert_in_days)
        self.assertEqual(intervention["Target_Property_Key"], "Risk")
        self.assertEqual(intervention["Target_Property_Value"], "High")
        self.assertEqual(intervention["class"], "PropertyValueChanger")
        self.assertEqual(camp_event["Start_Day"], start_day)

        ec = camp_event["Event_Coordinator_Config"]
        self.assertEqual(ec["Demographic_Coverage"], coverage)
        self.assertEqual(ec["Number_Repetitions"], number_repetitions)
        self.assertEqual(ec["Property_Restrictions"], ["Risk:Low"])
        self.assertEqual(ec["Target_Age_Max"], target_age_max)
        self.assertEqual(ec["Target_Age_Min"], target_age_min)
        self.assertEqual(ec["Target_Gender"], target_sex)
        self.assertEqual(ec["Target_Residents_Only"], target_residents_only)
        self.assertEqual(ec["Timesteps_Between_Repetitions"], timesteps_between_reps)
        self.assertEqual(camp_event['Nodeset_Config'], {
                "Node_List": [
                    1,
                    2
                ],
                "class": "NodeSetNodeList"
            })  

    def test_change_individual_property_triggered(self):
        camp_filename = 'change_prop_scheduled.json'
        delete_existing_file(camp_filename)
        new_ip_key = "Risk"
        new_ip_value = "High"
        start_day = 10
        node_ids = [1,2]
        daily_prob = 0.8
        max_duration = 10
        revert_in_days = 20
        ip_restrictions = {'Risk': 'Low'}
        coverage = 0.7
        target_age_min = 5
        target_age_max = 30
        target_sex = "Male"
        target_residents_only = True
        delay=2
        listening_duration=5
        blackout=False
        check_at_trigger = True
        triggers = ['GP_EVENT_000', 'GP_EVENT_001']

        for delay in [{"Delay_Period_Exponential": 5}, False]:
            camp.reset()
            if delay:
                common.change_individual_property_triggered(camp, triggers=triggers, new_ip_key=new_ip_key, new_ip_value=new_ip_value, start_day=start_day,
                                                            daily_prob=daily_prob, max_duration=max_duration,  revert_in_days= revert_in_days, node_ids=node_ids,
                                                            ip_restrictions=ip_restrictions, coverage=coverage, target_age_min=target_age_min, target_age_max=target_age_max,
                                                            target_sex=target_sex, target_residents_only=target_residents_only, delay=delay, listening_duration=listening_duration,
                                                            blackout=blackout, check_at_trigger=check_at_trigger)
            else:
                common.change_individual_property_triggered(camp, triggers=triggers, new_ip_key=new_ip_key, new_ip_value=new_ip_value, start_day=start_day,
                                                            daily_prob=daily_prob, max_duration=max_duration,  revert_in_days= revert_in_days, node_ids=node_ids,
                                                            ip_restrictions=ip_restrictions, coverage=coverage, target_age_min=target_age_min, target_age_max=target_age_max,
                                                            target_sex=target_sex, target_residents_only=target_residents_only, listening_duration=listening_duration,
                                                            blackout=blackout, check_at_trigger=check_at_trigger)

            camp.save(camp_filename)
            with open(camp_filename, 'r') as file:
                event = json.load(file)['Events'][0]


            self.assertEqual(event['Start_Day'], start_day)
            ic = event["Event_Coordinator_Config"]["Intervention_Config"]
            if delay:
                intervention = ic["Actual_IndividualIntervention_Config"]["Actual_IndividualIntervention_Configs"][0]
            else:
                intervention = ic["Actual_IndividualIntervention_Config"]
            self.assertEqual(ic["Demographic_Coverage"], coverage)
            self.assertEqual(ic["Trigger_Condition_List"], triggers)
            if delay:
                self.assertEqual(intervention["class"], "PropertyValueChanger")
                self.assertEqual(ic["Actual_IndividualIntervention_Config"]["Delay_Period_Distribution"], "EXPONENTIAL_DISTRIBUTION")
                self.assertEqual(ic["Actual_IndividualIntervention_Config"]["Delay_Period_Exponential"], 5)

            else:
                self.assertEqual(intervention["class"], "PropertyValueChanger")
            self.assertEqual(intervention["Maximum_Duration"], max_duration)
            self.assertEqual(ic["Property_Restrictions"], ["Risk:Low"])
            self.assertEqual(ic["Target_Age_Max"], target_age_max)
            self.assertEqual(ic["Target_Age_Min"], target_age_min)
            self.assertEqual(ic["Target_Gender"], target_sex)
            self.assertEqual(ic["Target_Residents_Only"], target_residents_only)

            # testing specifically for property value changer intervention
            self.assertEqual(intervention["Daily_Probability"], daily_prob)
            self.assertEqual(intervention["Maximum_Duration"], max_duration)
            self.assertEqual(intervention["Revert"], revert_in_days)
            self.assertEqual(intervention["Target_Property_Key"], "Risk")
            self.assertEqual(intervention["Target_Property_Value"], "High")
            self.assertEqual(intervention["class"], "PropertyValueChanger")

class CommonInterventionTestMalaria(CommonInterventionTest):
    def setUp(self):
        super(CommonInterventionTestMalaria, self).setUp()
        camp.schema_path = schema_path_malaria

    def test_standard_diagnostic(self):
        # Shouldn't expect same result with malaria schema, might add additional checks later
        pass

    def test_trigger_format(self):
        # Shouldn't be the same
        pass


if __name__ == '__main__':
    unittest.main()
