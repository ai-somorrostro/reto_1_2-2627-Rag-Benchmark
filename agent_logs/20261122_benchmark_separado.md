
### Date of the change

22/11/2026

#### Files changed

> 1. BGE/benchmark_common.py (new)
> 2. BGE/benchmark_boe.py (new)
> 3. BGE/benchmark_debian.py (new)
> 4. BGE/resultados_boe/ (new folder)
> 5. BGE/resultados_debian/ (new folder)
> 6. BGE/resultados_antiguos/ (old combined result files moved here)
> 7. BGE/scripts_antiguos/benchmark_bge.py (old combined script moved here)
> 8. Multilingual/benchmark_common.py (new)
> 9. Multilingual/benchmark_boe.py (new)
> 10. Multilingual/benchmark_debian.py (new)
> 11. Multilingual/scripts_antiguos/benchmark_multilingual.py (old combined script moved here)
> 12. Artic/benchmark_common.py (new)
> 13. Artic/benchmark_boe.py (new)
> 14. Artic/benchmark_debian.py (new)
> 15. agent_logs/20261122_benchmark_separado.md (new)
> 16. agent_logs/INDEX.md

#### Changes made by file

1. In "BGE/benchmark_common.py" the changes have been the following: new shared engine for the BGE folder. It contains the chunking (1200/200), retrieval (top-k 3), generation (greedy, 350 tokens), the four LLMs (`Qwen/Qwen2.5-3B-Instruct`, `HuggingFaceTB/SmolLM2-1.7B-Instruct`, `Qwen/Qwen2.5-7B-Instruct`, `mistralai/Mistral-7B-Instruct-v0.3`) and one `main(escenario)` function. Each run indexes only the markdown of the requested scenario, does its retrieval, frees the embedder and then loads the LLMs one by one. Results are written to `resultados_boe/` or `resultados_debian/`, one `.txt` per LLM, appending only the missing questions. No index cache is used.
2. In "BGE/benchmark_boe.py" the changes have been the following: new entry point that calls the shared engine with the BOE scenario (`BOE.md` + `boe_preguntas.txt`).
3. In "BGE/benchmark_debian.py" the changes have been the following: new entry point that calls the shared engine with the Debian scenario (`debian.md` + `debian_preguntas.txt`).
4. In "BGE/resultados_boe/" the changes have been the following: new folder for the BOE-only results. The 30 BOE records already generated for Qwen 3B, Qwen 7B and SmolLM2 were extracted from the old combined files.
5. In "BGE/resultados_debian/" the changes have been the following: new folder for the Debian-only results. The 30 Debian records already generated for Qwen 3B, Qwen 7B and SmolLM2 were extracted from the old combined files.
6. In "BGE/resultados_antiguos/" the changes have been the following: the three old combined `.txt` files were moved here (not deleted) after verifying that all their records had been copied to the new folders.
7. In "BGE/scripts_antiguos/benchmark_bge.py" the changes have been the following: the old combined script was moved here. It is no longer used.
8. In "Multilingual/benchmark_common.py" the changes have been the following: same engine as BGE but with `intfloat/multilingual-e5-large` and the E5 prefixes (`"query: "` for questions and `"passage: "` for chunks).
9. In "Multilingual/benchmark_boe.py" the changes have been the following: new entry point for the BOE corpus in the Multilingual folder.
10. In "Multilingual/benchmark_debian.py" the changes have been the following: new entry point for the Debian corpus in the Multilingual folder.
11. In "Multilingual/scripts_antiguos/benchmark_multilingual.py" the changes have been the following: the old combined script was moved here. It is no longer used.
12. In "Artic/benchmark_common.py" the changes have been the following: same engine with `Snowflake/snowflake-arctic-embed-l-v2.0`; the query prefix is `"query: "` and the passages have no prefix, as indicated by the model card.
13. In "Artic/benchmark_boe.py" the changes have been the following: new entry point for the BOE corpus in the Artic folder.
14. In "Artic/benchmark_debian.py" the changes have been the following: new entry point for the Debian corpus in the Artic folder.
15. In "agent_logs/20261122_benchmark_separado.md" the changes have been the following: this log.
16. In "agent_logs/INDEX.md" the changes have been the following: added the row for this log.

#### Run

- Command: `.venv/bin/python -m py_compile BGE/benchmark_common.py BGE/benchmark_boe.py BGE/benchmark_debian.py` → OK.
- Command: `.venv/bin/python -m py_compile Multilingual/benchmark_common.py Multilingual/benchmark_boe.py Multilingual/benchmark_debian.py` → OK.
- Command: `.venv/bin/python -m py_compile Artic/benchmark_common.py Artic/benchmark_boe.py Artic/benchmark_debian.py` → OK.
- Migration check: each new folder has 30 records per LLM for the three models that were already complete (Qwen 3B, Qwen 7B, SmolLM2) → OK.
- Full run launched sequentially: `BGE/benchmark_boe.py`, `BGE/benchmark_debian.py`, `Multilingual/benchmark_boe.py`, `Multilingual/benchmark_debian.py`, `Artic/benchmark_boe.py`, `Artic/benchmark_debian.py`, all with `--llm all`. Log: `/tmp/opencode/benchmark_separado.log`.
- Full run finished without errors. Verification: 24/24 result files (3 embeddings × 2 corpora × 4 LLMs), 30 records per file, 720 answers in total, with no duplicate or missing question IDs.

---

This changes have been made by *OpenCode*, the user has been *ibai_bonilla_g2*
