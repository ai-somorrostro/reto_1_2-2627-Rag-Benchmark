# Plan B (8 GB). Resultados de los LLM cuantizados

## Escenario: Estatuto de los Trabajadores (BOE)

Stack: llama.cpp · cuantización GGUF Q4_K_M · embedding: `harrier-oss-v1` · top-k = 5 · temperatura 0.0 · max_tokens 512 · max_model_len 8192 · mismo prompt para todos

### Tabla B. LLMs: calidad (con retrieval)

| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `nemotron-bolt-e4b-q4` | 8B (4B efect.) | GGUF Q4_K_M | 1,60 | 100 % | 3 de 3 | 1 de 12 | 100 % |
| `qwen3.5-9b-q4` | 9B | GGUF Q4_K_M | 1,87 | 100 % | 3 de 3 | 1 de 12 | 93 % |
| `nemotron-bolt-e4b-q8` | 8B (4B efect.) | GGUF Q8_0 | 1,60 | 100 % | 3 de 3 | 1 de 12 | 100 % |
| `qwen3.5-9b-q8` | 9B | GGUF Q8_0 | 1,80 | 100 % | 3 de 3 | 1 de 12 | 93 % |

### Extra. Retrieval frente a oráculo (solo preguntas con respuesta)

| Modelo | Corrección con retrieval | Corrección con oráculo | Fallo del retrieval | Fallo por ruido |
| --- | --- | --- | --- | --- |
| `nemotron-bolt-e4b-q4` | 1,50 | 1,67 | ninguno | BOE_D02 |
| `qwen3.5-9b-q4` | 1,83 | 1,92 | ninguno | BOE_C02 |
| `nemotron-bolt-e4b-q8` | 1,50 | 1,75 | ninguno | BOE_D02, BOE_C02 |
| `qwen3.5-9b-q8` | 1,75 | 2,00 | ninguno | BOE_D02, BOE_C01, BOE_C02 |

> Con el chunk correcto acierta (2) y con el retrieval no. **Fallo del retrieval**: no llegaron al top-k todos los chunks necesarios (en las combinadas basta con que falte uno). **Fallo por ruido**: llegaron todos, pero los demás fragmentos despistaron al LLM (no es culpa del embedding).

### Tabla C. LLMs: coste (mediana de 3 rondas tras descartar la primera, 5 preguntas)

| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) | VRAM del LLM (GB) | LLM + embedding (GB) | ¿Cabe en 8 GB? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `nemotron-bolt-e4b-q4` | llama.cpp b12633 | 0,41 | 93,0 | 0,76 | 3,75 | 3,47 | 4,57 | sí |
| `qwen3.5-9b-q4` | llama.cpp b12633 | 1,24 | 86,1 | 1,64 | 5,66 | 5,38 | 6,48 | sí |
| `nemotron-bolt-e4b-q8` | llama.cpp b12633 | 0,41 | 75,2 | 0,84 | 5,47 | 5,19 | 6,29 | sí |
| `qwen3.5-9b-q8` | llama.cpp b12633 | 1,11 | 66,6 | 1,92 | 8,77 | 8,49 | 9,59 | no |

> VRAM del LLM: pico de la instancia menos lo que había antes de arrancar llama-server. LLM + embedding: se suma ~1,1 GB del embedding del retrieval (FP16).

> TTFT: petición con max_tokens=1. Tokens/s: (tokens generados − 1) / (latencia total − TTFT). La latencia depende de lo larga que sea la respuesta: un modelo que se abstiene contesta antes, así que compárala solo entre modelos que cumplen los umbrales de calidad.

---

## Escenario: Manual del Administrador de Debian

Stack: llama.cpp · cuantización GGUF Q4_K_M · embedding: `bge-m3` · top-k = 5 · temperatura 0.0 · max_tokens 512 · max_model_len 8192 · mismo prompt para todos

### Tabla B. LLMs: calidad (con retrieval)

| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `nemotron-bolt-e4b-q4` | 8B (4B efect.) | GGUF Q4_K_M | 1,53 | 100 % | 3 de 3 | 3 de 12 | 100 % |
| `qwen3.5-9b-q4` | 9B | GGUF Q4_K_M | 1,53 | 100 % | 3 de 3 | 3 de 12 | 87 % |
| `nemotron-bolt-e4b-q8` | 8B (4B efect.) | GGUF Q8_0 | 1,53 | 100 % | 3 de 3 | 3 de 12 | 100 % |
| `qwen3.5-9b-q8` | 9B | GGUF Q8_0 | 1,53 | 100 % | 3 de 3 | 3 de 12 | 80 % |

### Extra. Retrieval frente a oráculo (solo preguntas con respuesta)

| Modelo | Corrección con retrieval | Corrección con oráculo | Fallo del retrieval | Fallo por ruido |
| --- | --- | --- | --- | --- |
| `nemotron-bolt-e4b-q4` | 1,42 | 1,75 | DEB_D03, DEB_C03, DEB_C04 | ninguno |
| `qwen3.5-9b-q4` | 1,42 | 1,83 | DEB_D03, DEB_C03, DEB_C04 | ninguno |
| `nemotron-bolt-e4b-q8` | 1,42 | 1,67 | DEB_D03 | ninguno |
| `qwen3.5-9b-q8` | 1,42 | 1,83 | DEB_D03, DEB_C03, DEB_C04 | ninguno |

> Con el chunk correcto acierta (2) y con el retrieval no. **Fallo del retrieval**: no llegaron al top-k todos los chunks necesarios (en las combinadas basta con que falte uno). **Fallo por ruido**: llegaron todos, pero los demás fragmentos despistaron al LLM (no es culpa del embedding).

### Tabla C. LLMs: coste (mediana de 3 rondas tras descartar la primera, 5 preguntas)

| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) | VRAM del LLM (GB) | LLM + embedding (GB) | ¿Cabe en 8 GB? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `nemotron-bolt-e4b-q4` | llama.cpp b12633 | 0,46 | 89,6 | 0,75 | 3,75 | 3,47 | 4,57 | sí |
| `qwen3.5-9b-q4` | llama.cpp b12633 | 1,24 | 86,9 | 1,76 | 5,66 | 5,38 | 6,48 | sí |
| `nemotron-bolt-e4b-q8` | llama.cpp b12633 | 0,44 | 84,4 | 0,69 | 5,47 | 5,19 | 6,29 | sí |
| `qwen3.5-9b-q8` | llama.cpp b12633 | 1,22 | 63,8 | 2,95 | 8,77 | 8,49 | 9,59 | no |

> VRAM del LLM: pico de la instancia menos lo que había antes de arrancar llama-server. LLM + embedding: se suma ~1,1 GB del embedding del retrieval (FP16).

> TTFT: petición con max_tokens=1. Tokens/s: (tokens generados − 1) / (latencia total − TTFT). La latencia depende de lo larga que sea la respuesta: un modelo que se abstiene contesta antes, así que compárala solo entre modelos que cumplen los umbrales de calidad.

---
