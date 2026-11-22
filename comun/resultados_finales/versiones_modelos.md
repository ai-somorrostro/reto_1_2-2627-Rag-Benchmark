# Versiones de los modelos usados

Revisión = hash del commit de Hugging Face del modelo cargado (carpeta `snapshots/` de la caché compartida). Cuantización de los LLM: bf16 (sin cuantizar); stack: transformers 5.23.0, torch 2.15.0.

| Modelo | Tipo | Revisión (hash HF) |
|---|---|---|
| Qwen/Qwen3-1.7B | LLM pequeño | `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` |
| HuggingFaceTB/SmolLM3-3B | LLM pequeño | `a07cc9a04f16550a088caea529712d1d335b0ac1` |
| Qwen/Qwen3-8B | LLM mediano | `b968826d9c46dd6066d109eabc6255188de91218` |
| mistralai/Ministral-3-8B-Instruct-2512 | LLM mediano | `5b26027e7b19eeb4b7352e1fed3926375dd2cb4d` |
| BAAI/bge-m3 | embedding | `5617a9f61b028005a4858fdac845db406aefb181` |
| Qwen/Qwen3-Embedding-0.6B | embedding | `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3` |
| google/embeddinggemma-300m | embedding (copia local en sendoa/modelos/) | `57c266a740f537b4dc058e1b0cda161fd15afa75` |
