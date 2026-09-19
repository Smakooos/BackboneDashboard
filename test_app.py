import unittest
from unittest.mock import patch

import app as application


class AppTests(unittest.TestCase):
    def setUp(self):
        application.app.config.update(TESTING=True)
        self.client = application.app.test_client()

    def test_pages_render_with_current_data(self):
        for route in ("/", "/dashboard", "/analytics", "/reports", "/project", "/faq"):
            self.assertEqual(self.client.get(route).status_code, 200)

    def test_dashboard_handles_unavailable_data(self):
        with patch.object(application, "load_csv", return_value=None):
            response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Total Devices", response.data)

    def test_report_is_returned_without_creating_a_file(self):
        response = self.client.get("/download-report")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/pdf")
        self.assertTrue(response.data.startswith(b"%PDF"))
