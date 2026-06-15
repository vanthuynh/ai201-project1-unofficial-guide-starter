# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

#### I chose this domain because a lot of UCLA students love outdoor activities such as hiking. This program aims to help them answer most questions about local hiking trails located in West Los Angeles". There are also mixed sources of hiking trail reviews such as personal blogs, campus's news, etc. so this interactive guide can consolidate those information and provide answer right away.
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|-------------|-----------------|
| 1 | AllTrails| Blog| documents/extracted/10BestHikesAndTrailsInSantaMonicaMountainsNationalRecreationArea_AllTrails.txt|
| 2 | Campbell Wellman Blog| Blog| documents/extracted/11BeautifulHikesNearWestLA_ Blog_Campbell Wellman.txt|
| 3 | LA Date Ideas| Article| documents/extracted/LosLionesCanyonTrail–MyFavoriteDateHikeintheSantaMonicaMountains-LA DateIdeas.txt|
| 4 | Brassy's Blog| Blog| documents/extracted/FavoriteLocalHike_TemescalCanyonTrail_Brassy.txt|
| 5 | Modern Hiker| Blog| documents/extracted/ParkerMesaviaLosLionesTrail-ModernHiker.txt|
| 6 | Modern Hiker| Blog| documents/extracted/TheGrottoTrailin theSantaMonicaMountains_ModernHiker.txt|
| 7 | Elden Team| Articles| documents/extracted/TheBestHikesinWestLA.txt|
| 8 | Alyssa Ponticello| Blog| documents/extracted/6BestHikesinLosAngeles(West Side Edition).txt|
| 9 | ShilianGroup| Articles| documents/extracted/TheBestHikingTrailsNearWestwoodLosAngeles_ShilianGroup.txt|
| 10 | Alltrails| Article| documents/extracted/TemescalCanyonTrail.txt|
| 11 | Bruin Life| UCLA News| documents/extracted/HikingTrailsNearUCLA–BruinLife.txt|

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->


**Final chunk count: 173**

**Chunk size: 400 characters**

**Overlap: 100 characters**

**Reasoning:**

- Most documents here list the trails' names and medium-length paragraphs (about 400 characters) for descriptions
- I use 100 characters overlap so that some chunks can have full meaning
- We use recursive chunking because our documents are not all the same types, some have long paragraphs, some have shorter paragraphs. Additionally, the source documents are mixed with personal blogs, news articles, and campus news, taking more chunk size can cause more noise.

**Sample Chunks**

#### Question: How far away from UCLA is Saddle Peak trail?

1. HikingTrailsNearUCLA–BruinLife — relevance score: 0.561

Peak Distance from UCLA: 20.9 miles Difficulty Level: Moderate / Difficult The Stunt High Trail to Saddle Peak is one of L.A.’s best kept secrets, as it is less popular and publicized than other inclu…

2. HikingTrailsNearUCLA–BruinLife — relevance score: 0.277

yline, the Hollywood sign, and Venice Beach. 2. Mandeville Canyon Fire Road Distance from UCLA: 3.3 miles Difficulty Level: Moderate The closest trail to UCLA located in our neighboring Brentwood is M…

3. HikingTrailsNearUCLA–BruinLife — relevance score: 0.241

er, intermediate, and advanced. Runyon Canyon also has an off-leash dog par attached to it as well as a yoga studio within the park that is however unfortunately closed during the COVID-19 pandemic. 5…

#### Question: Are dogs allowed on Temescal Canyon Trail?

2. LosLionesCanyonTrail–MyFavoriteDateHikeintheSantaMonicaMountains-LA DateIdeas — relevance score: 0.306

check out my list at TheFrugalNoodle.com: My No-Nonsense Day Hike Checklist Note that dogs are not allowed on this trail. Getting There and Parking It’s really easy to get to Los Liones Canyon. Take P…

3. TemescalCanyonTrail — relevance score: 0.259

ver there are some no-shade parts of this trail where the trail is exposed. On a clear day at the summit, you may be able to see the San Gabriel Mountains to Catalina. Dogs are only allowed at the bot…

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Embedding model:**

all-MiniLM-L6-v2 via sentence-transformers

**Top-k:**

3 chunks should be enough to give the LLM useful context for answering exact details/facts
5 chunks is useful to changeable topic such as weather conditions, parking, trail reviews, etc.

**Production tradeoff reflection:**

