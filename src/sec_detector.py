import re

SECTION_ALIASES = {
    "Abstract": ["abstract"],
    "Introduction": ["introduction"],
    "Methodology": ["methodology", "methods"],
    "Results": ["results", "experimental results", "evaluation", "results and discussion"],
    "Conclusion": ["conclusion", "conclusions"],
    "References": ["references", "bibliography"]
}

def find_section_positions(text):
    positions = {}
    lines = text.splitlines()
    current_pos = 0

    for line in lines:
        stripped = line.strip()
        upper = stripped.upper()

        for section, keywords in SECTION_ALIASES.items():
            for keyword in keywords:
                kw = keyword.upper()

                # RULE 1: Numbered heading (e.g., "1. INTRODUCTION")
                if stripped.startswith(tuple(str(i) for i in range(1, 10))) and kw in upper:
                    if len(stripped) < 100 and section not in positions:
                        positions[section] = current_pos

                # RULE 2: Standalone uppercase heading
                elif upper == kw or upper.startswith(kw + ":"):
                    if section not in positions:
                        positions[section] = current_pos

        current_pos += len(line) + 1

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