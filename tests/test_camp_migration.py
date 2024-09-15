import emod_api.interventions.migration as migration
from emod_api import campaign as camp
import emod_api.interventions.utils as utils
import copy
from camp_test import CampaignTest
import unittest


class MigrationTest(CampaignTest):
    def test_new_migration_event(self):
        duration_at_node_constant = 100
        duration_before_leaving_constant = 0
        nodeid_to_migrate_to = 5

        intervention = migration._new_migration_intervention(camp,
                                                             duration_at_node_constant=duration_at_node_constant,
                                                             duration_at_node_distribution="CONSTANT_DISTRIBUTION",
                                                             duration_before_leaving_constant=duration_before_leaving_constant,
                                                             duration_before_leaving_distribution="CONSTANT_DISTRIBUTION",
                                                             nodeid_to_migrate_to=nodeid_to_migrate_to)

        self.assertEqual(intervention["class"], "MigrateIndividuals")
        self.assertEqual(intervention["Duration_At_Node_Constant"], duration_at_node_constant)
        self.assertEqual(intervention["Duration_At_Node_Distribution"], "CONSTANT_DISTRIBUTION")
        self.assertEqual(intervention["Duration_Before_Leaving_Constant"], duration_before_leaving_constant)
        self.assertEqual(intervention["Duration_Before_Leaving_Distribution"], "CONSTANT_DISTRIBUTION")
        self.assertEqual(intervention["NodeID_To_Migrate_To"], nodeid_to_migrate_to)

    def test_add_migration_event_Triggered(self):
        start_day = 12
        trigger_condition_list = ["Births", "EveryUpdate"]
        nodeto = 5
        duration_at_node = {"Duration_At_Node_Constant": 3}
        duration_before_leaving = {"Duration_Before_Leaving_Constant": 4}
        nodes_from = [1, 2]
        target_age={"agemin": 13, "agemax": 77}

        camp.reset()
        migration.add_migration_event(camp,
                                      nodeto,
                                      start_day=start_day,
                                      trigger_condition_list=copy.deepcopy(trigger_condition_list),
                                      duration_at_node=duration_at_node,
                                      duration_before_leaving=duration_before_leaving,
                                      nodes_from_ids=nodes_from,
                                      target_age=target_age
                                      )

        migration_event = camp.campaign_dict["Events"][0]
        self.assertEqual(migration_event["class"], "CampaignEvent")
        self.assertEqual(migration_event["Start_Day"], start_day)

        event_coordinator_config = migration_event["Event_Coordinator_Config"]
        self.assertEqual(event_coordinator_config["class"], "StandardInterventionDistributionEventCoordinator")

        intervention_config = event_coordinator_config.get("Intervention_Config")
        self.assertIsNotNone(intervention_config.get("Actual_IndividualIntervention_Config"))
        self.assertListEqual(intervention_config["Trigger_Condition_List"], trigger_condition_list)
        self.assertEqual(intervention_config["class"], "NodeLevelHealthTriggeredIV")
        self.assertEqual(intervention_config["Target_Gender"], "All")
        self.assertEqual(intervention_config["Target_Age_Min"], 13)
        self.assertEqual(intervention_config["Target_Age_Max"], 77)

        actual_intervention_config = intervention_config["Actual_IndividualIntervention_Config"]["Actual_IndividualIntervention_Configs"][0]
        self.assertEqual(actual_intervention_config["Duration_At_Node_Constant"], 3)
        self.assertEqual(actual_intervention_config["Duration_Before_Leaving_Constant"], 4)

        nodeset_config = migration_event["Nodeset_Config"]
        self.assertEqual(nodeset_config["class"], "NodeSetNodeList")
        self.assertEqual(nodeset_config["Node_List"], nodes_from)

    def test_add_migration_event_Scheduled(self):
        start_day = 12
        nodeto = 5
        duration_at_node = {"Duration_At_Node_Constant": 3}
        duration_before_leaving = {"Duration_Before_Leaving_Constant": 4}
        nodes_from = [1, 2]
        target_gender = "Everyone"

        camp.reset()
        migration.add_migration_event(camp,
                                      nodeto,
                                      start_day=start_day,
                                      duration_at_node=duration_at_node,
                                      duration_before_leaving=duration_before_leaving,
                                      nodes_from_ids=nodes_from,
                                      target_age=target_gender
                                      )

        migration_event = camp.campaign_dict["Events"][0]
        self.assertEqual(migration_event["class"], "CampaignEvent")
        self.assertEqual(migration_event["Start_Day"], start_day)

        event_coordinator_config = migration_event["Event_Coordinator_Config"]
        self.assertEqual(event_coordinator_config["class"], "StandardInterventionDistributionEventCoordinator")

        intervention_config = event_coordinator_config.get("Intervention_Config")
        self.assertIsNone(intervention_config.get("Actual_IndividualIntervention_Config"))
        #self.assertEqual(intervention_config["class"], "MultiInterventionDistributor")

        intervention_list_zero = intervention_config
        self.assertEqual(intervention_list_zero["class"], "MigrateIndividuals")
        self.assertEqual(intervention_list_zero["Duration_At_Node_Constant"], 3)
        self.assertEqual(intervention_list_zero["Duration_Before_Leaving_Constant"], 4)

        nodeset_config = migration_event["Nodeset_Config"]
        self.assertEqual(nodeset_config["class"], "NodeSetNodeList")
        self.assertEqual(nodeset_config["Node_List"], nodes_from)


if __name__ == '__main__':
    unittest.main()

        
