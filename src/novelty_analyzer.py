import os
import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


CORPUS_PATH = "data/novelty_corpus"


def load_corpus():

    corpus_texts = []

    for file in os.listdir(CORPUS_PATH):

        if file.endswith(".json"):

            with open(os.path.join(CORPUS_PATH, file), "r", encoding="utf-8") as f:
                data = json.load(f)

                combined_text = " ".join(data.values())
                corpus_texts.append(combined_text)

    return corpus_texts


def combine_input_sections(sections):

    core_sections = [
        "Abstract",
        "Introduction",
        "Methodology",
        "Results",
        "Conclusion"
    ]

    combined_text = ""

    for sec in core_sections:
        if sec in sections:
            combined_text += sections[sec] + " "

    return combined_text.strip()

def estimate_novelty(sections):

    corpus_files = []
    corpus_texts = []

    for file in os.listdir(CORPUS_PATH):

        if file.endswith(".json"):

            with open(os.path.join(CORPUS_PATH, file), "r", encoding="utf-8") as f:
                data = json.load(f)

                combined_text = " ".join(data.values())

                corpus_texts.append(combined_text)
                corpus_files.append(file)

    paper_text = combine_input_sections(sections)

    if not paper_text or not corpus_texts:
        return None, None, None

    texts = corpus_texts + [paper_text]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(texts)

    similarity_scores = cosine_similarity(
        tfidf_matrix[-1], tfidf_matrix[:-1]
    )[0]

    max_index = similarity_scores.argmax()
    max_similarity = float(similarity_scores[max_index])

    most_similar_paper = corpus_files[max_index]

    # Novelty classification
    if max_similarity > 0.45:
        novelty_level = "Low Novelty"
    elif max_similarity > 0.25:
        novelty_level = "Moderate Novelty"
    else:
        novelty_level = "High Novelty"

    return round(max_similarity, 2), novelty_level, most_similar_paper