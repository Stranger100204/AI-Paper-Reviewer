import re

SECTION_ALIASES = {
    "Abstract": ["abstract"],
    "Introduction": ["introduction"],
    "Methodology": ["methodology", "methods"],
    "Results": ["results", "experimental results", "evaluation"],
    "Conclusion": ["conclusion", "conclusions"],
    "References": ["references", "bibliography"]
}

def find_section_positions(text):
    positions = {}

    for section, keywords in SECTION_ALIASES.items():
        for keyword in keywords:
            pattern = rf"\n\s*(\d+\.?\s*)?{keyword.upper()}\s*:?\s*\n"
            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                positions[section] = match.start()
                break

    return positions

def extract_sections(text):
    positions = find_section_positions(text)

    # Sort sections by appearance order
    sorted_sections = sorted(positions.items(), key=lambda x: x[1])

    section_text = {}

    for i in range(len(sorted_sections)):
        section_name, start_pos = sorted_sections[i]

        end_pos = (
            sorted_sections[i + 1][1]
            if i + 1 < len(sorted_sections)
            else len(text)
        )

        section_text[section_name] = text[start_pos:end_pos].strip()

    return section_text