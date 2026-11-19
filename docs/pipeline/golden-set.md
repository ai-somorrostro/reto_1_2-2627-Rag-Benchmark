# Golden set

The Phase 1 question sets live in `data/golden_set/` as JSONL: one JSON
object per line. Each file contains 15 questions for its scenario: 8 `direct`,
4 `multi_fragment`, and 3 `no_answer`.

`boe.jsonl` and `debian.jsonl` contain the original phase 1 questions.
`debian-en.jsonl` reuses the same Spanish questions and expected answers as
`debian.jsonl`, but points to chunks from the English handbook. This keeps the
query fixed while changing the corpus language for the cross-lingual retrieval
comparison.

Each record has:

- `id`: stable question identifier;
- `scenario`: `boe`, `debian`, or `debian-en`;
- `type`: `direct`, `multi_fragment`, or `no_answer`;
- `question`: original wording, not copied from the source corpus;
- `expected_answer`: concise answer or `No aparece en el documento.`;
- `relevant_chunk_ids`: one source chunk for a direct question, two for a
  multi-fragment question, or an empty list for an unanswerable question.

The references identify the chunk(s) containing the evidence, not a required
retrieval ranking. Run `uv run python -m unittest discover -s tests -v` to
check the question counts, schema, and chunk references.
