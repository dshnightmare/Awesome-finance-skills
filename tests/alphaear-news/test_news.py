import sys
import os
import unittest
import pytest

# Add skill root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../skills/alphaear-news')))

try:
    from scripts.news_tools import NewsNowTools
    from scripts.database_manager import DatabaseManager
except ImportError as e:
    pytest.skip(f"Import Error: {e}", allow_module_level=True)

class TestNews(unittest.TestCase):
    def test_init(self):
        print("Testing NewsNowTools Iteration...")
        db = DatabaseManager(":memory:") 
        tools = NewsNowTools(db)
        self.assertIsNotNone(tools)
        print("NewsNowTools Initialized.")

if __name__ == '__main__':
    unittest.main()