- Pros: all-MiniLM-L6-v2 is a lightweight model with fast inference and no API key dependency, fully self-hosted.

- Cons: The model has the context length limit of 256 tokens, which may not be the best option for long blog posts and long reviews


---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

GROUNDING RULES:
1. Answer ONLY using the context passages provided — do not use outside knowledge.
2. If the context does not contain enough information, respond with:
   "I don't have specific information about that in my hiking guide. Try checking AllTrails or the trail's official page for the most up-to-date details."
3. Cite the source document for each key claim (e.g. "According to Modern Hiker…").
4. If sources conflict, present both views and note the disagreement.
5. Distinguish facts (mileage, elevation) from opinions (reviewer sentiment).
6. Flag time-sensitive details (conditions, closures) and recommend verification.
7. If the question is outside hiking/trail topics, politely decline.

**How source attribution is surfaced in the response:**

- Answer the question directly in 2–5 sentences.
- Include practical details when available: distance, elevation gain, difficulty, \
parking, dog policy, and nearby amenities.
- Use bullet points only when comparing multiple trails side by side.
- End with: "Source: <document name(s)>" on a new line."""

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What is the elevation gain of Los Liones Trail?| 1292ft| "The elevation gain of Los Liones Trail is 1292 ft, according to Modern Hiker. This hike takes you nearly 1,300 feet above sea level, as also mentioned in TheBestHikesinWestLA..."| Relevant| Accurate|
| 2 | How far away from UCLA is Saddle Peak trail?| 20.9 miles| "The Saddle Peak trail is 20.9 miles away from UCLA..."| Relevant| Accurate|
| 3 | Which hike is always mentioned in most articles about West LA trails?| Los Leones Trail| "...the provided passages do not specifically mention a particular hike that is always mentioned in most articles but they do not provide a consistent recommendation for a single hike..."| Partially relevant| Partially accurate|
| 4 | What is Los Leones trail parking condition?| Free street parking and busy on Weekend| "...multiple parking options, including a small parking area along Los Liones Drive, as well as street parking and a few parking lots along the way...."| Relevant| Partially accurate|
| 5 | Which hikes have ocean/beach views?| Los Leones Trail, Temescal Canyon Trail, and the Grotto Trail| Temescal Canyon Trail and the Grotto Trail| Relevant| Partially accurate|

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

Which hikes near UCLA have ocean views?

**What the system returned:**

Temescal Canyon Trail offers great ocean views, making it a favorite among locals. This 3.8-mile loop trail is located in Pacific Palisades, near Santa Monica, and provides epic photo opportunities. 

**Root cause (tied to a specific pipeline stage):**

The system found that Temescal Canyon Trail is a 3.8-mile loop trail so it returned Temescal Canyon Trail as the answer but the trail is not located near UCLA. The ingest documents didn't have any information about any trails with ocean views that is located near UCLA. Most trails within UCLA's proximity don't have ocean views.

**What you would change to fix it:**

Even though the grounding rules are very detailed and specifically instruct the system not provide answers that it doesn't know correct, the system believed the information which it was ingested and embeded with is correct. One way that can help is to only ingest with only hiking trail articles that is tied with UCLA proximity (ingestion stage). That being said, increasing the chunk size and top-k (embeded and retrieve) may also provide the system more context before providing the answer.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

The planning.md file was especially helpful with Chunking stage of the pipeline. It helped me carefully choose the Chunking strategy and the reasoning behind it. 

**One way your implementation diverged from the spec, and why:**

I first chose chunking size of 600 and overlap size of 150 characters. The chunking resulted from that cover a lot more unnecessary data, which lead to distance score greater than 0.5 per chunking results for all 5 evaluation questions.


---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* I first implemented the PDF file extraction script myself but later realize that there were still a lot of irrelevant text left. I asked Claude to review the extracted step and specified which data I still need to clean before ingestion.
- *What it produced:* improved ```extract_pdfs.py``` with much more regex to remove time, footer content, etc. within the articles and reviews.
- *What I changed or overrode:* I read over the extracted data files and found that website's menu options are still included in the extracted files so I added more regular expression to remove those as well

**Instance 2**

- *What I gave the AI:* I always spend too much time designing any user interface so I requested help from Claude code to build an interactive interface with Gradio and connect generation code to it
- *What it produced:* a working website that can answer hiking trails questions near UCLA
- *What I changed or overrode:* I added example questions and 
