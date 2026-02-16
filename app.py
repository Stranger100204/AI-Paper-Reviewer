import os
import sys
import gradio as gr

# Allow imports from src folder
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from extractor import extract_text_from_pdf
from cleaner import clean_text
from sec_detector import extract_sections
from struct_analyzer import analyze_section_presence
from struct_analyzer import analyze_section_strength
from scorer import generate_structure_score
from writing_analyzer import analyze_readability
from writing_scorer import generate_writing_score, generate_writing_feedback
from novelty_analyzer import estimate_novelty
from report_generator import generate_final_report


def score_color(score):
    if score >= 80:
        return "#19e68c"
    if score >= 60:
        return "#ffb347"
    return "#ff5c5c"


def score_percent(value):
    try:
        return max(0.0, min(float(value), 100.0))
    except (TypeError, ValueError):
        return 0.0


def similarity_percent(similarity):
    try:
        value = float(similarity)
    except (TypeError, ValueError):
        return 0.0
    if value <= 1:
        value *= 100
    return max(0.0, min(value, 100.0))


def tone_upgrade(text):
    t = str(text)
    replacements = {
        "Missing": "Reviewer Note: Section not detected.",
        "missing": "reviewer note: section not detected.",
        "Weak": "Reviewer Concern: Limited depth observed.",
        "weak": "reviewer concern: limited depth observed.",
    }
    for src, target in replacements.items():
        t = t.replace(src, target)
    return t


def progress_bar(percent, gradient):
    safe_percent = max(0.0, min(float(percent), 100.0))
    return (
        "<div class='progress-track'>"
        f"<div class='progress-fill' style='width:{safe_percent:.1f}%; background:{gradient};'></div>"
        "</div>"
    )


def item_row(label, value, positive):
    state_class = "row-ok" if positive else "row-note"
    state_text = "OK" if positive else "NOTE"
    return (
        f"<div class='item-row {state_class}'>"
        f"<span class='item-state'>{state_text}</span>"
        f"<span class='item-label' style='color:#e8f2ff;'>{label}</span>"
        f"<span class='item-value' style='color:#e8f2ff;'>{tone_upgrade(value)}</span>"
        "</div>"
    )


def is_positive_signal(value):
    text = str(value).lower()
    positive_words = ["present", "detected", "strong", "good", "clear", "adequate"]
    negative_words = ["not", "missing", "weak", "limited", "absent"]
    if any(word in text for word in negative_words):
        return False
    return any(word in text for word in positive_words)


def analyze_paper(file_path):
    raw_text = extract_text_from_pdf(file_path)
    cleaned_text = clean_text(raw_text)
    sections = extract_sections(cleaned_text)

    presence_report = analyze_section_presence(sections)
    strength_report = analyze_section_strength(sections)
    structure_score, _ = generate_structure_score(strength_report)

    readability = analyze_readability(sections)
    writing_score = generate_writing_score(readability)
    writing_feedback = generate_writing_feedback(readability)

    similarity, novelty_level, similar_paper = estimate_novelty(sections)

    return generate_final_report(
        structure_score,
        presence_report,
        strength_report,
        readability,
        writing_score,
        writing_feedback,
        similarity,
        novelty_level,
        similar_paper,
    )


def report_text(report):
    lines = [
        "AI Research Paper Review Report",
        "",
        f"Overall Score: {report.get('Overall Score', 0)}/100",
        f"Structure Score: {report.get('Structure Score', 0)}/100",
        f"Writing Quality Score: {report.get('Writing Quality', {}).get('Score', 0)}/100",
        "",
        "Novelty Analysis",
        f"Similarity Score: {report.get('Novelty Analysis', {}).get('Similarity Score', 0)}",
        f"Novelty Level: {report.get('Novelty Analysis', {}).get('Novelty Level', 'Unknown')}",
        f"Most Similar Corpus Paper: {report.get('Novelty Analysis', {}).get('Most Similar Corpus Paper', 'N/A')}",
        "",
        "Section Presence",
    ]

    for key, value in report.get("Section Presence", {}).items():
        lines.append(f"- {key}: {tone_upgrade(value)}")

    lines.append("")
    lines.append("Section Strength")
    for key, value in report.get("Section Strength", {}).items():
        lines.append(f"- {key}: {tone_upgrade(value)}")

    lines.append("")
    lines.append("Writing Feedback")
    for feedback in report.get("Writing Quality", {}).get("Feedback", []):
        lines.append(f"- {tone_upgrade(feedback)}")

    return "\n".join(lines)


