# The Unofficial Guide

Hieu Cao - campus_life

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

I picked the "campus_life" corpus. It answer the general questions that a student might need the answer.

## Chunking Strategy

**Chunk size:** `CHUNK_SIZE = 610` — a soft cap on *body* characters per
chunk (the title line is not counted). Paragraphs are grouped until the next
one would push the body past 600. Cuts happen only at paragraph breaks.
**Overlap:** `CHUNK_OVERLAP = 0`. Instead of overlapping characters, the
document's title line is repeated at the top of every chunk.
**Function:** `chunker.py::split_documents`. Also `MIN_CHUNK = 80`: a
leftover group with a body shorter than 80 characters is folded into the
previous chunk rather than left as a fragment.

**What the starter did first.** `python app.py index` with the starter's
`fallback_split` reported:

```
88 chunks, 317 characters on average (shortest 178, longest 549), produced by chunker.py::fallback_split
```

88 documents, 88 chunks. Nothing in `campus_life` is 800 characters long, so
the fixed-size chunker never cut anything. On `advice_threads` the same
chunker's shortest chunk is 2 characters, the tail of a document that didn't
divide evenly.

**What I noticed reading the posts.** All 88 have one shape: a title line
naming the thing ("Morrow House — what it's actually like", "CS 340
Databases", "Kestrel Commons") and then one to four short paragraphs. Bodies
run 36 to 373 characters per paragraph, median 112. The name is only on the
title line; the useful figure is in a body sentence. And 62 of the 88 posts
come in templated families: 7 buildings × (main, laundry, noise), 9 courses ×
(main, exams, workload), 7 dining halls × (main, follow-up). Within a family
the wording is identical apart from the name and the figure, so a chunk that
loses its title line becomes indistinguishable from six others.

**The decision, and what I changed my mind about.** The question Milestone 3
asks for this corpus is whether a post holding two thoughts should come apart.
I tried it before committing to anything: I simulated paragraph grouping at
body caps of 200, 250, 300 and 400 and read the output for the documents my
test questions depend on.

| Body cap | Chunks | Shortest | Docs split | Chunks under 150 chars |
|---|---|---|---|---|
| 200 | 154 | 90 | 61 of 88 | 42 |
| 250 | 140 | 90 | 50 of 88 | 31 |
| 300 | 123 | 90 | 35 of 88 | 24 |
| 400 | 93 | 123 | 5 of 88 | 2 |

Two things pushed me back to one post per chunk. First, a size cap inside a
post does not separate thoughts, it glues unrelated ones: at 250, Morrow
House's "known damp problem on the ground floor" paragraph landed in the same
chunk as its laundry prices, while the room description above it became a
separate chunk. Second, the corpus authors already did the split for me. The
"two thoughts" in a housing post (description, then laundry and noise) each
have their own dedicated post, `housing_morrow_house_laundry.txt` and
`housing_morrow_house_noise.txt`, and the same is true of exams and workload
for courses and of the follow-ups for dining halls. Splitting the main post
would only add a second copy of a sentence that already has a focused chunk of
its own, and would put 24 to 42 chunks under the 150-character floor in my
criterion 4. At 400 only 5 of 7 housing posts split, which would treat one
template family inconsistently.

So the cap is 600, above the longest body in the corpus (502), and today the
output is 88 chunks from 88 posts, the same count as the starter. The
difference is how it gets there: my function cuts only at paragraph breaks,
never mid-sentence, keeps the title on every chunk, and folds fragments into
their neighbour. On `advice_threads` that takes the shortest chunk from 2
characters to 164, and on `city_guides` it splits each guide at its section
breaks (60 chunks from 14 guides) with each section heading kept with the
paragraph under it. Overlap is 0 because character overlap exists to repair
sentences cut in half, which paragraph cuts never do, and copying text between
neighbours would make this corpus's look-alike posts even more alike.

## Sample Chunks

Output of `python app.py chunks -n 5`, copied as printed. Every chunk is one
whole post, title line first. For each one: could someone answer a question
using only this? Yes. Chunk 1 answers "when does the add/drop window close",
chunk 2 answers "how many hours a week is BIOL 160", chunk 5 answers "how much
is laundry in Innisfree Hall", without reading anything else.

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_biol_160.txt#0` — produced by: `chunker.py::split_documents`

```
BIOL 160 Cell Biology

I lived here my sophomore year. Format is lecture three times a week with a weekly lab. Assessment: four unit tests and a cumulative final. Not curved.

Expect 9 to 11 hours a week, the heaviest first-year course by reputation.

The one piece of advice: the unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

**Chunk 3** — source: `course_hist_118_workload.txt#0` — produced by: `chunker.py::split_documents`

```
Workload for HIST 118 Modern World History

People keep asking so: a lot of reading, about 120 pages a week, but no problem sets. That's real time, not optimistic time.

It's front-loaded — the first month is heavier than the rest, partly because you're learning the format.
```

**Chunk 4** — source: `dining_pellew_dining_hall_followup.txt#0` — produced by: `chunker.py::split_documents`

```
Re: Pellew Dining Hall

Adding to what people have said about Pellew Dining Hall. The wait figure of 12 to 18 minutes at peak matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.

Also worth saying: the furthest hall from anywhere, next to the athletics centre. Nobody tells you this at orientation.
```

**Chunk 5** — source: `housing_innisfree_hall.txt#0` — produced by: `chunker.py::split_documents`

```
Innisfree Hall — what it's actually like

Transferred in last year, so take this with a grain of salt. Built 1991, renovated 2022. Rooms are doubles arranged as pairs sharing one bathroom between two rooms.

The good: the shared-bathroom-between-two-rooms arrangement is the best compromise on campus.

The bad: no air conditioning, which matters for the first three weeks of September.

Laundry costs $1.75 wash, $1.75 dry, app-based. On noise: moderate; the building is L-shaped and the short wing is much quieter.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** How much does laundry cost in Morrow House?

**Answer:**

```
Laundry in Morrow House costs $1.50 for a wash and $1.25 for a dry, and can be paid with coin or card.

Source: housing_morrow_house.txt
```

**My relevance cutoff:**

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

I kept `THRESHOLD = 0.6` and set `TOP_K = 4`.

How I got there:
- In-scope best distances (5 questions): `0.1729, 0.1998, 0.2058, 0.2761, 0.3056`
- Out-of-scope best distances (5 questions): `0.8246, 0.8442, 0.8859, 0.8960, 0.9340`
- The gap is wide: `0.3056` to `0.8246`.

Any cutoff in that gap works. I kept `0.6` because it safely accepts all in-corpus test questions and refuses all out-of-scope ones, with margin on both sides.

| Question | In corpus? | Best distance |
|---|---|---|
| What are the wait times at Kestrel Commons during lunch? | yes | 0.1729 |
| How much does laundry cost in Morrow House? | yes | 0.1998 |
| How late in the semester can I declare a course pass/fail? | yes | 0.2058 |
| How does the workload for CS 340 Databases change over the term? | yes | 0.2761 |
| What is the deadline to withdraw from a course, and how is it different from dropping? | yes | 0.3056 |
| What is the capital of Mongolia? | no | 0.8246 |
| How do I change the oil in a diesel engine? | no | 0.9340 |
| Who won the 1994 World Cup? | no | 0.8859 |
| What is the recommended dosage of ibuprofen for a headache? | no | 0.8442 |
| How do I write a for loop in Rust? | no | 0.8960 |

## How I Used AI

I used AI to help me analyze the errors. Based on the feed back, I changed the code, or the commands.

I also used AI to suggest a good chunking size, test each of them to see which one gave the result that I want.

**1.**

**2.**

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

Source: `results/run_2026-09-23_2326_before.md`, produced by
`run_eval.py::main`. Corpus `campus_life`, `TOP_K = 4`, `THRESHOLD = 0.6`,
3 runs per question, caching off. 15 model calls, 8,935 tokens.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 2. Every answer names a source | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 4. Name kept with the number | 10 of 10, none under 150 | 10 of 10, min 178 | 10 of 10, min 178 | 10 of 10, min 178 | MET |
| 5. No answer cites the wrong source | 0 wrong of 5 | 0 wrong | 0 wrong | 0 wrong | MET |

Criteria 1, 3 and 4 are measured once rather than three times. Retrieval is
deterministic, the gate is a comparison against a fixed number, and chunking
does not vary between runs, so the same figure goes in all three columns. Only
criteria 2 and 5 depend on generation, which does vary — the three runs below
are three different sentences.

### Criterion 1 — real output

Retrieved sources per question, from `store.py::search` at `TOP_K = 4`. The
file containing the `expects` phrase is **bold**; it came back at rank 1 every
time.

| Question | `expects` | Retrieved (rank order) | Best distance |
|---|---|---|---|
| Kestrel Commons wait times | `20 to 25 minutes` | **dining_kestrel_commons_followup.txt**, **dining_kestrel_commons.txt**, dining_the_ridgeway_cafe_followup.txt, dining_halden_hall_followup.txt | 0.1729 |
| Morrow House laundry | `$1.25` | **housing_morrow_house_laundry.txt**, **housing_morrow_house.txt**, housing_old_brewhouse_laundry.txt, housing_innisfree_hall_laundry.txt | 0.1998 |
| Pass/fail deadline | `week eight` | **admin_pass_fail_option.txt**, admin_declaring_a_major.txt, admin_add_drop_deadline.txt, admin_graduation_requirements.txt | 0.2058 |
| CS 340 workload | `last three weeks` | **course_cs_340_workload.txt**, course_cs_210_workload.txt, course_cs_340_exams.txt, **course_cs_340.txt** | 0.2761 |
| Withdrawal deadline | `week ten` | **admin_withdrawal_deadline.txt**, admin_add_drop_deadline.txt, admin_grade_appeals.txt, admin_pass_fail_option.txt | 0.3056 |

### Criteria 2 and 5 — real output

Three runs of the question I predicted would be the miss, copied from the run
log. Each names a source, and each names a Morrow House file:

```
run 1:  In Morrow House, laundry costs $1.50 for a wash and $1.25 for a dry,
        and can be paid with coin or card.

        Source: housing_morrow_house_laundry.txt

run 2:  Laundry in Morrow House costs $1.50 for a wash and $1.25 for a dryer.

        Source: housing_morrow_house.txt

run 3:  Laundry in Morrow House costs $1.50 for a wash and $1.25 for a dry,
        and can be paid with coin or card.

        Source: housing_morrow_house.txt
```

Both cited files contain `$1.25`. No run cited Old Brewhouse or Innisfree Hall,
the two other buildings' laundry posts that were in the prompt context.

### Criterion 3 — real output

From `run_eval.py::check_out_of_scope`, cutoff 0.6. Refused 5 of 5:

| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.825 | refused |
| How do I change the oil in a diesel engine? | 0.934 | refused |
| Who won the 1994 World Cup? | 0.886 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.844 | refused |
| How do I write a for loop in Rust? | 0.896 | refused |

### Criterion 4 — real output

From `python app.py chunks -n 10`, chunks by `chunker.py::split_documents`.
All 10 carry a figure, and all 10 carry the name it belongs to on the title
line. Two of the ten:

```
Workload for PHYS 130 Mechanics            <- source: course_phys_130_workload.txt#0

People keep asking so: 7 hours a week, plus 3 on lab weeks. That's real time,
not optimistic time.

It's front-loaded — the first month is heavier than the rest, partly because
you're learning the format.
```

```
Laundry in Morrow House                    <- source: housing_morrow_house_laundry.txt#0

Machines take $1.50 wash, $1.25 dry, coin or card. There are eight washers and
six dryers for the building, which is the wrong ratio and means the dryers back
up on Sunday evenings.

Best time to do laundry here is Tuesday or Wednesday morning. Sunday after 6pm
you will wait.
```

Index-wide figures from `chunker.py::describe`: `88 chunks, 317 characters on
average (shortest 178, longest 549)`. The 150-character floor holds with 28
characters to spare.

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunks contain the answer, 4 of 5 | **MET** | 5 of 5, and not narrowly: the file holding the `expects` phrase was at rank 1 for all five questions, with 0.16 to 0.27 of distance between it and the nearest wrong file. I checked rank rather than mere presence because at `TOP_K = 4` a chunk at rank 4 would still count as a pass while being one slot from falling out. |
| 2 | Every answer names a source, 15 of 15 | **MET** | Every one of the 15 answers ended with a `Source:` line naming a real file. No gate refusal on an in-corpus question, which was the other way this could have failed. |
| 3 | Gate stops out-of-corpus questions, 4 of 5 | **MET** | 5 of 5 refused. The two I flagged as borderline in unit 1 were not close: ibuprofen came back at 0.844 and the Rust question at 0.896, against a 0.6 cutoff. My worry that "health" would collide with `health_center.txt` was wrong — the embedding separates a topic from a building's opening hours more cleanly than I expected. |
| 4 | Name kept with the number, 10 of 10 and no chunk under 150 chars | **MET** | Read all ten chunks in the sample. Every one contains at least one figure and every one carries the name on its title line, because `split_documents` prefixes the title to every chunk it makes. Shortest chunk in the whole index is 178 characters. |
| 5 | No answer cites the wrong building, hall or course, 0 of 15 | **MET** | Opened each of the 15 cited files and searched for that question's `expects` phrase. All 15 contained it. The Morrow House question is the one that mattered: its prompt context included Old Brewhouse and Innisfree Hall laundry posts, and no run cited either. |

**One correction to disclose.** Question 1's `expects` read `20 to 30 minutes`,
a figure that appears nowhere in `campus_life`; the corpus says `20 to 25
minutes`, which is also what the comment above that line said all along. It was
a transcription slip, caught before this eval ran and fixed in `questions.py`.
The target did not change — only the string I measure it with. Had it gone
uncaught, criteria 1 and 5 would both have scored a false miss on question 1.

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
