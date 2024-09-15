from .. import schema_to_class as s2c
from emod_api.interventions.common import ScheduledCampaignEvent, TriggeredCampaignEvent
from typing import List


def _new_migration_intervention(camp,
                                duration_at_node_constant: float = None,
                                duration_at_node_distribution: str = None,
                                duration_at_node_exponential: float = None,
                                duration_at_node_gaussian_mean: float = None,
                                duration_at_node_gaussian_std_dev: float = None,
                                duration_at_node_kappa: float = None,
                                duration_at_node_lambda: float = None,
                                duration_at_node_log_normal_mu: float = None,
                                duration_at_node_log_normal_sigma: float = None,
                                duration_at_node_max: float = None,
                                duration_at_node_mean_1: float = None,
                                duration_at_node_mean_2: float = None,
                                duration_at_node_min: float = None,
                                duration_at_node_peak_2_value: float = None,
                                duration_at_node_poisson_mean: float = None,
                                duration_at_node_proportion_0: float = None,
                                duration_at_node_proportion_1: float = None,
                                duration_before_leaving_constant: float = None,
                                duration_before_leaving_distribution:	str = None,
                                duration_before_leaving_exponential: float = None,
                                duration_before_leaving_gaussian_mean: float = None,
                                duration_before_leaving_gaussian_std_dev: float = None,
                                duration_before_leaving_kappa: float = None,
                                duration_before_leaving_lambda: float = None,
                                duration_before_leaving_log_normal_mu: float = None,
                                duration_before_leaving_log_normal_sigma: float = None,
                                duration_before_leaving_max: float = None,
                                duration_before_leaving_mean_1: float = None,
                                duration_before_leaving_mean_2: float = None,
                                duration_before_leaving_min: float = None,
                                duration_before_leaving_peak_2_value: float = None,
                                duration_before_leaving_poisson_mean: float = None,
                                duration_before_leaving_proportion_0: float = None,
                                duration_before_leaving_proportion_1: float = None,
                                intervention_name: str = None,
                                is_moving: bool = None,
                                new_property_value: str = None,
                                nodeid_to_migrate_to: int = None):

    iv_name = "MigrateIndividuals"
    coordinator = s2c.get_class_with_defaults("StandardEventCoordinator", camp.schema_path)
    if coordinator is None:
        print("s2c.get_class_with_defaults returned None. Maybe no schema.json was provided.")
        return ""

    intervention = s2c.get_class_with_defaults(iv_name, camp.schema_path)

    intervention.Duration_At_Node_Constant = duration_at_node_constant
    intervention.Duration_At_Node_Distribution = duration_at_node_distribution
    intervention.Duration_At_Node_Exponential = duration_at_node_exponential
    intervention.Duration_At_Node_Gaussian_Mean = duration_at_node_gaussian_mean
    intervention.Duration_At_Node_Gaussian_Std_Dev = duration_at_node_gaussian_std_dev
    intervention.Duration_At_Node_Kappa = duration_at_node_kappa
    intervention.Duration_At_Node_Lambda = duration_at_node_lambda
    intervention.Duration_At_Node_Log_Normal_Mu = duration_at_node_log_normal_mu
    intervention.Duration_At_Node_Log_Normal_Sigma = duration_at_node_log_normal_sigma
    intervention.Duration_At_Node_Max = duration_at_node_max
    intervention.Duration_At_Node_Mean_1 = duration_at_node_mean_1
    intervention.Duration_At_Node_Mean_2 = duration_at_node_mean_2
    intervention.Duration_At_Node_Min = duration_at_node_min
    intervention.Duration_At_Node_Peak_2_Value = duration_at_node_peak_2_value
    intervention.Duration_At_Node_Poisson_Mean = duration_at_node_poisson_mean
    intervention.Duration_At_Node_Proportion_0 = duration_at_node_proportion_0
    intervention.Duration_At_Node_Proportion_1 = duration_at_node_proportion_1
    intervention.Duration_Before_Leaving_Constant = duration_before_leaving_constant
    intervention.Duration_Before_Leaving_Distribution = duration_before_leaving_distribution
    intervention.Duration_Before_Leaving_Exponential = duration_before_leaving_exponential
    intervention.Duration_Before_Leaving_Gaussian_Mean = duration_before_leaving_gaussian_mean
    intervention.Duration_Before_Leaving_Gaussian_Std_Dev = duration_before_leaving_gaussian_std_dev
    intervention.Duration_Before_Leaving_Kappa = duration_before_leaving_kappa
    intervention.Duration_Before_Leaving_Lambda = duration_before_leaving_lambda
    intervention.Duration_Before_Leaving_Log_Normal_Mu = duration_before_leaving_log_normal_mu
    intervention.Duration_Before_Leaving_Log_Normal_Sigma = duration_before_leaving_log_normal_sigma
    intervention.Duration_Before_Leaving_Max = duration_before_leaving_max
    intervention.Duration_Before_Leaving_Mean_1 = duration_before_leaving_mean_1
    intervention.Duration_Before_Leaving_Mean_2 = duration_before_leaving_mean_2
    intervention.Duration_Before_Leaving_Min = duration_before_leaving_min
    intervention.Duration_Before_Leaving_Peak_2_Value = duration_before_leaving_peak_2_value
    intervention.Duration_Before_Leaving_Poisson_Mean = duration_before_leaving_poisson_mean
    intervention.Duration_Before_Leaving_Proportion_0 = duration_before_leaving_proportion_0
    intervention.Duration_Before_Leaving_Proportion_1 = duration_before_leaving_proportion_1
    intervention.Intervention_Name = intervention_name
    intervention.Is_Moving = is_moving
    intervention.New_Property_Value = new_property_value
    intervention.NodeID_To_Migrate_To = nodeid_to_migrate_to
    return intervention


