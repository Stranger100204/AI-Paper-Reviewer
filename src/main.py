from extractor import extract_text_from_pdf
from cleaner import clean_text
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pdf_path = os.path.join(BASE_DIR, "data", "sample1.pdf")

raw_text = extract_text_from_pdf(pdf_path)
cleaned_text = clean_text(raw_text)

print(cleaned_text[:1000])