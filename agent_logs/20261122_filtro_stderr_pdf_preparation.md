
### Date of the change

22/11/2026

#### Files changed

> 1. pdf_preparation.py
> 2. setup.sh
> 3. agent_logs/20261122_filtro_stderr_pdf_preparation.md (new)
> 4. agent_logs/INDEX.md (new)

#### Changes made by file

1. In "pdf_preparation.py" the changes have been the following: added a small context manager `filtrar_avisos_onnxruntime()` that, while `pymupdf4llm.to_markdown()` runs, temporarily redirects file descriptor 2 to a temporary file and then re-emits every stderr line except those containing "onnxruntime". This hides the non-fatal `pthread_setaffinity_np ... error code: 22` warnings from onnxruntime without hiding real errors. New imports: `contextlib`, `sys`, `tempfile`.
2. In "setup.sh" the changes have been the following: fixed the typo in the last printed instruction, `python3 pdf_prepartion.py` → `python3 pdf_preparation.py`.
3. In "agent_logs/20261122_filtro_stderr_pdf_preparation.md" the changes have been the following: this log.
4. In "agent_logs/INDEX.md" the changes have been the following: new simple index of the agent logs (rule 6).

#### Run

- Command: `.venv/bin/python -m py_compile pdf_preparation.py` → OK.
- Command: `.venv/bin/python pdf_preparation.py` → `'/home/g2/reto_1_2-2627-Rag-Benchmark/BOE.md' ya existe; no se vuelve a convertir.` (BOE.md was already present, so the conversion branch was not re-run inside the repo).
- Filter check: an identical copy of the script plus BOE.pdf in `/tmp/opencode/pdftest3` produced 0 `onnxruntime` lines and `BOE.md` (409,269 bytes, 401,746 characters).

---

This changes have been made by *OpenCode*, the user has been *ibai_bonilla_g2*
