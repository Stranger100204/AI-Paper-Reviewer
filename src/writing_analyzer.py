import textstat


MAIN_CONTENT_SECTIONS = [
    "Abstract",
    "Introduction",
    "Methodology",
    "Results",
    "Conclusion"
]


def combine_main_text(sections):

    combined_text = ""

    for section in MAIN_CONTENT_SECTIONS:
        if section in sections:
            combined_text += sections[section] + "\n"

    return combined_text.strip()


def analyze_readability(sections):

    text = combine_main_text(sections)

    if not text:
        return None

    readability_report = {
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
        "avg_sentence_length": textstat.avg_sentence_length(text)
    }

    return readability_report