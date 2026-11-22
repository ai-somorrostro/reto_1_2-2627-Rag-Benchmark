# Umbrales de decisión (acordados por el grupo el 2026-11-22)

Se fijan ANTES de puntuar a mano y de rellenar las Tablas B y C. Se aplican por escenario; lo que no cumple se descarta aunque sea rápido o barato.

| Métrica | Umbral | Tabla |
|---|---|---|
| Recall@5 del embedding | ≥ 0,80 | A |
| Respuestas fieles | ≥ 90 % (no fieles ≤ 10 %) | B |
| Abstención correcta | ≥ 2 de 3 | B |
| Falsas abstenciones | ≤ 1 de 12 | B |
| Corrección media | ≥ 1,5 de 2 | B |
| Formato e idioma | ≥ 90 % | B |
| Latencia total (mediana) | ≤ 5 s | C |
| VRAM pico | ≤ 20 GB (plan B: ≤ 8 GB) | C |

Regla: entre los modelos que cumplen todo, el más barato (menos VRAM, luego más tokens/s, luego menos latencia).

Nota de transparencia: antes de fijar estos umbrales ya se conocían resultados provisionales de retrieval (Tabla A parcial: Recall@5 de 0,58 en Debian y 1,00 en BOE con Qwen3-Embedding). Los umbrales de calidad del LLM se fijaron sin ninguna nota puntuada.
