"""Backward-compatible import for the single supported report generator."""

from reports.pdf_generator import generate_pdf

__all__ = ["generate_pdf"]
