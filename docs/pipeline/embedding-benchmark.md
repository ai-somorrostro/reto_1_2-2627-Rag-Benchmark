# Benchmark de embeddings (Fase 2)

## Ejecución

El benchmark usa los tres modelos fijados en `config/embeddings.toml` y carga
solo artefactos disponibles localmente. No descarga modelos. Ejecuta BOE, el
manual de Debian en español y el manual en inglés con las preguntas en español:

```bash
uv run --extra embeddings ragbench embeddings
```

Para una prueba acotada, se pueden indicar el modelo y el escenario:

```bash
uv run --extra embeddings ragbench embeddings \
  --model snowflake_arctic_embed_l_v2_0 --scenario boe
```

El identificador aceptado por `--model` es el nombre de la sección en el TOML.
Los IDs de repositorio, prefijos, pooling y longitudes máximas se conservan en
la configuración. Antes de medir, la CLI compara los SHA-256 de los chunks y
las preguntas con los hashes congelados. Si falta un modelo, no se sustituye:
se informa del error y el comando termina con estado distinto de cero.

## Método

- Los escenarios BOE y Debian en español conservan las entradas congeladas de
  Fase 1. Debian en inglés tiene chunks y golden set independientes.
- El golden set inglés reutiliza exactamente las preguntas y respuestas
  españolas; solo cambia el corpus y los IDs de evidencia.
- Las consultas sin respuesta se ejecutan y guardan, pero no entran en Recall
  ni MRR.
- **Recall@k de pregunta** vale 1 si todos los chunks relevantes de esa
  pregunta aparecen en los primeros k resultados; si falta alguno, vale 0.
  Así, una pregunta multi-fragmento solo cuenta como recuperada cuando llega
  toda su evidencia.
- **Fragment recall@k** es la proporción de chunks relevantes presentes en
  los primeros k. Se reporta como diagnóstico, no reemplaza Recall@k.
- **MRR** usa la posición del primer chunk relevante.
- Se ordena por similitud coseno entre vectores normalizados; los empates
  conservan el orden del corpus.
- Se genera el índice denso exacto en NumPy, sin aproximación ANN.
- El tiempo de indexado comprende la codificación de los chunks y la escritura
  de `embeddings.npy`; no comprende la carga del modelo ni el embedding de las
  consultas.
- VRAM pico es el máximo de memoria CUDA asignada por PyTorch después de cargar
  el modelo, durante embeddings de documentos y consultas. En CPU se registra
  como `null`.

## Resultados y trazabilidad

Para cada modelo y escenario se generan:

- `embeddings.npy`: matriz de vectores normalizados en float32.
- `results.jsonl`: ranking, puntuaciones y métricas por pregunta.
- `memory.jsonl`: uso de memoria CUDA asignada/reservada por lote, con fase y
  marca de tiempo.
- `summary.json`: Recall@1/3/5, MRR, tiempo y tamaño de índice, pico de VRAM,
  dimensiones, dtype, cantidad de parámetros, hashes y marca de tiempo.

Los resultados quedan bajo `artifacts/embeddings/<modelo>/<escenario>/`.
El tamaño reportado corresponde al archivo de vectores del índice, no a los
registros JSON de resultados. La CLI también genera
`artifacts/embeddings/summary.csv` con los modelos que terminaron. Solo crea
`selection.json` si los tres modelos se han ejecutado correctamente; así una
ejecución parcial no se presenta como decisión final.

La selección final sigue Recall@5, luego MRR y finalmente menor coste. No se
debe declarar ganador hasta tener resultados de los tres modelos para el
escenario.
