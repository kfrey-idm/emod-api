from emod_api.utils import Distributions
import unittest


class UtilTest(unittest.TestCase):

    def setUp(self) -> None:
        print(f"\n{self._testMethodName} has started...")

    def tearDown(self) -> None:
        pass

    def test_constant_distribution(self):
        constant = 83
        expected_outcome = {"Distribution": "CONSTANT_DISTRIBUTION",
                            "Constant": constant}
        self.assertEqual(Distributions.constant(constant), expected_outcome)

    def test_uniform_distribution(self):
        test_min = 1
        test_max = 100
        expected_outcome = {"Distribution": "UNIFORM_DISTRIBUTION",
                            "Min": test_min,
                            "Max": test_max}
        self.assertEqual(Distributions.uniform(test_min, test_max), expected_outcome)

    def test_exponential_distribution(self):
        mean = 5
        expected_outcome = {"Distribution": "EXPONENTIAL_DISTRIBUTION",
                            "Exponential": mean}
        self.assertEqual(Distributions.exponential(mean), expected_outcome)

    def test_gaussian_distribution(self):
        mean = 5
        std_dev = 2
        expected_outcome = {"Distribution": "GAUSSIAN_DISTRIBUTION",
                            "Gaussian_Mean": mean,
                            "Gaussian_Std_Dev": std_dev}
        self.assertEqual(Distributions.gaussian(mean, std_dev), expected_outcome)

    def test_poisson_distribution(self):
        mean = 5
        expected_outcome = {"Distribution": "POISSON_DISTRIBUTION",
                            "Poisson_Mean": mean}
        self.assertEqual(Distributions.poisson(mean), expected_outcome)

    def test_log_normal_distribution(self):
        mu = 5
        sigma = 2
        expected_outcome = {"Distribution": "LOG_NORMAL_DISTRIBUTION",
                            "Log_Normal_Mu": mu,
                            "Log_Normal_Sigma": sigma}
        self.assertEqual(Distributions.log_normal(mu, sigma), expected_outcome)

    def test_dual_constant_distribution(self):
        proportion_0 = 83
        peak_2_value = 5
        expected_outcome = {"Distribution": "DUAL_CONSTANT_DISTRIBUTION",
                            "Peak_2_Value": peak_2_value,
                            "Proportion_0": proportion_0}
        self.assertEqual(Distributions.dual_constant(proportion_0, peak_2_value), expected_outcome)

    def test_weibull_distribution(self):
        weibull_lambda = 2
        weibull_kappa = 5
        expected_outcome = {"Distribution": "WEIBULL_DISTRIBUTION",
                            "Kappa": weibull_kappa,
                            "Lambda": weibull_lambda}
        self.assertEqual(Distributions.weibull(weibull_lambda, weibull_kappa), expected_outcome)

    def test_dual_exponential_distribution(self):
        mean_1 = 2
        mean_2 = 5
        proportion_1 = 0.44
        expected_outcome = {"Distribution": "DUAL_EXPONENTIAL_DISTRIBUTION",
                            "Mean_1": mean_1,
                            "Proportion_1": proportion_1,
                            "Mean_2": mean_2}
        self.assertEqual(Distributions.dual_exponential(mean_1, proportion_1, mean_2), expected_outcome)
