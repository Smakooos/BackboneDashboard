from io import BytesIO
import unittest

import pandas as pd

from reports.pdf_generator import generate_pdf
from utils.analyser import compute_statistics


class PdfReportTests(unittest.TestCase):
    def test_report_is_generated_in_memory(self):
        df = pd.DataFrame([["2026-09-19T10:00:00", "CORE1", "192.168.80.10", "eth0", 1, 12.5, 7.5]],
                          columns=["timestamp", "device", "ip", "interface", "status", "in_mbps", "out_mbps"])
        output = BytesIO()
        generate_pdf(output, compute_statistics(df), df)
        self.assertTrue(output.getvalue().startswith(b"%PDF"))
