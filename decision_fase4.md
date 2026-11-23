# Fase 4. Decisión por escenario
 
**Regla del enunciado:** elegir el modelo más pequeño y barato que cumple los umbrales de calidad. Se decide por separado para cada escenario. El coste solo desempata entre modelos que ya cumplen.
 
**Datos:** Fase 2 (`results/embeddings/tabla_a_embeddings.md`) y Fase 3 (`results/llms/tablas_b_c.md`).
Las notas de calidad salen de `results/llms/puntuacion_*.csv`: primera pasada realizada con IA con criterios fijos y auditada y revisada a mano por el grupo (**27 filas auditadas a mano**, 12 en BOE y 15 en Debian, cumpliendo el requisito del README de al menos 10 por escenario; ver §7). Las filas auditadas llevan `[revisado]` en la columna `notas`. Primero se auditaron las 18 filas representativas y de mayor peso en la decisión (coincidencia de 17/18, 94.4 %); al ajustar la regla de abstención parcial se revisaron además 9 filas de LFM3 para aplicarla con consistencia.

---

## 1. Umbrales

Los umbrales base se adoptan directamente de las especificaciones y ejemplos del enunciado (`README.md`): Recall@5 ≥ 0,80, fidelidad ≥ 90 %, abstención correcta ≥ 2 de 3, latencia total ≤ 5 s y VRAM ≤ 20 GB. Para asegurar que el modelo ganador cumpla unos mínimos operativos de corrección y respete las reglas del prompt, se completan con umbrales de corrección media, límite de falsas abstenciones y formato e idioma. En la sección 6 se presenta un análisis de sensibilidad que demuestra la solidez de la decisión.

| Prioridad | Métrica | Umbral | Origen |
|---|---|---|---|
| 1 | Recall@5 (criterio Hit, el del README) | ≥ 0,80 | Enunciado (ejemplo orientativo) |
| 2 | Respuestas fieles | ≥ 90 % (no fieles ≤ 10 %) | Enunciado (ejemplo orientativo) |
| 2 | Abstención correcta | ≥ 2 de 3 | Enunciado (ejemplo orientativo) |
| 3 | Corrección media | ≥ 1,5 / 2 | Calidad mínima requerida (escala 0–2 del enunciado) |
| 3 | Falsas abstenciones | ≤ 3 de 12 (25 %) | Filtro operativo contra el rechazo injustificado |
| 4 | Formato e idioma | ≥ 80 % | Requisito explícito del prompt en el enunciado |
| Requisito | VRAM pico (LLM + embedding) | ≤ 20 GB (Plan B: ≤ 8 GB) | Enunciado |
| 5 | Latencia total | ≤ 5 s | Enunciado (ejemplo orientativo) |
 
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
| LFM3-1.7B | 0,93 ❌ | 93 % | 3 de 3 | 11 de 12 ❌ | 40 % ❌ | 2,80 s | 5,4 GB | No |
| Llama-3.2-3B | 0,93 ❌ | 100 % | 3 de 3 | 6 de 12 ❌ | 93 % | 0,78 s | 7,1 GB | No |
| Nemotron E4B | 1,60 | 100 % | 3 de 3 | 1 de 12 | 100 % | 1,50 s | 14,8 GB | **Sí** |
| Qwen3.5-9B | **1,87** | 100 % | 3 de 3 | 1 de 12 | 93 % | **1,35 s** | **14,3 GB** | **Sí** |
 
Cumplen Nemotron y Qwen. **Qwen es más barato en las tres métricas de coste:** menos VRAM (14,3 frente a 14,8 GB), más tokens/s (45 frente a 27) y menos latencia (1,35 frente a 1,50 s). Además, es el de mejor corrección.
 
**VRAM total:** 14,3 GB (Qwen) + ~1,2 GB (harrier, FP16) ≈ 15,5 GB < 20 GB ✅
 
---
 
## 4. LLM: Debian (embedding bge-m3)
 
