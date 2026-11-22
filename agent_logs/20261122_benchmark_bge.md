
### Date of the change

22/11/2026

#### Files changed

> 1. BGE/benchmark_bge.py (new)
> 2. agent_logs/20261122_benchmark_bge.md (new)
> 3. agent_logs/INDEX.md

#### Changes made by file

1. In "BGE/benchmark_bge.py" the changes have been the following: new benchmark script for the BGE folder, based on `RAG_IACT/rag.py`. It uses `BAAI/bge-m3` as embedding and the four chosen LLMs: `Qwen/Qwen2.5-3B-Instruct`, `HuggingFaceTB/SmolLM2-1.7B-Instruct`, `Qwen/Qwen2.5-7B-Instruct` and `mistralai/Mistral-7B-Instruct-v0.3`. The two Llama models were replaced because their gated access request was still pending and blocked the benchmark; SmolLM2 and Mistral are public and meet the size requirements. It reads `boe_preguntas.txt` and `debian_preguntas.txt` from the same folder and the corpora `BOE.md` and `debian.md` from the repository root. It keeps the same chunking (1200/200) and retrieval (top-k 3) as `rag.py`, generates with greedy decoding (`do_sample=False`) and saves one `.txt` per LLM (`resultados_<llm>.txt`). If that file already exists, it appends only the questions that are not yet present, so an interrupted run can be resumed. It does not use or modify any index cache. It does all retrieval before loading the LLMs, so the embedding frees its VRAM before each model is loaded. It also loads `HF_TOKEN`/`HF_HOME` from the repository `.env` automatically (without overriding existing environment variables). It accepts `--llm`, `--escenario`, `--top-k` and `--max-preguntas`.
2. In "agent_logs/20261122_benchmark_bge.md" the changes have been the following: this log.
3. In "agent_logs/INDEX.md" the changes have been the following: added the row for this log.

#### Run

- Command: `.venv/bin/python -m py_compile BGE/benchmark_bge.py` → OK.
- Command: `.venv/bin/python BGE/benchmark_bge.py --help` → OK.
- Functional test: read 30 BOE questions and 30 Debian questions, split `BOE.md` into 494 chunks and `debian.md` into 1642 chunks, save a fake result and detect it as already done → OK.
- Full benchmark executed with `.venv/bin/python BGE/benchmark_bge.py --llm all`. `resultados_qwen2.5-3b.txt` and `resultados_qwen2.5-7b.txt` reached 60/60 questions. The run with SmolLM2 1.7B and Mistral 7B is launched afterwards and skips the two completed Qwen models thanks to the new skip check.

---

This changes have been made by *OpenCode*, the user has been *ibai_bonilla_g2*
