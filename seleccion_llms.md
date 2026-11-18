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

| Tamaño | Modelo | Familia | Parámetros | Español | Licencia | Formato usado |
|---|---|---|---|---|---|---|
| Pequeño | `LiquidAI/LFM3-1.7B` | Liquid (LFM3, arquitectura híbrida) | 1,73B | Sí (16 idiomas) | LFM Open License v1.0 | GGUF `LiquidAI/LFM3-1.7B-GGUF` |
| Pequeño | `meta-llama/Llama-3.2-3B-Instruct` | Llama | 3B | Sí (soporte oficial) | Llama 3.2 Community License (acceso restringido, hay que aceptarla en HF) | GGUF (Ollama `llama3.2:3b`) |
| Mediano | `Qwen/Qwen3.5-9B` | Qwen | ~9B | Sí (multilingüe) | Apache 2.0 *(comprobar en la card)* | GGUF Q4_K_M |
| Mediano | `nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-4GB` | Gemma 4 + post-entrenamiento NVIDIA | 8B totales / 4B efectivos | Sí *(comprobar en la card)* | OpenMDW-1.1 *(comprobar)* | GGUF oficial Q4_K_M |

> Rellenad las celdas marcadas *(comprobar)* con lo que diga la model card de Hugging Face y con la salida de `ollama show <modelo>`.

## 3. Justificación

- **Variedad:** cuatro familias distintas (Liquid, Llama, Qwen y Gemma/NVIDIA), en lugar de varios tamaños del mismo modelo.
- **Idioma:** todos incluyen español entre sus idiomas.
- **Modelos oficiales:** se evitan las variantes comunitarias (merges, destilados, versiones "uncensored"), porque no se puede verificar su procedencia y pueden alterar justo lo que medimos (fidelidad y abstención).
- **LFM3-1.7B:** muy ligero (~1 GB en Q4) y con contexto largo. Su card recomienda usarlo con retrieval para las tareas que dependen de conocimiento, así que encaja con un RAG.
- **Llama-3.2-3B-Instruct:** la referencia más usada en el rango pequeño, con mucho soporte en los stacks.
- **Qwen3.5-9B:** de los modelos abiertos más fuertes en el rango de 7–9B, y multilingüe.
- **Nemotron 3.5 Bolt E4B:** 8B parámetros en total, así que entra en la categoría mediana. Basado en Gemma 4 E4B. **Nota:** calcula como un modelo de ~4B efectivos, lo que debería hacerlo más rápido que otros de 8B. Lo indicamos para que la comparación sea transparente.

## 4. Candidatos descartados

| Modelo | Motivo |
|---|---|
| `xtools-at/DeepSeek-V4-Pro-Qwen3.5-9B-UNCENSORED-heretic` | Comunitario. Destilado para matemáticas y STEM, con las negativas eliminadas ("abliteration"): puede afectar a la abstención. Razonamiento activado por defecto |
| `Jackrong/DeepSeek-V4-Pro-Qwen3.5-9B` | Comunitario, orientado a razonamiento matemático, no a RAG en español |
| `meta-llama/Llama-3.2-1B` | Es la versión base (no instruct). Se sustituye por la de 3B Instruct |
| `BSC-LT/salamandra-2b/7b-instruct` | Interesante por ser español, pero sin versión oficial en Ollama y entrenado con datos del BOE (riesgo de que responda de memoria). Posible extra |
| `meta-llama/Llama-3.1-8B-Instruct` | Alternativa válida en el rango mediano. Descartado para no repetir familia con Llama-3.2-3B |

## 5. Stack de inferencia

- **Stack principal:** Ollama (sobre llama.cpp, con modelos en GGUF).
- **Justificación:** instalación sencilla, modelos ya cuantizados, API local compatible con OpenAI y reproducible (`ollama show` da la versión y la cuantización exactas).
- **Extra opcional:** comparar con `llama.cpp` (llama-server) o con vLLM usando el mismo modelo y la misma cuantización.

Para cargar un GGUF de Hugging Face que no esté en la biblioteca de Ollama:

```bash
ollama run hf.co/<usuario>/<repo-GGUF>:Q4_K_M
```

## 6. Cuantización y memoria

Misma cuantización para todos: **Q4_K_M**.

Estimación: VRAM ≈ parámetros × 0,6 (Q4) + 1–3 GB de caché KV + ~1 GB del embedding.

| Modelo | Pesos Q4 (aprox.) | Total estimado | ¿Cabe en 20 GB? | ¿Cabe en 8 GB (Plan B)? |
|---|---|---|---|---|
| LFM3-1.7B | ~1 GB | ~3 GB | Sí | Sí |
| Llama-3.2-3B-Instruct | ~2 GB | ~4 GB | Sí | Sí |
| Nemotron Bolt E4B | ~4–6 GB | ~6–8 GB | Sí | Justo |
| Qwen3.5-9B | ~5,5–6 GB | ~8–9 GB | Sí | Justo / no |

> La VRAM real se mide durante la prueba (pico), con `nvidia-smi --query-gpu=memory.used --format=csv -l 1 > vram_<modelo>.log`.

Extra opcional: repetir un modelo (por ejemplo, Qwen3.5-9B) en **Q8_0** para comparar Q4 con Q8.

## 7. Configuración común (igual para todos)

| Parámetro | Valor |
|---|---|
| Temperatura | 0 |
| top-k del retrieval | 5 *(fijar el definitivo)* |
| Límite de tokens de salida (`num_predict`) | 512 *(fijar)* |
| Ventana de contexto (`num_ctx`) | 8192 |
| Modo de razonamiento | **Desactivado** (`"think": false` en Ollama) |
| Prompt | El mismo para todos (ver abajo) |
| Embedding | El ganador de la Fase 2 para cada escenario |

### Prompt (borrador)

```text
Eres un asistente que responde preguntas usando ÚNICAMENTE los fragmentos proporcionados.

Reglas:
1. Responde solo con información que aparezca en los fragmentos.
2. Si la respuesta no está en los fragmentos, responde exactamente: "No aparece en el documento".
3. Cita siempre el artículo (BOE) o la sección (Debian) de donde sale la respuesta.
4. Responde en español y de forma breve.

Fragmentos:
{fragmentos}

Pregunta: {pregunta}
Respuesta:
```

## 8. Trampas a evitar

- [ ] Modo de razonamiento desactivado en Qwen3.5 y Nemotron.
- [ ] `num_ctx` suficiente: prompt + 5 chunks + respuesta. Si no, los fragmentos se cortan sin dar error.
- [ ] Misma cuantización (Q4_K_M) para todos.
- [ ] Usar siempre la versión **instruct**.
- [ ] Calentar el modelo antes de medir: descartar la primera ejecución, repetir 3 veces y usar la mediana.
- [ ] Anotar en cada ejecución: modelo, versión, cuantización, stack, parámetros, fecha y hora.

## 9. Evidencias que hay que guardar

- Salida de `ollama show <modelo>` para cada modelo.
- `ollama --version`.
- Registros de VRAM (`vram_<modelo>.log`).
- Respuestas brutas de cada modelo con su puntuación a mano (corrección 0–2, fiel sí/no, abstención, formato e idioma).
- Ficheros de resultados de los que salen las Tablas B y C.
