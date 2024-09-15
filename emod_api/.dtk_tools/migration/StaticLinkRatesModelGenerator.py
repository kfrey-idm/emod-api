from typing import Dict, Union
from dtk.tools.migration.LinkRatesModelGenerator import LinkRatesModelGenerator


class StaticLinkRatesModelGenerator(LinkRatesModelGenerator):
    """
    This is a utility class to allow using user defined or custom link rates inside
    the generation model of MigrationGenerator
    """

    def generate(self) -> dict:
        return self.link_rates

    def __init__(self, link_rates: Dict[str, Dict[str, Union[int, float]]]):
        super().__init__()
        self.link_rates = link_rates
