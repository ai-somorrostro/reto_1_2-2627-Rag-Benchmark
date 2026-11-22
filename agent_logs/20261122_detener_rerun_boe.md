
### Date of the change

22/11/2026

#### Files changed

> 1. agent_logs/20261122_detener_rerun_boe.md (new)
> 2. agent_logs/INDEX.md

#### Changes made by file

1. In "agent_logs/20261122_detener_rerun_boe.md" the changes: this log.
2. In "agent_logs/INDEX.md" the changes: added the row for this log.

#### Run

- Stopped the BOE rerun (script /tmp/opencode/boe_rerun.sh, log /tmp/opencode/boe_rerun2.log):
  - `pkill -f "benchmark_boe.py"`: killed Artic/benchmark_boe.py (pid 3140, started 21:43, running since 21:44). Artic/resultados_boe/ was still empty (no answers saved yet).
  - `pkill -f "boe_rerun.sh"`: killed the rerun script (pids 3138, 3139). Note: the shell running this pkill also matched the pattern and was killed by SIGTERM ("Killed by SIGTERM"); rerun continued to BGE/benchmark_boe.py (pid 7740), killed by the same command.
  - Verification: 0 processes matching benchmark_boe.py / boe_rerun.sh remain; `Artic/resultados_boe/` empty (no result files: `grep -c "Escenario: boe" Artic/resultados_boe/*.txt` → no files).
- Resume later: `bash /tmp/opencode/boe_rerun.sh` — the script reruns Artic first (its resultados_boe is empty), then BGE, then Multilingual.

---

This change has been made by *OpenCode*, the user has been *ibai_bonilla_g2*
