# Selección de LLMs para el benchmark RAG

## 1. Requisitos del enunciado

| Componente | Mínimo | Condición |
|---|---|---|
| LLM pequeños | 2 | Entre 1B y 3B parámetros |
| LLM medianos | 2 | Entre 7B y 9B parámetros |
| Stack de inferencia | 1 | Justificado (comparar dos es un extra) |
| Cuantización | Libre | Indicarla siempre (comparar Q4 y Q8 del mismo modelo es un extra) |

Criterios de elección: idioma (español), memoria, ventana de contexto, variedad de familias, licencia y formato compatible con el stack.

## 2. Modelos elegidos

| Tamaño | Modelo (repositorio usado) | Familia | Parámetros | Español | Licencia | Formato usado |
|---|---|---|---|---|---|---|
| Pequeño | `LiquidAI/LFM3-1.7B` | Liquid (LFM3, arquitectura híbrida) | 1,73B | Sí (16 idiomas) | LFM Open License v1.0 | Safetensors BF16 → FP8 al cargar |
| Pequeño | `meta-llama/Llama-3.2-3B-Instruct` | Llama | 3B | Sí (soporte oficial) | Llama 3.2 Community License (acceso restringido: hay que aceptarla en HF) | Safetensors BF16 → FP8 al cargar |
| Mediano | `Qwen/Qwen3.5-9B` | Qwen | ~9B | Sí (multilingüe) | Apache 2.0 | Safetensors BF16 → FP8 al cargar, modo solo texto |
| Mediano | `nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-BF16` | Gemma 4 + post-entrenamiento NVIDIA | 8B totales / 4B efectivos | Sí | OpenMDW-1.1 | Safetensors BF16 → FP8 al cargar, modo solo texto |

> **Cambio respecto al plan inicial:** para Nemotron se planeó `NVIDIA-Nemotron-3.5-Bolt-E4B-4GB`, pero ese repositorio es solo el GGUF Q4_K_M (sin `config.json`) y vLLM no lo carga. Se usa la versión en formato Hugging Face, `-BF16`.

## 3. Justificación

- **Variedad:** cuatro familias distintas (Liquid, Llama, Qwen y Gemma/NVIDIA), en lugar de varios tamaños del mismo modelo.
- **Idioma:** todos incluyen español entre sus idiomas.
- **Modelos oficiales:** se evitan las variantes comunitarias (merges, destilados, versiones "uncensored"), porque no se puede verificar su procedencia y pueden alterar justo lo que medimos (fidelidad y abstención).
- **LFM3-1.7B:** muy ligero y con contexto largo. Su card recomienda usarlo con retrieval para las tareas que dependen de conocimiento, así que encaja con un RAG.
- **Llama-3.2-3B-Instruct:** la referencia más usada en el rango pequeño, con mucho soporte en los stacks.
- **Qwen3.5-9B:** de los modelos abiertos más fuertes en el rango de 7–9B, y multilingüe.
- **Nemotron 3.5 Bolt E4B:** 8B parámetros en total, así que entra en la categoría mediana. Basado en Gemma 4 E4B. Calcula como un modelo de ~4B efectivos, por lo que se esperaba que fuera más rápido que otros de 8B. **Medido:** en nuestro stack fue el más lento (≈27 tok/s frente a ≈45 de Qwen3.5-9B) y ocupa más VRAM (ver §6), porque carga los 8B completos y vLLM usa kernels más lentos en esta GPU (`TRITON_ATTN`, FP8 Marlin).

## 4. Candidatos descartados

| Modelo | Motivo |
|---|---|
| `xtools-at/DeepSeek-V4-Pro-Qwen3.5-9B-UNCENSORED-heretic` | Comunitario. Destilado para matemáticas y STEM, con las negativas eliminadas ("abliteration"): puede afectar a la abstención. Razonamiento activado por defecto |
| `Jackrong/DeepSeek-V4-Pro-Qwen3.5-9B` | Comunitario, orientado a razonamiento matemático, no a RAG en español |
| `meta-llama/Llama-3.2-1B` | Es la versión base (no instruct). Se sustituye por la de 3B Instruct |
| `BSC-LT/salamandra-2b/7b-instruct` | Interesante por ser español, pero entrenado con datos del BOE (riesgo de que responda de memoria). Posible extra |
| `meta-llama/Llama-3.1-8B-Instruct` | Alternativa válida en el rango mediano. Descartado para no repetir familia con Llama-3.2-3B |