def add_migration_event(camp, nodeto,
                        start_day: int = 0,
                        coverage: float = 1,
                        repetitions: int = 1,
                        tsteps_btwn: int = 365,
                        duration_at_node: dict = None,
                        duration_before_leaving: dict = None,
                        target_age: dict = None,
                        nodes_from_ids: List[int] = None,
                        ind_property_restrictions=None,
                        node_property_restrictions=None,
                        triggered_campaign_delay=0,
                        trigger_condition_list=None,
                        listening_duration=-1):
    """Add a migration event to a campaign that moves individuals from one node to another.

    Args:
        camp: emod_api.campaign object with schema_path set.
        nodeto: The NodeID that the individuals will travel to.
        start_day: A day when intervention is distributed
        coverage: The proportion of the population covered by the intervention
        repetitions: The number of times to repeat the intervention
        tsteps_btwn: The number of time steps between repetitions.
        duration_before_leaving: Dictionary of parameters that define the distribution for duration before leaving node,
            including the distribution.
            Durations are in days.
            Examples:
                {"Duration_Before_Leaving_Distribution":"GAUSSIAN_DISTRIBUTION",
                "Duration_Before_Leaving_Gaussian_Mean": 14, "Duration_Before_Leaving_Gaussian_Std_Dev" 3}
                {"Duration_Before_Leaving_Distribution":"POISSON_DISTRIBUTION",
                "Duration_Before_Leaving_Poisson_Mean" 30}
        duration_at_node: Dictionary of parameters that define the distribution for duration at node,
            including the distribution
            Durations are in days.
            Examples:
                {"Duration_At_Node_Distribution":"GAUSSIAN_DISTRIBUTION",
                "Duration_At_Node_Gaussian_Mean": 14, "Duration_At_Node_Gaussian_Std_Dev" 3}
                {"Duration_At_Node_Distribution":"POISSON_DISTRIBUTION", "Duration_At_Node_Poisson_Mean" 30}
        target_age: The individuals to target with the intervention. To
            restrict by age, provide a dictionary of {'agemin' : x, 'agemax' :
            y}. Default is targeting everyone.
        nodes_from_ids: The list of node ids to apply this intervention to.
        ind_property_restrictions: The IndividualProperty key:value pairs
            that individuals must have to receive the intervention
            (**Property_Restrictions_Within_Node** parameter). In the format
            ``[{"BitingRisk":"High"}, {"IsCool":"Yes}]``.
        node_property_restrictions: The NodeProperty key:value pairs that
            nodes must have to receive the intervention. In the format
            ``[{"Place":"RURAL"}, {"ByALake":"Yes}]``.
        triggered_campaign_delay: After the trigger is received, the number of
            time steps until distribution starts. Eligibility of people or nodes
            for the campaign is evaluated on the start day, not the triggered
            day.
        trigger_condition_list: A list of the events that will trigger the intervention.
            If included, **start_days** is then used to distribute **NodeLevelHealthTriggeredIV**.
        listening_duration: The number of time steps that the distributed
            event will monitor for triggers. Default is -1, which is
            indefinitely.

    Returns:
        None

    Example:
        from emod_api import campaign as camp
        dan = {"Duration_At_Node_Distribution":"POISSON_DISTRIBUTION", "Duration_At_Node_Poisson_Mean" 30}
        dbl = {"Duration_Before_Leaving_Distribution":"GAUSSIAN_DISTRIBUTION",
        "Duration_Before_Leaving_Gaussian_Mean": 14, "Duration_Before_Leaving_Gaussian_Std_Dev" 3}

        add_migration_event(camp, nodeto=5, start_day=1, coverage=0.75, duration_at_node = dan,
            duration_before_leaving = dbl,
            repetitions=1, tsteps_btwn=90,
            target='Everyone', nodesfrom={"class": "NodeSetAll"},
            node_property_restrictions=[{"Place": "Rural"}])

    """
    
    if target_age is not None and all([k in target_age for k in ['agemin', 'agemax']]):
        target_age_min = target_age["agemin"]
        target_age_max = target_age["agemax"]
    else:
        target_age_min = 0
        target_age_max = 125*365

    duration_at_node = {} if duration_at_node is None else duration_at_node
    duration_before_leaving = {} if duration_before_leaving is None else duration_before_leaving

    duration_at_node_constant = duration_at_node.get("Duration_At_Node_Constant")
    duration_at_node_distribution = duration_at_node.get("Duration_At_Node_Distribution")
    duration_at_node_exponential = duration_at_node.get("Duration_At_Node_Exponential")
    duration_at_node_gaussian_mean = duration_at_node.get("Duration_At_Node_Gaussian_Mean")
    duration_at_node_gaussian_std_dev = duration_at_node.get("Duration_At_Node_Gaussian_Std_Dev")
    duration_at_node_kappa = duration_at_node.get("Duration_At_Node_Kappa")
    duration_at_node_lambda = duration_at_node.get("Duration_At_Node_Lambda")
    duration_at_node_log_normal_mu = duration_at_node.get("Duration_At_Node_Log_Normal_Mu")
    duration_at_node_log_normal_sigma = duration_at_node.get("Duration_At_Node_Log_Normal_Sigma")
    duration_at_node_max = duration_at_node.get("Duration_At_Node_Max")
    duration_at_node_mean_1 = duration_at_node.get("Duration_At_Node_Mean_1")
    duration_at_node_mean_2 = duration_at_node.get("Duration_At_Node_Mean_2")
    duration_at_node_min = duration_at_node.get("Duration_At_Node_Min")
    duration_at_node_peak_2_value = duration_at_node.get("Duration_At_Node_Peak_2_Value")
    duration_at_node_poisson_mean = duration_at_node.get("Duration_At_Node_Poisson_Mean")
    duration_at_node_proportion_0 = duration_at_node.get("Duration_At_Node_Proportion_0")
    duration_at_node_proportion_1 = duration_at_node.get("Duration_At_Node_Proportion_1")
    
    duration_before_leaving_constant = duration_before_leaving.get("Duration_Before_Leaving_Constant") 
    duration_before_leaving_distribution = duration_before_leaving.get("Duration_Before_Leaving_Distribution") 
    duration_before_leaving_exponential = duration_before_leaving.get("Duration_Before_Leaving_Exponential") 
    duration_before_leaving_gaussian_mean = duration_before_leaving.get("Duration_Before_Leaving_Gaussian_Mean")
    duration_before_leaving_gaussian_std_dev = duration_before_leaving.get("Duration_Before_Leaving_Gaussian_Std_Dev")
    duration_before_leaving_kappa = duration_before_leaving.get("Duration_Before_Leaving_Kappa") 
    duration_before_leaving_lambda = duration_before_leaving.get("Duration_Before_Leaving_Lambda") 
    duration_before_leaving_log_normal_mu = duration_before_leaving.get("Duration_Before_Leaving_Log_Normal_Mu")
    duration_before_leaving_log_normal_sigma = duration_before_leaving.get("Duration_Before_Leaving_Log_Normal_Sigma")
    duration_before_leaving_max = duration_before_leaving.get("Duration_Before_Leaving_Max") 
    duration_before_leaving_mean_1 = duration_before_leaving.get("Duration_Before_Leaving_Mean_1") 
    duration_before_leaving_mean_2 = duration_before_leaving.get("Duration_Before_Leaving_Mean_2") 
    duration_before_leaving_min = duration_before_leaving.get("Duration_Before_Leaving_Min") 
    duration_before_leaving_peak_2_value = duration_before_leaving.get("Duration_Before_Leaving_Peak_2_Value")
    duration_before_leaving_poisson_mean = duration_before_leaving.get("Duration_Before_Leaving_Poisson_Mean")
    duration_before_leaving_proportion_0 = duration_before_leaving.get("Duration_Before_Leaving_Proportion_0") 
    duration_before_leaving_proportion_1 = duration_before_leaving.get("Duration_Before_Leaving_Proportion_1")

    intervention_migration = _new_migration_intervention(camp,
                                                         duration_at_node_constant=duration_at_node_constant,
                                                         duration_at_node_distribution=duration_at_node_distribution,
                                                         duration_at_node_exponential=duration_at_node_exponential,
                                                         duration_at_node_gaussian_mean=duration_at_node_gaussian_mean,
                                                         duration_at_node_gaussian_std_dev=duration_at_node_gaussian_std_dev,
                                                         duration_at_node_kappa=duration_at_node_kappa,
                                                         duration_at_node_lambda=duration_at_node_lambda,
                                                         duration_at_node_log_normal_mu=duration_at_node_log_normal_mu,
                                                         duration_at_node_log_normal_sigma=duration_at_node_log_normal_sigma,
                                                         duration_at_node_max=duration_at_node_max,
                                                         duration_at_node_mean_1=duration_at_node_mean_1,
                                                         duration_at_node_mean_2=duration_at_node_mean_2,
                                                         duration_at_node_min=duration_at_node_min,
                                                         duration_at_node_peak_2_value=duration_at_node_peak_2_value,
                                                         duration_at_node_poisson_mean=duration_at_node_poisson_mean,
                                                         duration_at_node_proportion_0=duration_at_node_proportion_0,
                                                         duration_at_node_proportion_1=duration_at_node_proportion_1,
                                                         duration_before_leaving_constant=duration_before_leaving_constant,
                                                         duration_before_leaving_distribution=duration_before_leaving_distribution,
                                                         duration_before_leaving_exponential=duration_before_leaving_exponential,
                                                         duration_before_leaving_gaussian_mean=duration_before_leaving_gaussian_mean,
                                                         duration_before_leaving_gaussian_std_dev=duration_before_leaving_gaussian_std_dev,
                                                         duration_before_leaving_kappa=duration_before_leaving_kappa,
                                                         duration_before_leaving_lambda=duration_before_leaving_lambda,
                                                         duration_before_leaving_log_normal_mu=duration_before_leaving_log_normal_mu,
                                                         duration_before_leaving_log_normal_sigma=duration_before_leaving_log_normal_sigma,
                                                         duration_before_leaving_max=duration_before_leaving_max,
                                                         duration_before_leaving_mean_1=duration_before_leaving_mean_1,
                                                         duration_before_leaving_mean_2=duration_before_leaving_mean_2,
                                                         duration_before_leaving_min=duration_before_leaving_min,
                                                         duration_before_leaving_peak_2_value=duration_before_leaving_peak_2_value,
                                                         duration_before_leaving_poisson_mean=duration_before_leaving_poisson_mean,
                                                         duration_before_leaving_proportion_0=duration_before_leaving_proportion_0,
                                                         duration_before_leaving_proportion_1=duration_before_leaving_proportion_1,
                                                         nodeid_to_migrate_to=nodeto)

    if trigger_condition_list:
        tce_migration = TriggeredCampaignEvent(camp, start_day, "Event_Name", trigger_condition_list,
                                               Intervention_List=[intervention_migration],
                                               Node_Property_Restrictions=node_property_restrictions,
                                               Property_Restrictions=ind_property_restrictions,
                                               Demographic_Coverage=coverage,
                                               Number_Repetitions=repetitions,
                                               Timesteps_Between_Repetitions=tsteps_btwn,
                                               Node_Ids=nodes_from_ids,
                                               Delay=triggered_campaign_delay,
                                               Target_Age_Min=target_age_min,
                                               Target_Age_Max=target_age_max,
                                               Duration=listening_duration)
        camp.add(tce_migration)
    else:
        sce_migration = ScheduledCampaignEvent(camp, start_day,
                                               Node_Ids=nodes_from_ids,
                                               Number_Repetitions=repetitions,
                                               Timesteps_Between_Repetitions=tsteps_btwn,
                                               Property_Restrictions=ind_property_restrictions,
                                               Demographic_Coverage=coverage,
                                               Intervention_List=[intervention_migration],
                                               Target_Age_Min=target_age_min,
                                               Target_Age_Max=target_age_max
                                               )
        camp.add(sce_migration)
