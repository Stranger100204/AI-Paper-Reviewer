SECTION_WEIGHTS = {
    "Abstract": 10,
    "Introduction": 20,
    "Methodology": 25,
    "Results": 25,
    "Conclusion": 10,
    "References": 10
}

def generate_structure_score(strength_report):

    total_score = 0
    feedback = []

    for section, weight in SECTION_WEIGHTS.items():

        status = strength_report.get(section, "Missing")

        if "Adequate" in status:
            total_score += weight

        elif "Weak" in status:
            total_score += weight * 0.5
            feedback.append(f"{section} section could be improvised & elaborated.")

        else:
            feedback.append(f"{section} section is missing.")

    return round(total_score), feedback