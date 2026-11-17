# Modelos de embedding elegidos: justificación de requisitos

**Práctica:** benchmark de LLMs y embeddings locales para RAG
**Corpus:** Estatuto de los Trabajadores (BOE) y Manual del Administrador de Debian (ES)
**Fuente de los datos:** fichas oficiales de Hugging Face (consultadas el 17/11/2026)

---

## 1. Resumen

| Modelo | Params | Dimensión | Long. máx. | Idioma | Licencia | Familia |
|---|---|---|---|---|---|---|
| [google/embeddinggemma-300m](https://huggingface.co/google/embeddinggemma-300m) | ~300M | 768 | 2048 | Multilingüe (100+) | Gemma Terms | Gemma 3 (Google) |
| [jinaai/jina-embeddings-v2-base-es](https://huggingface.co/jinaai/jina-embeddings-v2-base-es) | ~161M | 768 | 8192 | Español + inglés | Apache 2.0 | JinaBERT (Jina AI) |
| [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) | ~568M | 1024 | 8192 | Multilingüe (100+) | MIT | XLM-RoBERTa (BAAI) |

---

## 2. Comprobación de requisitos

| Requisito | ¿Cumple? | Justificación |
|---|---|---|
| Mínimo 3 modelos | ✅ | Tenemos 3. |
| Hasta ~1B parámetros | ✅ | El mayor es bge-m3 con ~568M. |
| Al menos uno multilingüe | ✅ | Dos multilingües (embeddinggemma y bge-m3) y uno bilingüe español-inglés (jina). |
| Entiende bien el español | ✅ | Los tres están entrenados con español; ninguno es solo de inglés. |
| Memoria | ✅ | Ninguno pasa de ~1,2 GB (ver tabla de VRAM). Caben en 20 GB y en el plan B de 8 GB junto al LLM. |
| Longitud de entrada | ✅ | El límite más bajo es 2048 tokens (embeddinggemma). Con chunks de menos de 2048 tokens, los tres indexan el chunk completo. |
| Variedad | ✅ | Tres familias distintas: Gemma, JinaBERT y XLM-RoBERTa. |
| Licencia y formato | ✅ | MIT y Apache 2.0 de uso libre; Gemma aceptando términos en HF. Los tres funcionan con `sentence-transformers`. |

### Estimación de VRAM

`VRAM ≈ parámetros × bytes por parámetro`

| Modelo | Precisión | Cálculo | VRAM aprox. |
|---|---|---|---|
| embeddinggemma-300m | FP32* | 0,3B × 4 | ~1,2 GB |
| jina-embeddings-v2-base-es | FP16 | 0,16B × 2 | ~0,3 GB |
| bge-m3 | FP16 | 0,57B × 2 | ~1,1 GB |

\* embeddinggemma **no admite float16**: hay que usar float32 o bfloat16 (en bfloat16 serían ~0,6 GB).

> Son estimaciones. La VRAM real se mide en la Fase 2.

---

## 3. Prefijos e instrucciones

Si no se usan, la comparación no es justa: es una de las *trampas habituales* del enunciado.

| Modelo | ¿Necesita prefijo? | Consulta | Documento |
|---|---|---|---|
| embeddinggemma-300m | **Sí** | `task: search result \| query: {pregunta}` | `title: {título o none} \| text: {chunk}` |
| jina-embeddings-v2-base-es | No | texto tal cual | texto tal cual |
| bge-m3 | No | texto tal cual | texto tal cual |

- Para el BOE, el título del documento puede ser el del artículo (p. ej. `Artículo 38. Vacaciones anuales`).
- Para Debian, el título de la sección.
- `jina-embeddings-v2-base-es` necesita `trust_remote_code=True` al cargarlo.

---

## 4. Por qué esta combinación

- **Especializado frente a multilingüe:** jina está entrenado específicamente para español (con inglés), y los otros dos son multilingües generales.
- **Encaja con Debian:** jina está pensado para texto español con términos en inglés, justo lo que tiene el manual.
- **Tres tamaños:** pequeño (~161M), medio (~300M) y grande (~568M). Esto sirve para la regla de *elegir el más pequeño y barato que cumpla los umbrales*.
- **Pregunta para el viernes:** ¿rinde igual un modelo pequeño especializado en español que uno multilingüe 3,5 veces más grande?
