def generate_final_report(
    structure_score,
    section_presence,
    section_strength,
    writing_metrics,
    writing_score,
    writing_feedback,
    similarity,
    novelty_level,
    similar_paper
):

    overall_score = round(
        (structure_score * 0.3) +
        (writing_score * 0.3) +
        ((1 - similarity) * 100 * 0.4)
    )

    report = {
        "Structure Score": structure_score,
        "Section Presence": section_presence,
        "Section Strength": section_strength,
        "Writing Quality": {
            "Score": writing_score,
            "Metrics": writing_metrics,
            "Feedback": writing_feedback
        },
        "Novelty Analysis": {
            "Similarity Score": similarity,
            "Novelty Level": novelty_level,
            "Most Similar Corpus Paper": similar_paper
        },
        "Overall Score": overall_score
    }

    return report