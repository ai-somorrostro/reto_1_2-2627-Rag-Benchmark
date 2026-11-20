# Benchmark de Embeddings y LLMs Locales para Sistemas RAG

> **Proyecto de Práctica:** Evaluación en local para arquitectura RAG (*Retrieval-Augmented Generation*)  
> **Autores (Alumnos):** Alfred, Ane y Naiara  
> **Entorno de pruebas:** GPU NVIDIA A800, Ubuntu Linux, Python 3.12, PyTorch y Ollama

---

## 1. ¿De qué va este proyecto?

En esta práctica hemos diseñado, medido y analizado un sistema **RAG (*Retrieval-Augmented Generation*) 100% local**.

Cuando usamos un modelo de inteligencia artificial para responder preguntas sobre documentos específicos (como leyes o manuales de informática), los modelos normales suelen fallar:
- **Alucinan:** se inventan datos si no los saben con certeza.
- **No están actualizados:** su conocimiento termina el día en que fueron entrenados.
- **No son transparentes:** no pueden citar exactamente el número de artículo o la sección de donde sale la información.

Un sistema **RAG** soluciona esto en dos pasos muy sencillos:
1. **Recuperación (*Retrieval*):** cuando el usuario hace una pregunta, buscamos en nuestros propios documentos troceados cuáles son los 3 o 5 fragmentos más relevantes mediante modelos de *embedding* (vectores numéricos).
2. **Generación con LLM:** le pasamos esos fragmentos seleccionados a un modelo de lenguaje (LLM) con una instrucción muy estricta: *«Responde únicamente utilizando los fragmentos adjuntos, cita la fuente exacta y si el dato no aparece, di textualmente "No aparece en el documento"»*.

Nuestro objetivo como grupo ha sido **medir con datos reales** qué combinación de modelo de embedding y qué LLM funciona mejor para dos documentos radicalmente distintos.

---

## 2. Los Dos Escenarios Evaluados

Trabajamos sobre dos corpus oficiales que ponen a prueba retos muy diferentes:

| Escenario | Documento Oficial | Tipo de Texto | Retos Específicos |
| :--- | :--- | :--- | :--- |
| **1. Normativa Jurídica** | **Estatuto de los Trabajadores** (BOE consolidado, RDL 2/2015) | Legal / Legislativo | Artículos largos y formalmente parecidos entre sí, remisiones cruzadas («según lo dispuesto en el art. 12...») y necesidad de citar el artículo exacto con tolerancia cero al error. |
| **2. Documentación Técnica** | **Manual del Administrador de Debian** (Debian 11 Bullseye, en español) | Técnico / Informático | Prosa técnica mezclada con comandos de terminal (`apt`, `dpkg`), rutas de archivos (`/etc/...`), parámetros y términos en inglés dentro de frases en castellano. |

---

## 3. Arquitectura del Sistema RAG

El flujo completo que hemos implementado se divide en 4 fases conectadas:

```
[Documentos EPUB] 
       │
       ▼ (Fase 1: Extracción HTML + Chunking con overlap + Inyección de Título)
[Fragmentos / Chunks JSON]
       │
       ▼ (Fase 2: Sentence-Transformers / Modelos de Embedding)
[Vectores Densos en GPU] ──> Similitud Coseno con la Pregunta
       │
       ▼ (Top-3 Fragmentos más relevantes)
[Prompt del Sistema Estricto] + [Top-3 Chunks] + [Pregunta del Usuario]
       │
       ▼ (Fase 3: Inferencia en Ollama con Temperatura 0)
[Respuesta Fiel con Cita o Abstención Honesta]
```

---

## 4. Fase 1: Limpieza de Datos, Chunking y Golden Set