def _pdf_escape(text):
    safe = str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return safe.encode("latin-1", "replace").decode("latin-1")


def write_simple_pdf(text, output_path):
    lines = str(text).splitlines() or [""]
    max_lines_per_page = 46
    pages = [
        lines[i : i + max_lines_per_page] for i in range(0, len(lines), max_lines_per_page)
    ]
    if not pages:
        pages = [[""]]

    page_count = len(pages)
    first_page_id = 3
    first_content_id = first_page_id + page_count
    font_id = first_content_id + page_count

    objects = []
    objects.append("<< /Type /Catalog /Pages 2 0 R >>")

    kid_refs = " ".join(f"{first_page_id + i} 0 R" for i in range(page_count))
    objects.append(f"<< /Type /Pages /Kids [{kid_refs}] /Count {page_count} >>")

    for i in range(page_count):
        content_id = first_content_id + i
        page_obj = (
            "<< /Type /Page /Parent 2 0 R "
            "/MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        )
        objects.append(page_obj)

    for page_lines in pages:
        ops = ["BT", "/F1 11 Tf", "52 760 Td"]
        for line in page_lines:
            ops.append(f"({_pdf_escape(line)}) Tj")
            ops.append("0 -16 Td")
        ops.append("ET")
        stream = "\n".join(ops).encode("latin-1", "replace")
        content_obj = (
            f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1")
            + stream
            + b"\nendstream"
        )
        objects.append(content_obj)

    objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    chunks = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
    offsets = [0]
    current_offset = len(chunks[0])

    for index, obj in enumerate(objects, start=1):
        offsets.append(current_offset)
        if isinstance(obj, bytes):
            obj_bytes = obj
        else:
            obj_bytes = obj.encode("latin-1", "replace")
        block = f"{index} 0 obj\n".encode("latin-1") + obj_bytes + b"\nendobj\n"
        chunks.append(block)
        current_offset += len(block)

    xref_offset = current_offset
    total_objects = len(objects) + 1
    xref_lines = [f"xref\n0 {total_objects}\n", "0000000000 65535 f \n"]
    for off in offsets[1:]:
        xref_lines.append(f"{off:010d} 00000 n \n")
    trailer = (
        "".join(xref_lines)
        + f"trailer\n<< /Size {total_objects} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n"
    )
    chunks.append(trailer.encode("latin-1"))

    with open(output_path, "wb") as pdf_file:
        pdf_file.write(b"".join(chunks))


def build_dashboard_html(report):
    overall_score = score_percent(report.get("Overall Score", 0))
    structure_score = score_percent(report.get("Structure Score", 0))
    writing_score = score_percent(report.get("Writing Quality", {}).get("Score", 0))
    novelty_sim_percent = similarity_percent(
        report.get("Novelty Analysis", {}).get("Similarity Score", 0)
    )

    overall_color = score_color(overall_score)
    novelty_level = str(report.get("Novelty Analysis", {}).get("Novelty Level", "Unknown"))
    novelty_level_lc = novelty_level.lower()
    novelty_badge_class = "badge-low"
    if "high" in novelty_level_lc:
        novelty_badge_class = "badge-high"
    elif "moderate" in novelty_level_lc or "medium" in novelty_level_lc:
        novelty_badge_class = "badge-mid"

    presence_rows = []
    for section, status in report.get("Section Presence", {}).items():
        presence_rows.append(item_row(section, status, is_positive_signal(status)))

    strength_rows = []
    for section, status in report.get("Section Strength", {}).items():
        strength_rows.append(item_row(section, status, is_positive_signal(status)))

    feedback_rows = []
    for feedback in report.get("Writing Quality", {}).get("Feedback", []):
        feedback_rows.append(
            "<div class='feedback-row'><span class='item-state'>NOTE</span>"
            f"<span class='item-value' style='color:#e8f2ff;'>{tone_upgrade(feedback)}</span></div>"
        )

    metrics_rows = []
    for metric, value in report.get("Writing Quality", {}).get("Metrics", {}).items():
        try:
            display_value = f"{float(value):.2f}"
        except (TypeError, ValueError):
            display_value = str(value)
        metrics_rows.append(
            f"<div class='metric-row'><span style='color:#e8f2ff;'>{metric}</span><span style='color:#e8f2ff;'>{display_value}</span></div>"
        )

    hero_html = f"""
    <section class="card hero-card" style="--score-color: {overall_color}; --score-value: {overall_score:.1f};">
        <div class="score-ring" style="--score-value: {overall_score:.1f}; --score-color: {overall_color};">
            <div class="score-ring-inner">
                <div class="hero-score">{overall_score:.0f}/100</div>
                <div class="hero-subtitle">OVERALL REVIEW SCORE</div>
            </div>
        </div>
    </section>
    """

    novelty_html = f"""
    <section class="card section-card">
        <div class="section-head">
            <h2>Novelty Intelligence</h2>
            <span class="section-score">{novelty_sim_percent:.0f}% Similarity</span>
        </div>
        {progress_bar(novelty_sim_percent, "linear-gradient(90deg, #2fe0ce, #1ab6ff)")}
        <div class="novelty-grid">
            <div class="novelty-row">
                <span style="color:#e8f2ff;">Novelty Status</span>
                <span class="badge {novelty_badge_class}">{novelty_level}</span>
            </div>
            <div class="novelty-row">
                <span style="color:#e8f2ff;">Most Similar Corpus Paper</span>
                <span style="color:#e8f2ff;">{report.get('Novelty Analysis', {}).get('Most Similar Corpus Paper', 'N/A')}</span>
            </div>
            <div class="novelty-note">
                Reviewer Note: Novelty is estimated from semantic similarity against the reference corpus.
            </div>
        </div>
    </section>
    """

    structure_html = f"""
    <section class="card section-card">
        <div class="section-head">
            <h2>Structural Review</h2>
            <span class="section-score">{structure_score:.0f}/100</span>
        </div>
        {progress_bar(structure_score, "linear-gradient(90deg, #31d2ff, #16a3ff)")}
        <h3>Section Presence</h3>
        <div class="item-list">{''.join(presence_rows) or "<div class='empty'>No data available.</div>"}</div>
        <h3>Section Strength</h3>
        <div class="item-list">{''.join(strength_rows) or "<div class='empty'>No data available.</div>"}</div>
    </section>
    """

    writing_html = f"""
    <section class="card section-card">
        <div class="section-head">
            <h2>Writing Intelligence</h2>
            <span class="section-score">{writing_score:.0f}/100</span>
        </div>
        {progress_bar(writing_score, "linear-gradient(90deg, #ffb363, #ff8a3d)")}
        <h3>Metrics</h3>
        <div class="metrics-grid">{''.join(metrics_rows) or "<div class='empty'>No metrics available.</div>"}</div>
        <h3>Feedback</h3>
        <div class="item-list">{''.join(feedback_rows) or "<div class='empty'>No feedback available.</div>"}</div>
    </section>
    """

    return hero_html, novelty_html, structure_html, writing_html


def prepare_ui():
    return (
        gr.update(value="Analyzing...", interactive=False),
        gr.update(
            visible=True,
            value="<div class='loading-row'><span class='spinner'></span><span>Analyzing your paper...</span></div>",
        ),
        gr.update(visible=False, value=""),
    )


def finish_ui():
    return (
        gr.update(value="Analyze Paper", interactive=True),
        gr.update(visible=False, value=""),
    )


def run_analysis(file_path):
    if not file_path:
        return (
            "",
            "",
            "",
            "",
            gr.update(visible=False, value=None),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=True, value="Please upload a PDF file to continue."),
        )

    final_report = analyze_paper(file_path)
    hero_html, novelty_html, structure_html, writing_html = build_dashboard_html(final_report)

    report_path = "review_report.pdf"
    write_simple_pdf(report_text(final_report), report_path)

    return (
        hero_html,
        novelty_html,
        structure_html,
        writing_html,
        gr.update(visible=True, value=report_path),
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False, value=""),
    )


