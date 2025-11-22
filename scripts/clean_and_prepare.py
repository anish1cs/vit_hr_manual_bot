import os
import re
from langchain_community.document_loaders import PyPDFLoader

# --- Configuration ---
RAW_PDF_PATH = "data/raw/HR_POLICY_merged.pdf"
PROCESSED_TEXT_PATH = "data/processed/cleaned_policy.txt"
# ---------------------

def clean_text(text: str) -> str:
    """A simple function to clean the text content."""
    # Replace multiple spaces, newlines, and tabs with a single space
    text = re.sub(r'\s+', ' ', text)
    # You can add more specific cleaning rules here if needed
    return text.strip()

def main():
    print(f"--- Starting PDF cleaning process ---")
    print(f"Reading PDF from: {RAW_PDF_PATH}")
    if not os.path.exists(RAW_PDF_PATH):
        print(f"Error: File not found at {RAW_PDF_PATH}")
        print("Please make sure your PDF is named 'HR_POLICY_merged.pdf' and is in the 'data/raw' folder.")
        return

    loader = PyPDFLoader(RAW_PDF_PATH)
    pages = loader.load_and_split()

    print("Cleaning and concatenating text from all pages...")
    full_text = ""
    for page in pages:
        full_text += page.page_content + " "

    cleaned_text = clean_text(full_text)

    # Ensure the processed directory exists
    os.makedirs(os.path.dirname(PROCESSED_TEXT_PATH), exist_ok=True)

    with open(PROCESSED_TEXT_PATH, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    print(f"✅ Cleaned text successfully saved to: {PROCESSED_TEXT_PATH}")

if __name__ == "__main__":
    main()