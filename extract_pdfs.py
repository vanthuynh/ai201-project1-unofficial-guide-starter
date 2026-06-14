import re
from pathlib import Path

DOCUMENTS_DIR = Path("documents")
OUTPUT_DIR = Path("documents/extracted")

_MONTHS = (
    r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?"
    r"|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?"
)

# AllTrails review condition tags that appear as tag-only summary lines
_ALLTRAILS_TAGS = {
    "not crowded", "bathrooms available", "dog-friendly", "dog friendly",
    "great views", "great conditions", "no shade", "easy to park",
    "wildflowers", "dry ground", "well maintained", "bugs", "rocky",
    "crowded", "muddy", "some bugs", "shaded", "no fee",
}

# Inline substitutions: (compiled_pattern, replacement)
_INLINE_SUBS = [
    # Parenthesized absolute URLs: (https://...) (mailto:...) (tel:...)
    (re.compile(r'\(\s*(?:https?|mailto|tel|ftp|javascript):[^)]*\)', re.IGNORECASE), ''),
    # Parenthesized relative URLs: (/path/to/page?query=val)
    (re.compile(r'\(/[a-zA-Z0-9_\-./?=&%#@+*!~;:,]{5,}\)'), ''),
    # Malformed URL fragments left from PDF extraction: (://SITE.COM/...)
    (re.compile(r'\([^)]*://[^)]*\)'), ''),
    # Bare https/http URLs
    (re.compile(r'https?://\S+', re.IGNORECASE), ''),
    # Email addresses
    (re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'), ''),
    # Phone numbers like 310.437.5334 or 310-437-5334
    (re.compile(r'\b\d{3}[.\-]\d{3}[.\-]\d{4}\b'), ''),
    # Unicode BMP private use area (PDF icon/glyph artifacts)
    (re.compile(r'[-]'), ''),
    # Unicode supplementary private use area planes
    (re.compile(r'[\U000f0000-\U0010ffff]'), ''),
    # Mathematical alphanumeric symbols used as PDF icon stand-ins (𝐏, 𝔻, etc.)
    (re.compile(r'[\U0001D400-\U0001D7FF]'), ''),
    # "...more" / "…more" AllTrails truncation artifacts
    (re.compile(r'\s*[.…]{1,3}\s*more\b', re.IGNORECASE), ''),
    # Specific pdfplumber artifact: "t. emr…ore"
    (re.compile(r'\bt\.\s*emr[….]+ore\b', re.IGNORECASE), ''),
    # AllTrails trailing "less" (show-less button leaked into text)
    (re.compile(r'\bless\s*$'), ''),
    # Placeholder URLs from blog CMS: ([blogurrl])
    (re.compile(r'\(\s*\[blogurrl\]\s*\)', re.IGNORECASE), ''),
    # "·" followed by word boundary used as AllTrails tag separator
    (re.compile(r'·'), ' '),
]

# Lines whose stripped content exactly matches one of these patterns → remove
_EXACT_NOISE = re.compile(
    r'^\d+/\d+$'                          # PDF page number "1/9", "2/26"
    r'|^Search$'
    r'|^SUBSCRIBE$'
    r'|^Show more$'
    r'|^Get directions$'
    r'|^Customize route$'
    r'|^Share Map$'
    r'|^Remove ads$'
    r'|^Closure$'
    r'|^Visitor info$'
    r'|^Accessibility$'
    r'|^Top sights$'
    r'|^Top trails$'
    r'|^Open in Maps$'
    r'|^Report a map error$'
    r'|^Embed from Getty Images$'
    r'|^Image not found$'
    r'|^Photo via Wikipedia$'
    r'|^Share this with someone$'
    r'|^YOU MAY ALSO LIKE$'
    r'|^On Trend$'
    r'|^Popular Stories$'
    r'|^REAL ESTATE NEWS$'
    r'|^LEAVE A COMMENT$'
    r'|^CONTACT US$'
    r'|^WHY WORK$'
    r'|^WITH US$'
    r'|^SUBMIT$'
    r'|^Home Eat Hike Guide to LA$'
    r'|^Discover About$'
    r'|^Continue to Map$'
    r'|^Earth View 360 Open$'
    r'|^HIKE INFO$'
    r'|^WEATHER$'
    r'|^--$'
    r'|^Featured In$'
    r'|^BEST HIKES IN LOS ANGELES$'
    r'|^\($'                               # lone open parenthesis artifact
    r'|^0$'                                # lone zero (comment count artifact)
    , re.IGNORECASE
)

# Lines whose stripped content starts with one of these → remove
_PREFIX_NOISE = re.compile(
    r'^,\s+\S'                                          # PDF repeated page header ", Site Title…"
    r'|^Hiking\s*/\s*United States'                     # AllTrails breadcrumb nav
    r'|^United States\s*/\s*California'                 # AllTrails breadcrumb (variant)
    r'|^Get facility info'
    r'|^Busiest in \w'
    r'|^\d[\d,]+ trailgoers'
    r'|^Difficulty:\s+(?:Easy|Moderate|Hard|Strenuous)'
    r'|^Conditions:\s+'
    r'|^Parking:\s+'
    r'|^Showing results \d'
    r'|^Map data\s*[©]'
    r'|^This ad supports'
    r'|^This image is no longer'
    r'|^Search for more images on gettyimages'
    r'|^Don.?t forget to share'
    r'|^FACEBOOK\s+TWITTER'
    r'|^You must be logged in to post a comment'
    r'|^previous post'
    r'|^READ MORE\s*[»>]'
    r'|^All rights reserved'
    r'|^Real Estate Website Design'
    r'|^Colin Wellman is committed'
    r'|^Moving to LA\?'
    r'|^By using this website'
    r'|^WANDER\s*[·•]'
    r'|^Home\s*\('
    r'|^Home\s*[»>]'
    r'|^ABOUT\s+SEARCH'                                 # Campbell Wellman footer nav block
    r'|^PROPERTIES\s+CONTACT'
    , re.IGNORECASE
)


def _is_alltrails_tag_line(line: str) -> bool:
    """Return True if the line consists entirely of AllTrails condition tags."""
    lower = line.lower().strip()
    # Require at least 2 known tags to avoid false-positives on short sentences
    matches = sum(1 for tag in _ALLTRAILS_TAGS if tag in lower)
    if matches < 2:
        return False
    remaining = lower
    for tag in sorted(_ALLTRAILS_TAGS, key=len, reverse=True):
        remaining = remaining.replace(tag, "")
    return re.sub(r'[\s,\-]+', '', remaining) == ""


def clean_text(text: str) -> str:
    # Remove spaced-out capital letters — nav artifacts like "T A C  T A C  T"
    text = re.sub(r'\b(?:[A-Z] ){2,}[A-Z]\b', '', text)

    # Remove times: "9:12 AM", "14:30"
    text = re.sub(r'\b\d{1,2}:\d{2}(?:\s?[AP]M)?\b', '', text)

    # Remove full dates: "May 1, 2026", "Apr 27, 2026·Hiking"
    text = re.sub(rf'\b(?:{_MONTHS})\s+\d{{1,2}},?\s+\d{{4}}(?:·\w+)?', '', text)

    # Remove short numeric dates: "6/9/26", "01/15/2025"
    text = re.sub(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b', '', text)

    # Remove copyright lines entirely
    text = re.sub(r'^.*©\s*\d{4}.*$', '', text, flags=re.MULTILINE)

    output_lines = []
    for raw_line in text.split('\n'):
        # Apply all inline substitutions
        line = raw_line
        for pattern, replacement in _INLINE_SUBS:
            line = pattern.sub(replacement, line)

        stripped = line.strip()

        if not stripped:
            output_lines.append('')
            continue

        # Drop lines that are pure punctuation/symbols (lone '(', '--', etc.)
        if re.fullmatch(r'[^\w\s]+', stripped):
            output_lines.append('')
            continue

        if _EXACT_NOISE.fullmatch(stripped):
            output_lines.append('')
            continue

        if _PREFIX_NOISE.match(stripped):
            output_lines.append('')
            continue

        if _is_alltrails_tag_line(stripped):
            output_lines.append('')
            continue

        output_lines.append(line)

    text = '\n'.join(output_lines)

    # Collapse runs of blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Collapse multiple spaces
    text = re.sub(r' {2,}', ' ', text)

    return text.strip()


def extract_pdf(pdf_path: Path, output_path: Path) -> None:
    import pdfplumber
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
