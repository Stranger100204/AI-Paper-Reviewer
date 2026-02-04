from extractor import extract_text_from_pdf
from cleaner import clean_text
from sec_detector import extract_sections
from struct_analyzer import analyze_section_presence
from struct_analyzer import analyze_section_strength
from scorer import generate_structure_score
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pdf_path = os.path.join(BASE_DIR, "data", "sample2.pdf")

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


print("\n--- Section Strength Report ---")

strength_report = analyze_section_strength(sections)

for sec, status in strength_report.items():
    print(f"{sec}: {status}")

print("\n--- Overall Structure Score ---")

score, feedback = generate_structure_score(strength_report)

print(f"Structure Score: {score}/100")

print("\n--- Feedback ---")
for f in feedback:
    print("-", f)