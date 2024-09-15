import unittest
import emod_api


class EmodapiVersionTest(unittest.TestCase):
    def test_version(self):
        version = emod_api.__version__
        print(version)
        pass
