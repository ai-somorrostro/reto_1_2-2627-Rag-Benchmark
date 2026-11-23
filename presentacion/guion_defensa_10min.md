# Guión de Defensa · Presentación de 10 Minutos
## Práctica: Benchmark de LLMs y Embeddings Locales para RAG (Grupo 1)

**Equipo:** Nicolás Pascual · Aimar Mora · Íñigo Guzmán  
**Tiempo límite estricto:** 10:00 minutos (+ preguntas del profesor)

---

### Estructura de Tiempos y Reparto de Voz

```
[00:00 - 01:30]  1. Contexto, Escenarios y Stack de Inferencia  ──────────  Nicolás
[01:30 - 03:30]  2. Fase 1 (Golden Set) y Fase 2 (Embeddings)    ──────────  Aimar
[03:30 - 06:15]  3. Fase 3 (Benchmark LLMs: Calidad y Coste)     ──────────  Íñigo
[06:15 - 08:00]  4. Decisiones por Escenario y Plan B (8 GB)     ──────────  Íñigo / Aimar
[08:00 - 10:00]  5. Lo que no esperábamos y Trazabilidad         ──────────  Íñigo / Nicolás
```

---

### Minuto a Minuto: Qué decir en cada Diapositiva

#### [00:00 - 01:30] Diapositiva 1 & 2: Contexto, Escenarios y Hardware
**Ponente:** X
- **Idea clave:** No venimos a opinar sobre modelos abstractos de MTEB; traemos datos empíricos medidos por nosotros en hardware real.
- **Puntos a tocar:**
  - Evaluamos dos escenarios radicalmente opuestos:
    1. *Estatuto de los Trabajadores (BOE)*: Dominio normativo, artículos interconectados, lenguaje jurídico homogéneo y necesidad de citación exacta.
    2. *Manual del Administrador de Debian*: Jerga técnica, comandos de terminal, rutas absolutas y mezcla de inglés técnico dentro del español.
  - **Stack técnico:** Corremos sobre una instancia MIG `3g.20gb` (20 GB VRAM asignados) en una NVIDIA A800 de 40 GB. Todo el pipeline de inferencia está unificado en **vLLM 0.34.0** con pesos en FP8 y caché KV fija a 2 GB para asegurar comparativas justas entre modelos.

---

#### [01:30 - 03:30] Diapositiva 3: Fase 1 (Golden Set) y Fase 2 (Embeddings)
**Ponente:** X
- **Idea clave:** El retrieval condiciona todo el sistema. Si el chunk no llega al top-5, el LLM no tiene nada que hacer.
- **Puntos a tocar:**
  - Creamos un *Golden Set* riguroso de 15 preguntas por escenario: 8 directas, 4 combinadas (requieren dos artículos/secciones) y 3 sin respuesta para medir la abstención.
  - **Resultados de Embeddings:**
    - En el **BOE**, `microsoft/harrier-oss-v1-0.6b` aplastó con un **Recall@5 de 1.0000** (recuperó el 100% de los fragmentos, incluso en combinadas) y un MRR de 0.736.
    - En **Debian**, sin embargo, *harrier* cayó al peor resultado (0.75). El ganador fue `BAAI/bge-m3`, siendo el único modelo que alcanzó el umbral mínimo del 80% (Recall@5 Hit = 0.8333).
  - Fijamos estos dos embeddings ganadores para alimentar la Fase 3, garantizando que todos los LLMs reciban idéntico contexto.

---

#### [03:30 - 06:15] Diapositivas 4 & 5: Fase 3 (LLMs: Calidad, Ruido y Rendimiento)
**Ponente:** X
- **Idea clave:** Los LLMs pequeños colapsan por falsas abstenciones y ruido; los medianos ofrecen la fidelidad que exige un entorno de producción.
- **Puntos a tocar:**
  - **Métricas de Calidad (Tabla B):**
    - En el BOE, **`Qwen3.5-9B`** es el líder indiscutible con **1.87 sobre 2.0** de corrección media, 100% de fidelidad y solo 1 falsa abstención.
    - `Llama-3.2-3B` y `LFM3-1.7B` caen por debajo de 1.0 en corrección (0.93). ¿Por qué? Por una **histeria de abstención**: LFM3 dice que no aparece la respuesta en 11 de las 12 preguntas con datos válidos, y Llama en 6 de 12.
    - En Debian, tanto `Nemotron-Bolt` como `Qwen3.5-9B` empatan en corrección (1.53) y 100% de fidelidad, pero Nemotron clava el formato y las citas de sección al **100%**, frente al 67% de Qwen.
  - **Experimento Oráculo vs Retrieval (Extra):**
    - Al aislar el LLM y darle solo el chunk exacto (oráculo), la corrección de LFM3 salta de 0.67 a 1.25. Esto demuestra que los modelos pequeños sufren de **fallo por ruido**: el embedding hace bien su trabajo metiendo los chunks en el top-5, pero el modelo se despista con el contexto sobrante.
  - **Coste y Rendimiento (Tabla C):**
    - `Llama-3.2-3B` es el más rápido (66.4 tok/s, latencia 0.78s), pero inusable por calidad.
    - `Qwen3.5-9B` mantiene un equilibrio excelente de 45.0 tok/s con solo 1.35s de latencia total.
    - `Nemotron-Bolt` fue la gran decepción en velocidad: solo 26.7 tok/s.

