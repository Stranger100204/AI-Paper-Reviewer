from extractor import extract_text_from_pdf

pdf_path = "data/sample3.pdf"

text = extract_text_from_pdf(pdf_path)

print(text[:1000])  # print first 1000 chars