def back_to_upload():
    return (
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(value=None),
        gr.update(value=""),
        gr.update(value=""),
        gr.update(value=""),
        gr.update(value=""),
        gr.update(visible=False, value=None),
        gr.update(visible=False, value=""),
        gr.update(value="Analyze Paper", interactive=True),
        gr.update(visible=False, value=""),
    )


custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --bg-1: #060c1b;
    --bg-2: #0e1a33;
    --bg-3: #102646;
    --text-main: #e8f2ff;
    --text-muted: #9db5d3;
    --card-bg-top: rgba(12, 25, 46, 0.80);
    --card-bg-bottom: rgba(9, 20, 38, 0.88);
    --card-border: 1px solid rgba(133, 179, 230, 0.20);
    --card-shadow: 0 12px 32px rgba(8, 16, 32, 0.45);
    --tile-bg: rgba(12, 34, 64, 0.55);
    --tile-border: 1px solid rgba(140, 184, 230, 0.16);
    --ring-inner-top: rgba(11, 24, 44, 0.96);
    --ring-inner-bottom: rgba(9, 20, 38, 0.98);
    --radius-card: 18px;
    --radius-btn: 12px;
    --space-1: 8px;
    --space-2: 16px;
    --space-3: 24px;
    --space-4: 32px;
    --size-content: 99vw;
}

