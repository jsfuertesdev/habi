"""
Module for test
"""

import unittest
import json
import threading
import requests
import time
from unittest.mock import patch, MagicMock
from src.database import get_properties
from src.property_service import run_server
from utils.Logger import Logger


class TestPropertyService(unittest.TestCase):
    """
    Class for test
    """

    @classmethod
    def setUpClass(cls):
        """
        set up server for test
        """
        cls.server_thread = threading.Thread(target=run_server)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1)

    @patch("src.database.DatabaseConnection")
    def test_get_properties_no_filters(self, mock_db):
        """
        Verify properties without apply filters
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {
                "address": "carrera 100 #15-90",
                "city": "bogota",
                "state": "en_venta",
                "price": 350000000,
                "description": "Amplio apartamento en conjunto cerrado",
            }
        ]
        mock_db.return_value.__enter__.return_value = mock_cursor
        result = get_properties({})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["address"], "carrera 100 #15-90")
        self.assertEqual(result[0]["city"], "bogota")
        self.assertEqual(result[0]["state"], "en_venta")
        self.assertEqual(result[0]["price"], 350000000)
        self.assertEqual(
            result[0]["description"], "Amplio apartamento en conjunto cerrado"
        )
        mock_cursor.execute.assert_called_once()
        Logger.add_to_log(
            "info", "Test test_get_properties_no_filters runned successfully"
        )

    @patch("src.database.DatabaseConnection")
    def test_get_properties_with_filters(self, mock_db):
        """
        Verify properties with filters
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_db.return_value.__enter__.return_value = mock_cursor

        filters = {"year": 2020, "city": "bogota", "state": "pre_venta"}
        get_properties(filters)

        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args[0]
        self.assertIn("AND p.year = %s", call_args[0])
        self.assertIn("AND p.city = %s", call_args[0])
        self.assertIn("AND s.name = %s", call_args[0])
        self.assertEqual(call_args[1], [2020, "bogota", "pre_venta"])
        Logger.add_to_log(
            "info", "Test test_get_properties_with_filters runned successfully"
        )

    def test_property_handler_get(self):
        """
        Valid GET request response
        """
        response = requests.get(
            "http://localhost:8000/properties?year=2020&city=bogota"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertIsInstance(json.loads(response.content), list)
        Logger.add_to_log("info", "Test test_property_handler_get runned successfully")

    def test_invalid_year_filter(self):
        """
        Valid response for invalid value in year
        """
        response = requests.get("http://localhost:8000/properties?year=invalid")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(json.loads(response.content), [])
        Logger.add_to_log("info", "Test test_invalid_year_filter runned successfully")

    def test_invalid_path(self):
        """
        Verify server response for invalid route
        """
        response = requests.get("http://localhost:8000/invalid_path")
        self.assertEqual(response.status_code, 404)
        Logger.add_to_log("info", "Test test_invalid_path runned successfully")


if __name__ == "__main__":
    unittest.main()
