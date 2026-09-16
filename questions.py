"""
Your test questions.

Milestone 2 asks you to write five questions your system should be able to
answer from your corpus, specific enough to have a right answer.

  ✗ "What are good dining halls?"          — no right answer
  ✓ "What do students say about wait times at Commons during lunch?"

Fill in `QUESTIONS` below. `expects` is a word or short phrase you'd expect a
correct answer to contain — you'll use it in unit 2 when you build a scorer,
and having written it now means you decided what "correct" meant before you saw
any results.

`OUT_OF_SCOPE` holds five questions your documents clearly don't cover. You
need these in Milestone 4 to find where your relevance cutoff belongs, and
again in unit 2, where `run_eval.py` runs them through the gate and writes what
happened into your run log — that's the evidence for criterion 3.

Swap them for your own if you like. Keep five of them either way: criterion 3
names a target of "4 of 5", and four of three is not a thing.
"""

QUESTIONS = [
    # Written in unit 1, before running any retrieval. Corpus: campus_life.
    #
    # Each `expects` is a phrase that appears verbatim in the document(s) that
    # answer the question, and that does NOT appear in the near-duplicate
    # documents about other buildings, halls, or courses — so a match means
    # the system found the right post, not just a post of the right kind.

    # 1. Dining. Two posts contain the figure (the original and its follow-up),
    #    and no other post mentions "20 to 25 minutes".
    {
        "question": "What are the wait times at Kestrel Commons during lunch?",
        "expects": "20 to 25 minutes",
    },

    # 2. Housing / laundry. The hard one: 7 laundry posts and 7 housing posts
    #    share almost identical wording and differ only by building name and
    #    price. "$1.25" is the Morrow House dryer price and appears in no other
    #    building's post.
    {
        "question": "How much does laundry cost in Morrow House?",
        "expects": "$1.25",
    },

    # 3. Admin rule. Exactly one document covers pass/fail. ("week eight" also
    #    shows up in the CS 340 posts, in a sentence about the term project —
    #    a wrong answer built from those would be about databases, not
    #    pass/fail, so I'll read the answer as well as matching the phrase.)
    {
        "question": "How late in the semester can I declare a course pass/fail?",
        "expects": "week eight",
    },

    # 4. Course workload. Two posts contain it (the course post and its
    #    workload post). The 9 workload posts share boilerplate, so the course
    #    code has to do the work.
    {
        "question": "How does the workload for CS 340 Databases change over the term?",
        "expects": "last three weeks",
    },

    # 5. Admin rule with a distractor: the add/drop post says dropping ends at
    #    week six, and the withdrawal post says withdrawal runs to week ten. A
    #    correct answer has to mention the withdrawal date, not just the drop.
    {
        "question": "What is the deadline to withdraw from a course, and how is it different from dropping?",
        "expects": "week ten",
    },
]

# Questions from a different world entirely. Your gate should refuse all five.
#
# There are five of these because criterion 3 in criteria.md names a target of
# "at least 4 of 5" — you need five things to try before you can report 4 of 5.
# `run_eval.py` runs these through retrieval and the gate on every eval and
# records what happened, so criterion 3 has evidence in the run log alongside
# the others. They cost no model calls: a refusal never reaches the model.
OUT_OF_SCOPE = [
    "What is the capital of Mongolia?",
    "How do I change the oil in a diesel engine?",
    "Who won the 1994 World Cup?",
    "What is the recommended dosage of ibuprofen for a headache?",
    "How do I write a for loop in Rust?",
]


def answered() -> list[dict]:
    """The questions you've actually filled in."""
    return [q for q in QUESTIONS if q.get("question", "").strip()]
