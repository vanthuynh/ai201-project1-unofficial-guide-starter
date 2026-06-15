import chromadb
from sentence_transformers import SentenceTransformer

from embed import CHROMA_PATH, COLLECTION_NAME, EMBED_MODEL

TOP_K = 3

# Evaluation questions from planning.md with their expected answers
EVAL_QUESTIONS = [
    {
        "question": "How far away from UCLA is Saddle Peak trail?",
        "expected": "20.9 miles",
    },
    {
        "question": "What is the elevation gain of Los Leones Trail?",
        "expected": "1292 ft",
    },
    {
        "question": "Which hike is always mentioned in most articles about West LA trails?",
        "expected": "Los Leones Trail",
    },
    {
        "question": "What is Los Leones trail parking condition?",
        "expected": "Free street parking, should arrive early, especially on weekend",
    },
    {
        "question": "Which hikes have ocean/beach views?",
        "expected": "Los Leones Trail, Temescal Canyon Trail, and the Grotto Trail" ,
    },
]


def retrieve(
    query: str,
    collection: chromadb.Collection,
    model: SentenceTransformer,
    k: int = TOP_K,
) -> list[dict]:
    """Embed query and return the top-k most relevant chunks with source info.

    Returns a list of dicts with keys: text, source, chunk_index, distance.
    """
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for text, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": text,
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
            "distance": round(distance, 4),
        })

    return chunks


def print_results(query: str, results: list[dict], expected: str | None = None) -> None:
    print(f"\nQuery: {query}")
    if expected:
        print(f"Expected answer: {expected}")
    print("-" * 70)
    for i, chunk in enumerate(results, 1):
        print(f"[{i}] {chunk['source']} | chunk #{chunk['chunk_index']} | distance: {chunk['distance']}")
        print(chunk["text"])
        print()


def run_eval(collection: chromadb.Collection, model: SentenceTransformer) -> None:
    """Run all 5 evaluation questions and print the retrieved chunks."""
    print("=" * 70)
    print("RETRIEVAL EVALUATION — 5 test questions")
    print("=" * 70)

    for entry in EVAL_QUESTIONS:
        results = retrieve(entry["question"], collection, model)
        print_results(entry["question"], results, expected=entry["expected"])
        print("=" * 70)


def main() -> None:
    print("Loading embedding model...")
    model = SentenceTransformer(EMBED_MODEL)

    print("Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(COLLECTION_NAME)
    print(f"Collection '{COLLECTION_NAME}' loaded — {collection.count()} vectors.\n")

    run_eval(collection, model)


if __name__ == "__main__":
    main()