---

#### [06:15 - 08:00] Diapositivas 6 & 7: Recomendación Final y Plan B (8 GB VRAM)
**Ponente:** X
- **Idea clave:** Decisiones basadas en umbrales estrictos de negocio/calidad, no en intuición.
- **Puntos a tocar:**
  - **Para el BOE:** Elegimos **Harrier + Qwen3.5-9B**. Corrección casi perfecta (1.87), fidelidad absoluta (100%) y excelente velocidad.
  - **Para Debian:** Elegimos **BGE-M3 + Nemotron-Bolt-E4B**. BGE-M3 por su solvencia en vocabulario técnico en inglés, y Nemotron por su respeto religioso al formato de citación técnica (100%).
  - **Defensa del Plan B (Restricción de 8 GB VRAM):**
    - Si el cliente o la infraestructura solo tiene 8 GB de VRAM, **ninguno de los modelos recomendados es viable**: Qwen consume 14.3 GB y Nemotron 14.8 GB.
    - Los modelos de 1.7B y 3B sí caben (5.4 GB y 7.1 GB), pero tienen una tasa de falsas abstenciones inaceptable (50% a 92%).
    - **Nuestra propuesta técnica para el Plan B:** No desplegar un modelo pequeño en bruto; optaríamos por cuantizar agresivamente Qwen a AWQ 4-bits o GGUF Q4_K_M en llama.cpp (que consume ~6.5 GB), o realizar un SFT ligero sobre Llama-3.2-3B para calibrar la abstención.

---

#### [08:00 - 10:00] Diapositivas 8 & 9: Lo que no esperábamos y Cierre
**Ponente:** X
- **Idea clave:** Los 3 hallazgos experimentales sorprendentes que demuestran rigor y análisis crítico.
- **Puntos a tocar:**
  1. **La paradoja de Nemotron:** NVIDIA lo promociona como "4B efectivos", pero vLLM carga los 8B de parámetros en VRAM (14.8 GB) y utiliza kernels más lentos (`TRITON_ATTN` y FP8 Marlin en Ampere), resultando en el modelo más lento de la prueba (26.7 tok/s).
  2. **Inconsistencia entre dominios de embeddings:** El mejor modelo en legal fue el peor en técnico. Demuestra que consultar una tabla genérica de MTEB sin validar con el corpus propio es una mala práctica de ingeniería.
  3. **El comportamiento bipolar de LFM3:** Responde "No aparece en el documento", y en la siguiente frase añade: "Sin embargo, según el fragmento 1..." y acierta la pregunta. Es un defecto de seguimiento de instrucciones de modelos sub-2B.
- **Cierre (Nicolás/Íñigo):** Todo el código, los logs de VRAM segundo a segundo y las respuestas brutas están trazadas y versionadas en el repositorio. Quedamos a disposición para las preguntas del tribunal.

---

### Respuestas Preparadas ante Preguntas Trampa del Profesor

- **¿Por qué vLLM en lugar de Ollama si en el documento inicial hablabais de Ollama?**  
  *Respuesta:* vLLM permite aislar el proceso y controlar exactamente la memoria de la caché KV (`kv_cache_memory_bytes` o `--gpu-memory-utilization`) de forma determinista para comparar VRAM de modelos, mientras que Ollama gestiona la memoria de manera opaca y añade sobrecarga de servidor. Además, vLLM aprovecha FP8 directamente en hardware de centros de datos como la A800.
- **¿Por qué FP8 en una A800 no aumentó los tokens por segundo respecto a BF16?**  
  *Respuesta:* La arquitectura Ampere (A800/A100) no tiene aceleración de cómputo FP8 en sus Tensor Cores (eso se introdujo en Ada Lovelace y Hopper). En Ampere, vLLM ejecuta FP8 como compresión de solo-pesos (Marlin), lo que reduce el consumo de VRAM pero no la latencia de cálculo.
- **¿Por qué penalizasteis tan duro el formato en Debian a Qwen si la respuesta era correcta?**  
  *Respuesta:* En un RAG corporativo o técnico, la citación de la fuente (la sección exacta del manual) es un requisito no negociable para que el operador valide la acción en terminal. Una respuesta correcta sin citar la sección obliga al técnico a buscar a ciegas, por lo que la regla de negocio del prompt exigía citar obligatoriamente.
