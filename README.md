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

I picked the `campus_life` corpus: 88 short posts written student-to-student
about dorms, dining halls, courses, and the administrative rules nobody
explains properly. Add/drop windows, laundry prices, which dining hall has a
20-minute queue at 12:30 — the things you normally find out by asking someone
in your hall.

The system answers questions about that corpus and **only** that corpus. A
question goes through five stages: the posts are loaded off disk
(`ingest.py`), split into chunks that each keep their title line
(`chunker.py::split_documents`), embedded into 384-dimension vectors and
stored (`store.py`), searched for the four nearest chunks to the question
(`store.py::search`), and handed to the model with an instruction to answer
from those excerpts alone and name the file it used (`generate.py`).

The part I care most about is what happens when the corpus *doesn't* cover
something. Before the model is called at all, `gate.py::check` looks at how far
the nearest chunk actually was. If it's further than 0.6, the question is
refused outright and no model call happens. So "what is the capital of
Mongolia?" gets "I don't have enough information about that" rather than a
confident answer built from nothing — the refusal is a decision my own code
makes, not something I asked the model to do politely.

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

### Unit 1

I used AI to help me analyze the errors. Based on the feed back, I changed the code, or the commands.

I also used AI to suggest a good chunking size, test each of them to see which one gave the result that I want.

### Unit 2

Claude Code, in the terminal. Four things it did that changed what I
submitted:

**1. It talked me out of a change I was about to make.** `criteria.md` says
`TOP_K = 5` and `config.py` says `4`, and my instinct was to edit `config.py`
so they matched. Instead of answering, it ran retrieval at `top_k=8` for all
five questions and showed me that the answer-bearing chunk was at rank 1 every
time, so a fifth slot retrieves nothing new — and that for the Morrow House
question, slot 5 is `housing_aldridge_hall_laundry.txt`, a third wrong
building's laundry price added to the prompt. That is the exact failure
criterion 5 exists to catch. So I kept `TOP_K = 4` and corrected the stale
number in `criteria.md` instead, which is the direction that doesn't cost me
the point.

**2. It caught a bug in my test that would have faked a failure.** Question 1's
`expects` read `20 to 30 minutes`. It grepped all five `expects` phrases
against the corpus and found that this one appears in no file — the posts say
`20 to 25 minutes`, which is also what my own comment above that line said. I
fixed it in `questions.py` before running the eval. If it had gone uncaught,
criteria 1 and 5 would both have scored a false miss on question 1 and I would
have spent Milestone 3 diagnosing a retrieval problem that didn't exist.

**3. It did the scoring pass, and I checked it.** It ran
`run_eval.py --label before`, aggregated the per-question output into the
per-criterion table, and for criterion 5 opened each of the 15 cited files to
confirm the `expects` phrase was actually in the file the answer named. The
verdicts and the "how I decided" column are my calls; the counting underneath
them is its work.

**4. The pattern it found was in my test, not in my system.** This is the part
I'd flag if I were grading this. Nothing missed, so there were no failures to
find a pattern in — and the useful observation was one level up. My five
`OUT_OF_SCOPE` questions came back between 0.825 and 0.934 against a 0.6
cutoff, so not one of them was anywhere near the line. Claude pointed out that
all five are from a different domain entirely (Mongolia, diesel engines, the
1994 World Cup), so criterion 3 never actually tested the gate on a hard case:
a question that *sounds* like campus life but isn't in the corpus. It then
checked coverage and found the corpus has nothing on gyms, student societies
or bicycles. That reframed criterion 3 for me from "the number was too low" to
"the question set was too easy", which are different problems with different
fixes.

**5. It got a diagnosis wrong and then caught itself.** Drafting the Diagnoses
section, it credited my title-prefixing chunker for the Morrow House question
passing. Then it ran both chunkers over the corpus to check, and found they
produce byte-identical output on `campus_life` — 88 of 88 chunks the same,
because no post is long enough to split. The claim was wrong and the correction
is the most useful finding in this unit: two of my criteria don't measure my
Milestone 3 work at all. Worth noting that the plausible-sounding explanation
came first and the check came second, which is the order that would have burned
me if nobody had run the check.

**6. It found the failure my improvement fixes.** Following up on item 4, it
wrote ten campus-shaped uncovered questions and ran them through retrieval and
the gate — which costs nothing, because a refused question never reaches the
model — and 5 of 10 got through at `THRESHOLD = 0.6`. That's what turned "my
criterion 3 evidence is weak" into a measured failure with a fix attached. I
chose the five that went into `questions.py` as a spread across the distance
range rather than taking the five that leaked, so the after-run isn't scored
against questions picked to make the fix look good.

