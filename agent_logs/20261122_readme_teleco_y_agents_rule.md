
### Date of the change

22/11/2026

#### Files changed

> 1. README_teleco.md (rewritten)
> 2. README.md (edited, then reverted to original)
> 3. AGENTS.md (rule 8 added)
> 4. agent_logs/20261122_readme_teleco_y_agents_rule.md (new)
> 5. agent_logs/INDEX.md

#### Changes made by file

1. In "README_teleco.md" the file was rewritten from a stub to a basic, direct guide understandable by people with no prior knowledge: intro explaining what the practice is (measuring embeddings and small LLMs in a RAG system; the two scenarios), a table of the two scenarios, prerequisites, step-by-step installation (clone, checkout TeamTeleco, setup.sh, activate venv, load .env, verify), and a basic flow per team folder (pdf_preparation.py, epub_preparation.py, generar_chunks.py, benchmark_boe.py / benchmark_debian.py, where results land).
2. In "README.md" an "Estado del proyecto" section was added and then REVERTED: the user said "no toques el README.md", so the file is back to its original content.
3. In "AGENTS.md" rule 8 was added: "Don't modify README.md without the user's explicit confirmation."
4. In "agent_logs/20261122_readme_teleco_y_agents_rule.md" this log.
5. In "agent_logs/INDEX.md" the row for this log.

#### Verification

- Command: `git diff --stat -- README.md` → empty (README.md restored to HEAD).
- Command: `grep -n "Estado del proyecto" README.md` → no output.
- Command: `sed -n '1,30p' README_teleco.md` → new guide content.

---

This change has been made by *OpenCode*, the user has been *ibai_bonilla_g2*
