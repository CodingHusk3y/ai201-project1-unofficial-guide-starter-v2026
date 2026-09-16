# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**

Corpus: `campus_life`, 88 posts, `TOP_K = 5`. Four of my five questions have
one or two documents that contain the answer and use vocabulary nothing else
in the corpus uses ("Kestrel Commons", "pass/fail", "CS 340", "withdrawal").
The fifth, "How much does laundry cost in Morrow House?", competes with 14
near-duplicate posts: all 7 `housing_*_laundry.txt` files share the same
~200 characters of boilerplate about eight washers and Sunday evenings, and
all 7 `housing_*.txt` files share the same "what it's actually like" template.
The only thing that distinguishes Morrow House's post is the building name and
the price, so with 14 look-alikes and only 5 slots I expect that one to be the
miss. I'm not saying 3 of 5 because a system that only handles the easy four
would pass 3 of 5 without the hard question ever being tested.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**

Measured over all 15 answers to my five in-corpus questions (5 questions × 3
runs). I'm asking for 15 of 15 because the filename is injected into every
excerpt as `[from <file>]` by `generate.py::build_prompt`, and the model is
told to name the file twice: once in the system instruction and again at the
end of the prompt. The only ways this fails are the model ignoring both
instructions, or the gate refusing an in-corpus question and returning the
fixed refusal string, which names nothing. Either of those is a real defect I
want counted, so a refusal on one of my five questions counts as a failure
here, not as a pass.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**

The cutoff is still the starter default, 0.6 in `config.py`; I have not
measured the two groups of distances yet, so this is a prediction, not a
reading. Three of the five `OUT_OF_SCOPE` questions (Mongolia, diesel oil, the
1994 World Cup) share no vocabulary with a corpus about dorms, dining halls and
course workloads, and I expect them to be refused easily. The other two are
borderline on purpose: the ibuprofen question is a health question and the
corpus has `health_center.txt`; the Rust for-loop question is a programming
question and the corpus has three CS posts. If either of those lands under 0.6
it will be one of them, so 4 of 5 leaves room for exactly one near miss. 5 of
5 would be claiming the gate separates "health" from "the health centre's
walk-in hours" before I've seen a single distance.

---

## 4. Every chunk keeps the name with the number

In a sample of 10 chunks from `python app.py chunks -n 10`, 10 of 10 that
contain a figure (a price, a time, an hours-per-week number, a week number)
also contain the name of the building, dining hall, course, or policy that
figure belongs to, and no chunk in the whole index is shorter than 150
characters.

**Why this target:**

I read every file in `campus_life`. All 88 are between 183 and 554 characters
and have the same shape: a title line naming the thing ("Morrow House — what
it's actually like", "CS 340 Databases", "Kestrel Commons") followed by two to
five short paragraphs. The name lives on the title line and the useful figure
lives in a body sentence, and 62 of the 88 posts (7 buildings × 3 posts,
9 courses × 3 posts, 7 dining halls × 2 posts) are templated near-duplicates
whose body text is identical apart from that name and that figure. So a chunk
that has "$1.50 wash, $1.25 dry" but not "Morrow House" is not slightly worse,
it is indistinguishable from six other buildings' chunks. That is why the
target is 10 of 10 and not 9 of 10: chunking is deterministic and a single
failure in the sample means a whole template family (all seven laundry posts,
say) is broken the same way. The 150-character floor comes from the shortest
post being 183 characters, so any chunk under 150 can only be a title line
with no body under it. I'm keeping one post per chunk unless Milestone 3 gives
me a reason not to, and this criterion is what would tell me a split had gone
wrong.

---

## 5. No answer cites the wrong building, hall, or course

Across all 15 answers to my five test questions (5 × 3 runs), zero answers
name a source file that does not contain the `expects` phrase for that
question. Checked by opening each file an answer names and searching for the
phrase. An answer that says it doesn't have enough information and names no
file is not a wrong citation (it fails criterion 2 instead).

**Why this target:**

Criterion 2 says a source is named; this says the named source is the right
one, which for this corpus is the thing I actually care about. The failure I
expect from `campus_life` is specific: the housing, laundry, noise, dining and
course posts come in look-alike families, so the realistic wrong answer is
not nonsense but Calder Annexe's laundry price presented as Morrow House's,
with `housing_calder_annexe_laundry.txt` cited as if it settled the matter. A
student who trusts that walks to the wrong building. One wrong citation in 15
is about 7%, and I would rather the system refuse than be confidently wrong
one time in fifteen, so the target is zero. It should be reachable: the model
never sees a chunk without its filename attached, so a wrong citation means it
either mixed up two excerpts or answered from a chunk that didn't contain the
answer, and both are things I want to find out about.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