| LLM | Corrección | Fieles | Abst. correcta | Falsas abst. | Formato | Latencia | VRAM pico | ¿Cumple? |
|---|---|---|---|---|---|---|---|---|
| LFM3-1.7B | 0,93 ❌ | 93 % | 3 de 3 | 12 de 12 ❌ | 40 % ❌ | 2,41 s | 5,4 GB | No |
| Llama-3.2-3B | 1,07 ❌ | 87 % ❌ | 3 de 3 | 5 de 12 ❌ | 73 % ❌ | 0,31 s | 7,1 GB | No |
| Nemotron E4B | 1,53 | 100 % | 3 de 3 | 3 de 12 | **100 %** | **1,10 s** | 14,8 GB | **Sí** |
| Qwen3.5-9B | 1,53 | 100 % | 3 de 3 | 3 de 12 | 67 % ❌ | 3,23 s | 14,3 GB | No |
 
Solo cumple **Nemotron**. Qwen empata en todo lo de prioridad 1–3, pero solo cita bien la sección en el 67 % de las respuestas (a menudo pone «Fragmento 1»).
 
**VRAM total:** 14,8 GB (Nemotron) + ~1,1 GB (bge-m3, FP16) ≈ 15,9 GB < 20 GB ✅
 
> Las 3 falsas abstenciones de Nemotron y Qwen en Debian (`DEB_D03`, `DEB_C03`, `DEB_C04`) son preguntas en las que bge-m3 no recuperó todos los chunks necesarios en el top-5: en `DEB_D03` falta el único chunk relevante, en la combinada `DEB_C03` no llega ninguno de los dos y en `DEB_C04` llega solo uno de los dos (`debian_120_p4`). Con el oráculo, Qwen acierta las tres (2/2) y Nemotron acierta `DEB_D03` y `DEB_C04` (2/2) y responde de forma incompleta en `DEB_C03` (1/2). En Debian el límite principal es el retrieval, no el LLM.
 
---
 
## 5. Decisión final
 
> **BOE:** «Para el Estatuto de los Trabajadores usaría **harrier-oss-v1 + Qwen3.5-9B (FP8, vLLM)** porque harrier recupera el fragmento correcto en 12 de 12 preguntas, y Qwen es el LLM con mejor corrección (1,87/2), 100 % de respuestas fieles, abstención correcta en 3 de 3 y solo 1 falsa abstención; entre los que cumplen es además el más barato: 14,3 GB de VRAM, 45 tok/s y 1,35 s de latencia.»
 
> **Debian:** «Para el manual de Debian usaría **bge-m3 + Nemotron 3.5 Bolt E4B (FP8, vLLM)** porque bge-m3 es el único embedding con Recall@5 ≥ 0,80 (0,83), y Nemotron es el único LLM que cumple todos los umbrales: corrección 1,53/2, 100 % fiel, abstención 3 de 3 y 100 % de citas correctas, con 1,10 s de latencia y 14,8 GB de VRAM.»
 
### Plan B: solo 8 GB de VRAM

**1. Con el stack de la Fase 3 (vLLM, FP8) no cabe ningún modelo que cumpla.** Solo caben los dos pequeños, y ninguno pasa los umbrales:

| LLM (vLLM, FP8) | VRAM LLM + embedding | BOE: corrección / falsas abst. | Debian: corrección / falsas abst. |
|---|---|---|---|
| LFM3-1.7B | 5,4 + 1,1 ≈ 6,5 GB ✅ | 0,93 ❌ / 11 de 12 ❌ | 0,93 ❌ / 12 de 12 ❌ |
| Llama-3.2-3B | 7,1 + 1,1 ≈ 8,2 GB ⚠️ (cabe bajando la caché KV a 1 GB) | 0,93 ❌ / 6 de 12 ❌ | 1,07 ❌ / 5 de 12 ❌ (y 87 % fiel) |

