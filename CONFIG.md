# Congelación de la Fase 1

Fecha de congelación: **2026-11-17 (UTC)**  
Revisión Git de referencia: `8b816ab`

## Corpus y troceado

Configuración: [`config/chunking.toml`](config/chunking.toml)  
SHA-256 de la configuración: `9f82a1b8df584fc3c8c34173e87b8bab589a2f546786df954b569189b68855ee`

| Escenario | Markdown de origen | SHA-256 del origen | Chunks | Artefacto | SHA-256 del artefacto |
| --- | --- | --- | ---: | --- | --- |
| BOE | `data/Estatuto_Trabajadores_HTML.md` | `691c92537f5255f4a0f70ee8f6692815cbec418fa53a514a142e64db93bcfe00` | 349 | `artifacts/chunks/boe.jsonl` | `c1ff0754574ce7f0b7afd9981321573c92130b21208e937b0098f37ce52fcb28` |
| Debian | `data/Manual_Debian_Spanish.md` | `0d3f7802566e4cbe6902bf3e1ca29626584def4a98f5cac7a4c0e4213b3b77f5` | 1,074 | `artifacts/chunks/debian.jsonl` | `2f7b059aa93e0df61cd9e2269bf046ff8425798d40f2fd4b455fab0173773216` |

El manifiesto generado está en [`artifacts/chunks/manifest.json`](artifacts/chunks/manifest.json). Ambos escenarios validan sin errores ni avisos del parser. Se mantienen los avisos de tamaño: 11 chunks BOE y 52 Debian están por debajo de 80 tokens estimados; se aceptan como secciones breves y no se mezclan entre secciones.

El ejemplo de configuración y los comandos de `coturn` se normalizaron como bloques cercados antes de generar estos artefactos. El validador ya no confunde comentarios `#` dentro de bloques de código con títulos.

## Golden set

Cada escenario contiene 15 preguntas: 8 directas, 4 multi-fragmento y 3 sin respuesta.

| Escenario | Fichero | SHA-256 |
| --- | --- | --- |
| BOE | `data/golden_set/boe.jsonl` | `004b8902eeade621b4f58e4cedb6bc68b2d4a6c425b7a48827bf7574d6c32bfc` |
| Debian | `data/golden_set/debian.jsonl` | `8eac2a1a6feb0d3c534396f649193a970eb7ca1cb61b65831fa377af8c159b5f` |

Los IDs de evidencia apuntan a los artefactos de chunks de esta congelación. La prueba `test_golden_set.py` comprueba la composición, el esquema y que todas las referencias existan.

## Comparación multilingüe: manual Debian en inglés

Este extra no modifica los artefactos congelados anteriores. Usa una
configuración y un directorio de chunks independientes:

| Recurso | Ruta | SHA-256 / cantidad |
| --- | --- | --- |
| Configuración de chunking | `config/chunking-debian-en.toml` | `151d55ee1b92d06a129b906637809e6bca2438d234510e58418709b32432fcbd` |
| Markdown de origen | `data/Manual_Debian_English.md` | `750d512e7f9c7254f0648a55b44af5dd6b2ef36b56d0864296013efacee99cbb` |
| Chunks | `artifacts/chunks-english/debian-en.jsonl` | 1,014 chunks; `96283d6a346588a7472d18e995123f36c254000084540a69e79295f1f8907f89` |
| Golden set | `data/golden_set/debian-en.jsonl` | 15 preguntas; `6a6f658bebf577695aa3d5855799142fb1fa6b1d32720dfd3a81501ccdba4353` |

El golden set inglés reutiliza las preguntas y respuestas españolas del manual
en español y remapea la evidencia a los chunks ingleses. Así la comparación
mantiene fija la consulta y cambia el idioma del corpus. La validación señala
un aviso de posible título en un comentario de configuración y 62 chunks
inferiores a 80 tokens; no hay errores y las referencias del golden set son
válidas.
