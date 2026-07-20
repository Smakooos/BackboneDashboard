from reports.pdf_generator import generate_pdf
from utils.parser import load_csv
from utils.analyser import compute_statistics
import os

df = load_csv('data/sample.csv')
stats = compute_statistics(df)
filename = 'generated_reports/test_report.pdf'
generate_pdf(filename, stats, df)
print('exists:', os.path.exists(filename))
