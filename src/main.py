from extractor import extract_text_from_pdf
from cleaner import clean_text
from sec_detector import extract_sections
from struct_analyzer import analyze_section_presence
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pdf_path = os.path.join(BASE_DIR, "data", "sample1.pdf")

raw_text = extract_text_from_pdf(pdf_path)
cleaned_text = clean_text(raw_text)

sections = extract_sections(cleaned_text)

#Week 1
for sec, content in sections.items():
    print(f"\n--- {sec} ---")
    print(content[:500])

#Week 2 
print("\n--- Section Presence Report ---")

presence_report = analyze_section_presence(sections)

for sec, status in presence_report.items():
    print(f"{sec}: {status}")