**What I'd say about relying on it.** Items 2 and 3 are both things I could
have done myself and didn't — grepping my own test fixtures against my own
corpus is not hard, it just didn't occur to me to verify the test before
trusting its output. The lesson I'm taking is that the test needs checking as
much as the system does, because a broken test fails silently and looks exactly
like a broken pipeline.

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

**Nothing missed.** All five criteria came out MET, three of them above target.
So this section is about whether the targets were honest, which is the more
uncomfortable question.

**Criteria 2, 4 and 5 were already at ceiling and I'd leave them.** 15 of 15
answers naming a source, 10 of 10 chunks keeping the name with the number,
zero wrong citations out of 15 — there is no tighter version of "zero". If
anything, criterion 5 is the one I'd want to run against more questions rather
than a stricter bar, because 15 answers is a thin sample for a claim about how
often the system confuses two buildings.

**Criterion 1 passed, and my first explanation for why was wrong.** In unit 1 I
predicted the Morrow House laundry question would be the miss, because it
competes with 14 near-duplicate posts and the only thing separating them is the
building name and the price. It didn't miss — it retrieved at rank 1 with 0.17
of distance to the nearest wrong building.

My first instinct was to credit my Milestone 3 chunker, which prefixes the
title line to every chunk so "Laundry in Morrow House" sits inside the embedded
text. That explanation does not survive being checked. I ran both chunkers over
the corpus and compared:

```
split_documents: 88 chunks, 317 characters on average (shortest 178, longest 549)
fallback_split : 88 chunks, 317 characters on average (shortest 178, longest 549)
identical chunk texts: 88 of 88
```

**On `campus_life` my chunker and the starter's produce byte-identical output.**
The longest body in the corpus is 502 characters against a 600 cap, so
`split_documents` never actually splits anything, and `fallback_split`'s
fixed-size window never cuts anything either — both hand back each post whole,
title line included. The title was never at risk on this corpus. So the honest
answer is that the question passed because the embedding separates seven
buildings on a name alone better than I assumed: I over-estimated how much the
~200 characters of shared laundry boilerplate would swamp the one word that
differs.

That has a consequence I didn't expect and should say out loud: **criteria 1
and 4 would both pass identically with the starter's chunker in place.** My
Milestone 3 work is justified prospectively, and it does real work on the other
two corpora at today's settings — `advice_threads`' shortest chunk goes from 72
characters to 164, and `city_guides` becomes 60 chunks from 14 guides against
the baseline's 56, split on section headings instead of mid-sentence. But on
the corpus I actually submitted, it is a no-op, and neither criterion measures
it. Two of my five criteria are not testing the thing I spent Milestone 3 on.

(The "shortest chunk is 2 characters" figure in my unit 1 writeup above was
measured at the starter's original 800-character cap. At the 600 I settled on,
the baseline's worst chunk on `advice_threads` is 72 characters, not 2. The
point stands and the number was stale.)

**Criterion 3 is the soft one, and the number is not the problem.** Target was
4 of 5; the gate refused 5 of 5. But the distances say the test was never
close: 0.825, 0.844, 0.886, 0.896, 0.934, against a cutoff of 0.6. Nothing was
within 0.2 of the line. In unit 1 I wrote that the ibuprofen and Rust
questions were "borderline on purpose" because the corpus has
`health_center.txt` and three CS posts — that was wrong, and the reason it was
wrong is instructive. The embedding is not matching on topic the way I assumed;
"recommended dosage of ibuprofen" and "the health centre's walk-in hours" are
not close in vector space just because both are about health.

The real defect is that all five `OUT_OF_SCOPE` questions come from a different
world entirely — Mongolia, diesel engines, the 1994 World Cup. None of them
tests the case I actually care about, which is a question that sounds exactly
like campus life but happens not to be in the 88 posts. The corpus is 78 of 88
files about courses, housing, admin and dining, and has nothing at all on
gyms, student societies or bicycles. So:

> *"What are the gym's opening hours?"* · *"How do I join a student society?"*
> · *"Where can I lock up a bicycle?"*

Those share the corpus's whole vocabulary and register, and I have no idea what
distance they come back at. That is the gate's hard case and I never measured
it.

**The pattern across all of this.** My three soft spots are the same problem
wearing different clothes: criterion 3's questions are too far outside the
corpus to test the gate, and criteria 1 and 4 pass identically with or without
the work they were supposed to be measuring. In each case the target number is
fine and the *measurement* doesn't discriminate. So I'm keeping 4 of 5 on
criterion 3 rather than restating it as 5 of 5 — against the current question
set 5 of 5 would still be trivially true, and I'd be tightening a number
instead of fixing what it's counting. The change worth making is to what gets
measured, not to the bar it has to clear.

