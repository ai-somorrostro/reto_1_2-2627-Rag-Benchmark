# Propuestas de Nahia para cerrar con el grupo (borrador, nada aprobado)

## 1. Umbrales (hay que fijarlos ANTES de ver resultados)
Basados en el ejemplo del README. Se aplican por escenario; lo que no cumple se descarta aunque sea rápido.

| Métrica | Umbral propuesto | Dónde se mide |
|---|---|---|
| Recall@5 del embedding | ≥ 0,80 | Tabla A (Sendoa) |
| Respuestas no fieles | ≤ 10 % (fieles ≥ 90 %) | Tabla B |
| Abstención correcta | ≥ 2 de 3 | Tabla B |
| Falsas abstenciones | ≤ 1 de 12 | Tabla B |
| Corrección media | ≥ 1,5 de 2 | Tabla B |
| Formato e idioma | ≥ 90 % | Tabla B |
| Latencia total | ≤ 5 s | Tabla C |
| VRAM pico | ≤ 20 GB (plan B: ≤ 8 GB) | Tabla C |

Regla de decisión: entre los modelos que cumplen todo, el más barato (menos VRAM, luego más tokens/s, luego menos latencia).
**Fechar y firmar (mensaje del grupo) antes del primer resultado oficial.**

## 2. Criterio común de puntuación a mano (para que puntúen igual los 4)
- **Corrección:** 2 = dato correcto y completo (todos los datos clave de `respuesta_esperada`); 1 = correcto pero falta un dato o es impreciso; 0 = incorrecto o contradice. Sin respuesta: «No aparece en el documento» = 2; si inventa una respuesta = 0.
- **Fiel (sí/no):** «no» si afirma algo que NO está en los fragmentos que se le dieron, aunque sea cierto en la vida real.
- **Se abstiene:** «sí» solo si dice «No aparece en el documento» (o equivalente); «no» si responde; «na» no se usa (la abstención se evalúa en las 15).
- **Formato e idioma (sí/no):** español **y** cita el artículo o la sección. Sin cita = no.
- Anotar `puntuado_por` siempre. Si un caso es dudoso, decidirlo entre dos y apuntarlo.

## 3. Hoja de turnos de GPU (copiar a la hoja compartida)
| Día | Hora inicio | Hora fin | Persona | Qué lanza (modelo, escenario) | Medida de VRAM/latencia (sí/no) |
|---|---|---|---|---|---|
Reglas: durante una medida nadie más usa la GPU; comprobar antes `nvidia-smi` (instancia MIG ≈ 102 MiB en reposo); indexado y preparación fuera de esas franjas.

## 4. Comprobaciones ya hechas
- **Ventana de contexto:** peor caso de top-5 = 2 618 tokens (BOE) y 3 309 (Debian) con el tokenizador de Ministral + 300 de salida. Ventanas: Qwen3 32 k, SmolLM3 64 k, Ministral 262 k → sobra en todos.
- **Medido:** Ministral 3 8B en bf16 = 17,6 GB de pico (de 20), ~33 tokens/s.

## 5. Plan B con 8 GB (estimación por la fórmula del README: parámetros × bytes + 1–3 GB de KV + embedding ≈ 1 GB)
| Modelo | bf16 | Q8 | Q4 | ¿Cabe en 8 GB? |
|---|---|---|---|---|
| Qwen3-1.7B | 3,4 + 2 + 1 ≈ 6–7 GB | ≈ 4–5 GB | ≈ 3–4 GB | sí, incluso bf16 |
| SmolLM3-3B | 6 + 2 + 1 ≈ 9–10 GB | ≈ 6 GB | ≈ 4–5 GB | solo Q8 o Q4 |
| Qwen3-8B / Ministral 3 8B | ≈ 17–19 GB | ≈ 10–11 GB | 4,8 + 2 + 1 ≈ 7–8 GB | solo Q4, muy justo |
Son estimaciones, no medidas. Para medirlas haría falta cuantizar con `bitsandbytes` (no está instalado en el entorno) o con un stack GGUF; hay que decidir si se mide (extra) o si el plan B se defiende solo con la cuenta.
