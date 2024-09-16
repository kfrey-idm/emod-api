"""  file that has various utility functions that are general to EMOD"""
from emod_api.schema_to_class import ReadOnlyDict

class Distributions:
    """
    Class with methods that return the configured distribution dictionaries. It is up to user to pipe the parameters
    to correct prefix variables. For example, if your variable names are 'Sample_Size_Distribution' etc. then you would
    add the prefix 'Sample_Size with the trailing underscore' to the keys of the dictionary to add to campaign/config
    and pass to EMOD.

    """

    @staticmethod
    def constant(constant: float) -> dict:
        """
            This function configures and returns dictionary of the parameters for CONSTANT_DISTRIBUTION.

        Args:
            constant: Each instance will receive this constant/fixed value.

        Returns:
            Dictionary of the distribution parameters that needs specific parameter prefix to pass to EMOD
        """
        return {"Distribution": "CONSTANT_DISTRIBUTION",
                "Constant": constant}

    @staticmethod
    def uniform(uniform_min: float, uniform_max: float) -> dict:
        """
            This function configures and returns dictionary of the parameters for UNIFORM_DISTRIBUTION.

        Args:
            uniform_min: The minimum value of the uniform distribution.
            uniform_max: The maximum of the uniform distribution.

        Returns:
            Dictionary of the distribution parameters that needs specific parameter prefix to pass to EMOD
        """
        return {"Distribution": "UNIFORM_DISTRIBUTION",
                "Min": uniform_min,
                "Max": uniform_max}

    @staticmethod
    def gaussian(gaussian_mean: float, gaussian_std_dev: float) -> dict:
        """
            This function configures and returns dictionary of the parameters for GAUSSIAN_DISTRIBUTION.

        Args:
            gaussian_mean: The mean for the Gaussian distribution.
            gaussian_std_dev: The standard deviation for the Gaussian distribution.

        Returns:
            Dictionary of the distribution parameters that needs specific parameter prefix to pass to EMOD
        """
        return {"Distribution": "GAUSSIAN_DISTRIBUTION",
                "Gaussian_Mean": gaussian_mean,
                "Gaussian_Std_Dev": gaussian_std_dev}

    @staticmethod
    def exponential(exponential_mean: float) -> dict:
        """
            This function configures and returns dictionary of the parameters for EXPONENTIAL_DISTRIBUTION.

        Args:
            exponential_mean: The mean for the exponential distribution.

        Returns:
            Dictionary of the distribution parameters that needs specific parameter prefix to pass to EMOD
        """
        return {"Distribution": "EXPONENTIAL_DISTRIBUTION",
                "Exponential": exponential_mean}

    @staticmethod
    def log_normal(mu: float, sigma: float) -> dict:
        """
            This function configures and returns dictionary of the parameters for LOG_NORMAL_DISTRIBUTION.

        Args:
            mu: The mean for the log-normal distribution.
            sigma: The width for the log-normal distribution.

        Returns:
            Dictionary of the distribution parameters that needs specific parameter prefix to pass to EMOD
        """
        return {"Distribution": "LOG_NORMAL_DISTRIBUTION",
                "Log_Normal_Mu": mu,
                "Log_Normal_Sigma": sigma}

    @staticmethod
    def poisson(poisson_mean: float) -> dict:
        """
            This function configures and returns dictionary of the parameters for POISSON_DISTRIBUTION.

        Args:
            poisson_mean: The mean for the Poisson distribution.

        Returns:
            Dictionary of the distribution parameters that needs specific parameter prefix to pass to EMOD
        """
        return {"Distribution": "POISSON_DISTRIBUTION",
                "Poisson_Mean": poisson_mean}

    @staticmethod
    def dual_constant(proportion_0: float, peak_2_value: float) -> dict:
        """
            This function configures and returns dictionary of the parameters for DUAL_CONSTANT_DISTRIBUTION.

        Args:
            proportion_0: The proportion of outcomes to assign a value of zero.
            peak_2_value: The value to assign to the remaining outcomes.

        Returns:
            Dictionary of the distribution parameters that needs specific parameter prefix to pass to EMOD
        """
        return {"Distribution": "DUAL_CONSTANT_DISTRIBUTION",
                "Proportion_0": proportion_0,
                "Peak_2_Value": peak_2_value}

    @staticmethod
    def weibull(weibull_lambda: float, weibull_kappa: float) -> dict:
        """
            This function configures and returns dictionary of the parameters for WEIBULL_DISTRIBUTION.

        Args:
            weibull_lambda: The scale value in the Weibull distribution
            weibull_kappa: The shape value in a Weibull distribution.

        Returns:
            Dictionary of the distribution parameters that needs specific parameter prefix to pass to EMOD
        """
        return {"Distribution": "WEIBULL_DISTRIBUTION",
                "Lambda": weibull_lambda,
                "Kappa": weibull_kappa}

    @staticmethod
    def dual_exponential(mean_1: float, proportion_1: float, mean_2: float) -> dict:
        """
            This function configures and returns dictionary of the parameters for DUAL_EXPONENTIAL_DISTRIBUTION.

        Args:
            mean_1: The mean of the first exponential distribution.
            proportion_1: The proportion of outcomes to assign to the first exponential distribution.
            mean_2: The mean of the second exponential distribution.

        Returns:
            Dictionary of the distribution parameters that needs specific parameter prefix to pass to EMOD
        """
        return {"Distribution": "DUAL_EXPONENTIAL_DISTRIBUTION",
                "Mean_1": mean_1,
                "Proportion_1": proportion_1,
                "Mean_2": mean_2}

    @staticmethod
    def set_distribution_parameters(distribution_containing_obj: ReadOnlyDict, distribution: dict, prefix: str) -> None:
        """
            This function sets the distribution parameters in the schema_to_class-created dictionary.

        Args:
            distribution_containing_obj: ReadOnlyDict: Schema-based smart dictionary representing the structure 
                (intervention or demographics or config) that we're setting the distribution parameters for.
            distribution: The distribution dictionary, generated by one of the distribution functions or user defined.
            prefix: The prefix to be used for the distribution parameters in this intervention.

        Returns:
            Nothing. The intervention dictionary is updated in place.
        """
        if prefix in list(distribution.keys())[0]:
            # assume was generated by user and is correctly formatted
            for key, value in distribution.items():
                setattr(distribution_containing_obj, key, value)
        else:
            # assume was generated by emod_api.utils.Distributions
            for key, value in distribution.items():
                setattr(distribution_containing_obj, prefix + key, value)
