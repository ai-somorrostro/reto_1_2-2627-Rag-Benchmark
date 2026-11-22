# Candidatos, recomendación, plan B y sorpresas

Cifras: `Tabla_B_*.md`, `Tabla_C_*.md`, `tabla_A/`, `decision_fase4_20GB.md`, `decision_fase4_8GB.md`. Trazabilidad: `INDICE.md` e `INDICE_ejecuciones.md`. Versiones: `versiones_modelos.md`.

## 1. Candidatos y stack (qué y por qué)
- **Embeddings (3):** BAAI/bge-m3 (multilingüe, referencia habitual), Qwen3-Embedding-0.6B (multilingüe, instrucciones de consulta) y EmbeddingGemma-300M (pequeño, 768 dim). Tres familias distintas y tamaños de 0,3 a 0,6 B. Se cargan con sentence-transformers en precisión por defecto (float32; los configs no fijan dtype). EmbeddingGemma se cargó de una copia local porque el repositorio es de acceso restringido.
- **LLM (4, dos tamaños):** pequeños Qwen3-1.7B y SmolLM3-3B; medianos Qwen3-8B y Ministral 3 8B. Todos abiertos, con español, y con ventana de contexto de sobra para top-5 (peor caso ~3,3 k tokens). Dos medianos de familias distintas (Qwen y Mistral) para no depender de una sola.
- **Stack:** Hugging Face transformers 5.23 + torch 2.15, bf16 sin cuantizar, una GPU MIG de 20 GB. No hay Ollama en el clúster. Mismo prompt, top-k = 5, temperatura 0, 300 tokens máx., sin modo de razonamiento.
- **Chunking:** Docling HybridChunker, máx. 450 tokens (`comun/chunks_*.json`).

## 2. Recomendación (umbrales de `umbrales.md`, fijados antes de puntuar)
- **BOE: usaría Qwen3-Embedding-0.6B + Qwen3-8B**, porque el embedding da Recall@5 = 1,000 y el LLM cumple todos los umbrales (corrección 2,00; 100 % fieles; 0 falsas abstenciones; 3,8 s; 16,6 GB), con menos VRAM que Ministral (18,4 GB, también cumple).
- **Debian: no recomendaría ninguna combinación todavía.** El mejor embedding (EmbeddingGemma) llega a Recall@5 = 0,667 < 0,80, así que el retrieval ya falla antes del LLM. Y ningún LLM cumple todo: Ministral falla por 3 falsas abstenciones (máx. 1), Qwen3-8B por 2 falsas abstenciones y formato 67 %. Qué cambiar primero: mejorar el retrieval (chunking, reranker o más fragmentos), no cambiar de LLM.

## 3. Plan B con 8 GB
- **Medido en bf16:** sólo caben Qwen3-1.7B (4 GB) y SmolLM3-3B (6,8 GB), y ninguno cumple los umbrales en BOE (fieles 73 % y 60 %). Los de 8 B (16,6 y 18,4 GB) no caben.
- **Medido en 4 bits (nf4, bitsandbytes, mismo prompt y método):** Qwen3-8B en BOE llega a **7,08 GB** de pico (nvidia-smi), corrección 2,00, 100 % fiel, 3/3 abstenciones, 0 falsas abstenciones, formato 100 %, latencia 4,13 s, 28,5 tok/s: **cumple todos los umbrales con ≤ 8 GB**. Ejecución: `nahia/resultados/Qwen_Qwen3-8B-nf4__boe__20261122-211519*`; decisión: `decision_fase4_8GB.md`. Las 10 respuestas que difieren de bf16 se pre-puntuaron con ayuda de un LLM y las validó Nahia a mano.
- **Ministral 3 8B no se pudo cuantizar así:** su checkpoint ya viene en FP8 y bitsandbytes no lo admite (error al cargar). No hay medida para él en el plan B.
- **Debian en plan B:** no se midió; no se recomienda por el retrieval (R@5 < 0,80).
- **Recomendación plan B para BOE:** Qwen3-Embedding-0.6B + Qwen3-8B en nf4. Margen justo (7,08 de 8 GB).

## 4. Lo que no esperabais
- **Debian es mucho peor que BOE, y la causa es el retrieval, no el LLM:** Recall@5 de 0,58–0,67 frente a 1,00. El manual mezcla texto con muchos bloques de comandos y salidas parecidas entre sí; el embedding trae fragmentos de otro ejemplo del mismo comando.
- **El modelo más grande no gana siempre:** Ministral 3 8B es el más fiel en Debian (100 %) pero se abstiene de más (3 falsas abstenciones), y en BOE es peor que Qwen3-8B.
- **Los modelos pequeños fallan por fidelidad, no por velocidad:** SmolLM3 (60 % fieles en BOE) inventa datos aunque es rápido (52 tok/s).
- **Un error nuestro del golden set:** la pregunta q_deb_10 exigía un fragmento (un ejemplo con /home al 83 %) que no existe en el manual, y bajaba artificialmente el Recall. Se reescribió para usar un ejemplo real (/srv/files al 90 %, fragmento 824), se repitió toda la parte de Debian y la conclusión no cambió (R@5 sigue < 0,80). Las ejecuciones antiguas de Debian siguen en `nahia/resultados/` pero no cuentan (golden con otro sha256).

## 5. Limitaciones
15 preguntas por escenario (ruido alto: una pregunta = 6,7 puntos); sólo bf16; una GPU compartida; puntuación a mano con pre-puntuación asistida por un LLM y validada a ciegas en 10 respuestas (8/10 en corrección, 10/10 en abstención). La fila de q_deb_10 de Debian y 10 filas del plan B (nf4) se pre-puntuaron con ayuda de un LLM y las validó Nahia a mano (columna `puntuado_por`).
