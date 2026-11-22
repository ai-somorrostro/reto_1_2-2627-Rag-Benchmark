
### Date of the change

22/11/2026

#### Files changed

> 1. README.md (new section added)
> 2. agent_logs/20261122_detener_benchmark_readme.md (new)
> 3. agent_logs/INDEX.md

#### Changes made by file

1. In "README.md" the changes: added new section "Detener un benchmark en curso" before "Fase 4": how to stop a running benchmark (Ctrl+C in terminal, "Cancelar" button of the model-load dialog in graphical environment); where results are saved (resultados_boe/resultados_debian per team folder, resultados_<llm>.txt); that it is safe: the script skips already-saved questions so re-running resumes where it stopped.
2. In "agent_logs/20261122_detener_benchmark_readme.md" the changes: this log.
3. In "agent_logs/INDEX.md" the changes: added the row for this log.

#### Verification

- Command: `grep -n "Detener un benchmark" README.md` → line found.
- Command: `git diff --stat -- README.md` → shows the README.md change.
- Benchmark rerun (Artic, benchmark_boe.py) still running.

---

This changes have been made by *OpenCode*, the user has been *ibai_bonilla_g2*
