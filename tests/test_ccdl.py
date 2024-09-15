#!/usr/bin/env python
import unittest
import io
import json
import sys

import emod_api.peek_camp as ccdl

class TestCCDLDecoder(unittest.TestCase):
    def setUp(self) -> None:
        print(f"\n{self._testMethodName} started...")

    def test_json_to_ccdl(self):
        # This is just a quick-and-dirty "did we change anything?" regression test. Need full set of
        # requirements-based capabilities tests.
        cached_stdout = sys.stdout
        with open( "test_camp.ccdl", "w" ) as test_ccdl_w:
            sys.stdout = test_ccdl_w
            ccdl.decode( "campaign.json", "config_ccdl.json" )
        sys.stdout = cached_stdout 
        with open( "test_camp.ccdl" ) as test_ccdl_r:
            myccdl = test_ccdl_r.read() 
            with open( "campaign.ccdl") as ref_ccdl:
                self.assertEqual(myccdl, ref_ccdl.read())


if __name__ == '__main__':
    unittest.main()
