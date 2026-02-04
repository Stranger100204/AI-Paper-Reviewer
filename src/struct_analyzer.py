import re

EXPECTED_SECTIONS = [
    "Abstract",
    "Introduction",
    "Methodology",
    "Results",
    "Conclusion",
    "References"
]

def analyze_section_presence(extracted_sections):
    presence = {}

    for section in EXPECTED_SECTIONS:
        presence[section] = "Present" if section in extracted_sections else "Missing"

    return presence

def analyze_section_strength(extracted_sections):

    # --- Hybrid Threshold Rules ---
    percentage_thresholds = {
        "Abstract": 0.02,
        "Introduction": 0.08,
        "Methodology": 0.10,
        "Results": 0.10,
        "Conclusion": 0.03
    }

    absolute_thresholds = {
        "Abstract": 100,
        "Introduction": 200,
        "Methodology": 200,
        "Results": 200,
        "Conclusion": 100
    }

    # --- Total Paper Word Count ---
    total_words = sum(len(content.split()) for content in extracted_sections.values())

    strength_report = {}

    for section in EXPECTED_SECTIONS:

        # --- Missing Section ---
        if section not in extracted_sections:
            strength_report[section] = "Missing – Section not detected in paper"
            continue

        content = extracted_sections[section]

        # =====================================================
        # REFERENCES ANALYSIS (Hybrid detection)
        # =====================================================
        if section == "References":

            # --- Robust IEEE numbering detection ---
            numbered_refs = set(
                re.findall(r'\[\s*\d+\s*\]', content)
            )

            if len(numbered_refs) >= 2:
                citations = len(numbered_refs)

            else:
                # --- Fallback for non-numbered reference styles ---
                # Detect each new reference entry by capitalized author + year pattern
                fallback_refs = re.findall(
                    r'[A-Z][A-Za-z\-]+.*,?\s*\(?\d{4}\)?',
                    content
                )

                citations = len(set(fallback_refs))

            # --- Strength evaluation ---
            if citations < 5:
                strength_report[section] = (
                    f"Weak – Limited supporting literature detected (~{citations} references)"
                )
            else:
                strength_report[section] = (
                    "Adequate – Reference coverage appears sufficient"
                )

            continue

        # =====================================================
        # WORD COUNT ANALYSIS (Hybrid thresholds)
        # =====================================================
        section_words = len(content.split())

        percent_required = int(total_words * percentage_thresholds[section])
        absolute_required = absolute_thresholds[section]

        required_words = max(percent_required, absolute_required)

        # --- Weak Section ---
        if section_words < required_words:
            strength_report[section] = (
                f"Weak – Section appears shorter than recommended academic norms "
                f"(Detected ~{section_words} words, recommended ≥ {required_words})"
            )

        # --- Adequate Section ---
        else:
            strength_report[section] = (
                "Adequate – Section depth meets academic norms"
            )

    return strength_report