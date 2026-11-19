# Modelos de embedding elegidos: justificación de requisitos
 
**Práctica:** benchmark de LLMs y embeddings locales para RAG
**Corpus:** Estatuto de los Trabajadores (BOE) y Manual del Administrador de Debian (ES)
**Fuente de los datos:** fichas oficiales de Hugging Face (consultadas el 17/11/2026 y el 19/11/2026)
 
---
 
## 1. Resumen
 
| Modelo | Params | Dimensión | Long. máx. | Idioma | Licencia | Organización |
|---|---|---|---|---|---|---|
| [Qwen/Qwen3-Embedding-0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B) | ~600M | 1024 (MRL 32–1024) | 32K | Multilingüe (100+) | Apache 2.0 | Alibaba (Qwen) |
| [microsoft/harrier-oss-v1-0.6b](https://huggingface.co/microsoft/harrier-oss-v1-0.6b) | ~600M | 1024 | 32K | Multilingüe (incluye español) | MIT | Microsoft |
| [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) | ~568M | 1024 | 8192 | Multilingüe (100+) | MIT | BAAI |
 
---
 
## 2. Comprobación de requisitos
 
| Requisito | ¿Cumple? | Justificación |
|---|---|---|
| Mínimo 3 modelos | ✅ | Tenemos 3. |
| Hasta ~1B parámetros | ✅ | Los tres rondan los 600M. |
| Al menos uno multilingüe | ✅ | Los tres son multilingües. |
| Entiende bien el español | ✅ | Los tres incluyen el español entre sus idiomas de entrenamiento; ninguno es solo de inglés. |
| Memoria | ✅ | Ninguno pasa de ~1,2 GB en FP16 (ver tabla de VRAM). Caben en 20 GB y en el plan B de 8 GB junto al LLM. |
| Longitud de entrada | ✅ | El límite más bajo es 8192 tokens (bge-m3). Nuestros chunks miden como máximo ~1.800 caracteres (~500 tokens), así que los tres indexan el chunk completo. |
| Variedad | ⚠️ | Tres organizaciones y entrenamientos distintos, pero dos arquitecturas: bge-m3 es un encoder (XLM-RoBERTa); Qwen3-Embedding y harrier son decoder. La ficha de harrier lleva la etiqueta `qwen3`, así que probablemente comparten la arquitectura base de Qwen3, aunque son modelos entrenados por separado. |
| Licencia y formato | ✅ | Apache 2.0 y MIT, de uso libre. Los tres funcionan con `sentence-transformers`. |
 
### Estimación de VRAM
 
`VRAM ≈ parámetros × bytes por parámetro` (FP16 = 2 bytes)
 
| Modelo | Precisión | Cálculo | VRAM aprox. |
|---|---|---|---|
| Qwen3-Embedding-0.6B | FP16 | 0,6B × 2 | ~1,2 GB |
| harrier-oss-v1-0.6b | FP16 | 0,6B × 2 | ~1,2 GB |
| bge-m3 | FP16 | 0,57B × 2 | ~1,1 GB |
 
> Son estimaciones. La VRAM real se mide en la Fase 2.
 
---
 
## 3. Prefijos e instrucciones
 
Si no se usan, la comparación no es justa: es una de las *trampas habituales* del enunciado.
 
| Modelo | ¿Necesita prefijo? | Consulta | Documento |
|---|---|---|---|
| Qwen3-Embedding-0.6B | **Sí, solo en la consulta** | `Instruct: {tarea}\nQuery:{pregunta}` | texto tal cual |
| harrier-oss-v1-0.6b | **Sí, solo en la consulta** | `Instruct: {tarea}\nQuery: {pregunta}` | texto tal cual |
| bge-m3 | No | texto tal cual | texto tal cual |
 
Tarea usada en los dos modelos con instrucción (la de sus fichas):
`Given a web search query, retrieve relevant passages that answer the query`
 
- En harrier es el prompt `web_search_query` de su `config_sentence_transformers.json`.
- La ficha de harrier avisa de que sin la instrucción el rendimiento baja.
- La misma instrucción se usa para todas las preguntas y queda fijada para todo el benchmark.
### Notas técnicas
 
- **Qwen3-Embedding:** necesita `transformers >= 4.51.0` y `sentence-transformers >= 2.7.0`. Con versiones anteriores da `KeyError: 'qwen3'`.
- **Qwen3-Embedding:** el tokenizer usa padding a la izquierda (`padding_side="left"`).
- **harrier:** los pesos se publican en BF16; en el benchmark se carga en FP16, igual que los otros dos, para que la comparación sea justa.
- **harrier:** usa la similitud coseno, como los otros dos.
---
 
## 4. Por qué esta combinación
 
- **Encoder frente a decoder:** bge-m3 (encoder) frente a Qwen3-Embedding y harrier (decoder).
- **Mismo tamaño, distinto entrenamiento:** Qwen3-Embedding y harrier tienen ~600M parámetros; la comparación muestra si el entrenamiento de Microsoft o el de Alibaba rinde mejor en nuestros corpus.
- **Notas de referencia:** Qwen3-Embedding-0.6B tiene una media de 64,33 en MTEB multilingüe, y harrier-oss-v1-0.6b declara 69,0 en MTEB v2 multilingüe. Un ranking sirve para elegir candidatos, no para decidir.
- **Pregunta para el viernes:** ¿se mantiene en nuestros corpus en español la ventaja que harrier tiene en MTEB?
 