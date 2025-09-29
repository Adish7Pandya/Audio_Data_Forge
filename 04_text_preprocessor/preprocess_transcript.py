import os
import re
import string
from num2words import num2words
from PyPDF2 import PdfReader

def pdf_to_text(pdf_path):
    """Extract raw text from a PDF file."""
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    return full_text
def remove_unspoken_segments(text):
    """Remove unspoken transcript segments using general patterns."""
    patterns_to_remove = [
        r"\(refer slide time: \d{2}:\d{2}\)",         # (Refer Slide Time: )
        r"\bprof\.\s+[a-z\s]+\n?",                   # Lines with professor names
        r"department of [a-z\s&]+",                  # Department names
        r"indian institute of technology[^\n]*",     # IIT + location
        r"lecture\s*[-–—]?\s*\d+",                   # Lecture numbers
        r"\btable of contents\b",                    # Table of contents
        r"\(.*?\)",                                  # Bracketed titles or asides
        r"^\s*\d+\s*$",                              # Standalone numbers (slide/page numbers)
        r"^\s*$",                                    # Empty lines
        r"^[a-z\s:]{0,50}history of deep learning.*$", # Flexible match for titles
    ]

    for pattern in patterns_to_remove:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)
    
    return text

def clean_text(text):
    """Lowercase, remove punctuation, convert digits to words, and remove unspoken parts."""
    text = text.lower()
    text = remove_unspoken_segments(text)
    text = text.translate(str.maketrans('', '', string.punctuation))

    def replace_digits(match):
        return num2words(match.group())

    text = re.sub(r'\d+', replace_digits, text)
    return text

def process_all_transcripts(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]

    for file_name in pdf_files:
        input_path = os.path.join(input_dir, file_name)
        base_name = os.path.splitext(file_name)[0]
        output_path = os.path.join(output_dir, f"{base_name}.txt")

        print(f"Processing: {file_name}")
        raw_text = pdf_to_text(input_path)
        cleaned_text = clean_text(raw_text)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

    print(f"\n✅ All transcripts processed and saved to: {output_dir}")


def main():
    input_dir = "data/transcript_downloads"
    output_dir = "data/transcript_processed"
    process_all_transcripts(input_dir, output_dir)
    print("✅ All transcripts processed and saved to:", output_dir)

    
if __name__ == "__main__":
    main()
