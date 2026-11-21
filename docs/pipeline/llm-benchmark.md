# Benchmark local de LLMs (Fase 3)

## Candidatos y configuración fija

El benchmark compara cuatro checkpoints locales BF16 sin cuantizar:

| Grupo | Modelo | Formato de prompt |
| --- | --- | --- |
| Pequeño | `Qwen/Qwen2.5-3B-Instruct` | Chat template del tokenizer |
| Pequeño | `meta-llama/Llama-3.2-3B-Instruct` | Chat template del tokenizer |
| Mediano | `Qwen/Qwen2.5-7B-Instruct` | Chat template del tokenizer |
| Mediano | `ibm-granite/granite-4.1-8b-llmon-preview` | Marcadores de rol nativos de Granite |

Los IDs, tamaños, precisión y formato están en `config/llms.toml`. Todos los
modelos deben estar ya en la caché de Hugging Face; no se intenta descargar
nada. vLLM ejecuta un modelo cada vez, con tensor parallelism 1.

La configuración común es top-k 5, temperatura 0, máximo de 256 tokens de
salida, contexto de servidor de 3.072 tokens y modo eager de vLLM. Se usa el embedding ganador por
escenario desde `artifacts/embeddings/selection.json`; los hashes de corpus,
preguntas y resumen del embedding se comprueban antes de generar; también se
validan las referencias de cada ranking y se guarda el hash de `results.jsonl`.
Por defecto
se ejecutan BOE y Debian en español. Debian en inglés se puede incluir con
`--scenario debian-en`.

El prompt compartido pide responder en español solo con el contexto, abstenerse
con «No aparece en el documento» cuando falte la respuesta y citar artículo o
sección. Se aplican las plantillas oficiales de Qwen/Llama y los marcadores de
rol de Granite; se guarda el prompt ya renderizado para cada respuesta.

## Ejecución

El entorno `vllm-env` debe tener vLLM, PyTorch, Transformers y los cuatro
checkpoints locales. Primero valida cachés, entradas y longitud de todos los
prompts sin cargar pesos:

```bash
PYTHONPATH=src ./vllm-env/bin/python -m reto_1_2_2627_rag_benchmark.llms.cli run --dry-run
```

Ejecución completa:

```bash
PYTHONPATH=src ./vllm-env/bin/python -m reto_1_2_2627_rag_benchmark.llms.cli run
```

Para una comprobación acotada:

```bash
PYTHONPATH=src ./vllm-env/bin/python -m reto_1_2_2627_rag_benchmark.llms.cli run \
  --model qwen2_5_3b_instruct --scenario boe --dry-run
```

La ejecución completa genera una respuesta por pregunta y modelo (15 preguntas
por escenario). Para medir coste, primero hace una llamada de calentamiento que
se registra pero se excluye; después usa cinco preguntas representativas por
modelo y escenario, con tres repeticiones por pregunta. El resumen toma primero
la mediana de las repeticiones de cada pregunta y luego la mediana de las cinco
preguntas.

## Salidas y puntuación manual

Cada ejecución crea un directorio con timestamp bajo `artifacts/llms/`:

- `manifest.json`: modelos/revisiones, conteo de parámetros del checkpoint,
  versiones, GPU, configuración, hashes y estado.
- `responses.jsonl`: preguntas, contexto, prompt exacto, respuesta bruta y métricas.
- `cost_runs.jsonl`: calentamientos y repeticiones de coste; incluye respuestas brutas.
- `memory.jsonl`: muestras de memoria CUDA asignada/reservada y uso global de GPU.
- `cost_summary.csv`: medianas de TTFT, tokens/s y latencia, además del pico de VRAM.
- `scores.jsonl`: plantilla de anotación manual, una fila por respuesta.

En `scores.jsonl`, completad `correctness_score` (0, 1 o 2), `faithful`,
`abstention` y `format_language`. No modifiquéis `response_id` ni los campos de
identificación. Después de puntuar las 15 respuestas de cada modelo/escenario:

```bash
PYTHONPATH=src ./vllm-env/bin/python -m reto_1_2_2627_rag_benchmark.llms.cli summarize \
  artifacts/llms/<timestamp>
```

El resumen valida que cada respuesta tenga anotación y genera
`quality_summary.csv` y `summary.csv`. Las métricas se calculan como en la
plantilla de la práctica: corrección media 0–2, fidelidad y formato/idioma en
porcentaje, abstenciones correctas de las tres preguntas sin respuesta y
recuento de falsas abstenciones.

La traza registra tanto el pico del asignador PyTorch como el uso global de la
GPU; el segundo puede incluir otros procesos que compartan la tarjeta. El
benchmark fuerza el modo vLLM de un solo proceso para que el pico del asignador
incluya el motor en la misma instancia de PyTorch. `vram_peak_gb` en los CSV es
el pico reservado por PyTorch; `vram_peak_allocated_gb` es lo asignado y
`device_used_peak_gb` es el uso global de la tarjeta. TTFT y latencia se guardan
por solicitud; tokens/s usa el intervalo de decodificación de vLLM. Para comparar
VRAM con precisión, ejecutad sin otros trabajos en la GPU.