## 5. Stack de inferencia

- **Stack usado:** vLLM (modo offline, clase `LLM`), el mismo que en la Fase 2 de embeddings.
- **Justificación:** un único stack para todo el benchmark; carga los modelos oficiales de Hugging Face sin conversiones; nunca trunca el prompt en silencio (da error si no cabe); y permite fijar la misma caché KV para todos, de modo que la VRAM medida compara modelos y no la reserva del motor.
- **Plan inicial descartado:** Ollama con GGUF Q4_K_M. Se cambió a vLLM para usar el mismo stack que en los embeddings.
- **Script:** `scripts/benchmark_llms_vllm.py` (un proceso por modelo y escenario). Tablas: `scripts/generar_tablas_llm.py`.
- **Versión:** vLLM 0.34.0, PyTorch 2.14.0+cu130, NVIDIA A800 40GB (instancia MIG 3g.20gb). El script guarda la versión real en cada JSON de resultados.

## 6. Cuantización y memoria

Misma cuantización para todos: **FP8** (cuantización al cargar con `quantization="fp8"`, pesos BF16 de origen).

- **Por qué FP8 y no BF16:** Qwen3.5-9B en BF16 ocupa ~18 GB y no cabe en la instancia de 20 GB junto a la caché.
- **Por qué FP8 y no Q4:** vLLM no carga bien los GGUF; FP8 es la cuantización que aplica al cargar y es la misma para los cuatro modelos.
- **Nota de hardware:** la A800 (Ampere) no calcula en FP8; vLLM lo aplica solo a los pesos (kernel Marlin). Ahorra memoria, pero no acelera.
- **Modo solo texto:** Qwen3.5-9B y Nemotron son multimodales. Se cargan con `limit_mm_per_prompt` a 0 para que vLLM no reserve memoria para los codificadores de imagen, audio y vídeo. Con ellos activos, la VRAM pico de Qwen subía de 14,3 a 15,9 GB (ejecución de prueba del 20/11/2026 a las 14:31, guardada en el commit `706b415`: `results/llms/data/qwen3.5-9b_boe.json`). En Nemotron también subía, pero esa ejecución no se conservó, así que no damos la cifra.
- **Caché KV:** fija en 2 GB para todos (`kv_cache_memory_bytes`).

VRAM pico medida (toda la instancia MIG, con caché KV de 2 GB):

| Modelo | Pesos en GPU (log de vLLM) | VRAM pico medida | ¿Cabe en 20 GB? | ¿Cabe en 8 GB (Plan B)? |
|---|---|---|---|---|
| LFM3-1.7B | 2,0 GB | 5,4 GB | Sí | Sí |
| Llama-3.2-3B-Instruct | 3,4 GB | 7,1 GB | Sí | Justo (sin contar el embedding) |
| Nemotron Bolt E4B | 10,5 GB | 14,8 GB | Sí | No |
| Qwen3.5-9B | 10,3 GB | 14,3 GB | Sí | No |

> La estimación inicial en Q4 (pesos × 0,6) no aplica: con FP8 los pesos ocupan ~1 byte por parámetro, y Nemotron carga además tablas de embeddings por capa muy grandes.

## 7. Configuración común (igual para todos)

| Parámetro | Valor |
|---|---|
| Temperatura | 0 (`seed` = 42) |
| top-k del retrieval | 5 (top-5 guardado por el embedding ganador en la Fase 2) |
| Límite de tokens de salida (`max_tokens`) | 512 |
| Ventana de contexto (`max_model_len`) | 8192 (prompt más largo medido: ~2.500 tokens) |
| Latencia total | Solo la generación del LLM (petición completa a vLLM). No incluye el retrieval, porque se reutiliza el top-5 de la Fase 2; la búsqueda cuesta ~0,03 s por pregunta (`query_retrieval_time_sec` en `results/embeddings/data/*.json`) y no cambia ninguna comparación |
| Modo de razonamiento | Desactivado (`chat_template_kwargs={"enable_thinking": False}`) |
| Caché de prefijos | Desactivada (para que repetir una pregunta no abarate el TTFT) |
| Prompt | El mismo para todos (ver abajo) |
| Embedding | BOE: `harrier-oss-v1`. Debian: `bge-m3` |

