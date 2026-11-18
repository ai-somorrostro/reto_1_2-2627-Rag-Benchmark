# Modelos de embedding elegidos: justificación de requisitos

**Práctica:** benchmark de LLMs y embeddings locales para RAG
**Corpus:** Estatuto de los Trabajadores (BOE) y Manual del Administrador de Debian (ES)
**Fuente de los datos:** fichas oficiales de Hugging Face (consultadas el 17/11/2026)

---

## 1. Resumen

| Modelo | Params | Dimensión | Long. máx. | Idioma | Licencia | Familia |
|---|---|---|---|---|---|---|
| [Qwen/Qwen3-Embedding-0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B) | ~600M | 1024 (MRL 32–1024) | 32K | Multilingüe (100+) | Apache 2.0 | Qwen3 (Alibaba) |
| [jinaai/jina-embeddings-v2-base-es](https://huggingface.co/jinaai/jina-embeddings-v2-base-es) | ~161M | 768 | 8192 | Español + inglés | Apache 2.0 | JinaBERT (Jina AI) |
| [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) | ~568M | 1024 | 8192 | Multilingüe (100+) | MIT | XLM-RoBERTa (BAAI) |

---

## 2. Comprobación de requisitos

| Requisito | ¿Cumple? | Justificación |
|---|---|---|
| Mínimo 3 modelos | ✅ | Tenemos 3. |
| Hasta ~1B parámetros | ✅ | El mayor es Qwen3-Embedding con ~600M. |
| Al menos uno multilingüe | ✅ | Dos multilingües (Qwen3-Embedding y bge-m3) y uno bilingüe español-inglés (jina). |
| Entiende bien el español | ✅ | Los tres están entrenados con español; ninguno es solo de inglés. |
| Memoria | ✅ | Ninguno pasa de ~1,2 GB en FP16 (ver tabla de VRAM). Caben en 20 GB y en el plan B de 8 GB junto al LLM. |
| Longitud de entrada | ✅ | El límite más bajo es 8192 tokens (jina y bge-m3). Nuestros chunks serán mucho más cortos, así que los tres indexan el chunk completo. |
| Variedad | ✅ | Tres familias distintas: Qwen3, JinaBERT y XLM-RoBERTa. |
| Licencia y formato | ✅ | Apache 2.0 y MIT, de uso libre. Los tres funcionan con `sentence-transformers`. |

### Estimación de VRAM

`VRAM ≈ parámetros × bytes por parámetro` (FP16 = 2 bytes)

| Modelo | Precisión | Cálculo | VRAM aprox. |
|---|---|---|---|
| Qwen3-Embedding-0.6B | FP16 | 0,6B × 2 | ~1,2 GB |
| jina-embeddings-v2-base-es | FP16 | 0,16B × 2 | ~0,3 GB |
| bge-m3 | FP16 | 0,57B × 2 | ~1,1 GB |

> Son estimaciones. La VRAM real se mide en la Fase 2.

---

## 3. Prefijos e instrucciones

Si no se usan, la comparación no es justa: es una de las *trampas habituales* del enunciado.

| Modelo | ¿Necesita prefijo? | Consulta | Documento |
|---|---|---|---|
| Qwen3-Embedding-0.6B | **Sí, solo en la consulta** | `Instruct: {tarea}\nQuery:{pregunta}` | texto tal cual |
| jina-embeddings-v2-base-es | No | texto tal cual | texto tal cual |
| bge-m3 | No | texto tal cual | texto tal cual |

Tarea de ejemplo de la ficha de Qwen3:
`Given a web search query, retrieve relevant passages that answer the query`

La misma instrucción se usa para todas las preguntas y queda fijada para todo el benchmark.

### Notas técnicas

- **Qwen3-Embedding:** necesita `transformers >= 4.51.0` y `sentence-transformers >= 2.7.0`. Con versiones anteriores da `KeyError: 'qwen3'`.
- **Qwen3-Embedding:** el tokenizer usa padding a la izquierda (`padding_side="left"`).
- **Qwen3-Embedding:** flash attention es opcional; acelera y ahorra memoria.
- **jina-embeddings-v2-base-es:** se carga con `trust_remote_code=True`.

---

## 4. Por qué esta combinación

- **Especializado frente a multilingüe:** jina está entrenado específicamente para español (con inglés), y los otros dos son multilingües generales.
- **Encaja con Debian:** jina está pensado para texto español con términos en inglés, justo lo que tiene el manual.
- **Calidad de referencia:** Qwen3-Embedding-0.6B tiene una media de 64,33 en MTEB multilingüe, una de las más altas por debajo de 1B. Lo usamos como techo de calidad.
- **Coste:** jina (~161M) es casi 4 veces más pequeño que los otros dos. Esto sirve para la regla de *elegir el más pequeño y barato que cumpla los umbrales*.
- **Pregunta para el viernes:** ¿rinde igual un modelo pequeño especializado en español que uno multilingüe casi 4 veces más grande?