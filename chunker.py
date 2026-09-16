"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def _paragraphs(text: str) -> list[str]:
    """Non-empty paragraphs, in order. `ingest.clean_text` has already
    collapsed runs of blank lines to one, so a blank line is the boundary."""
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def _is_heading(paragraph: str) -> bool:
    """A section label rather than content: a Markdown heading, or a short
    line with no sentence-ending punctuation ("Getting around"). campus_life
    has none of these in post bodies; city_guides is made of them."""
    if paragraph.startswith("#"):
        return True
    return len(paragraph) < 60 and "\n" not in paragraph and paragraph[-1] not in ".!?)"


def _attach_headings(paragraphs: list[str]) -> list[str]:
    """Glue each heading to the paragraph after it, so a heading can never be
    the last thing in one chunk while its content is the first thing in the
    next. A heading with nothing after it stays as it is."""
    merged: list[str] = []
    pending: list[str] = []
    for paragraph in paragraphs:
        if _is_heading(paragraph):
            pending.append(paragraph)
            continue
        merged.append("\n\n".join(pending + [paragraph]))
        pending = []
    if pending:
        merged.append("\n\n".join(pending))
    return merged


def split_documents(
    documents: list[Document],
    chunk_size: int | None = None,
    min_chunk: int | None = None,
) -> list[Chunk]:
    """
    Paragraph-aware chunking that keeps the document's name on every chunk.

    Written for `campus_life`, where every post is one title line ("Morrow
    House — what it's actually like", "CS 340 Databases") followed by one to
    four short paragraphs. The name is on the title line and the useful figure
    is in a body sentence, and 62 of the 88 posts are templated look-alikes
    that differ only by that name and that figure. So the rules are:

      1. Cut only on paragraph breaks. A sentence is never split in half.
      2. The first paragraph is the title. It is prefixed to every chunk made
         from the document, so a chunk that says "$1.50 wash, $1.25 dry" also
         says which building.
      3. Body paragraphs are grouped in order until adding the next one would
         push the group's body past `chunk_size`. A single paragraph longer
         than the cap stays whole rather than being cut.
      4. A trailing group whose body is shorter than `min_chunk` is folded into
         the previous chunk instead of becoming a fragment.
      5. A section heading ("## Getting around") travels with the paragraph
         under it, so it can't end one chunk while its content starts the next.
         campus_life posts have no headings in their bodies; this is for the
         sectioned corpora.

    With the campus_life numbers in config.py no post reaches the cap, so the
    output is one chunk per post — the same count as the starter, but arrived
    at by a rule that still holds if a longer post is added. On `city_guides`
    the same function splits each guide at its section breaks.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    min_chunk = config.MIN_CHUNK if min_chunk is None else min_chunk

    chunks: list[Chunk] = []
    for doc in documents:
        paragraphs = _paragraphs(doc.text)
        if not paragraphs:
            continue

        title, body = paragraphs[0], _attach_headings(paragraphs[1:])
        if not body:
            # A one-paragraph document: the "title" is the whole content.
            groups: list[list[str]] = [[title]]
            title = ""
        else:
            groups = []
            current: list[str] = []
            current_len = 0
            for paragraph in body:
                if current and current_len + len(paragraph) > chunk_size:
                    groups.append(current)
                    current, current_len = [], 0
                current.append(paragraph)
                current_len += len(paragraph)
            if current:
                groups.append(current)

            # Rule 4: don't leave a fragment at the end.
            if len(groups) > 1 and sum(len(p) for p in groups[-1]) < min_chunk:
                groups[-2].extend(groups.pop())

        for index, group in enumerate(groups):
            text = "\n\n".join(([title] if title else []) + group)
            chunks.append(
                Chunk(
                    text=text,
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
