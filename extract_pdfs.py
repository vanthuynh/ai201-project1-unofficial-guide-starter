import re
import pdfplumber
from pathlib import Path

DOCUMENTS_DIR = Path("documents")
OUTPUT_DIR = Path("documents/extracted")

_MONTHS = (
    r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?"
    r"|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?"
)

def clean_text(text: str) -> str:
    # Remove URLs (http/https)
    text = re.sub(r"https?://\S+", "", text)

    # Remove spaced-out capital letters, e.g. "S E A R C H" or "L O S A N G E L E S"
    text = re.sub(r"\b(?:[A-Z] ){2,}[A-Z]\b", "", text)

    # Remove times: "9:12 AM", "14:30", "6:16 PM"
    text = re.sub(r"\b\d{1,2}:\d{2}(?:\s?[AP]M)?\b", "", text)

    # Remove dates: "May 1, 2026", "Apr 27, 2026·Hiking"
    text = re.sub(rf"\b(?:{_MONTHS})\s+\d{{1,2}},?\s+\d{{4}}(?:·\w+)?", "", text)

    # Remove short numeric dates: "6/9/26", "01/15/2025"
    text = re.sub(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", "", text)

    # Collapse leftover multiple spaces and excess blank lines
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

def extract_pdf(pdf_path: Path, output_path: Path) -> None:
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    text = clean_text("\n\n".join(pages))
    output_path.write_text(text, encoding="utf-8")
    print(f"Extracted: {pdf_path.name} -> {output_path.name}")

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_files = sorted(DOCUMENTS_DIR.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in documents/")
        return

    for pdf_path in pdf_files:
        output_path = OUTPUT_DIR / (pdf_path.stem + ".txt")
        try:
            extract_pdf(pdf_path, output_path)
        except Exception as e:
            print(f"Failed to extract {pdf_path.name}: {e}")

    print(f"\nDone. {len(pdf_files)} files extracted to {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