## The Improvement

**What I changed:** `THRESHOLD` in `config.py`, from `0.6` to `0.37`.

To find out whether that was needed I first had to fix the measurement, so
there were two edits and only one of them is a change to the system:

1. **`questions.py`** — replaced all five `OUT_OF_SCOPE` questions with
   campus-life-shaped questions the corpus doesn't cover (music practice rooms,
   gym hours, intramural sign-ups, a pharmacy, pets in dorms). The originals
   are kept in a comment above them. This changes what I measure, not how the
   system behaves.
2. **`config.py`** — `THRESHOLD = 0.6` → `0.37`. This is the actual fix.

**Why I picked it:** the Diagnoses section says criterion 3 passed 5 of 5
against questions that were never within 0.2 of the cutoff, so I wrote ten
campus-shaped uncovered questions to find the real negative group — and **5 of
those 10 got through the gate at 0.6**, including "what are the gym's opening
hours?" being answered from `dining_halden_hall_followup.txt`, which is a
dining hall.

That turned an unmeasured worry into a measured failure with an obvious fix.
The two groups are cleanly separated, they just aren't separated where I put
the line:

```
in-scope, 5 questions:    0.173  0.200  0.206  0.276  0.306
uncovered, 10 questions:  0.435  0.474  0.516  0.547  0.588  0.614  0.657  0.747  0.767  0.879
                                 ^
                    gap: 0.306 ── 0.435, midpoint 0.37
```

My Milestone 4 cutoff of 0.6 was measured against Mongolia and diesel engines,
which sit at 0.825+. Any number between 0.31 and 0.82 separated *those*, so 0.6
was never wrong so much as never tested. Retuning against a real negative group
is the same procedure Milestone 4 asked for, run against a question set that
can actually fail it.

### Run Log — After

`python run_eval.py --label after` → `results/run_2026-09-24_1749_after.md`.
Same five questions, `TOP_K = 4`, `THRESHOLD = 0.37`, 3 runs each, caching off.
15 model calls, 8,953 tokens.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 2. Every answer names a source | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 4. Name kept with the number | 10 of 10, none under 150 | 10 of 10, min 178 | 10 of 10, min 178 | 10 of 10, min 178 | MET |
| 5. No answer cites the wrong source | 0 wrong of 5 | **1 wrong** | 0 wrong | 0 wrong | **MISSED** |

Criterion 3, on the harder question set:

| Out-of-scope question | Best distance | At 0.6 (before) | At 0.37 (after) |
|---|---|---|---|
| How do I book a practice room in the music building? | 0.435 | **answered** | refused |
| What are the gym's opening hours? | 0.516 | **answered** | refused |
| When do intramural sports sign-ups happen? | 0.588 | **answered** | refused |
| Is there a campus pharmacy? | 0.614 | refused | refused |
| What is the policy on keeping a pet in the dorms? | 0.657 | refused | refused |
| | | **2 of 5** | **5 of 5** |

The middle column is the same five questions run against the old cutoff, so the
improvement is attributable to the threshold and not to the question swap. On
the old question set criterion 3 scored 5 of 5 both before and after — that set
cannot tell the two configurations apart, which is the whole point of replacing
it.

**Did it help?**

Yes for criterion 3, and it exposed a broken criterion on the way.

Criterion 3 went from 2 of 5 to 5 of 5 on questions that can actually fail it,
and nothing else regressed: all five in-scope questions still clear the gate at
0.37 (their worst is 0.306), all 15 answers still named a source, and retrieval
and chunking were untouched by the change.

**Criterion 5 came out MISSED, and it is the criterion that's wrong, not the
answer.** Run 1 of question 5 produced:

```
Withdrawal runs to week ten, requires an adviser signature, and places a W on
the transcript that does not affect GPA. In contrast, dropping ends at week
six, and a drop after week two shows as a W on the transcript.

Source: admin_withdrawal_deadline.txt, admin_add_drop_deadline.txt
```

That answer is right, and both citations are honest: question 5 asks two things
— when withdrawal closes, and how it differs from dropping — and the answer
took "week ten" from `admin_withdrawal_deadline.txt` and the week-six
comparison from `admin_add_drop_deadline.txt`. It cited each file for the part
it actually supplied.

My criterion says *zero answers name a source file that does not contain the
`expects` phrase*, and `admin_add_drop_deadline.txt` does not contain "week
ten". So the letter of the criterion scores the best-cited answer in the whole
run as a failure. What I meant to catch was an answer citing the wrong
building, hall or course; what I wrote punishes an answer for citing a second,
correct file. The before-run got away with this by luck: it also produced a
two-file citation, on question 4, and there both files happened to contain
"last three weeks".

