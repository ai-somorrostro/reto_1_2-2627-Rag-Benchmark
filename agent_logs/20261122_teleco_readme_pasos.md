
### Date of the change

22/11/2026

#### Files changed

> 1. README_teleco.md (rewritten)
> 2. agent_logs/20261122_teleco_readme_pasos.md (new)
> 3. agent_logs/INDEX.md

#### Changes made by file

1. In "README_teleco.md" the file was rewritten to be a step-by-step guide for anyone that doesn't understand nothing: "1. ¿Qué es esta práctica?", "2. Los dos escenarios", "3. Preparar el ordenador" (prerequisites, steps: clonar, checkout TeamTeleco, ./setup.sh, source .venv/bin/activate, set -a; source .env; set +a, verificar), "4. Preparar los corpora" (pdf_preparation.py, epub_preparation.py, generar_chunks.py), "5. Ejecutar el benchmark" (cd Artic; python benchmark_boe.py / benchmark_debian.py; resultados guardados), "6. Detener el benchmark en curso" (Ctrl+C, respuestas ya guardadas, reanudación al relanzar), "7. Dónde quedan los resultados". Simple language, short sentences, commands in separate blocks.
2. In "agent_logs/20261122_teleco_readme_pasos.md" this log.
3. In "agent_logs/INDEX.md" the row for this log.

#### Verification

- Command: `grep -c "^## " README_teleco.md` → 7 sections + 1 title.
- Command: `sed -n '1,20p' README_teleco.md` → new content.

---

This change has been made by *OpenCode*, the user has been *ibai_bonilla_g2*
