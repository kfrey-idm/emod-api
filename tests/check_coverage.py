import coverage
import unittest
loader = unittest.TestLoader()
cov = coverage.Coverage(source=[
    "emod_api.campaign"
    , "emod_api.channelreports"
    , "emod_api.config"
    , "emod_api.demographics"
    , "emod_api.interventions"
    , "emod_api.migration"
    , "emod_api.schema"
    , "emod_api.schema_to_class"
    , "emod_api.serialization"
    , "emod_api.spatialreports"
    , "emod_api.weather"
])
cov.start()

# First, load and run the unittest tests
from test_camp_common import CommonInterventionTest
from test_camp_importpressure import ImportPressureTest
from test_camp_outbreak import OutbreakTest
from test_camp_sv import VaccineTest
from test_channel_reports import TestHeader, TestChannel, TestChannels
from test_config import ConfigTest
from test_demog import DemoTest
from test_demog_Parser import TestDemogParsers
from test_demog_from_pop import DemogFromPop
from test_migration import MigrationTests
from test_serialization import TestReadVersionOne, TestReadVersionTwo, TestReadVersionThree, TestReadVersionFour
from test_spatial_reports import TestSpatial
from test_utils import UtilTest
from test_weather_files import TestMetadata, TestWeather, TestWeatherNode
from test_config_demog import DemoConfigTest


test_classes_to_run = [CommonInterventionTest,
                       ImportPressureTest,
                       OutbreakTest,
                       VaccineTest,
                       TestHeader,
                       TestChannel,
                       TestChannels,
                       ConfigTest,
                       DemoTest,
                       TestDemogParsers,
                       DemogFromPop,
                       MigrationTests,
                       TestReadVersionOne,
                       TestReadVersionTwo,
                       TestReadVersionThree,
                       TestReadVersionFour,
                       TestSpatial,
                       UtilTest,
                       TestMetadata,
                       TestWeather,
                       TestWeatherNode,
                       DemoConfigTest]

suites_list = []
for tc in test_classes_to_run:
    suite = loader.loadTestsFromTestCase(tc)
    suites_list.append(suite)
    pass

big_suite = unittest.TestSuite(suites_list)
runner = unittest.TextTestRunner()
results = runner.run(big_suite)

cov.stop()
cov.save()
cov.html_report()