
### Date of the change

18/11/2026

#### Files changed

> 1. epub_preparation.py
> 2. debian.md (generated)
> 3. requirements.txt

#### Changes made by file

1. In "epub_preparation.py" the changes have been the following: new script that converts debian.epub into debian.md using docling; it skips the conversion if debian.md already exists.
2. In "debian.md" the changes have been the following: new file generated automatically from debian.epub (1,306,599 bytes, 9,548 lines); the 69 images are kept as  placeholders.
3. In "requirements.txt" the changes have been the following: added docling==2.150.1.

#### Run

- Command: `.venv/bin/python epub_preparation.py`
- Result: OK, debian.md created. The onnxruntime `pthread_setaffinity_np ... error code: 22` messages are non-fatal warnings (the container restricts CPU affinity).

---

This changes have been made by *OpenCode*, the user has been *ibai_bonilla_g2*
