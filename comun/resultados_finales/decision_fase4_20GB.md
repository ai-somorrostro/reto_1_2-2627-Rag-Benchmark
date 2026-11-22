# Decisión Fase 4 (VRAM máx. 20 GB)


## BOE

Retrieval: mejor Recall@5 = 1.000 (>= 0,80, cumple).

- HuggingFaceTB/SmolLM3-3B: corrección 1.40, fieles 60%, abst. 2/3, falsas 0, formato 73%, lat. 3.33s, 51.8 tok/s, VRAM 6.8 GB -> DESCARTADO: fieles 60%, corrección 1.40, formato 73%
- Qwen/Qwen3-1.7B: corrección 1.33, fieles 73%, abst. 3/3, falsas 2, formato 73%, lat. 1.48s, 51.0 tok/s, VRAM 4.01 GB -> DESCARTADO: fieles 73%, falsas abst. 2, corrección 1.33, formato 73%
- Qwen/Qwen3-8B: corrección 2.00, fieles 100%, abst. 3/3, falsas 0, formato 100%, lat. 3.80s, 31.8 tok/s, VRAM 16.57 GB -> CUMPLE
- mistralai/Ministral-3-8B-Instruct-2512: corrección 1.80, fieles 93%, abst. 3/3, falsas 0, formato 100%, lat. 3.74s, 32.5 tok/s, VRAM 18.39 GB -> CUMPLE

**Para BOE el más barato que cumple: Qwen/Qwen3-8B** (VRAM 16.57 GB, 31.8 tok/s, latencia 3.80 s).

## DEBIAN

**Retrieval: el mejor Recall@5 es 0.667 (< 0,80). Para DEBIAN no se recomienda este RAG tal cual: primero hay que mejorar el retrieval; los LLM de abajo se evalúan igualmente.**

- HuggingFaceTB/SmolLM3-3B: corrección 1.40, fieles 73%, abst. 3/3, falsas 1, formato 33%, lat. 1.45s, 51.1 tok/s, VRAM 6.56 GB -> DESCARTADO: fieles 73%, corrección 1.40, formato 33%
- Qwen/Qwen3-1.7B: corrección 1.53, fieles 93%, abst. 3/3, falsas 2, formato 53%, lat. 1.19s, 49.3 tok/s, VRAM 3.96 GB -> DESCARTADO: falsas abst. 2, formato 53%
- Qwen/Qwen3-8B: corrección 1.60, fieles 93%, abst. 3/3, falsas 2, formato 67%, lat. 3.70s, 31.4 tok/s, VRAM 16.48 GB -> DESCARTADO: falsas abst. 2, formato 67%
- mistralai/Ministral-3-8B-Instruct-2512: corrección 1.60, fieles 100%, abst. 3/3, falsas 3, formato 100%, lat. 4.55s, 32.0 tok/s, VRAM 18.44 GB -> DESCARTADO: falsas abst. 3

**Ningún modelo cumple todos los umbrales en este escenario.**
