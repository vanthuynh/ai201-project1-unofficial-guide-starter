import chromadb
from sentence_transformers import SentenceTransformer

from ingest import load_and_chunk_all

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "hiking_guides"
EMBED_MODEL = "all-MiniLM-L6-v2"
BATCH_SIZE = 64


def load_embedding_model(model_name: str = EMBED_MODEL) -> SentenceTransformer:
    print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    print(f"Model loaded — embedding dimension: {model.get_sentence_embedding_dimension()}")
    return model


def get_or_reset_collection(client: chromadb.PersistentClient, name: str) -> chromadb.Collection:
    """Delete and recreate the collection so re-runs never produce duplicates."""
    try:
        client.delete_collection(name)
        print(f"Existing collection '{name}' cleared.")
    except Exception:
        pass
    return client.create_collection(name)


def embed_and_store(
    chunks: list[dict],
    collection: chromadb.Collection,
    model: SentenceTransformer,
) -> None:
    """Embed chunks in batches and upsert into ChromaDB with source metadata."""
    texts = [c["text"] for c in chunks]

    print(f"Embedding {len(texts)} chunks in batches of {BATCH_SIZE}...")
    embeddings = model.encode(texts, batch_size=BATCH_SIZE, show_progress_bar=True)

    # Insert in batches to avoid memory spikes on large corpora
    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start : start + BATCH_SIZE]
        collection.add(
            ids=[f"{c['source']}__chunk{c['chunk_index']}" for c in batch],
            embeddings=embeddings[start : start + BATCH_SIZE].tolist(),
            documents=[c["text"] for c in batch],
            metadatas=[{"source": c["source"], "chunk_index": c["chunk_index"]} for c in batch],
        )

    print(f"Stored {len(chunks)} chunks in collection '{collection.name}'.")


def main() -> None:
    # Stage 2 → load chunks from ingestion pipeline
    print("=== Stage 2: Loading chunks ===")
    chunks = load_and_chunk_all()
    print(f"Total chunks loaded: {len(chunks)}\n")

    # Stage 3a → embedding model
    print("=== Stage 3a: Embedding model ===")
    model = load_embedding_model()
    print()

    # Stage 3b → vector store
    print("=== Stage 3b: Vector store (ChromaDB) ===")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = get_or_reset_collection(client, COLLECTION_NAME)
    embed_and_store(chunks, collection, model)

    print(f"\nDone. Vector store saved to '{CHROMA_PATH}/'.")
    print(f"Collection '{COLLECTION_NAME}' contains {collection.count()} vectors.")


if __name__ == "__main__":
    main()
