def score_reading_ease(value):

    if value >= 50:
        return 100
    elif 30 <= value < 50:
        return 80
    elif 20 <= value < 30:
        return 65
    else:
        return 50


def score_grade_level(value):

    if 10 <= value <= 16:
        return 100
    elif 8 <= value < 10 or 16 < value <= 18:
        return 75
    else:
        return 60


def score_sentence_length(value):

    if 15 <= value <= 25:
        return 100
    elif 10 <= value < 15 or 25 < value <= 30:
        return 75
    else:
        return 60


def generate_writing_score(readability_report):

    reading_score = score_reading_ease(
        readability_report["flesch_reading_ease"]
    )

    grade_score = score_grade_level(
        readability_report["flesch_kincaid_grade"]
    )

    sentence_score = score_sentence_length(
        readability_report["avg_sentence_length"]
    )

    final_score = (
        reading_score * 0.4 +
        grade_score * 0.3 +
        sentence_score * 0.3
    )

    return round(final_score)

def generate_writing_feedback(readability_report):

    feedback = []

    reading = readability_report["flesch_reading_ease"]
    grade = readability_report["flesch_kincaid_grade"]
    sentence = readability_report["avg_sentence_length"]

    # Reading Ease Feedback
    if reading < 30:
        feedback.append("Writing is highly complex. Consider simplifying sentence structure.")
    elif reading < 50:
        feedback.append("Writing is moderately complex but acceptable for academic work.")

    # Grade Level Feedback
    if grade > 16:
        feedback.append("Text may be overly technical. Consider improving clarity.")
    elif grade < 10:
        feedback.append("Writing may be too simplistic for academic research.")

    # Sentence Length Feedback
    if sentence > 25:
        feedback.append("Sentences are long. Consider breaking them for better readability.")
    elif sentence < 10:
        feedback.append("Sentences are very short. Consider improving flow and coherence.")

    if not feedback:
        feedback.append("Writing quality is strong and academically appropriate.")

    return feedback