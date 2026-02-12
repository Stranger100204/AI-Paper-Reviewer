import os
import json

from extractor import extract_text_from_pdf
from cleaner import clean_text
from sec_detector import extract_sections


CORPUS_SAVE_PATH = "data/novelty_corpus"

CORE_SECTIONS = [
    "Abstract",
    "Introduction",
    "Methodology",
    "Results",
    "Conclusion"
]

# Minimum number of sections required
MIN_VALID_SECTIONS = 3


os.makedirs(CORPUS_SAVE_PATH, exist_ok=True)


def log_sections(sections):

    print("Sections detected:", list(sections.keys()))

    for sec, content in sections.items():
        word_count = len(content.split())
        print(f"   {sec}: {word_count} words")


def build_corpus_entry(pdf_path, output_name):

    print(f"\n📄 Processing: {pdf_path}")

    try:
        raw_text = extract_text_from_pdf(pdf_path)
        cleaned_text = clean_text(raw_text)
        sections = extract_sections(cleaned_text)

    except Exception as e:
        print(f"⚠ Extraction failed: {e}")
        return

    # Filter only core sections
    corpus_entry = {
        sec: sections[sec]
        for sec in CORE_SECTIONS
        if sec in sections
    }

    log_sections(corpus_entry)

    if len(corpus_entry) < MIN_VALID_SECTIONS:
        print("⚠ Skipping → insufficient sections\n")
        return

    save_path = os.path.join(CORPUS_SAVE_PATH, output_name)

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(corpus_entry, f, indent=4)

    print(f"✅ Corpus saved → {output_name}\n")


if __name__ == "__main__":

    corpus_pdf_folder = "data/corpus_pdf"

    for file in os.listdir(corpus_pdf_folder):

        if file.endswith(".pdf"):

            pdf_path = os.path.join(corpus_pdf_folder, file)
            output_name = file.replace(".pdf", ".json")

            build_corpus_entry(pdf_path, output_name)