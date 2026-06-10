# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
I chose this domain because UCLA students most likely prefer outdoor activities such as hiking and this program aims to help them answer most questions about local hiking trails located in West Los Angeles"
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | AllTrails| Blog| documents/extracted/10BestHikesAndTrailsInSantaMonicaMountainsNationalRecreationArea_AllTrails.txt|
| 2 | Campbell Wellman Blog| Blog| documents/extracted/11BeautifulHikesNearWestLA_ Blog_Campbell Wellman.txt|
| 3 | Articles| Blog| documents/extracted/LosLionesCanyonTrail–MyFavoriteDateHikeintheSantaMonicaMountains-LA DateIdeas.txt|
| 4 | Brassy's Blog| Blog| documents/extracted/FavoriteLocalHike_TemescalCanyonTrail_Brassy.txt|
| 5 | Modern Hiker| Blog| documents/extracted/ParkerMesaviaLosLionesTrail-ModernHiker.txt|
| 6 | Modern Hiker| Blog| documents/extracted/TheGrottoTrailin theSantaMonicaMountains_ModernHiker.txt|
| 7 | Articles| Blog| documents/extracted/TheBestHikesinWestLA.txt|
| 8 | Review| Blog| documents/extracted/6BestHikesinLosAngeles(West Side Edition).txt|
| 9 | Articles| Blog| documents/extracted/TheBestHikingTrailsNearWestwoodLosAngeles_ShilianGroup.txt|
| 10 | Personal Blog| Blog| documents/extracted/TemescalCanyonTrail.txt|
| 11 | UCLA News| Blog| documents/extracted/HikingTrailsNearUCLA–BruinLife.txt|

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size: 400 characters**

**Overlap: 100 characters**

**Reasoning:**

- Most documents here list the trails' names and medium-length paragraphs (about 400 characters) for descriptions
- I use 100 characters overlap so that some chunks can have full meaning
- We use recursive chunking because our documents are not all the same types, some have long paragraphs, some have shorter paragraphs. The intuition here is to try to keep paragraphs together; if a paragraph is too long, split at sentences; if a sentence is too long, split at words
---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->


**Embedding model:**

all-MiniLM-L6-v2 via sentence-transformers

**Top-k:**

5 chunks should be enough to give the LLM useful context

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What is the longest hike among the best trails in West Los Angeles Area?| Los Liones Trail|
| 2 | Number 1 hike that is always mentioned in most articles| Temescal Canyon Trail|
| 3 | What is the easiest or shortest hike among these trails?| The Grotto Trail|
| 4 | Which hike is more accessible to restaurants or nearby food?| Eaton Canyon|
| 5 | What is the most challenging hike (longer than 7 miles and high elevation) among the these trails?| Los Liones Trail| |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Noisy or inconsistent documents

2. Chunks that split key information across boundaries

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
```txt
=========================================================================================
                          CUSTOM 5-STAGE RAG PIPELINE
=========================================================================================

[ DATA SOURCE ]
      |
      | (.pdf files)
      v
+-------------+      +------------------+      +--------------------------+
|  STAGE 1    |      |     STAGE 2      |      |         STAGE 3          |
|             |      |                  |      |                          |
| Document    |=====>|    Chunking      |=====>|       Embedding &        |
| Ingestion   |      |                  |      |       Vector Store       |
+-------------+      +------------------+      +--------------------------+
| TOOL:       |      | STRATEGY:        |      | MODEL:                   |
| pdfplumber  |      | Recursive        |      | sentence-transformers    |
|             |      |                  |      | (all-MiniLM-L6-v2)       |
| ACTION:     |      | CONFIG:          |      |                          |
| Extract raw |      | - Size: 500 char |      | DB:                      |
| text from   |      | - Overlap: 100   |      | Chroma DB                |
| PDFs        |      |   char           |      |                          |
+-------------+      +------------------+      +--------------------------+
                                                          ||
                                                          || (Stores vectors
                                                          ||  & metadata)
[ USER QUERY ]                                            ||
      |                                                   vv
      v                                        +--------------------------+
+-------------+                                |      VECTOR DATABASE     |
|    Query    |------------------------------->|       (Chroma DB)        |
|  Embedding  |        (Search Vector)         | +------+ +------+ +------+ |
+-------------+                                | |vec1  | |vec2  | |vec3  | |
                                               | +------+ +------+ +------+ |
                                               +--------------------------+
                                                          ||
                                                          || (Hierarchical/
                                                          ||  Parent search)
                                                          vv
      +---------------------------------------------------+
      |
      v
+-------------+      +------------------+
|  STAGE 4    |      |     STAGE 5      |      [ FINAL ANSWER ]
|             |      |                  |             ^
| Retrieval   |=====>|    Generation    |-------------|
|             |      |                  |
+-------------+      +------------------+
| METHOD:     |      | MODEL:           |
| Recursive   |      | LLM (various)    |
| Search      |      |                  |
|             |      | API:             |
| ACTION:     |      | Groq API         |
| Fetches     |      |                  |
| relevant    |      | INPUT:           |
| full context|      | Query + Context  |
+-------------+      +------------------+

```
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

AI Tool: Claude

Input: All PDFs related to the topcis are saved in the Documents folder.

Expected Output: Python code converts PDFs into text.

Verification: Run the comparison between pdfs and the txt file to make sure it exacts the useful imformation. (Remove irrelavant ads as much as possible)
**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
