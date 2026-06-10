import pdfplumber
from pathlib import Path

DOCUMENTS_DIR = Path("documents")
OUTPUT_DIR = Path("documents/extracted")

def extract_pdf(pdf_path: Path, output_path: Path) -> None:
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    text = "\n\n".join(pages).strip()
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
