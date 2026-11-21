# Fase 4. Decisión por escenario
 
**Regla del enunciado:** elegir el modelo más pequeño y barato que cumple los umbrales de calidad. Se decide por separado para cada escenario. El coste solo desempata entre modelos que ya cumplen.
 
**Datos:** Fase 2 (`results/embeddings/tabla_a_embeddings.md`) y Fase 3 (`results/llms/tablas_b_c.md`).
Las notas de calidad salen de `results/llms/puntuacion_*.csv`: primera pasada hecha con IA con criterios fijos y revisada a mano por el grupo (**10 filas revisadas, 0 cambiadas (coincidencia 10 de 10)**).
 
---
 
## 1. Umbrales
 
> **Nota de honestidad:** los umbrales se escribieron el 21/11/2026, **después** de ver los resultados de la Fase 3. Por eso partimos de los del ejemplo del enunciado y solo añadimos los imprescindibles para que la regla tenga sentido (sin un umbral de corrección ganaría siempre el modelo más pequeño, aunque se equivoque en todo). En la sección 6 mostramos qué cambiaría sin los umbrales añadidos.
 
| Prioridad | Métrica | Umbral | Origen |
|---|---|---|---|
| 1 | Recall@5 (criterio Hit, el del README) | ≥ 0,80 | Ejemplo del enunciado |
| 2 | Respuestas fieles | ≥ 90 % (no fieles ≤ 10 %) | Ejemplo del enunciado |
| 2 | Abstención correcta | ≥ 2 de 3 | Ejemplo del enunciado |
| 3 | Corrección media | ≥ 1,5 / 2 | Añadido |
| 3 | Falsas abstenciones | ≤ 3 de 12 (25 %) | Añadido |
| 4 | Formato e idioma | ≥ 80 % | Añadido: citar artículo o sección es un requisito del prompt del enunciado |
| Requisito | VRAM pico (LLM + embedding) | ≤ 20 GB (Plan B: ≤ 8 GB) | Enunciado |
| 5 | Latencia total | ≤ 5 s | Ejemplo del enunciado |
 
---
 
## 2. Embedding (Recall@5, criterio Hit)
 
| Embedding | Parámetros | BOE | Debian |
|---|---|---|---|
| bge-m3 | 568M (encoder) | 0,83 ✅ | **0,83 ✅** |
| Qwen3-Embedding-0.6B | 600M | 0,83 ✅ | 0,75 ❌ |
| harrier-oss-v1-0.6b | 600M | **1,00 ✅** | 0,75 ❌ |
 
- **Debian → bge-m3.** Es el único que cumple, y además es el más pequeño.
- **BOE → harrier-oss-v1.** Cumplen los tres. El coste real es prácticamente el mismo: los tres tienen ~0,6B parámetros, dimensión 1024 (índice del mismo tamaño) y ~1,1–1,2 GB de pesos en FP16. La diferencia de VRAM de la Fase 2 (1,9 frente a 3,5 GB) no sirve aquí, porque es la reserva fija de vLLM (`gpu_memory_utilization=0.15`), no lo que ocupa cada modelo. Con el coste empatado, desempata la métrica de mayor prioridad (el retrieval): harrier recupera **12 de 12**, y bge-m3 y Qwen3-Embedding 10 de 12, a una sola pregunta de no llegar al umbral. Además, harrier es el único que recupera los dos chunks en todas las combinadas (Recall@5 estricto 1,00).
> Si se aplicara la regla al pie de la letra sin aceptar el empate de coste, el BOE usaría bge-m3. Sería una decisión distinta de la Fase 3, que se ejecutó con harrier.
 
---
 
## 3. LLM: BOE (embedding harrier-oss-v1)
 
| LLM | Corrección | Fieles | Abst. correcta | Falsas abst. | Formato | Latencia | VRAM pico | ¿Cumple? |
|---|---|---|---|---|---|---|---|---|
| LFM3-1.7B | 0,47 ❌ | 93 % | 3 de 3 | 11 de 12 ❌ | 40 % ❌ | 2,80 s | 5,4 GB | No |
| Llama-3.2-3B | 0,93 ❌ | 100 % | 3 de 3 | 6 de 12 ❌ | 93 % | 0,78 s | 7,1 GB | No |
| Nemotron E4B | 1,60 | 100 % | 3 de 3 | 1 de 12 | 100 % | 1,50 s | 14,8 GB | **Sí** |
| Qwen3.5-9B | **1,80** | 100 % | 3 de 3 | 1 de 12 | 93 % | **1,35 s** | **14,3 GB** | **Sí** |
 
Cumplen Nemotron y Qwen. **Qwen es más barato en las tres métricas de coste:** menos VRAM (14,3 frente a 14,8 GB), más tokens/s (45 frente a 27) y menos latencia (1,35 frente a 1,50 s). Además, es el de mejor corrección.
 
**VRAM total:** 14,3 GB (Qwen) + ~1,2 GB (harrier, FP16) ≈ 15,5 GB < 20 GB ✅
 
---
 
## 4. LLM: Debian (embedding bge-m3)
 
