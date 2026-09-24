"""
Settings for The Unofficial Guide.

Everything you're likely to change lives here, at the top, on purpose.
You'll edit THRESHOLD in Milestone 4 and the chunking numbers in Milestone 3.

Anything you set in your .env file wins over the defaults here.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")


# ─── The corpus you're working with ──────────────────────────────────────────
# Change this to switch corpora, or pass --corpus on the command line.
# Options are the folder names inside corpora/. See corpora/README.md.

CORPUS = os.getenv("AI201_CORPUS", "campus_life")


# ─── Chunking (Milestone 3) ──────────────────────────────────────────────────
# Set for `campus_life` after reading all 88 posts. Every post is a title line
# plus one to four short paragraphs, 178 to 549 characters in total, and the
# authors already split each subject into topical posts (laundry, noise,
# exams, workload, follow-ups). See README.md → Chunking Strategy.
#
# `split_documents` cuts on paragraph breaks only, never mid-sentence, and
# repeats the title line on every chunk it makes from a document.

CHUNK_SIZE = 600        # soft cap on BODY characters per chunk (title excluded).
                        # Paragraphs are grouped until the next one would push
                        # the body past this. No campus_life post reaches it
                        # (longest body is 502), so today one post = one chunk;
                        # it exists so a longer post is split at a paragraph
                        # break instead of mid-sentence.
CHUNK_OVERLAP = 0       # character overlap exists to repair sentences cut in
                        # half; paragraph cuts never do that, and copying text
                        # between neighbours would make the look-alike posts
                        # in this corpus even more alike. The repeated title
                        # line is the shared context instead.
MIN_CHUNK = 80          # a leftover group with a body shorter than this is
                        # folded into the previous chunk rather than standing
                        # alone as a fragment (the starter made a 2-character
                        # chunk on advice_threads this way).


# ─── Retrieval (Milestone 4) ─────────────────────────────────────────────────

TOP_K = 4               # how many chunks to pull back per question.
                        # Chosen after retrieval checks: 4 kept the best chunk
                        # for every in-scope test question while trimming one
                        # lower-ranked distractor from the prompt context.

# The relevance gate. If the best chunk is further away than this, the system
# refuses to answer instead of handing the model thin material.
#
# LOWER IS BETTER: 0.3 is a close match, 0.9 is unrelated.
#
# 0.6 is a reasonable starting point, not a right answer. Milestone 4 has you
# measure your own two groups of distances and put the cutoff in the gap.
# Most corpora land somewhere between 0.45 and 0.75.
#
# Unit 2: retuned 0.6 -> 0.37. The 0.6 was measured in Milestone 4 against
# out-of-scope questions about Mongolia and diesel engines, which came back at
# 0.825 to 0.934. Any cutoff between 0.31 and 0.82 separated those, so 0.6
# looked safe and told me nothing. Against questions that are campus-shaped but
# uncovered (gym hours, music practice rooms, intramural sign-ups) the real
# negative group starts at 0.435, and 0.6 let 5 of 10 of them through to the
# model. The two groups that matter are:
#
#     in-scope, 5 questions:   0.173  0.200  0.206  0.276  0.306
#     uncovered, 10 questions: 0.435  0.474  0.516  0.547  0.588  0.614 ...
#
# 0.37 is the midpoint of that gap. It refuses all 10 uncovered questions and
# still accepts all 5 in-scope ones, but the margin is now ~0.065 on each side
# rather than ~0.5, so a new in-scope question phrased unlike my five could be
# refused. See README.md -> What's Still Broken.
THRESHOLD = 0.37


# ─── Models ──────────────────────────────────────────────────────────────────
# Embeddings run on your own machine and cost no API quota.
# Only generation calls out to a service.

# This is the model Chroma bundles, and leaving it alone is the fast path: it
# downloads about 80 MB from Chroma's own CDN and needs nothing else installed.
#
# Setting it to any other name — unit 2's "try a second embedding model"
# stretch option — switches to loading that model from Hugging Face instead,
# which needs `pip install 'sentence-transformers>=3.4,<3.5'` first. store.py
# says so with a real error message rather than a stack trace if you forget.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MODEL = os.getenv("AI201_MODEL", "gemini-3.5-flash-lite")


# ─── Rate limiting and quota guards ──────────────────────────────────────────
# You should not need to touch these. They exist so that a runaway loop costs
# you a warning instead of your whole day's allowance.

REQUESTS_PER_MINUTE = 30       # outgoing calls the limiter will allow per minute
SESSION_REQUEST_BUDGET = 300   # stop and warn rather than draining the daily quota
MAX_RETRIES = 4                # on 429 / resource-exhausted, with backoff

CACHE_ENABLED = os.getenv("AI201_CACHE", "1") != "0"
CACHE_DIR = ROOT / ".cache"


# ─── Paths ───────────────────────────────────────────────────────────────────

CORPORA_DIR = ROOT / "corpora"
CHROMA_DIR = ROOT / "chroma_db"
RESULTS_DIR = ROOT / "results"


def corpus_path(name: str | None = None) -> Path:
    """Folder holding the documents for a corpus."""
    return CORPORA_DIR / (name or CORPUS) / "documents"


def collection_name(name: str | None = None, variant: str = "default") -> str:
    """
    Name of the vector-store collection for a corpus.

    `variant` lets you index the same corpus two different ways and query both
    without deleting anything — you'll want that in unit 2 when you compare
    chunking strategies.

    Chroma is fussy about collection names: 3 to 63 characters, starting and
    ending with a letter or digit, and nothing but letters, digits, underscores
    and hyphens in between. If you bring your own corpus and name the folder
    something Chroma won't accept, this cleans it up rather than failing.
    """
    import re

    raw = f"{name or CORPUS}__{variant}"
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "-", raw)
    cleaned = cleaned.strip("_-")          # must start and end alphanumeric
    if not cleaned or not cleaned[0].isalnum():
        cleaned = f"c{cleaned}"
    if not cleaned[-1].isalnum():
        cleaned = f"{cleaned}0"
    return cleaned[:63].rstrip("_-") or "collection"
