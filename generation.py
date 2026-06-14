import os

import chromadb
import gradio as gr
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

from embed import CHROMA_PATH, COLLECTION_NAME, EMBED_MODEL
from retrieve import retrieve, TOP_K

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"

# ── Grounding rules injected as the system prompt ───────────────────────────
SYSTEM_PROMPT = """\
You are a helpful hiking trail assistant for UCLA students exploring trails \
near West Los Angeles and the Santa Monica Mountains.

GROUNDING RULES:
1. Answer ONLY using the context passages provided — do not use outside knowledge.
2. If the context does not contain enough information, respond with:
   "I don't have specific information about that in my hiking guide. \
Try checking AllTrails or the trail's official page for the most up-to-date details."
3. Cite the source document for each key claim (e.g. "According to Modern Hiker…").
4. If sources conflict, present both views and note the disagreement.
5. Distinguish facts (mileage, elevation) from opinions (reviewer sentiment).
6. Flag time-sensitive details (conditions, closures) and recommend verification.
7. If the question is outside hiking/trail topics, politely decline.
8. Be concise — lead with the direct answer, then support with context details.

OUTPUT FORMAT:
- Answer the question directly in 2–5 sentences.
- Include practical details when available: distance, elevation gain, difficulty, \
parking, dog policy, and nearby amenities.
- Use bullet points only when comparing multiple trails side by side.
- End with: "Source: <document name(s)>" on a new line."""


# ── Pipeline helpers ─────────────────────────────────────────────────────────

def _build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a numbered context block for the LLM prompt."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk["source"].replace(".txt", "")
        parts.append(f"[Passage {i} — {source}]\n{chunk['text']}")
    return "\n\n---\n\n".join(parts)


def _format_sources(chunks: list[dict]) -> str:
    """Render retrieved passages as a markdown list for the UI sources panel."""
    lines = ["**Passages retrieved for this answer:**\n"]
    for i, chunk in enumerate(chunks, 1):
        name = chunk["source"].replace(".txt", "").replace("_", " ")
        score = round(1 - chunk["distance"], 3)
        lines.append(
            f"**{i}.** {name}  —  relevance score: **{score}**\n"
            f"> {chunk['text'][:200].strip()}…"
        )
    return "\n\n".join(lines)


def generate_answer(
    query: str,
    model: SentenceTransformer,
    collection: chromadb.Collection,
    groq_client: Groq,
) -> tuple[str, str]:
    """
    Stage 4 (Retrieve) + Stage 5 (Generate).
    Returns (answer_markdown, sources_markdown).
    """
    query = query.strip()
    if not query:
        return "Please enter a hiking question.", ""

    # Stage 4 — semantic retrieval
    chunks = retrieve(query, collection, model, k=TOP_K)

    # Stage 5 — grounded generation via Groq
    context_block = _build_context(chunks)
    user_message = f"Context:\n{context_block}\n\nQuestion: {query}"

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
        max_tokens=512,
    )

    answer = response.choices[0].message.content.strip()
    sources_md = _format_sources(chunks)
    return answer, sources_md


# ── Gradio UI ────────────────────────────────────────────────────────────────

def build_ui(
    model: SentenceTransformer,
    collection: chromadb.Collection,
    groq_client: Groq,
) -> gr.Blocks:

    def on_ask(question: str) -> tuple[str, str]:
        try:
            return generate_answer(question, model, collection, groq_client)
        except Exception as exc:
            return f"⚠️ Error generating answer: {exc}", ""

    with gr.Blocks(title="UCLA Unofficial Hiking Guide", theme=gr.themes.Soft()) as demo:

        # Header
        gr.Markdown("# UCLA Unofficial Hiking Guide")
        gr.Markdown(
            "Ask anything about hiking trails near UCLA and West Los Angeles. "
            "Every answer is grounded in curated hiking articles and trail reviews — "
            "no hallucinated facts."
        )

        # Input
        question_box = gr.Textbox(
            label="Your question",
            placeholder="e.g. What is the easiest hike with ocean views near UCLA?",
            lines=2,
        )
        with gr.Row():
            ask_btn = gr.Button("Ask", variant="primary", scale=1)
            clear_btn = gr.Button("Clear", scale=1)

        # Output
        gr.Markdown("### Answer")
        answer_box = gr.Markdown()

        with gr.Accordion("Retrieved sources", open=False):
            sources_box = gr.Markdown()

        # Example questions
        gr.Examples(
            label="Try one of these:",
            examples=[
                "What is the elevation gain of Los Leones Trail?",
                "Which hikes near UCLA have ocean views?",
                "Are dogs allowed on Temescal Canyon Trail?",
                "How difficult is the hike to Sandstone Peak?",
                "Which West LA trail is best for a first-time hiker?",
            ],
            inputs=question_box,
        )

        # Event wiring
        ask_btn.click(
            on_ask,
            inputs=question_box,
            outputs=[answer_box, sources_box],
        )
        question_box.submit(
            on_ask,
            inputs=question_box,
            outputs=[answer_box, sources_box],
        )
        clear_btn.click(
            lambda: ("", "", ""),
            outputs=[question_box, answer_box, sources_box],
        )

    return demo


# ── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set — add it to your .env file.")

    print("Loading embedding model...")
    model = SentenceTransformer(EMBED_MODEL)

    print("Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(COLLECTION_NAME)
    print(f"Collection '{COLLECTION_NAME}' loaded — {collection.count()} vectors.\n")

    groq_client = Groq(api_key=api_key)

    demo = build_ui(model, collection, groq_client)
    print("Launching Gradio — open http://127.0.0.1:7860 in your browser.")
    demo.launch()


if __name__ == "__main__":
    main()
