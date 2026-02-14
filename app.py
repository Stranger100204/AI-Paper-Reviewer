import os
import sys
import tempfile
import gradio as gr

# Allow imports from src folder
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from extractor import extract_text_from_pdf
from cleaner import clean_text
from sec_detector import extract_sections
from struct_analyzer import analyze_section_presence
from struct_analyzer import analyze_section_strength
from scorer import generate_structure_score
from writing_analyzer import analyze_readability
from writing_scorer import generate_writing_score, generate_writing_feedback
from novelty_analyzer import estimate_novelty
from report_generator import generate_final_report

def analyze_paper(file):

    if file is None:
        return "Please upload a PDF file."

    # Gradio already gives file path
    pdf_path = file

    # ---- Pipeline ----
    raw_text = extract_text_from_pdf(pdf_path)
    cleaned_text = clean_text(raw_text)
    sections = extract_sections(cleaned_text)

    # Structure
    presence_report = analyze_section_presence(sections)
    strength_report = analyze_section_strength(sections)
    score, structure_feedback = generate_structure_score(strength_report)

    # Writing
    readability = analyze_readability(sections)
    writing_score = generate_writing_score(readability)
    writing_feedback = generate_writing_feedback(readability)

    # Novelty
    similarity, novelty_level, similar_paper = estimate_novelty(sections)

    # Final Report
    final_report = generate_final_report(
        score,
        presence_report,
        strength_report,
        readability,
        writing_score,
        writing_feedback,
        similarity,
        novelty_level,
        similar_paper
    )

    presence_text = "\n".join(
        [f"- **{k}**: {v}" for k, v in final_report['Section Presence'].items()]
    )

    strength_text = "\n".join(
        [f"- **{k}**: {v}" for k, v in final_report['Section Strength'].items()]
    )

    metrics_text = "\n".join(
        [f"- **{k}**: {round(v, 2)}" for k, v in final_report['Writing Quality']['Metrics'].items()]
    )

    feedback_text = "\n".join(
        [f"- {f}" for f in final_report['Writing Quality']['Feedback']]
    )

    formatted_output = f"""
# 📊 AI Research Paper Review Report

## ⭐ Overall Score: {final_report['Overall Score']}/100

---

## 🤖 Novelty Analysis

- **Similarity Score:** {final_report['Novelty Analysis']['Similarity Score']}

- **Novelty Level:** {final_report['Novelty Analysis']['Novelty Level']}

- **Most Similar Corpus Paper:** {final_report['Novelty Analysis']['Most Similar Corpus Paper']}

---

## 📑 Structure Score: {final_report['Structure Score']}/100

### Section Presence
{presence_text}

### Section Strength
{strength_text}

---

## ✍ Writing Quality Score: {final_report['Writing Quality']['Score']}/100

### Writing Metrics
{metrics_text}

### Writing Feedback
{feedback_text}

---
"""

    return formatted_output


interface = gr.Interface(
    fn=analyze_paper,
    inputs=gr.File(file_types=[".pdf"], type="filepath"),
    outputs=gr.Markdown(),
    title="AI-Based Research Paper Reviewer & Quality Analyzer",
    description="Upload a research paper PDF to receive automated structural, writing, and novelty evaluation.",
    flagging_mode="never"
)

if __name__ == "__main__":
    interface.launch()