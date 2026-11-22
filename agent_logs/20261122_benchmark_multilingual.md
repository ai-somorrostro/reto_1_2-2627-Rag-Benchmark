
### Date of the change

22/11/2026

#### Files changed

> 1. Multilingual/benchmark_multilingual.py (new)
> 2. agent_logs/20261122_benchmark_multilingual.md (new)
> 3. agent_logs/INDEX.md

#### Changes made by file

1. In "Multilingual/benchmark_multilingual.py" the changes have been the following: new benchmark script for the Multilingual folder, copied from `BGE/benchmark_bge.py` so both folders share the same chunking (1200/200), retrieval (top-k 3) and generation settings. The embedding is `intfloat/multilingual-e5-large` and it uses the prefixes required by E5: `"query: "` for the questions and `"passage: "` for the corpus chunks. The LLMs are `Qwen/Qwen2.5-3B-Instruct`, `HuggingFaceTB/SmolLM2-1.7B-Instruct`, `Qwen/Qwen2.5-7B-Instruct` and `mistralai/Mistral-7B-Instruct-v0.3`. It reads `boe_preguntas.txt` and `debian_preguntas.txt` from the Multilingual folder and the corpora `BOE.md` and `debian.md` from the repository root. It saves one `.txt` per LLM (`resultados_<llm>.txt`) and, if the file exists, appends only the missing questions. It does not use or modify any index cache, does all retrieval before loading the LLMs and frees the embedding from VRAM before each model is loaded. It skips a model whose result file already contains all the questions. It loads `HF_TOKEN`/`HF_HOME` from the repository `.env` without overriding existing environment variables.
2. In "agent_logs/20261122_benchmark_multilingual.md" the changes have been the following: this log.
3. In "agent_logs/INDEX.md" the changes have been the following: added the row for this log.

#### Run

- Command: `.venv/bin/python -m py_compile Multilingual/benchmark_multilingual.py` → OK.
- Command: `.venv/bin/python Multilingual/benchmark_multilingual.py --help` → OK.
- Full benchmark not executed yet: it is waiting for the BGE run to finish so both folders do not compete for the 19.6 GB of VRAM.

---

This changes have been made by *OpenCode*, the user has been *ibai_bonilla_g2*
