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

    def test_dashboard_and_analytics_render_each_lab_device(self):
        for route in ("/dashboard", "/analytics"):
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200)
            for device, ip in (("CORE1", "192.168.80.10"), ("EDGE1", "10.0.1.1"),
                               ("EDGE2", "10.0.1.9"), ("CORE2", "10.0.1.18")):
                self.assertIn(device.encode(), response.data)
                self.assertIn(ip.encode(), response.data)

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
