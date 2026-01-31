import re

def clean_text(text: str) -> str:
    """
    Cleans extracted PDF text while preserving structure
    """

    # Replace multiple newlines with max two newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Replace multiple spaces with single space
    text = re.sub(r'[ \t]+', ' ', text)

    # Strip leading/trailing whitespace
    return text.strip()