**2. Cuantizar a 4 bits en vLLM tampoco basta.** Las versiones AWQ / W4A16 publicadas solo cuantizan las capas del transformer y dejan los embeddings en BF16, que en estos modelos son enormes (vocabulario de ~250k tokens). Leyendo las cabeceras de los safetensors: `cyankiwi/Qwen3.5-9B-AWQ-4bit` pesa ~8,0 GB solo de pesos de texto (2 GB de `embed_tokens` + 2 GB de `lm_head`) y `turintech/Nemotron-3.5-Bolt-E4B-Artemis-W4A16` ~10,3 GB (5,8 GB son los embeddings por capa). Sin caché KV ni embedding del retrieval ya superan los 8 GB, así que no se midieron.

**3. Con GGUF en llama.cpp sí caben.** En GGUF también se cuantizan los embeddings, y llama.cpp deja las tablas de embeddings de entrada en la RAM de la CPU. Medido con `scripts/benchmark_plan_b_llamacpp.py` (llama.cpp b12633, mismo top-5, mismo prompt y mismos parámetros que la Fase 3; resultados en `results/llms/plan_b/tablas_b_c.md`):

| LLM (llama.cpp) | VRAM LLM + embedding | BOE: corr. / fieles / falsas abst. / formato | Debian: corr. / fieles / falsas abst. / formato | Latencia BOE / Debian | ¿Cumple? |
|---|---|---|---|---|---|
| **Nemotron E4B Q4_K_M** (GGUF oficial de NVIDIA) | **3,5 + 1,1 ≈ 4,6 GB** ✅ | 1,60 / 100 % / 1 de 12 / 100 % | 1,53 / 100 % / 3 de 12 / 100 % | **0,76 / 0,75 s** | **Sí** |
| Qwen3.5-9B Q4_K_M (Unsloth) | 5,4 + 1,1 ≈ 6,5 GB ✅ | **1,87** / 100 % / 1 de 12 / 93 % | 1,53 / 100 % / 3 de 12 / 87 % | 1,64 / 1,76 s | Sí |
| Nemotron E4B Q8_0 (extra) | 5,2 + 1,1 ≈ 6,3 GB ✅ | 1,60 / 100 % / 1 de 12 / 100 % | 1,53 / 100 % / 3 de 12 / 100 % | 0,84 / 0,69 s | Sí |
| Qwen3.5-9B Q8_0 (extra) | 8,5 + 1,1 ≈ 9,6 GB ❌ | 1,80 / 100 % / 1 de 12 / 93 % | 1,53 / 100 % / 3 de 12 / 80 % | 1,92 / 2,95 s | No (VRAM) |

Abstención correcta: 3 de 3 en todos. En los dos escenarios cumplen Nemotron y Qwen en Q4, y **Nemotron Q4 es más barato en las tres métricas de coste**: menos VRAM (3,5 frente a 5,4 GB), más tokens/s (93 frente a 86 en el BOE) y menos latencia (0,76 frente a 1,64 s). Pasar de Q8 a Q4 no cambia la calidad de ninguno de los dos (las diferencias son de una pregunta).

> **Plan B (BOE y Debian):** «Con 8 GB de VRAM usaría el mismo embedding de cada escenario (harrier en el BOE, bge-m3 en Debian) + **Nemotron 3.5 Bolt E4B en GGUF Q4_K_M con llama.cpp**, porque cumple todos los umbrales en los dos escenarios (BOE: 1,60/2, 100 % fiel, 1 falsa abstención, 100 % de citas; Debian: 1,53/2, 100 % fiel, 3 falsas abstenciones, 100 % de citas) y es el más barato de los que cumplen: ~4,6 GB con el embedding, 0,75 s de latencia y ~90 tok/s.»

