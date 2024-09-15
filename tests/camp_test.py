#!/usr/bin/env python
import os
import unittest

from emod_api import campaign as camp

current_directory = os.path.dirname(os.path.realpath(__file__))


def delete_existing_file(file):
    if os.path.isfile(file):
        print(f'\tremove existing {file}.')
        os.remove(file)


class CampaignTest(unittest.TestCase):
    """
    Base test class for interventions tests
    """
    @classmethod
    def setUpClass(cls) -> None:
        cls.output_folder = os.path.join(current_directory, 'data', 'campaign')
        if not os.path.isdir(cls.output_folder):
            print(f"\t{cls.output_folder} doesn't exist, creating {cls.output_folder}.")
            os.mkdir(cls.output_folder)
        camp.schema_path = os.path.join(current_directory, 'data', 'config', 'input_generic_schema.json')

    def setUp(self) -> None:
        print(f"\n{self._testMethodName} started...")

    def rec_check_camp(self, camp):
        if "schema" in camp:
            return 1
        for key, value in camp.items():
            if isinstance(value, dict):
                item = self.rec_check_camp(value)
                if item is not None:
                    return 1

    