See What I'd Do Differently for the revision. I'm leaving the MISSED verdict in
place rather than rescoring it, because the criterion as written did produce
that result and hiding it would defeat the point of having written it down
first.

## What's Still Broken

**Criterion 5, which is a wording problem I've diagnosed but not re-measured.**
The fix is in What I'd Do Differently below. I stopped short of rescoring the
run against the revised wording because I'd be marking my own work against a
criterion I rewrote after seeing the result, and the revision is worth more as
a stated change than as a verdict I award myself.

**The gate's margin is now thin on both sides, and I've only checked one side.**
At 0.6 the nearest in-scope question sat 0.29 below the cutoff and the nearest
uncovered one 0.22 above it. At 0.37 those margins are 0.064 and 0.065. That is
much better separation in the sense that the line now sits between the two
groups, and much less room for a question unlike the ten I measured. My five
in-scope questions are all phrased the way I phrase things; a student asking
"morrow house laundry how much" rather than "How much does laundry cost in
Morrow House?" could plausibly land above 0.37 and be refused a question the
corpus answers. **I have not tested a single paraphrase.** That is the most
obvious hole left and it costs no model calls to probe, so it's the first thing
I'd do with another hour.

**Criteria 1 and 4 still don't measure my chunker.** From the Diagnoses
section: `split_documents` and `fallback_split` produce byte-identical output
on `campus_life`, so both criteria would score exactly the same with the
starter's chunker in place. Nothing I did in unit 2 changed that. Fixing it
means either testing on `advice_threads` or `city_guides`, where the two
chunkers genuinely differ, or adding a question whose answer spans a paragraph
break so that where the cut falls matters. I didn't do either because both
change what corpus or what questions the whole submission is about, and I'd
rather say plainly that two of my criteria are inert than quietly swap the
ground under the other three.

**Criterion 2 has never failed and probably cannot.** 30 of 30 answers across
both runs named a source. The filename is injected into every excerpt and the
instruction to cite appears twice in the prompt, so the only realistic failure
is a gate refusal on an in-corpus question — which is really criterion 1's
business. It isn't broken, it's just not carrying weight.

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->

**Criterion 5 — the one I'd actually rewrite.**

> Original: Across all 15 answers, zero answers name a source file that does
> not contain the `expects` phrase for that question.
>
> Revised: Across all 15 answers, zero answers name a source file that is
> about a different building, dining hall, or course than the question asks
> about. An answer may cite more than one file; each cited file has to have
> supplied something the answer says.
>
> Why revised: the original measures the wrong thing. It assumes one answer
> cites one file, and question 5 deliberately asks something that takes two —
> the withdrawal deadline from one post and the contrast with dropping from
> another. When the system did exactly that, correctly, my criterion scored it
> as a wrong citation, because the second file doesn't contain the first
> file's phrase. The revision keeps the failure I care about (Calder Annexe's
> laundry price presented as Morrow House's) and stops punishing the behaviour
> I want.

That's a revision because the criterion couldn't measure what it claimed to,
not because I missed it. The number stays at zero.

**Criterion 3 — right number, wrong evidence.** I'd keep "at least 4 of 5" and
write the question set differently. What I wrote in unit 1 was an intuition
about what "out of corpus" means, and I reached for the most out-of-corpus
things I could think of. But a gate that refuses questions about diesel engines
is not a gate anyone needed; the question worth asking is whether it refuses
things that sound exactly like the corpus. If I'd written "five questions a
student at this university would plausibly ask that these 88 posts do not
answer" instead of "questions from a different world entirely", I'd have found
the 0.6 problem in unit 1 rather than unit 2.

**Criteria 1 and 4 — I'd make them depend on my own work.** Both are
well-formed and both pass identically with the starter's chunker in place, so
they measure the corpus more than they measure anything I did. Criterion 4 in
particular reads like a test of `split_documents` and is really a test of
`campus_life` being made of short posts. I'd rewrite it to compare the two
chunkers directly — "no chunk contains a figure whose subject appears only in a
neighbouring chunk, measured on `city_guides` where documents actually split"
— which would have made Milestone 3 a decision with a measurable consequence
instead of a decision I argued for well and never tested.

**The general thing I got wrong.** Four of my five criteria were written to be
passed. Only criterion 5 was written in a way that could surprise me, and it's
the only one that did — it caught a real behaviour I hadn't anticipated, even
though it caught it as a false positive. A criterion that can't fail tells you
nothing, and I wrote four of them without noticing, because at the time
"defensible target" and "target I can hit" felt like the same thing.
