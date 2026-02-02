# AI-Based Research Paper Reviewer and Quality Analyzer (NLP)

## 📌 Project Overview
This project implements an AI-based system that analyzes a research paper and provides a preliminary quality review using Natural Language Processing (NLP) techniques. The system is designed as a **pre-submission assistance tool** to help students and researchers evaluate the structure and completeness of their papers before formal review.

⚠️ This system is **not intended to replace human reviewers**, but to act as a decision-support tool.

---

## 🎯 Project Objectives
- Extract text from research paper PDFs
- Identify standard academic sections (e.g., Abstract, Conclusion, References)
- Analyze paper structure and completeness
- Detect missing or weak sections
- Provide structured feedback for improvement
- Generate a machine-readable analysis output

---

## 🧠 System Architecture
PDF Input
↓
PDF Text Extraction
↓
Text Cleaning & Normalization
↓
Rule-Based Section Detection
↓
Section-wise Content Extraction
↓
Structured Output (JSON)

---

## 🛠️ Technologies Used
- **Python 3**
- **pdfplumber** – PDF text extraction
- **Regular Expressions (re)** – Rule-based NLP
- **spaCy** (installed for later stages)
- **Git & GitHub** – Version control

---

## 📁 Project Structure
ai-paper-reviewer/
│
├── data/ # Sample research paper PDFs
├── src/
│ ├── extractor.py # PDF text extraction
│ ├── cleaner.py # Safe text cleaning
│ ├── section_detector.py # Rule-based section detection
│ └── main.py # Pipeline runner
│
├── output/ # Extracted outputs (JSON/text)
├── requirements.txt
└── README.md

---

## ⚙️ How the System Works

### 1️⃣ PDF Text Extraction
- Research papers are parsed using `pdfplumber`
- Text is extracted page-by-page
- Multi-column formatting may appear slightly jumbled (acceptable for scope)

### 2️⃣ Text Cleaning
- Excessive whitespace and newlines are normalized
- Section headings are **explicitly preserved**
- No aggressive preprocessing is applied

### 3️⃣ Section Detection (Rule-Based NLP)
- Uses keyword and pattern matching
- Supports:
  - Uppercase headings (e.g., ABSTRACT)
  - Numbered headings (e.g., 1. INTRODUCTION)
  - Punctuated headings (e.g., REFERENCES:)

Detected standard sections include:
- Abstract
- Introduction
- Methodology (if present)
- Results (if present)
- Conclusion
- References

### 4️⃣ Section Content Extraction
- Text is sliced between detected section boundaries
- Each detected section is stored separately for analysis

---

## 📤 Sample Output
```json
{
  "Abstract": "Text of abstract...",
  "Conclusion": "Text of conclusion...",
  "References": "[1] Author et al..."
}