Matices:
- En el BOE el Plan B pierde calidad frente a la decisión principal (1,60 de Nemotron frente a 1,87 de Qwen). Si se prefiere la mejor nota, Qwen3.5-9B Q4 también cumple y cabe (6,5 GB).
- Es otro stack: las cifras de coste no se comparan con las de vLLM FP8, solo entre modelos del Plan B (todos con llama.cpp).
- llama.cpp guarda las tablas de embeddings de entrada en la RAM del sistema, así que el equipo necesita RAM suficiente (el GGUF de Nemotron ocupa 6,2 GB en disco).
- La VRAM del LLM es el pico de la instancia menos lo que había antes de arrancar llama-server, con la caché KV para 8192 tokens. El embedding (~1,1 GB) se suma sin medir juntos.
- Las 216 respuestas del Plan B las puntuó una IA con los criterios de `seleccion_llms.md` §7 (marcadas `[puntuado IA]` en `results/llms/plan_b/puntuacion_*.csv`); falta la revisión a mano del grupo. El 87 % de formato de Qwen Q4 en Debian depende de una cita dudosa (`DEB_C02`); con 0 quedaría en el 80 % y seguiría cumpliendo. Ninguna de las dos cambia la decisión, porque gana Nemotron por coste.

---

## 6. Sensibilidad: qué cambia según los umbrales añadidos
 
- **Sin el umbral de formato (≥ 80 %):** en Debian cumplirían Nemotron y Qwen, y el coste no da un ganador claro: Qwen gana en VRAM (14,3 frente a 14,8 GB) y en tokens/s (45 frente a 27), y Nemotron en latencia (1,10 frente a 3,23 s). Por 2 de 3 métricas sería Qwen. Mantenemos el umbral porque citar el artículo o la sección es un requisito explícito del enunciado.
- **Con otro criterio de formato para las abstenciones:** el 67 % de Qwen en Debian son 10 de 15. De sus 5 respuestas con formato 0, 3 citan «Fragmento N» en vez de la sección y 2 (`DEB_D03` y `DEB_C04`) se abstienen y luego añaden una explicación. Si abstenerse con explicación contara como formato correcto, Qwen llegaría a 12 de 15 (80 %), cumpliría el umbral y pasaríamos al caso anterior: por 2 de 3 métricas de coste ganaría Qwen. Mantenemos el criterio porque el prompt pide «No aparece en el documento» «y nada más», y lo aplicamos igual a los cuatro modelos (criterios en `seleccion_llms.md` §7). Aun así, la decisión de Debian depende de estas dos respuestas.
- **Sin los tres umbrales añadidos (corrección, falsas abstenciones y formato):** en el BOE cumplirían también LFM3 (fiel 93 %, abstención 3 de 3, 2,80 s) y Llama-3.2-3B (fiel 100 %, 3 de 3, 0,78 s), y por coste ganaría Llama (más tokens/s y menos latencia que LFM3; LFM3 solo gana en VRAM). En Debian cumpliría LFM3 (fiel 93 %, 3 de 3, 2,41 s) y sería el elegido por ser el más barato. Es decir, ganaría un modelo pequeño que se abstiene en 6 (Llama) u 11–12 (LFM3) de las 12 preguntas con respuesta. Por eso hacen falta esos umbrales.
- **Recall@5 con criterio estricto** (todos los chunks de las combinadas): en el BOE solo cumple harrier (1,00); en Debian no cumple ninguno (el mejor es harrier con 0,75).
## 7. Limitaciones
 
- Solo 12 preguntas con respuesta por escenario: cada pregunta vale 8,3 puntos de Recall y ~0,17 de corrección media. Las diferencias pequeñas (por ejemplo, 1,53 frente a 1,60) no son concluyentes.
- La puntuación de calidad la hizo primero una IA con criterios fijos; el grupo auditó y revisó a mano 27 de las 120 filas con retrieval (12 en BOE y 15 en Debian, superando en ambos escenarios el requisito de al menos 10 filas del README L117):
  - **18 filas elegidas por su peso en la decisión y representatividad (incluyendo todos los modelos):** coincidencia de 17 sobre 18 (94,4 %). El cambio: `BOE_C02` de Qwen pasó de corrección 0 a 1, porque tras abstenerse da bien la mitad de la respuesta. Como la IA sí tenía en cuenta el texto tras la abstención para penalizar (`BOE_D02` de LFM3, fiel 0), se decidió tenerlo en cuenta también para premiar. Las 5 filas añadidas en el BOE para completar la auditoría (`llama3.2-3b`, `nemotron` y `qwen`) tuvieron coincidencia plena (5 de 5) con la nota previa.
  - **9 filas de LFM3 en el mismo caso** (se abstiene y después responde): se repuntuaron con esa regla. 8 cambiaron de corrección (7 a 2 y 1 a 1; dos de ellas marcadas como dudosas) y en `DEB_D01` se cambió fiel de 1 a 0.
  - Estos cambios suben la corrección de LFM3 de 0,47 a 0,93 (BOE) y de 0,40 a 0,93 (Debian), y la de Qwen en el BOE de 1,80 a 1,87. Ninguna decisión cambia.