### Prompt (final)

Se envía como plantilla de chat (mensaje de sistema + mensaje de usuario). `{cita}` vale «el artículo» en el BOE y «la sección» en Debian.

```text
[sistema]
Eres un asistente que responde preguntas usando ÚNICAMENTE los fragmentos proporcionados.

Reglas:
1. Responde solo con información que aparezca en los fragmentos. No uses conocimientos propios.
2. Si la respuesta no está en los fragmentos, responde exactamente: "No aparece en el documento" y nada más.
3. Cita siempre {cita} de donde sale la respuesta (aparece en la línea «Fuente» de cada fragmento).
4. Responde en español y de forma breve.

[usuario]
Fragmentos:

[Fragmento 1]
Fuente: <artículo o sección del chunk>
<texto del chunk>

... (5 fragmentos)

Pregunta: {pregunta}
```

### Criterios de puntuación a mano

Se aplican igual a los cuatro modelos. Escala del enunciado para la corrección.

| Campo | Valor | Criterio |
|---|---|---|
| Corrección | 2 / 1 / 0 | 2: correcta y completa. 1: incompleta o imprecisa (también si añade un dato que no está en los fragmentos). 0: incorrecta, o se abstiene teniendo respuesta y no dice nada más. Si se abstiene y después responde, se puntúa ese texto, tanto para premiar como para penalizar (la fila sigue contando como abstención). En las preguntas sin respuesta, abstenerse vale 2 |
| Fiel | 1 / 0 | 0 si afirma algo que no está en los fragmentos |
| Abstiene | 1 / 0 | 1 si la respuesta **empieza** diciendo que la información no aparece, aunque luego añada texto. Casi siempre es la frase exacta; en 2 casos es otra redacción («Según los fragmentos proporcionados, no aparece información…»). Si responde y al final dice que una parte no aparece, cuenta como respuesta (0) |
| Formato e idioma | 1 / 0 | 1 si está en español y cita el artículo (BOE) o la sección (Debian), tal y como aparece en la línea «Fuente». 0 si solo cita «Fragmento N». La abstención sola («No aparece en el documento») cuenta como 1, porque es exactamente lo que pide el prompt. Abstenerse y después añadir texto cuenta como 0, porque el prompt pide esa frase «y nada más» |

> El criterio de formato decide el escenario Debian: ver `decision_fase4.md` §6.

## 8. Trampas a evitar

- [x] Modo de razonamiento desactivado en Qwen3.5 y Nemotron (el script avisa si detecta `<think>`).
- [x] Contexto suficiente: prompt + 5 chunks + respuesta caben en 8192 tokens; vLLM daría error si no.
- [x] Misma cuantización (FP8) para todos.
- [x] Usar siempre la versión **instruct**.
- [x] Calentar el modelo antes de medir: se descarta la primera ronda, se repite 3 veces y se usa la mediana.
- [x] Anotar en cada ejecución: modelo, versión, cuantización, stack, parámetros, fecha y hora (en `meta` de cada JSON).
- [x] Multimodales en modo solo texto, para que la VRAM sea comparable.

## 9. Evidencias guardadas

- Respuestas brutas y métricas por modelo y escenario: `results/llms/data/<modelo>_<escenario>.json`.
- Registros de VRAM: `results/llms/logs/vram_<modelo>_<escenario>.log`.
- Logs completos de ejecución: `results/llms/logs/ejecucion_completa.log`, `results/llms/logs/nemotron.log`.
- Puntuación a mano (corrección 0–2, fiel, abstención, formato e idioma): `results/llms/puntuacion_boe.csv` y `puntuacion_debian.csv`.
- Tablas B y C: `results/llms/tablas_b_c.md`.