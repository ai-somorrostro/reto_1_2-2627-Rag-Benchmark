### Date of the change

23/11/2026

#### Files changed

> 1. Artic/resultados_boe/resultados_qwen2.5-3b.txt
> 2. Artic/resultados_boe/resultados_qwen2.5-7b.txt
> 3. Artic/resultados_debian/resultados_mistral-7b.txt
> 4. Artic/resultados_debian/resultados_qwen2.5-3b.txt
> 5. Artic/resultados_debian/resultados_qwen2.5-7b.txt
> 6. Artic/resultados_debian/resultados_smollm2-1.7b.txt
> 7. BGE/resultados_boe/resultados_qwen2.5-3b.txt
> 8. BGE/resultados_boe/resultados_qwen2.5-7b.txt
> 9. BGE/resultados_debian/resultados_mistral-7b.txt
> 10. BGE/resultados_debian/resultados_qwen2.5-3b.txt
> 11. BGE/resultados_debian/resultados_qwen2.5-7b.txt
> 12. BGE/resultados_debian/resultados_smollm2-1.7b.txt
> 13. Multilingual/resultados_boe/resultados_qwen2.5-3b.txt
> 14. Multilingual/resultados_boe/resultados_qwen2.5-7b.txt
> 15. agent_logs/20261123_untrack_gitignore_files.md (new)
> 16. agent_logs/INDEX.md

#### Changes made by file

1. In each of the "resultados_*.txt" files the changes have been the following: untracked — `git rm --cached` removed them from the index (they match the `resultados_boe/` and `resultados_debian/` patterns in `.gitignore`); they no longer appear when the branch is pushed. The files remain on disk, untracked and ignored.
2. In "agent_logs/20261123_untrack_gitignore_files.md" the changes have been the following: new log of this change.
3. In "agent_logs/INDEX.md" the changes have been the following: new row in the index table.

Verification: `git ls-files -i --exclude-standard -c` returns nothing (no tracked file matches the ignore rules).

---

This changes have been made by *OpenCode*, the user has been *ibai_bonilla_g2*
