
### Date of the change

22/11/2026

#### Files changed

> 1. BOE.md (regenerated, cleaned)
> 2. chunks_boe.csv (regenerated)
> 3. chunks_debian.csv (regenerated)
> 4. Artic/boe_preguntas.txt, Artic/debian_preguntas.txt (rewritten, tipo/oficial/chunks_relevantes columns)
> 5. BGE/boe_preguntas.txt, BGE/debian_preguntas.txt (rewritten, same columns)
> 6. Multilingual/boe_preguntas.txt, Multilingual/debian_preguntas.txt (rewritten, same columns)
> 7. pdf_preparation.py (new limpiar_markdown: removes "Página N" lines and the repeated "BOLETÍN OFICIAL DEL ESTADO LEGISLACIÓN CONSOLIDADA" header, collapses blank lines, with --forzar option)
> 8. generar_chunks.py (new: generates chunks_boe.csv, chunks_debian.csv with the same dividir_markdown used by the benchmarks)
> 9. setup.sh run (repo venv .venv created, deps installed, .env created)
> 10. agent_logs/20261122_golden_set_and_boe_corpus.md (new)
> 11. agent_logs/INDEX.md

#### Changes made by file

1. In "pdf_preparation.py": added `limpiar_markdown()` that drops lines matching `Página \d+` and `BOLETÍN OFICIAL DEL ESTADO\s+LEGISLACIÓN CONSOLIDADA`, normalizes 3+ blank lines and strips trailing whitespace; main() now writes the cleaned markdown; added `--forzar` to reconvert even when BOE.md exists.
2. In "generar_chunks.py": new script importing `dividir_markdown` from BGE/benchmark_common; regenerates `chunks_boe.csv` (486 chunks) and `chunks_debian.csv` (1642 chunks). Verified: chunks_boe.csv == the chunk list used by the benchmark on the new cleaned BOE.md (0 occurrences of the repeated header line).
3. In "Artic/boe_preguntas.txt", "BGE/boe_preguntas.txt", "Multilingual/boe_preguntas.txt": golden set now has 33 questions per scenario (idem tras 8 directas + 4 multifragmento). New columns `tipo`, `oficial`, `chunks_relevantes` (ids semicolon-separated into `chunks_boe.csv`/`chunks_debian.csv`). New questions BOE_031-033 (oficial si): 3 sin respuesta, ids en áreas sin representación en la normativa (metadatos, registro del Estado, plazos trámite).
   - Official BOE: oficial=si → 8 directas (001,005,006,009,012,015,016,026), 4 multifragmento (003,020,023,028), 3 sin respuesta (031-033).
   - Other BOE: multifragmento 003,004,007,008,010,011,014,017,018,019,021,022,024,030; directa el resto.
   - Verification: ids in chunks_relevantes dentro del rango (0-485 BOE, 0-1641 Debian) y no vacías en las directas; tipo ok.
4. In the three "debian_preguntas.txt": same structure; 33 questions (DEB_001-033); new questions DEB_031-033 (oficial si) sobre contenido ausente del manual: precio asistencia comercial, versión publicada en 2026, importe donaciones 2025. Expected answers and references corrected where the corpus didn't match (see point 5).
   - Official DEB: oficial=si → 8 directas (002,003,006,007,010,016,018,022), 4 multifragmento (004,009,011,025), 3 sin respuesta (031-033).
   - Other DEB: multifragmento 004,005,009,013,015,017,021,025,027,029; directa el resto.
5. Corrections of expected answers/references (confirmado por el usuario al pedir "Corregir respuestas/referencias donde el corpus no trae el contenido alegado"):
   - DEB_003: referencia de Prologo → Capítulo 2.3 (OEBPS/ch02s03.html); la respuesta ya concuerda con la redacción del prefacio del 2.3.
   - DEB_009: pregunta y respuesta ajustadas al manual: remove = -r, conserva ficheros; purge = -P, elimina ficheros de configuración; chunk 5.2.2.2.
   - DEB_023: respuesta ajustada al manual: rsyslogd, archivos /var/log/, reglas /etc/rsyslog.conf, systemd-journald/journalctl; chunk 9.5 (9.5.1/9.5.2). Se eliminó el fragmento en /var/log/auth.log que el manual no describe.
   - DEB_025: respuesta ajustada: security.debian.org + unattended-upgrades (/etc/apt/apt.conf.d/50unattended-upgrades); eliminado debsecan; referencia unificada 6 y 14.
   - DEB_028: pregunta y respuesta ajustadas: MTAs posibles OpenSSL? Ajustar: Exim4 (default), Postfix, Postfix/Exim; MTA sin servidor IMAP/POP3 descrito; eliminado Dovecot. Chunks 943/950.
   - DEB_029: respuesta ajustada: FAI (12.3.1, 1241/1244), Munin (1269/1271), Nagios (1269/1279); se eliminaron Ansible, Puppet (ausentes del manual).
6. BOE golden set verified against the new chunks_boe.csv: spot-checked 20 de los 33 ids; cada id contiene el contenido esperado de la respuesta (e.g., BOE_002 → chunk 37 con "prestación de servicios por cuenta ajena...").
7. BOE.md regenerado con limpiar_markdown: 395,485 caracteres, 0 ocurrencias de "BOLETÍN OFICIAL"; heads no incluyen redundancias. chunks_boe.csv generado: 486 chunks (matches the g2 session count).

#### Environment notes

- setup.sh ejecutado (repo has no .venv pre-existente): creó /home/ibaib/repos/reto_1_2-2627-Rag-Benchmark/.venv con torch 2.15.0, sentence-transformers 6.2.0, transformers 5.22.2, pymupdf4llm 2.1, docling 2.150.1; generó .env.
- BOE re-runs: script /tmp/opencode/boe_rerun.sh lanzado (shell 20500357b001Z3jkczIABw1iRB, log /tmp/opencode/boe_rerun2.log) para los 3 motores (Artic, BGE, Multilingual), todos con `--llm all`.

#### Run

- `./setup.sh` → exit 0; `.venv` creado en /home/ibaib/repos/reto_1_2-2627-Rag-Benchmark.
- `.venv/bin/python pdf_preparation.py --forzar` → OK, Listo: '/home/ibaib/repos/reto_1_2-2627-Rag-Benchmark/BOE.md' (395485 caracteres).
- `.venv/bin/python generar_chunks.py` → boe: 486 chunks, debian: 1642 chunks.
- `bash /tmp/opencode/boe_rerun.sh` → lanzado (BOE reruns: Artic, BGE, Multilingual).

---

This change has been made by *OpenCode*, the user has been *ibai_bonilla_g2*