- La latencia depende de la longitud de la respuesta. Los 0,31 s de Llama-3.2-3B en Debian salen de una mediana de 8 tokens de salida, porque se abstiene en 3 de las 5 preguntas de coste. Por eso la latencia solo desempata entre modelos que ya cumplen la calidad.
- La VRAM se midió con la caché KV fija en 2 GB y para toda la instancia MIG (incluye el contexto de CUDA).
- FP8 en una A800 (Ampere) solo ahorra memoria; en una GPU con FP8 nativo los tiempos serían distintos.
 
---

## 8. Lo que no esperábamos

1. **Nemotron, con 4B parámetros efectivos, es el LLM más lento y no el más rápido.** Esperábamos que calculara como un modelo de ~4B, pero da **27 tok/s**, frente a 45 de Qwen3.5-9B y 66 de Llama-3.2-3B, y su VRAM pico (14,8 GB) supera la de Qwen (14,3 GB). *Explicación:* vLLM carga los 8B parámetros completos (incluidas las tablas de embeddings por capa) y en esta GPU usa kernels más lentos para su arquitectura (`TRITON_ATTN` y FP8 Marlin, que en Ampere solo comprime los pesos). Tener «4B efectivos» ahorra cómputo en teoría, pero no memoria, y en nuestro stack tampoco tiempo. El Plan B lo confirma: con llama.cpp, que deja esas tablas en la RAM de la CPU, Nemotron en Q4 ocupa solo 3,5 GB de VRAM y genera a ~90 tok/s, más rápido que Qwen3.5-9B en Q4 (5,4 GB). (Datos: `results/llms/tablas_b_c.md`, Tabla C; detalle en `seleccion_llms.md` §3 y §6.)

2. **El mejor embedding cambia de un corpus a otro.** harrier-oss-v1 recupera **12 de 12** en el BOE (Recall@5 = 1,00) y es el peor en Debian (0,75), mientras que bge-m3, el más antiguo y el único encoder, es el único que llega a 0,80 en Debian (0,83). Un mismo ranking de MTEB no predice el resultado en los dos corpus. *Hipótesis (no comprobada):* el BOE es prosa jurídica en español «limpio», y Debian mezcla español con comandos, rutas y términos en inglés, donde los modelos se comportan de forma distinta. (Datos: `results/embeddings/tabla_a_embeddings.md`.)

3. **LFM3-1.7B dice «No aparece en el documento»... y luego responde.** Empieza abstiéndose en 11 de 12 preguntas con respuesta en el BOE y en 12 de 12 en Debian, aunque en el BOE el chunk correcto estaba en el top-5 en todas. Pero en 8 de esas respuestas, justo después, da la respuesta correcta o casi («Sin embargo, según el Fragmento 1…»). Con el fragmento correcto solo (oráculo), su corrección sube de **0,67 a 1,25** en el BOE y de **0,67 a 1,00** en Debian. *Explicación:* el modelo pequeño no sigue bien la instrucción de abstención: la aplica casi por reflejo y luego contesta igualmente, y con 5 fragmentos parecidos se pierde más que con uno. Para un usuario, una respuesta que empieza diciendo que no hay respuesta es inútil aunque luego acierte; por eso sus falsas abstenciones y su formato (40 %) lo descartan aunque la corrección haya subido a 0,93. (Datos: `results/llms/tablas_b_c.md`, tabla «Retrieval frente a oráculo».)