| LLM | Corrección | Fieles | Abst. correcta | Falsas abst. | Formato | Latencia | VRAM pico | ¿Cumple? |
|---|---|---|---|---|---|---|---|---|
| LFM3-1.7B | 0,40 ❌ | 100 % | 3 de 3 | 12 de 12 ❌ | 40 % ❌ | 2,41 s | 5,4 GB | No |
| Llama-3.2-3B | 1,07 ❌ | 87 % ❌ | 3 de 3 | 5 de 12 ❌ | 73 % ❌ | 0,31 s | 7,1 GB | No |
| Nemotron E4B | 1,53 | 100 % | 3 de 3 | 3 de 12 | **100 %** | **1,10 s** | 14,8 GB | **Sí** |
| Qwen3.5-9B | 1,53 | 100 % | 3 de 3 | 3 de 12 | 67 % ❌ | 3,23 s | 14,3 GB | No |
 
Solo cumple **Nemotron**. Qwen empata en todo lo de prioridad 1–3, pero solo cita bien la sección en el 67 % de las respuestas (a menudo pone «Fragmento 1»).
 
**VRAM total:** 14,8 GB (Nemotron) + ~1,1 GB (bge-m3, FP16) ≈ 15,9 GB < 20 GB ✅
 
> Las 3 falsas abstenciones de Nemotron y Qwen en Debian (`DEB_D03`, `DEB_C03`, `DEB_C04`) son preguntas en las que bge-m3 no recuperó todos los chunks necesarios en el top-5: en `DEB_D03` falta el único chunk relevante, en la combinada `DEB_C03` no llega ninguno de los dos y en `DEB_C04` llega solo uno de los dos (`debian_120_p4`). Con el oráculo, Qwen acierta las tres (2/2) y Nemotron acierta `DEB_D03` y `DEB_C04` (2/2) y responde de forma incompleta en `DEB_C03` (1/2). En Debian el límite principal es el retrieval, no el LLM.
 
---
 
## 5. Decisión final
 
> **BOE:** «Para el Estatuto de los Trabajadores usaría **harrier-oss-v1 + Qwen3.5-9B (FP8, vLLM)** porque harrier recupera el fragmento correcto en 12 de 12 preguntas, y Qwen es el LLM con mejor corrección (1,80/2), 100 % de respuestas fieles, abstención correcta en 3 de 3 y solo 1 falsa abstención; entre los que cumplen es además el más barato: 14,3 GB de VRAM, 45 tok/s y 1,35 s de latencia.»
 
> **Debian:** «Para el manual de Debian usaría **bge-m3 + Nemotron 3.5 Bolt E4B (FP8, vLLM)** porque bge-m3 es el único embedding con Recall@5 ≥ 0,80 (0,83), y Nemotron es el único LLM que cumple todos los umbrales: corrección 1,53/2, 100 % fiel, abstención 3 de 3 y 100 % de citas correctas, con 1,10 s de latencia y 14,8 GB de VRAM.»
 
### Plan B: solo 8 GB de VRAM
 
Solo caben los dos LLM pequeños, y hay que sumar el embedding (~1,1 GB):
 
| LLM | VRAM LLM + embedding | BOE: corrección / fieles | Debian: corrección / fieles |
|---|---|---|---|
| LFM3-1.7B | 5,4 + 1,1 ≈ 6,5 GB ✅ | 0,47 / 93 % | 0,40 / 100 % |
| Llama-3.2-3B | 7,1 + 1,1 ≈ 8,2 GB ⚠️ (cabe bajando la caché KV a 1 GB) | 0,93 / 100 % | 1,07 / 87 % |
 
> **Plan B (BOE y Debian):** «Con 8 GB **no desplegaríamos ninguno de los modelos medidos**, porque ninguno cumple los umbrales: LFM3 se abstiene en 11–12 de 12 preguntas con respuesta y Llama-3.2-3B en 5–6, y en Debian Llama además inventa datos (87 % fiel). Lo siguiente que probaríamos es Qwen3.5-9B o Nemotron en cuantización de 4 bits (~5–6 GB de pesos), que no hemos medido.»
 
---
 
## 6. Sensibilidad: qué cambia según los umbrales añadidos
 
- **Sin el umbral de formato (≥ 80 %):** en Debian cumplirían Nemotron y Qwen, y el coste no da un ganador claro: Qwen gana en VRAM (14,3 frente a 14,8 GB) y en tokens/s (45 frente a 27), y Nemotron en latencia (1,10 frente a 3,23 s). Por 2 de 3 métricas sería Qwen. Mantenemos el umbral porque citar el artículo o la sección es un requisito explícito del enunciado.
- **Sin el umbral de corrección (≥ 1,5):** LFM3 cumpliría en el BOE (fiel 93 %, abstención 3 de 3, latencia baja) y sería el elegido por barato, aunque casi nunca responde. Por eso el umbral es imprescindible.
- **Recall@5 con criterio estricto** (todos los chunks de las combinadas): en el BOE solo cumple harrier (1,00); en Debian no cumple ninguno (el mejor es harrier con 0,75).
## 7. Limitaciones
 
- Solo 12 preguntas con respuesta por escenario: cada pregunta vale 8,3 puntos de Recall y ~0,17 de corrección media. Las diferencias pequeñas (por ejemplo, 1,53 frente a 1,60) no son concluyentes.
- La puntuación de calidad la hizo primero una IA con criterios fijos; el grupo revisó 10 filas y cambió 0 (coincidencia 10 de 10).
- La VRAM se midió con la caché KV fija en 2 GB y para toda la instancia MIG (incluye el contexto de CUDA).
- FP8 en una A800 (Ampere) solo ahorra memoria; en una GPU con FP8 nativo los tiempos serían distintos.
 