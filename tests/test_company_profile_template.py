import json
import unittest
from pathlib import Path


class CompanyProfileTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).parents[1] / "atpa-v1" / "template" / "company-profile.json"
        cls.profile = json.loads(path.read_text(encoding="utf-8"))

    def test_template_is_safe_and_unconfigured(self):
        self.assertEqual(self.profile["schema_version"], 1)
        self.assertEqual(self.profile["status"], "not_configured")
        self.assertEqual(self.profile["sources"], [])
        self.assertIsNone(self.profile["business"]["revenue"]["value"])
        self.assertEqual(self.profile["business"]["revenue"]["status"], "unknown")

    def test_dashboard_fields_are_present(self):
        self.assertIn("identity", self.profile)
        self.assertIn("business", self.profile)
        self.assertIn("operations", self.profile)
        self.assertIn("automation_priorities", self.profile["operations"])


if __name__ == "__main__":
    unittest.main()