body, .gradio-container {
    font-family: "Manrope", "Segoe UI", sans-serif;
    color: var(--text-main);
    background:
        radial-gradient(1200px 700px at 20% -10%, rgba(16, 198, 255, 0.10), transparent 60%),
        radial-gradient(900px 600px at 110% 10%, rgba(44, 121, 255, 0.12), transparent 55%),
        linear-gradient(145deg, var(--bg-1), var(--bg-2) 45%, var(--bg-3));
    background-color: #0a1530;
}

.gradio-container {
    max-width: 99vw !important;
    padding: 20px 12px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    background: transparent !important;
}

.gradio-container > .main {
    max-width: 99vw !important;
}

html, body {
    background-color: #0a1530 !important;
}

#root, .app, .main {
    background: transparent !important;
}

.landing-shell {
    min-height: 85vh;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(145deg, rgba(8, 19, 42, 0.40), rgba(6, 12, 27, 0.10));
}

.landing-wrap {
    width: min(720px, 94vw);
    margin: 0 auto;
    text-align: center;
    padding: var(--space-4);
    border-radius: var(--radius-card);
    background: linear-gradient(180deg, var(--card-bg-top), var(--card-bg-bottom));
    border: var(--card-border);
    box-shadow: var(--card-shadow);
    backdrop-filter: blur(8px);
}

.landing-title {
    margin: 0;
    font-size: clamp(32px, 4vw, 44px);
    font-weight: 800;
    letter-spacing: 0.2px;
    color: #111111;
    text-align: center;
}

.landing-subtitle {
    margin: var(--space-2) 0 var(--space-4);
    font-size: 20px;
    color: #2d4f7b;
    text-align: center;
}

.upload-box {
    max-width: 460px;
    margin: 0 auto;
    padding: var(--space-2);
    border-radius: 14px;
    border: var(--card-border);
    background: linear-gradient(180deg, var(--card-bg-top), var(--card-bg-bottom));
}

.upload-title {
    margin-bottom: 12px;
    font-size: 18px;
    font-weight: 700;
    text-align: center;
    color: #2d4f7b;
}

#upload-input {
    max-width: 360px;
    margin: 0 auto;
}

#upload-input * {
    color: #000000 !important;
}

#analyze-btn {
    max-width: 220px;
    margin: var(--space-2) auto 0 auto;
}

#download-btn, #back-btn {
    width: 100%;
    min-height: 58px;
    font-size: 20px !important;
}

.action-col {
    min-height: 260px;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

#back-btn {
    flex: 0 0 58px;
}

#download-btn {
    flex: 1 1 auto;
}

#download-btn button,
#back-btn button {
    width: 100% !important;
    height: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    white-space: normal !important;
    line-height: 1.2 !important;
}

