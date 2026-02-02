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