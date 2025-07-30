import os
import pathlib
from unittest import TestCase

from job_analyzer.database.models import LayOff


class TestDataModel(TestCase):
    """Test LayOff Database Model"""

    def setUp(self):

        current_path = os.path.dirname(os.path.abspath(__file__))

        test_folder_path = pathlib.Path(current_path).parent

        test_files_path = test_folder_path / "testfiles"

        self.layoff_file_path = test_files_path / "lay_off_test_file.csv"

        self.parsed_model_list: list[LayOff] = LayOff.from_csv(self.layoff_file_path)

    def test_parse_file(self):
        """Test LayOff File being parsed"""

        self.assertEqual(len(self.parsed_model_list), 8)

    def test_as_context(self):
        """Test LayOff Model as properly formatted context for AI"""

        temp_data_str = (
            "```markdown\n"
            + "### Layoffs\n"
            + "| Company   | Location HQ     | # Laid Off   | Date       | %   | Industry   | Source                                                                                                             | Stage    | $ Raised (mm)   | Country   | Date Added   |\n"
            + "|:----------|:----------------|:-------------|:-----------|:----|:-----------|:-------------------------------------------------------------------------------------------------------------------|:---------|:----------------|:----------|:-------------|\n"
            + "| WiseTech  | sydney,non-u.s. |              | 2025-07-23 |     | logistics  | https://www.reuters.com/world/asia-pacific/australias-wisetech-cut-some-jobs-ai-driven-efficiency-push-2025-07-23/ | post-ipo | $3000           | australia | 2025-07-24   |\n"
            + "```"
        )

        self.assertEqual(temp_data_str, LayOff.as_context([self.parsed_model_list[0]]))
