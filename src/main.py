from extractor import extract_text_from_pdf
from cleaner import clean_text
from sec_detector import extract_sections
from struct_analyzer import analyze_section_presence
from struct_analyzer import analyze_section_strength
from scorer import generate_structure_score
from writing_analyzer import analyze_readability
from writing_scorer import generate_writing_score
from writing_scorer import generate_writing_feedback
from novelty_analyzer import estimate_novelty
from report_generator import generate_final_report
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pdf_path = os.path.join(BASE_DIR, "data", "sample_test", "sample2.pdf")

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

print("\n--- Writing Quality Metrics ---")

readability = analyze_readability(sections)

if readability:
    for key, value in readability.items():
        print(f"{key}: {round(value, 2)}")

if readability:
    writing_score = generate_writing_score(readability)

    print("\n--- Writing Quality Score ---")
    print(f"Writing Score: {writing_score}/100")

print("\n--- Writing Feedback ---")

feedback = generate_writing_feedback(readability)

for f in feedback:
    print("-", f)

print("\n--- Novelty Estimation ---")

similarity, novelty_level, similar_paper = estimate_novelty(sections)

if similarity is not None:
    print(f"Similarity Score: {similarity}")
    print(f"Novelty Level: {novelty_level}")
    print(f"Most Similar Corpus Paper: {similar_paper}")

final_report = generate_final_report(
    score,                    # structure_score → score
    presence_report,          # section_presence → presence_report
    strength_report,          # section_strength → strength_report
    readability,              # writing_metrics → readability
    writing_score,
    feedback,                 # writing_feedback → feedback
    similarity,
    novelty_level,
    similar_paper
)

print("\n========== FINAL AI REVIEW REPORT ==========\n")

for key, value in final_report.items():
    print(f"{key}:\n{value}\n")