Todo el código de esta fase se encuentra documentado y explicado paso a paso en el notebook [`data/preparar_datos.ipynb`](file:///home/g4/reto_1_2-2627-Rag-Benchmark/data/preparar_datos.ipynb).

### ¿Por qué usamos EPUB en vez de PDF?
Descargamos los documentos originales en formato **EPUB**. Un archivo EPUB es internamente un `.zip` con código XHTML/HTML limpio. Al parsearlo directamente con Python (`zipfile`, `html.parser`):
- Eliminamos por completo el ruido típico de los PDF (cabeceras repetitivas, números de página en medio del texto, notas al pie cortando párrafos).
- Conservamos intactos los títulos de los artículos y capítulos.

### Nuestra estrategia de troceado (*Chunking*)
- **Estructura natural:** el corte respeta artículos enteros (en el BOE) o secciones de capítulo (en Debian).
- **Límite de 1.400 caracteres:** si cabe, el artículo o sección se guarda íntegro en un único fragmento.
- **Solapamiento (*Overlap*):** si es más largo, se divide por párrafos en bloques de **1.200 caracteres con 200 caracteres de solapamiento** para evitar cortar ideas a la mitad.
- **Metadatos en el texto:** cada fragmento lleva al inicio una cabecera `[Artículo X]` o `[Capítulo Y]`, asegurando que el embedding capture el tema principal.

### El Golden Set (Banco de Pruebas de 60 Preguntas)
Diseñamos a mano un conjunto de evaluación de **30 preguntas para el BOE** y **30 preguntas para Debian** (ubicadas en `preguntas/boe_questions.json` y `preguntas/debian_questions.json`). Cada conjunto cuenta con una distribución equilibrada:
- **16 Preguntas Directas (*single-hop*):** la respuesta se encuentra íntegra dentro de un único fragmento.
- **8 Preguntas Multi-fragmento (*multi-hop*):** requieren combinar y sintetizar información de dos artículos o secciones distintas.
- **6 Preguntas Negativas / Sin Respuesta (*unanswerable*):** evalúan si el sistema sabe abstenerse honestamente diciendo *«No aparece en el documento»* en vez de inventarse una respuesta.

---

## 5. Fase 2: Benchmark de Modelos de Embedding (Recuperación)

Evaluamos de forma aislada 3 modelos de embedding sobre los dos corpus, sin intervención de LLMs. El código completo está en [`benchmark_embeddings.ipynb`](file:///home/g4/reto_1_2-2627-Rag-Benchmark/benchmark_embeddings.ipynb).

### Modelos de Embedding Evaluados:
1. **`EmbeddingGemma-2`** (`google/embeddinggemma-2`): 0.7B parámetros, arquitectura densa de Google.
2. **`Spanish-BETO`** (`hiiamsid/sentence_similarity_spanish_es`): 0.11B parámetros, especialista monolingüe en castellano.
3. **`Multilingual-E5-Small`** (`intfloat/multilingual-e5-small`): 0.12B parámetros, modelo multilingüe de Microsoft optimizado con prefijos `passage:` y `query:`.

### Métricas de Retrieval:
- **Recall@k (k=1, 3, 5):** porcentaje de preguntas con respuesta donde el fragmento correcto (*ground truth*) aparece entre los $k$ primeros resultados devueltos.
- **MRR (*Mean Reciprocal Rank*):** premia que el fragmento acertado aparezca en la primera posición ($1 / \text{posición}$).
- **Coste computacional:** tiempo de indexado (segundos), tamaño del índice en disco (MB) y consumo de memoria VRAM (GB).

### Resultados Obtenidos (Tabla A):

#### Documento 1: Normativa Jurídica (BOE - Estatuto de los Trabajadores)
| Modelo | Parámetros | Dimensión | Recall@1 | Recall@3 | Recall@5 | MRR | Tiempo Indexado | Tamaño Índice | VRAM Pico |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **EmbeddingGemma-2** | 0.7B | 768 | 0.750 | **0.958** | **1.000** | **0.865** | 2.19 s | 1.23 MB | 2.82 GB |
| **Spanish-BETO** | 0.11B | 768 | 0.583 | 0.833 | 0.917 | 0.720 | 2.39 s | 1.23 MB | 2.13 GB |
| **Multilingual-E5-Small** | 0.12B | 384 | **0.792** | 0.833 | 0.958 | 0.844 | **0.97 s** | **0.62 MB** | **1.81 GB** |

#### Documento 2: Documentación Técnica (Manual del Administrador de Debian)
| Modelo | Parámetros | Dimensión | Recall@1 | Recall@3 | Recall@5 | MRR | Tiempo Indexado | Tamaño Índice | VRAM Pico |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **EmbeddingGemma-2** | 0.7B | 768 | 0.333 | **0.542** | **0.667** | 0.484 | 9.73 s | 3.54 MB | 9.97 GB |
| **Spanish-BETO** | 0.11B | 768 | 0.208 | 0.250 | 0.333 | 0.261 | 14.01 s | 3.54 MB | 2.37 GB |
| **Multilingual-E5-Small** | 0.12B | 384 | **0.417** | **0.542** | 0.625 | **0.493** | **4.00 s** | **1.77 MB** | **1.80 GB** |

### Selección de Ganadores en Embeddings:
- **Para el BOE:** Elegimos **`EmbeddingGemma-2`**. Alcanza un **Recall@5 perfecto del 100% (1.000)** y el mayor MRR (0.865). En leyes no podemos permitirnos perder el artículo clave.
- **Para Debian:** Elegimos **`Multilingual-E5-Small`**. Logra el mayor Recall@1 (41.7%) y el mejor MRR (0.493), consumiendo solo **1.80 GB de VRAM** y 4 segundos de indexado frente a los **9.97 GB** que necesitó EmbeddingGemma-2.
- **Elección Global:** **`Multilingual-E5-Small`**. Es el modelo más equilibrado, rápido y ligero para un despliegue completo en producción.

---

## 6. Fase 3: Benchmark de Modelos LLM (Generación)

Fijando los 3 mejores fragmentos recuperados para cada pregunta, evaluamos 4 LLMs locales servidos a través de **Ollama** con **temperatura = 0**. El código y las pruebas están en [`benchmark_llms.ipynb`](file:///home/g4/reto_1_2-2627-Rag-Benchmark/benchmark_llms.ipynb).

### Modelos LLM Evaluados:
- **Pequeños (~2.6B):** `Gemma-2-2B` (Google, Q4_0) y `Granite-3-2B` (IBM, Q4_K_M).
- **Medianos (~7B):** `Mistral-7B` (Mistral AI, Q4_K_M) y `Qwen-2.5-7B` (Alibaba Cloud, Q4_K_M).

### Métricas de Evaluación:
- **Corrección media (0 a 2):** 2 = correcta y completa, 1 = parcial, 0 = incorrecta (en preguntas sin respuesta, decir «No aparece» puntúa 2).
- **Fidelidad factual (%):** porcentaje de respuestas sin datos inventados fuera de los fragmentos.
- **Abstención correcta:** aciertos sobre las 12 preguntas negativas totales (6 de cada corpus).
- **Falsas abstenciones:** veces que el modelo dice «No aparece» a pesar de que la respuesta sí estaba en el texto.
- **Coste en GPU:** TTFT (*Time to First Token* en segundos), velocidad de generación (tokens/segundo), latencia total (segundos) y memoria VRAM (GB).

### Resultados de Calidad y Coste:

#### Tabla B: Calidad de Respuestas RAG (sobre las 60 preguntas)
| Modelo | Tamaño | Cuantización | Corrección Media (0–2) | % Fieles (Sin Alucinación) | Abstención Correcta | Falsas Abstenciones | Formato e Idioma (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Gemma-2-2B** | 2.6B | Q4_0 | 1.70 | 98.3 % | 11 / 12 | 6 | 98.3 % |
| **Granite-3-2B** | 2.6B | Q4_K_M | 1.68 | 98.3 % | 11 / 12 | **4** | 75.0 % |
| **Mistral-7B** | 7.2B | Q4_K_M | **1.75** | **100.0 %** | **12 / 12** | 6 | **100.0 %** |
| **Qwen-2.5-7B** | 7.6B | Q4_K_M | 1.73 | **100.0 %** | **12 / 12** | 8 | **100.0 %** |

#### Tabla C: Rendimiento y Coste Computacional en GPU
| Modelo | Inferencia | TTFT (s) | Velocidad (tok/s) | Latencia Media (s) | VRAM en GPU (GB) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Gemma-2-2B** | Ollama | 0.044 s | 86.7 tok/s | 0.44 s | 1.52 GB |
| **Granite-3-2B** | Ollama | 0.015 s | **98.9 tok/s** | **0.41 s** | **1.49 GB** |
| **Mistral-7B** | Ollama | 0.016 s | 72.9 tok/s | 0.68 s | 4.07 GB |
| **Qwen-2.5-7B** | Ollama | **0.014 s** | 74.0 tok/s | 0.43 s | 4.36 GB |

#### Desglose de Corrección por Tipo de Documento:
| Modelo | Corrección en BOE (Legal) | Corrección en Debian (Técnico) | Corrección Global |
| :--- | :---: | :---: | :---: |
| **Gemma-2-2B** | 1.80 / 2.00 | 1.60 / 2.00 | 1.70 / 2.00 |
| **Granite-3-2B** | 1.73 / 2.00 | **1.63 / 2.00** | 1.68 / 2.00 |
| **Mistral-7B** | 1.87 / 2.00 | **1.63 / 2.00** | **1.75 / 2.00** |
| **Qwen-2.5-7B** | **1.93 / 2.00** | 1.53 / 2.00 | 1.73 / 2.00 |

---

## 7. Fase 4: Decisiones Finales del Grupo

Siguiendo la regla de oro del proyecto: *«elegir el modelo más eficiente y barato que cumpla nuestros umbrales de calidad»*.

### Nuestras Decisiones Justificadas («Para X usaría Y porque Z»):

1. **Para el Escenario 1 (BOE - Normativa Legal):**
   > *«Para el BOE usaríamos **`Qwen-2.5-7B`** porque alcanza la nota más alta de todo el benchmark (**1.93 sobre 2.00**), con un **100% de respuestas fieles**, **6/6 en abstenciones correctas**, solo 1 falsa abstención y cita de forma impecable el artículo exacto en apenas 0.43 segundos».*
   - **Motivo:** en el ámbito laboral y legal un error o alucinación acarrea consecuencias graves; la fidelidad total es un requisito no negociable.

2. **Para el Escenario 2 (Debian - Documentación Técnica):**
   > *«Para Debian usaríamos **`Granite-3-2B`** porque empata en la máxima corrección técnica (**1.63 sobre 2.00**), comete solo 2 falsas abstenciones (frente a las 7 de Qwen y 5 de Mistral), genera texto a **98.9 tokens/segundo** y consume únicamente **1.49 GB de VRAM**».*
   - **Motivo:** en comandos y administración de sistemas los modelos grandes pecan a veces de exceso de prudencia; Granite es directo, ultra rápido y no se abstiene innecesariamente.

3. **Decisión Global para Todo el Sistema:**
   > *«Si la organización solo puede desplegar un único LLM para ambos corpus, nos quedamos con **`Qwen-2.5-7B`**».*
   - **Motivo:** ofrece un 100% de fidelidad factual (cero datos inventados), una corrección media sobresaliente (1.73 global) y es notablemente más rápido que Mistral (0.43 s de latencia frente a 0.68 s, con un TTFT de tan solo 14 milisegundos).

4. **Plan B (Si nuestro servidor solo tuviera 8 GB de VRAM):**
   > *«Si estuviéramos limitados a un servidor de 8 GB de VRAM, cambiaríamos el LLM a **`Gemma-2-2B`**».*
   - **Motivo:** `Multilingual-E5-Small` (1.80 GB) + `Qwen-2.5-7B` (4.36 GB) sumaría 6.16 GB, lo que dejaría poco margen para varias peticiones a la vez. Con `Gemma-2-2B` (1.52 GB), el sistema completo consume solo **3.32 GB de VRAM**, manteniendo un excelente **1.70 / 2.00** de corrección y dejando casi 5 GB de memoria libres para concurrencia.

---

## 8. Trabajo Extra: Comparativa de Cuantización (Q4 vs Q8)

Evaluamos de manera exhaustiva **`Qwen-2.5-7B`** en sus variantes `Q4_K_M` (~4 bits) y `Q8_0` (~8 bits) sobre las 60 preguntas del Golden Set para comprobar si duplicar la precisión de los pesos merece la pena en RAG:

| Cuantización | Tamaño en Disco | VRAM en GPU | Tokens/s | TTFT | Latencia Media | Corrección (0–2) | % Fieles | Abstención |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Q4_K_M** | **4.68 GB** | **4.36 GB** | **74.0 tok/s** | **0.014 s** | **0.43 s** | **1.73** | **100.0 %** | **12 / 12** |
| **Q8_0** | 8.10 GB | 7.76 GB | 61.1 tok/s | 0.021 s | 0.52 s | 1.72 | 100.0 % | 12 / 12 |

### Conclusión del Grupo sobre Cuantización:
**No compensa en absoluto usar Q8 en una arquitectura RAG.**
- La calidad factual es idéntica (1.73 frente a 1.72, ambas con 100% de fidelidad y 12/12 en abstención).
- Esto ocurre porque en RAG el conocimiento exacto lo aportan los fragmentos de texto inyectados en el contexto, no la memorización interna del modelo.
- Sin embargo, Q8 penaliza fuertemente el sistema: ocupa casi el doble de memoria en disco y GPU (+78% VRAM) y es un **17% más lento** generando respuestas. Por tanto, **Q4 es la opción óptima para producción**.

---

## 9. Estructura del Repositorio

```text
├── README.md                           <- Este documento: guía y reporte del proyecto
├── requirements.txt                    <- Librerías necesarias para ejecutar el proyecto
├── make_balanced_deck.py               <- Script para generar las diapositivas oficiales
├── presentacion_rag_benchmark.pptx     <- Diapositivas en PowerPoint (7 slides limpias)
├── presentacion.html                   <- Presentación interactiva en HTML para el navegador
├── manual_conceptos_rag_benchmark.pdf  <- Manual técnico en PDF con TODOS los conceptos explicados
│
├── data/
│   ├── preparar_datos.ipynb            <- Notebook de la Fase 1: limpieza y chunking
│   ├── raw/                            <- Archivos originales (EPUB de BOE y Debian)
│   └── processed/                      <- Chunks procesados en formato JSON con metadatos
│
├── preguntas/
│   ├── boe_questions.json              <- 30 preguntas del Golden Set para normativa
│   └── debian_questions.json           <- 30 preguntas del Golden Set para documentación técnica
│
├── resultados/
│   ├── embeddings_benchmark.json       <- Métricas y datos de la Fase 2 (Embeddings)
│   ├── llms_benchmark.json             <- Tablas B y C de la Fase 3 (LLMs)
│   ├── llms_respuestas_detalladas.json <- Respuestas completas de cada modelo para las 60 preguntas
│   └── qwen_q8_benchmark.json          <- Registro de la prueba comparativa Q4 vs Q8
│
├── benchmark_embeddings.ipynb          <- Notebook ejecutable de la Fase 2
└── benchmark_llms.ipynb                <- Notebook ejecutable de la Fase 3
```

---

## 10. Cómo Reproducir Nuestras Pruebas

### 1. Clonar el repositorio y crear el entorno virtual
```bash
git clone https://github.com/tu-usuario/reto_1_2-2627-Rag-Benchmark.git
cd reto_1_2-2627-Rag-Benchmark

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Iniciar Ollama y descargar los modelos
Asegúrate de que el demonio de Ollama esté ejecutándose (`ollama serve`) y descarga los 4 modelos evaluados:
```bash
ollama pull gemma2:2b
ollama pull granite3-dense:2b
ollama pull mistral:7b
ollama pull qwen2.5:7b
```

### 3. Ejecutar los notebooks en orden
1. Abrir y ejecutar [`data/preparar_datos.ipynb`](file:///home/g4/reto_1_2-2627-Rag-Benchmark/data/preparar_datos.ipynb) para generar los archivos `boe_chunks.json` y `debian_chunks.json`.
2. Abrir y ejecutar [`benchmark_embeddings.ipynb`](file:///home/g4/reto_1_2-2627-Rag-Benchmark/benchmark_embeddings.ipynb) para reproducir el benchmark de embeddings y generar las tablas A.
3. Abrir y ejecutar [`benchmark_llms.ipynb`](file:///home/g4/reto_1_2-2627-Rag-Benchmark/benchmark_llms.ipynb) para ejecutar la inferencia de los LLMs con Ollama y calcular las métricas de calidad y coste.

---

## 11. Conclusiones y Aprendizajes del Grupo

A lo largo de este proyecto hemos aprendido que:
1. **El éxito de un sistema RAG depende en un 80% de la fase de preparación y recuperación:** Si el modelo de embedding no rescata el fragmento acertado en los 3 primeros puestos, el mejor LLM del mundo no podrá contestar bien o se verá forzado a abstenerse.
2. **Los prefijos importan:** Modelos modernos como `Multilingual-E5-Small` multiplican su rendimiento cuando se les indica si el texto es un pasaje (`passage:`) o una consulta (`query:`). Omitir esto destruye su precisión.
3. **Más grande no siempre es mejor:** Para tareas técnicas o con comandos específicos, modelos pequeños como `Granite-3-2B` son más directos y comenten menos falsas abstenciones que modelos de 7B, gastando una fracción de la memoria y el tiempo.
4. **La cuantización a 4 bits es una maravilla de la ingeniería:** Permite correr modelos de 7B con precisión factual intacta en hardware de consumo y GPUs modestas, demostrando que para RAG no hace falta gastar memoria en pesos de 8 o 16 bits.

---
*Práctica realizada por Alfred, Ane y Naiara — Noviembre 2026*