button {
    border-radius: var(--radius-btn) !important;
    border: none !important;
    padding: 12px 20px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    background: linear-gradient(90deg, #17d3ff, #157bff) !important;
    color: #ffffff !important;
    transition: transform 180ms ease, box-shadow 180ms ease, filter 180ms ease !important;
}

button:hover {
    transform: translateY(-1px);
    box-shadow: 0 0 0 1px rgba(102, 220, 255, 0.3), 0 8px 22px rgba(10, 134, 255, 0.35);
    filter: brightness(1.03);
}

button:disabled {
    opacity: 0.72;
    cursor: wait;
}

.loading-row {
    margin-top: var(--space-2);
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
    color: var(--text-muted);
    font-size: 14px;
}

.spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(220, 240, 255, 0.25);
    border-top: 2px solid #4dd6ff;
    border-radius: 50%;
    animation: spin 900ms linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.status-note {
    margin-top: var(--space-2);
    color: #ff8f8f;
    font-size: 14px;
}

.dashboard-shell {
    animation: fadeIn 280ms ease-out;
    max-width: 99vw;
    width: 100%;
    margin: 0 auto !important;
}

#top-report-row {
    align-items: stretch !important;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

.card {
    border-radius: var(--radius-card);
    padding: var(--space-3);
    margin-bottom: var(--space-3);
    background: linear-gradient(180deg, var(--card-bg-top), var(--card-bg-bottom));
    border: var(--card-border);
    box-shadow: var(--card-shadow);
    backdrop-filter: blur(7px);
}

.hero-card {
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 260px;
}

.score-ring {
    width: 228px;
    height: 228px;
    border-radius: 50%;
    padding: 12px;
    background: conic-gradient(var(--score-color) calc(var(--score-value) * 1%), rgba(170, 196, 225, 0.18) 0);
    box-shadow: 0 0 0 1px rgba(133, 179, 230, 0.24), 0 0 20px color-mix(in srgb, var(--score-color) 24%, transparent);
}

.score-ring-inner {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: linear-gradient(180deg, var(--ring-inner-top), var(--ring-inner-bottom));
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.hero-score {
    font-size: clamp(40px, 5.4vw, 52px);
    line-height: 1.05;
    margin-bottom: 10px;
    font-weight: 800;
    color: var(--score-color);
}

.hero-subtitle {
    letter-spacing: 1.4px;
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 0;
}

.section-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2);
    margin-bottom: var(--space-2);
}

.section-head h2 {
    margin: 0;
    font-size: 24px;
    color: var(--text-main);
}

.section-score {
    font-size: 24px;
    font-weight: 700;
    color: var(--text-main);
}

.section-card h3 {
    margin: var(--space-3) 0 var(--space-2);
    font-size: 18px;
    color: var(--text-main);
}

.progress-track {
    width: 100%;
    height: 10px;
    border-radius: 999px;
    overflow: hidden;
    background: rgba(157, 189, 225, 0.18);
    border: 1px solid rgba(157, 189, 225, 0.20);
}

.progress-fill {
    height: 100%;
    border-radius: inherit;
    box-shadow: 0 0 16px rgba(35, 204, 255, 0.28);
}

.item-list {
    display: grid;
    gap: 10px;
}

.item-row,
.feedback-row {
    display: grid;
    grid-template-columns: 60px 180px 1fr;
    gap: var(--space-2);
    align-items: center;
    padding: 12px;
    border-radius: 12px;
    background: var(--tile-bg);
    border: var(--tile-border);
}

.feedback-row {
    grid-template-columns: 60px 1fr;
}

.item-state {
    font-size: 11px;
    letter-spacing: 1px;
    font-weight: 700;
    border-radius: 999px;
    text-align: center;
    padding: 5px 8px;
}

.row-ok .item-state {
    color: #0d3628;
    background: rgba(47, 222, 152, 0.85);
}

.row-note .item-state,
.feedback-row .item-state {
    color: #3c2900;
    background: rgba(255, 184, 85, 0.90);
}

.item-label {
    color: var(--text-main);
    font-weight: 700;
}

.item-value {
    color: var(--text-muted);
    font-size: 15px;
}

.metrics-grid {
    display: grid;
    gap: 10px;
}

.metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    border-radius: 12px;
    background: var(--tile-bg);
    border: var(--tile-border);
    color: var(--text-muted);
}

.novelty-grid {
    display: grid;
    gap: var(--space-2);
    margin-top: var(--space-3);
}

.novelty-row {
    display: flex;
    justify-content: space-between;
    gap: var(--space-2);
    align-items: center;
    padding: 12px;
    border-radius: 12px;
    background: var(--tile-bg);
    border: var(--tile-border);
    color: var(--text-muted);
}

.badge {
    font-size: 13px;
    font-weight: 700;
    padding: 6px 12px;
    border-radius: 12px;
}

.badge-high {
    background: rgba(38, 219, 122, 0.20);
    border: 1px solid rgba(38, 219, 122, 0.50);
    color: #89f3c0;
}

