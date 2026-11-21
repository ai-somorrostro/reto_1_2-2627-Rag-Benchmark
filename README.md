# Práctica: benchmark de LLMs y embeddings locales para RAG

## Objetivo

Cada grupo decide, con datos que mide él mismo, qué modelo de embedding y qué LLM local usaría en un sistema RAG para cada uno de los dos escenarios, y lo defiende el viernes. El código y los registros de ejecución son la evidencia: una cifra sin ellos no cuenta.

## Los dos escenarios

Todos los grupos usan los mismos dos corpus, así los resultados se pueden comparar entre grupos el viernes.

| Escenario | Documento | Qué pone a prueba |
| --- | --- | --- |
| 1. Normativa larga | [Estatuto de los Trabajadores](https://www.boe.es/eli/es/rdlg/2015/10/23/2/con), RDL 2/2015, texto consolidado (BOE-A-2015-11430) | Artículos parecidos entre sí, lenguaje jurídico, remisiones entre artículos, citar el artículo exacto |
| 2. Documentación técnica | [El manual del Administrador de Debian](https://www.debian.org/doc/manuals/debian-handbook/index.es.html), edición en español para Debian 11 | Prosa mezclada con comandos, rutas y opciones; términos en inglés dentro del español |

- **BOE:** usad el texto consolidado en HTML o el [PDF consolidado](https://www.boe.es/buscar/pdf/2015/BOE-A-2015-11430-consolidado.pdf). Si usáis el PDF, quitad cabeceras y pies de página antes de trocear.
- **Debian:** mejor HTML o [EPUB](https://debian-handbook.info/download/es-ES/stable/debian-handbook.epub) que PDF. Conservad los títulos de sección para poder citarlos.
- **Extra opcional:** la [versión en inglés](https://debian-handbook.info/get/) del manual permite medir qué pasa al preguntar en español sobre un corpus en inglés.

## Decisiones del grupo y mínimos

El grupo elige sus candidatos libremente, respetando estos mínimos.

| Componente | Mínimo | Condición |
| --- | --- | --- |
| Modelos de embedding | 3 | Hasta unos 1B parámetros; al menos uno multilingüe |
| LLM pequeños | 2 | Entre 1B y 3B parámetros |
| LLM medianos | 2 | Entre 7B y 9B parámetros |
| Stack de inferencia | 1 | Justificado; comparar dos es un extra |
| Cuantización | Libre | Indicadla siempre; comparar Q4 y Q8 del mismo modelo es un extra |

Criterios para elegir candidatos:

- **Idioma:** que entienda bien el español. Muchos embeddings populares solo funcionan bien en inglés.
- **Memoria:** haced la cuenta antes de descargar. VRAM ≈ parámetros × bytes por parámetro (FP16 = 2, Q8 ≈ 1, Q4 ≈ 0,6) + 1–3 GB de caché KV + el embedding.
- **Longitud de entrada:** la longitud máxima del embedding y la ventana de contexto del LLM deben admitir vuestros chunks y vuestro prompt.
- **Variedad:** mejor familias distintas que tres versiones del mismo modelo.
- **Licencia y formato:** que se pueda usar y que lo admita vuestro stack.

Dónde buscar: [MTEB](https://huggingface.co/spaces/mteb/leaderboard) (filtrad multilingüe y retrieval), [Hugging Face](https://huggingface.co/models) y la [biblioteca de Ollama](https://ollama.com/library). Un ranking sirve para elegir candidatos, no para decidir.

## Fase 1: corpus y golden set

Al acabar esta fase tenéis los dos corpus troceados y un golden set de 15 preguntas por escenario. La limpieza y el chunking los decidís vosotros; una vez elegidos, fijadlos para todo el benchmark.

El golden set de cada escenario incluye:

- 8 preguntas directas: la respuesta está en un solo fragmento.
- 4 preguntas que necesitan combinar dos fragmentos.
- 3 preguntas sin respuesta en el corpus, para medir la abstención.

Cada pregunta lleva su respuesta esperada y los fragmentos del corpus que la contienen. No copiéis frases literales del documento en las preguntas.

Los conjuntos de preguntas de este proyecto están en [`data/golden_set/`](data/golden_set/) y su formato se describe en [docs/pipeline/golden-set.md](docs/pipeline/golden-set.md).

| Tipo | Pregunta de ejemplo | Respuesta esperada |
| --- | --- | --- |
| Directa | ¿Cuántos días de vacaciones me corresponden como mínimo? | 30 días naturales (art. 38) |
| Sin respuesta | ¿Cuánto es el salario mínimo este año? | No aparece: el art. 27 dice que lo fija el Gobierno, pero no da la cifra |

## Fase 2: benchmark de embeddings

Objetivo: elegir un embedding por escenario midiendo solo el retrieval, sin LLM.

- Los modelos fijados para el benchmark son `snowflake-arctic-embed-l-v2.0`,
  `Nemotron-3.5-Embed-1B-BF16` y `hs-embed-1`. Sus IDs locales, prefijos,
  pooling y límites están en [`config/embeddings.toml`](config/embeddings.toml).
- Debian se mide con el manual español y también con el manual inglés usando
  las mismas preguntas en español. Los chunks y el golden set ingleses están
  separados en `artifacts/chunks-english/` y `data/golden_set/debian-en.jsonl`.
- Ejecución e interpretación de métricas: [docs/pipeline/embedding-benchmark.md](docs/pipeline/embedding-benchmark.md).
- **Mínimo a reportar por modelo:** Recall@1, Recall@3, Recall@5, MRR, tiempo de indexado, tamaño del índice y VRAM.
- **Criterio:** mejor Recall@5; desempate por MRR y después por coste.
- **Ojo:** algunos modelos necesitan prefijos o instrucciones en la consulta. Sin ellos, la comparación no es justa.

## Fase 3: benchmark de LLMs

Objetivo: con el embedding ganador fijo, comparar los LLMs en calidad y en coste.

- **Misma configuración para todos:** top-k, prompt, temperatura 0 y límite de tokens de salida.
- **El prompt lo diseñáis vosotros,** pero debe pedir que responda solo con los fragmentos, que diga «No aparece en el documento» si no está y que cite el artículo o la sección.
- **Calidad:** puntuad a mano las respuestas con la escala de la sección de métricas.
- **Coste:** medidlo en al menos 5 preguntas por modelo; descartad la primera ejecución, repetid 3 veces y usad la mediana.
- **Ejecución local:** candidatos, comandos, registros y puntuación manual: [docs/pipeline/llm-benchmark.md](docs/pipeline/llm-benchmark.md).
- **Extra opcional:** pasad al LLM directamente el fragmento correcto. Si así acierta y con el retrieval no, el fallo es del retrieval.

## Fase 4: decisión por escenario

La regla es elegir el modelo más pequeño y barato que cumple vuestros umbrales de calidad.

1. **Fijad los umbrales antes de ver los resultados** y escribidlos. Ejemplo orientativo: Recall@5 ≥ 0,80; respuestas no fieles ≤ 10 %; abstención correcta ≥ 2 de 3; latencia total ≤ 5 s.
2. **Descartad lo que no cumple**, por rápido o barato que sea.
3. **Entre los que cumplen, quedaos con el más barato:** menos VRAM, más tokens/s, menos latencia.
4. **Decidid por separado para cada escenario.** Lo que vale para el BOE puede no valer para Debian.
5. **Plan B:** repetid la decisión como si solo tuvierais 8 GB de VRAM.

El resultado de esta fase es una frase por escenario: «Para X usaría Y porque Z», con los números que la respaldan.

## Métricas: qué medir y qué priorizar

El orden de prioridad es: primero el retrieval, después la honestidad del LLM, después la corrección, y el coste solo para desempatar entre modelos que ya cumplen.

| Prioridad | Métrica | Qué mide | Cómo se calcula | Qué decisión informa |
| --- | --- | --- | --- | --- |
| 1 | Recall@k | Si el fragmento correcto llega a los k primeros | Preguntas con acierto en el top-k / preguntas con respuesta | Embedding, chunking, top-k |
| 2 | Fidelidad | Si todo lo que afirma está en los fragmentos | % de respuestas sin datos inventados | Tamaño del LLM |
| 2 | Abstención correcta | Si dice «no aparece» cuando no está | Abstenciones / preguntas sin respuesta | Tamaño del LLM |
| 3 | Corrección | Si la respuesta coincide con la esperada | Media de la escala 0–2 | Tamaño del LLM, cuantización |
| 3 | Falsas abstenciones | Si dice «no aparece» cuando sí está | Abstenciones / preguntas con respuesta | Prompt, tamaño del LLM |
| 4 | MRR | Si el fragmento correcto sale arriba | Media de 1 / posición del primer acierto | Desempate de embeddings |
| 4 | Formato e idioma | Español y cita del artículo o sección | % de respuestas que cumplen | Tamaño del LLM, prompt |
| Requisito | VRAM pico | Si cabe en 20 GB y con qué margen | Máximo de memoria de GPU durante la prueba | Tamaño, cuantización, stack |
| 5 | Latencia total y TTFT | Cuánto espera el usuario | Mediana de 3 ejecuciones tras calentar | Tamaño, cuantización, stack |
| 5 | Tokens por segundo | Velocidad de generación | Tokens generados / tiempo de generación | Stack, cuantización |
| 5 | Tiempo de indexado y tamaño del índice | Coste de preparar el corpus | Tiempo total y espacio en disco | Embedding |

Escala de corrección: **2** correcta y completa, **1** incompleta o imprecisa, **0** incorrecta. En las preguntas sin respuesta, «No aparece en el documento» cuenta como 2.

No prioricéis estas métricas:

- **BLEU y ROUGE:** cuentan palabras coincidentes y castigan una paráfrasis correcta.
- **Perplejidad:** mide lo fluido que es el texto, no si la respuesta es correcta.
- **Rankings generales (MMLU, leaderboards):** no usan vuestro corpus ni vuestro idioma.
- **Tokens por segundo sin mirar la calidad:** un modelo rápido que inventa no sirve.
- **Una sola ejecución:** la primera siempre es más lenta (carga del modelo).

En la literatura sobre evaluación de RAG estos conceptos aparecen como faithfulness, answer correctness, context precision y context recall. Si un LLM local hace de juez, validad a mano al menos 10 respuestas y anotad cuántas coinciden con vuestra nota.

## Reglas para un benchmark justo

Si cambiáis dos cosas a la vez, no sabréis cuál explica la diferencia.

- Cambiad una sola variable cada vez.
- Mismo chunking, top-k y prompt para todos los modelos.
- Temperatura 0 o la más baja posible.
- Las mismas preguntas para todos los modelos.
- Medid el retrieval por separado de la generación.
- Calentad el modelo antes de medir velocidad.
- Anotad versión, cuantización y stack de cada prueba.
- Comprobad que el prompt cabe en la ventana de contexto.

Trampas habituales:

| Trampa | Qué pasa |
| --- | --- |
| Modo de razonamiento activo por defecto | Más latencia y texto extra en la respuesta |
| Ventana de contexto del servidor menor que el prompt | Los fragmentos se cortan sin dar error |
| Olvidar los prefijos o instrucciones del embedding | Recall más bajo de lo que da el modelo |
| Chunks más largos que el límite del embedding | El final del chunk no se indexa |
| Comparar el Q4 de un modelo con el FP16 de otro | Comparáis cuantizaciones, no modelos |
| PDF con cabeceras y pies de página | Ruido repetido en todos los chunks |

## Plantillas de resultados

Rellenad una tabla de cada tipo por escenario. Son las que se enseñan el viernes.

**Tabla A. Embeddings — BOE**

| Modelo | Parámetros | Dimensión | Recall@1 | Recall@3 | Recall@5 | MRR | Indexado (s) | Índice (MB) | VRAM (GB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hs-embed-1 | 0.11B | 384 | 0.333 | 0.583 | 0.750 | 0.711 | 0.94 | 0.51 | 0.57 |
| Nemotron-3.5-Embed-1B-BF16 | 1.55B | 2048 | 0.583 | 0.833 | 1.000 | 0.944 | 4.02 | 2.73 | 3.23 |
| snowflake-arctic-embed-l-v2.0 | 0.57B | 1024 | 0.500 | 0.833 | 0.917 | 0.892 | 10.68 | 1.36 | 2.36 |

**Tabla A. Embeddings — Debian (preguntas en español, corpus por idioma)**

| Modelo | Idioma del corpus | Parámetros | Dimensión | Recall@1 | Recall@3 | Recall@5 | MRR | Indexado (s) | Índice (MB) | VRAM (GB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hs-embed-1 | Español | 0.11B | 384 | 0.417 | 0.583 | 0.667 | 0.756 | 4.10 | 1.57 | 0.92 |
| hs-embed-1 | Inglés | 0.11B | 384 | 0.417 | 0.667 | 0.833 | 0.795 | 3.89 | 1.49 | 0.92 |
| Nemotron-3.5-Embed-1B-BF16 | Español | 1.55B | 2048 | 0.417 | 0.750 | 0.833 | 0.799 | 20.56 | 8.39 | 3.87 |
| Nemotron-3.5-Embed-1B-BF16 | Inglés | 1.55B | 2048 | 0.417 | 0.750 | 0.833 | 0.799 | 18.68 | 7.92 | 3.85 |
| snowflake-arctic-embed-l-v2.0 | Español | 0.57B | 1024 | 0.500 | 0.583 | 0.583 | 0.801 | 58.12 | 4.20 | 2.74 |
| snowflake-arctic-embed-l-v2.0 | Inglés | 0.57B | 1024 | 0.500 | 0.750 | 0.750 | 0.879 | 54.85 | 3.96 | 2.77 |

**Tabla B. LLMs: calidad — BOE**

| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen2.5-3B-Instruct | 3.09B | Ninguna (BF16) | 1.53 | 66.7 | 3/3 | 3 | 33.3 |
| Llama-3.2-3B-Instruct | 3.21B | Ninguna (BF16) | 0.67 | 46.7 | 3/3 | 8 | 26.7 |
| Qwen2.5-7B-Instruct | 7.62B | Ninguna (BF16) | 1.73 | 93.3 | 3/3 | 1 | 86.7 |
| Granite-4.1-8B-llmon-preview | 8.79B | Ninguna (BF16) | 1.67 | 93.3 | 3/3 | 0 | 100.0 |

**Tabla B. LLMs: calidad — Debian**

| Modelo | Tamaño | Cuantización | Corrección media (0–2) | Respuestas fieles (%) | Abstención correcta (de 3) | Falsas abstenciones | Formato e idioma (%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen2.5-3B-Instruct | 3.09B | Ninguna (BF16) | 1.40 | 80.0 | 1/3 | 0 | 6.7 |
| Llama-3.2-3B-Instruct | 3.21B | Ninguna (BF16) | 1.13 | 60.0 | 3/3 | 1 | 20.0 |
| Qwen2.5-7B-Instruct | 7.62B | Ninguna (BF16) | 1.67 | 93.3 | 2/3 | 0 | 46.7 |
| Granite-4.1-8B-llmon-preview | 8.79B | Ninguna (BF16) | 1.60 | 86.7 | 1/3 | 0 | 53.3 |

**Tabla C. LLMs: coste — BOE**

| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) |
| --- | --- | --- | --- | --- | --- |
| Qwen2.5-3B-Instruct | vLLM | 0.11 | 70.48 | 1.21 | 6.75 |
| Llama-3.2-3B-Instruct | vLLM | 0.11 | 86.55 | 0.19 | 6.85 |
| Qwen2.5-7B-Instruct | vLLM | 0.24 | 44.79 | 2.16 | 15.66 |
| Granite-4.1-8B-llmon-preview | vLLM | 0.30 | 36.01 | 4.88 | 17.20 |

**Tabla C. LLMs: coste — Debian**

| Modelo | Stack | TTFT (s) | Tokens/s | Latencia total (s) | VRAM pico (GB) |
| --- | --- | --- | --- | --- | --- |
| Qwen2.5-3B-Instruct | vLLM | 0.12 | 71.89 | 1.34 | 6.75 |
| Llama-3.2-3B-Instruct | vLLM | 0.12 | 86.60 | 0.45 | 6.85 |
| Qwen2.5-7B-Instruct | vLLM | 0.26 | 44.73 | 3.43 | 15.66 |
| Granite-4.1-8B-llmon-preview | vLLM | 0.32 | 35.98 | 2.88 | 17.20 |

Las puntuaciones de calidad son anotaciones manuales de las 15 respuestas por
modelo y escenario, comparadas con la respuesta esperada y los fragmentos
recuperados. Una abstención correcta en preguntas sin respuesta se considera
fiel y no necesita cita; las respuestas sustantivas deben estar en español y
citar un artículo o sección para contar en «Formato e idioma». El detalle por
respuesta está en [`scores.jsonl`](artifacts/llms/20261120T122007.077886Z/scores.jsonl)
y las métricas derivadas en
[`quality_summary.csv`](artifacts/llms/20261120T122007.077886Z/quality_summary.csv).
Las métricas de coste son medianas de cinco preguntas con tres repeticiones por
pregunta después del calentamiento; la VRAM pico es la reservada por PyTorch.
Los datos brutos están en
[`responses.jsonl`](artifacts/llms/20261120T122007.077886Z/responses.jsonl),
[`cost_runs.jsonl`](artifacts/llms/20261120T122007.077886Z/cost_runs.jsonl)
y [`cost_summary.csv`](artifacts/llms/20261120T122007.077886Z/cost_summary.csv).

Para la puntuación a mano, registrad de cada respuesta: la pregunta, el modelo, la respuesta tal como salió, la corrección (0–2), si es fiel (sí/no), si se abstiene (sí/no/no aplica) y si cumple formato e idioma (sí/no).

## Entrega del viernes

Cada grupo presenta 10 minutos y entrega su material de trabajo.

1. **Candidatos y stack:** qué modelos y stack elegisteis, y por qué.
2. **Resultados:** las tablas A, B y C de cada escenario.
3. **Recomendación:** «Para X usaría Y porque Z», una por escenario, con vuestros umbrales.
4. **Plan B:** qué cambiaríais con solo 8 GB de VRAM.
5. **Lo que no esperabais:** un resultado que os sorprendió y cómo lo explicáis.

Evidencias obligatorias (sin ellas, los resultados no se dan por válidos):

- **Código** que genera todas las cifras y se ejecuta de principio a fin.
- **Registros brutos de cada ejecución:** modelo, versión, cuantización, stack, parámetros, fecha y hora.
- **Respuestas de los LLMs tal como salieron**, junto a su puntuación a mano.
- **Registro del uso de memoria de la GPU** durante las medidas de VRAM.
- **Trazabilidad:** cada cifra de las tablas sale de un fichero de resultados concreto.

## Recursos

- [Estatuto de los Trabajadores, texto consolidado (BOE)](https://www.boe.es/eli/es/rdlg/2015/10/23/2/con) y [PDF consolidado](https://www.boe.es/buscar/pdf/2015/BOE-A-2015-11430-consolidado.pdf)
- [El manual del Administrador de Debian, en español](https://www.debian.org/doc/manuals/debian-handbook/index.es.html), [EPUB](https://debian-handbook.info/download/es-ES/stable/debian-handbook.epub) y [otras versiones e idiomas](https://debian-handbook.info/get/)
- [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- [Biblioteca de modelos de Ollama](https://ollama.com/library)
