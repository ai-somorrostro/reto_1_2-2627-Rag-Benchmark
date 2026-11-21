# Análisis Forense de Fallos en el Pipeline RAG
## Grupo 1 · Evaluación Cualitativa y Diagnóstico de Errores

Este documento desglosa la anatomía de los fallos observados durante la Fase 3 del benchmark en los escenarios del **BOE (Estatuto de los Trabajadores)** y **Debian (Manual del Administrador)**.

---

### 1. Taxonomía de Errores en RAG

A partir de las 480 inferencias y las 120 evaluaciones de calidad sobre el Golden Set, clasificamos los errores en cuatro categorías técnicas:

```
                          ┌─── [1] Fallo de Retrieval (Embedding) ─── Chunk ausente en Top-5
                          │
Error en Respuesta RAG ───┼─── [2] Fallo por Ruido (Context Rot) ───── Chunk presente pero ignorado
                          │
                          ├─── [3] Histeria de Abstención (Refusal) ── Responde "No aparece" erróneamente
                          │
                          └─── [4] Violación de Formato/Cita ──────── Omite sección/artículo obligatorio
```

---

### 2. Desglose y Evidencias por Categoría

#### Categoría 1: Fallo de Retrieval (Ausencia en Top-5)
- **Definición:** El LLM falla porque el modelo de embedding no fue capaz de recuperar uno o más fragmentos clave en el top-5.
- **Caso Crítico en Debian (`DEB_D03` y `DEB_C04`):**
  - En la pregunta `DEB_D03` (*"¿Qué comando se usa para regenerar los ficheros Packages tras actualizar un repositorio local?"*), el chunk `ch06s04_02` no entró en el top-5 de `bge-m3`.
  - **Consecuencia:** Tanto `qwen3.5-9b` como `nemotron-bolt` respondieron *"No aparece en el documento"*.
  - **Validación con Oráculo:** Al inyectar manualmente el chunk correcto (`ch06s04_02`), la corrección de Qwen pasó de **0 a 2** y la de Nemotron de **0 a 2**. El fallo es 100% imputable al retriever, no al modelo generativo.

#### Categoría 2: Fallo por Ruido (Distracción en Contexto)
- **Definición:** Todos los fragmentos necesarios están en el top-5, pero el LLM se confunde por la similitud léxica de otros fragmentos adyacentes.
- **Evidencia en Modelos Sub-3B (`lfm3-1.7b` y `llama3.2-3b`):**
  - En el BOE, el embedding `harrier` entregó el 100% de los fragmentos correctos en el top-5 (Recall@5 = 1.0).
  - Sin embargo, en preguntas directas como `BOE_D01` (*"¿A qué tipo de trabajadores se aplica el Estatuto...?"*), `lfm3` y `llama3.2` obtuvieron corrección 0 con retrieval, mientras que con el **oráculo aislado** (1 solo chunk) obtuvieron un 2.
  - **Diagnóstico:** Los modelos pequeños sufren de una ventana de atención difusa ante fragmentos legales densos; la presencia de 5 chunks compitiendo diluye la señal relevante.

#### Categoría 3: Histeria de Abstención (False Refusals)
- **Definición:** El modelo aplica la regla de abstención de manera hiperconservadora, priorizando la negación ante la mínima duda de redacción.
- **Evidencia Numérica:**
  | Modelo | Falsas Abstenciones (BOE) | Falsas Abstenciones (Debian) | Tasa de Negación Injustificada |
  |---|---|---|---|
  | `lfm3-1.7b` | **11 de 12** | **12 de 12** | **95.8%** |
  | `llama3.2-3b` | **6 de 12** | **5 de 12** | **45.8%** |
  | `nemotron-bolt-e4b` | 1 de 12 | 3 de 12 | 16.7% |
  | `qwen3.5-9b` | 1 de 12 | 3 de 12 | 16.7% |
- **El caso bipolar de LFM3-1.7B:**
  - En preguntas como `BOE_D02`, LFM3 emite la frase obligatoria: `"No aparece en el documento."`, pero a continuación redacta: `"Sin embargo, según el Fragmento 1 el artículo 2 establece..."` y acierta la respuesta completa.
  - Esto refleja un conflicto entre el prompt de sistema y los pesos del modelo, activando el token de rechazo por reflejo superficial.

#### Categoría 4: Violación de Formato y Citación Técnica
- **Definición:** El modelo responde el contenido exacto pero ignora la instrucción de negocio que exige citar la fuente exacta.
- **Impacto en Debian:**
  - En Debian, la citación de la sección (`ch04s02`, etc.) es vital para un administrador de sistemas.
  - `Qwen3.5-9B` cayó al **67%** en cumplimiento de formato en Debian porque en 5 preguntas explicó la respuesta técnica sin anteponer la sección.
  - `Nemotron-Bolt-E4B` mantuvo un **100% de citación**, citando rigurosamente la sección en todas las respuestas. Este criterio fue el factor decisivo para seleccionar a Nemotron sobre Qwen en el escenario 2.

---

### 3. Conclusiones para Producción

1. **El retrieval top-5 no debe aumentarse arbitrariamente:** Subir de top-5 a top-10 degradaría críticamente a los modelos pequeños por ruido, sin aportar ganancias sustanciales a los modelos medianos.
2. **Los modelos sub-3B requieren Reranking o Few-Shot:** Para producción con modelos de 3B, es indispensable un paso intermedio de *Cross-Encoder Reranker* para reducir el contexto a máximo 2 chunks y mitigar las falsas abstenciones.
3. **Calibración del umbral de decisión:** En entornos corporativos, una falsa abstención es preferible a una alucinación (100% de fidelidad lograda por los modelos medianos), pero una tasa del 95% de abstención convierte al asistente en un sistema inoperable.
