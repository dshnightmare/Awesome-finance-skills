import sys
import os
import unittest
import pytest

# Add skill root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../skills/alphaear-reporter')))

try:
    from scripts.visualizer import VisualizerTools
    from scripts.report_agent import ReportUtils
    from scripts.utils.database_manager import DatabaseManager
except ImportError as e:
    pytest.skip(f"Import Error: {e}", allow_module_level=True)

class TestReporter(unittest.TestCase):
    def test_visualizer(self):
        print("Testing Visualizer...")
        viz = VisualizerTools()
        self.assertIsNotNone(viz)

    def test_report_utils_init(self):
        print("Testing ReportUtils...")
        db = DatabaseManager(":memory:")
        utils = ReportUtils(db)
        self.assertIsNotNone(utils)

if __name__ == '__main__':
    unittest.main()
