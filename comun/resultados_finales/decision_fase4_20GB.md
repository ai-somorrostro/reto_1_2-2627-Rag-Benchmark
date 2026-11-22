# Decisión Fase 4 (VRAM máx. 20 GB)


## BOE

- HuggingFaceTB/SmolLM3-3B: corrección 1.40, fieles 60%, abst. 2/3, falsas 0, formato 73%, lat. 3.27s, 52.4 tok/s, VRAM 6.8 GB -> DESCARTADO: fieles 60%, corrección 1.40, formato 73%
- Qwen/Qwen3-1.7B: corrección 1.33, fieles 73%, abst. 3/3, falsas 2, formato 73%, lat. 1.46s, 51.7 tok/s, VRAM 4.01 GB -> DESCARTADO: fieles 73%, falsas abst. 2, corrección 1.33, formato 73%
- Qwen/Qwen3-8B: corrección 2.00, fieles 100%, abst. 3/3, falsas 0, formato 100%, lat. 3.80s, 31.9 tok/s, VRAM 16.57 GB -> CUMPLE
- mistralai/Ministral-3-8B-Instruct-2512: corrección 1.80, fieles 93%, abst. 3/3, falsas 0, formato 100%, lat. 3.74s, 32.5 tok/s, VRAM 18.39 GB -> CUMPLE

**Para BOE el más barato que cumple: Qwen/Qwen3-8B** (VRAM 16.57 GB, 31.9 tok/s, latencia 3.80 s).

## DEBIAN

- HuggingFaceTB/SmolLM3-3B: corrección 1.53, fieles 80%, abst. 3/3, falsas 1, formato 33%, lat. 1.59s, 52.5 tok/s, VRAM 6.7 GB -> DESCARTADO: fieles 80%, formato 33%
- Qwen/Qwen3-1.7B: corrección 1.53, fieles 93%, abst. 3/3, falsas 2, formato 60%, lat. 1.66s, 49.3 tok/s, VRAM 4.05 GB -> DESCARTADO: falsas abst. 2, formato 60%
- Qwen/Qwen3-8B: corrección 1.60, fieles 93%, abst. 3/3, falsas 2, formato 67%, lat. 3.50s, 31.4 tok/s, VRAM 16.49 GB -> DESCARTADO: falsas abst. 2, formato 67%
- mistralai/Ministral-3-8B-Instruct-2512: corrección 1.60, fieles 100%, abst. 3/3, falsas 3, formato 100%, lat. 4.59s, 32.0 tok/s, VRAM 18.23 GB -> DESCARTADO: falsas abst. 3

**Ningún modelo cumple todos los umbrales en este escenario.**
