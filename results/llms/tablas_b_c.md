# Fase 3. Resultados del benchmark de LLMs

## Escenario: Estatuto de los Trabajadores (BOE)

Stack: vLLM · cuantización FP8 · embedding: `harrier-oss-v1` · top-k = 5 · temperatura 0.0 · num_predict 512 · num_ctx 8192 · mismo prompt para todos

### Tabla B. LLMs: calidad (con retrieval)

| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `lfm3-1.7b` | 1,7B | FP8 | 0,47 | 93 % | 3 de 3 | 11 de 12 | 40 % |
| `llama3.2-3b` | 3B | FP8 | 0,93 | 100 % | 3 de 3 | 6 de 12 | 93 % |
| `nemotron-bolt-e4b` | 8B (4B efect.) | FP8 | 1,60 | 100 % | 3 de 3 | 1 de 12 | 100 % |
| `qwen3.5-9b` | 9B | FP8 | 1,80 | 100 % | 3 de 3 | 1 de 12 | 93 % |

### Extra. Retrieval frente a oráculo (solo preguntas con respuesta)

| Modelo | Corrección con retrieval | Corrección con oráculo | Fallo del retrieval | Fallo por ruido |
| --- | --- | --- | --- | --- |
| `lfm3-1.7b` | 0,08 | 1,25 | ninguno | BOE_D01, BOE_D03, BOE_D04, BOE_D05, BOE_D08, BOE_C03 |
| `llama3.2-3b` | 0,67 | 0,92 | ninguno | BOE_D01, BOE_D06, BOE_C03 |
| `nemotron-bolt-e4b` | 1,50 | 1,75 | ninguno | BOE_D02, BOE_C02 |
| `qwen3.5-9b` | 1,75 | 2,00 | ninguno | BOE_C01, BOE_C02 |

> Con el chunk correcto acierta (2) y con el retrieval no. **Fallo del retrieval**: el chunk correcto no llegó al top-k. **Fallo por ruido**: sí llegó, pero los demás fragmentos despistaron al LLM (no es culpa del embedding).

### Tabla C. LLMs: coste (mediana de 3 rondas tras descartar la primera, 5 preguntas)

| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) |
| --- | --- | --- | --- | --- | --- |
| `lfm3-1.7b` | vLLM 0.34.0 | 0,10 | 63,9 | 2,80 | 5,36 |
| `llama3.2-3b` | vLLM 0.34.0 | 0,20 | 66,4 | 0,78 | 7,07 |
| `nemotron-bolt-e4b` | vLLM 0.34.0 | 0,27 | 26,7 | 1,50 | 14,80 |
| `qwen3.5-9b` | vLLM 0.34.0 | 0,41 | 45,0 | 1,35 | 14,27 |

---

## Escenario: Manual del Administrador de Debian

Stack: vLLM · cuantización FP8 · embedding: `bge-m3` · top-k = 5 · temperatura 0.0 · num_predict 512 · num_ctx 8192 · mismo prompt para todos

### Tabla B. LLMs: calidad (con retrieval)

| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `lfm3-1.7b` | 1,7B | FP8 | 0,40 | 100 % | 3 de 3 | 12 de 12 | 40 % |
| `llama3.2-3b` | 3B | FP8 | 1,07 | 87 % | 3 de 3 | 5 de 12 | 73 % |
| `nemotron-bolt-e4b` | 8B (4B efect.) | FP8 | 1,53 | 100 % | 3 de 3 | 3 de 12 | 100 % |
| `qwen3.5-9b` | 9B | FP8 | 1,53 | 100 % | 3 de 3 | 3 de 12 | 67 % |

### Extra. Retrieval frente a oráculo (solo preguntas con respuesta)

| Modelo | Corrección con retrieval | Corrección con oráculo | Fallo del retrieval | Fallo por ruido |
| --- | --- | --- | --- | --- |
| `lfm3-1.7b` | 0,00 | 1,00 | DEB_D03 | DEB_D01, DEB_D04, DEB_D06, DEB_D07, DEB_D08 |
| `llama3.2-3b` | 0,83 | 1,25 | DEB_D03 | ninguno |
| `nemotron-bolt-e4b` | 1,42 | 1,75 | DEB_D03, DEB_C04 | ninguno |
| `qwen3.5-9b` | 1,42 | 1,83 | DEB_D03, DEB_C03, DEB_C04 | ninguno |

> Con el chunk correcto acierta (2) y con el retrieval no. **Fallo del retrieval**: el chunk correcto no llegó al top-k. **Fallo por ruido**: sí llegó, pero los demás fragmentos despistaron al LLM (no es culpa del embedding).

### Tabla C. LLMs: coste (mediana de 3 rondas tras descartar la primera, 5 preguntas)

| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) |
| --- | --- | --- | --- | --- | --- |
| `lfm3-1.7b` | vLLM 0.34.0 | 0,12 | 60,9 | 2,41 | 5,36 |
| `llama3.2-3b` | vLLM 0.34.0 | 0,21 | 66,4 | 0,31 | 7,07 |
| `nemotron-bolt-e4b` | vLLM 0.34.0 | 0,31 | 26,7 | 1,10 | 14,80 |
| `qwen3.5-9b` | vLLM 0.34.0 | 0,45 | 44,8 | 3,23 | 14,27 |

**Avisos**

- **lfm3-1.7b:** 1 respuestas cortadas por num_predict

---
