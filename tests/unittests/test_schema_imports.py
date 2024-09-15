import unittest

class EmodapiSchemaImportTest(unittest.TestCase):
    def setUp(self) -> None:
        self.expected_items = None
        self.found_items = None
        pass

    def verify_expected_items_present(self, namespace):
        self.found_items = dir(namespace)
        for item in self.expected_items:
            self.assertIn(
                item,
                self.found_items
            )

    def tearDown(self) -> None:
        pass

    def test_get_schema_import(self):
        self.expected_items = [
            "dtk_to_schema"
        ]
        import emod_api.schema.get_schema as eass
        self.verify_expected_items_present(namespace=eass)
        pass

    def test_post_schema_import(self):
        self.expected_items = [
            "application",
            "idm_type_schemas"
        ]
        import emod_api.schema.dtk_post_process_schema as eaps
        self.verify_expected_items_present(namespace=eaps)
        pass

    def test_schema_to_class_import(self):
        self.expected_items = [
            "get_class_with_defaults"
        ]
        import emod_api.schema_to_class as eas2c
        self.verify_expected_items_present(namespace=eas2c)
        pass