.badge-mid {
    background: rgba(255, 187, 71, 0.18);
    border: 1px solid rgba(255, 187, 71, 0.45);
    color: #ffd593;
}

.badge-low {
    background: rgba(255, 99, 99, 0.16);
    border: 1px solid rgba(255, 99, 99, 0.45);
    color: #ff9f9f;
}

.novelty-note {
    padding: 12px;
    border-radius: 12px;
    background: color-mix(in srgb, var(--tile-bg) 82%, transparent);
    border: 1px dashed rgba(133, 179, 230, 0.35);
    color: var(--text-muted);
    font-size: 14px;
}

.empty {
    color: var(--text-muted);
    font-size: 14px;
}

.dashboard-shell .section-head h2,
.dashboard-shell .section-score,
.dashboard-shell .section-card h3,
.dashboard-shell .section-card p,
.dashboard-shell .item-label,
.dashboard-shell .item-value,
.dashboard-shell .metric-row,
.dashboard-shell .metric-row span,
.dashboard-shell .novelty-row,
.dashboard-shell .novelty-row span,
.dashboard-shell .novelty-note,
.dashboard-shell .empty,
.dashboard-shell .card * {
    color: #e8f2ff !important;
}

.dashboard-shell .badge-high {
    color: #89f3c0 !important;
}

.dashboard-shell .badge-mid {
    color: #ffd593 !important;
}

.dashboard-shell .badge-low {
    color: #ff9f9f !important;
}

footer {
    display: none !important;
}

@media (max-width: 900px) {
    .item-row {
        grid-template-columns: 52px 1fr;
    }
    .item-value {
        grid-column: 1 / -1;
    }
}
"""

with gr.Blocks(css=custom_css, title="Automated Research Paper Reviewer") as app:
    with gr.Group(visible=True, elem_classes=["landing-shell"]) as landing_view:
        with gr.Group(elem_classes=["landing-wrap"]):
            gr.HTML(
                """
                <h1 class="landing-title">Automated Research Paper Reviewer</h1>
                <p class="landing-subtitle">Intelligent Structural - Writing - Novelty Evaluation</p>
                """
            )
            with gr.Group(elem_classes=["upload-box"]):
                gr.HTML("<div class='upload-title'>Upload Research Paper</div>")
                pdf_input = gr.File(
                    file_types=[".pdf"],
                    type="filepath",
                    label="",
                    elem_id="upload-input",
                )
                analyze_btn = gr.Button("Analyze Paper", elem_id="analyze-btn")
                loading_ui = gr.HTML(visible=False)
                status_message = gr.Markdown(visible=False, elem_classes=["status-note"])

    with gr.Group(visible=False, elem_classes=["dashboard-shell"]) as dashboard_view:
        with gr.Row(elem_id="top-report-row"):
            with gr.Column(scale=4):
                hero_display = gr.HTML()
            with gr.Column(scale=1, min_width=220, elem_classes=["action-col"]):
                back_btn = gr.Button("Back to Upload", elem_id="back-btn")
                download_btn = gr.DownloadButton(
                    label="Download PDF Report",
                    value=None,
                    visible=False,
                    elem_id="download-btn",
                )
        novelty_display = gr.HTML()
        structure_display = gr.HTML()
        writing_display = gr.HTML()

    start_event = analyze_btn.click(
        fn=prepare_ui,
        inputs=[],
        outputs=[analyze_btn, loading_ui, status_message],
        queue=False,
    )

    analysis_event = start_event.then(
        fn=run_analysis,
        inputs=pdf_input,
        outputs=[
            hero_display,
            novelty_display,
            structure_display,
            writing_display,
            download_btn,
            dashboard_view,
            landing_view,
            status_message,
        ],
    )

    analysis_event.then(
        fn=finish_ui,
        inputs=[],
        outputs=[analyze_btn, loading_ui],
        queue=False,
    )

    back_btn.click(
        fn=back_to_upload,
        inputs=[],
        outputs=[
            dashboard_view,
            landing_view,
            pdf_input,
            hero_display,
            novelty_display,
            structure_display,
            writing_display,
            download_btn,
            status_message,
            analyze_btn,
            loading_ui,
        ],
        queue=False,
    )

if __name__ == "__main__":
    app.launch()
