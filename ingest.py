import random
from pathlib import Path

EXTRACTED_DIR = Path("documents/extracted")
CHUNK_SIZE = 400
OVERLAP = 75

# Tried in order: paragraph → line → sentence-end → word boundary
SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", " "]


def _split_into_pieces(text: str, chunk_size: int, separators: list[str]) -> list[str]:
    """Recursively split text into pieces that each fit within chunk_size.

    Tries each separator in order (coarse → fine). If a piece is still too
    large after all separators are exhausted, it falls back to a hard character
    split.
    """
    if len(text) <= chunk_size:
        stripped = text.strip()
        return [stripped] if stripped else []

    for i, sep in enumerate(separators):
        if sep and sep not in text:
            continue

        pieces = []
        for part in text.split(sep):
            part = part.strip()
            if not part:
                continue
            if len(part) <= chunk_size:
                pieces.append(part)
            else:
                pieces.extend(_split_into_pieces(part, chunk_size, separators[i + 1:]))
        return pieces

    # Last resort: hard character split
    return [
        text[i : i + chunk_size].strip()
        for i in range(0, len(text), chunk_size)
        if text[i : i + chunk_size].strip()
    ]


def _merge_with_overlap(pieces: list[str], chunk_size: int, overlap: int) -> list[str]:
    """Merge small pieces into chunks of ~chunk_size.

    When a chunk is emitted, its last `overlap` characters are prepended to the
    next chunk so context is not lost at boundaries.
    """
    chunks = []
    current = ""

    for piece in pieces:
        candidate = f"{current} {piece}".strip() if current else piece
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
                tail = current[-overlap:] if overlap else ""
                current = f"{tail} {piece}".strip() if tail else piece
            else:
                # Single piece larger than chunk_size — emit as-is
                chunks.append(piece)
                current = ""

    if current:
        chunks.append(current)

    return chunks


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    """Recursively chunk text with overlap between consecutive chunks."""
    pieces = _split_into_pieces(text, chunk_size, SEPARATORS)
    return _merge_with_overlap(pieces, chunk_size, overlap)


def load_and_chunk_all(extracted_dir: Path = EXTRACTED_DIR) -> list[dict]:
    """Load every .txt file in extracted_dir and return a flat list of chunk dicts."""
    all_chunks = []
    for txt_path in sorted(extracted_dir.glob("*.txt")):
        text = txt_path.read_text(encoding="utf-8")
        for i, chunk in enumerate(chunk_text(text)):
            all_chunks.append({
                "source": txt_path.name,
                "chunk_index": i,
                "text": chunk,
            })
    return all_chunks


def preview_chunks(chunks: list[dict], n: int = 10) -> None:
    """Print n randomly selected chunks and the total chunk count."""
    print(f"Total chunks: {len(chunks)}\n")
    print(f"--- Sample {n} random chunks ---\n")
    for chunk in random.sample(chunks, min(n, len(chunks))):
        print(f"[{chunk['source']} | chunk #{chunk['chunk_index']}]")
        print(chunk["text"])
        print("-" * 60)


if __name__ == "__main__":
    chunks = load_and_chunk_all()
    preview_chunks(chunks)
