# Troceado del corpus (Fase 1)

Este módulo convierte los markdown de `data/` en `artifacts/chunks/<escenario>.jsonl`.
No modifica los documentos: solo los lee y produce chunks con IDs estables.

## Decisiones congelables

| Decisión | BOE | Debian |
| --- | --- | --- |
| Corte principal | Título de artículo o disposición | Título de sección |
| Tamaño máximo | 420 tokens estimados | 520 tokens estimados |
| Solape | 50 tokens | 80 tokens |
| Código | No aplica | Bloques íntegros, nunca mezclados con prosa |

Reglas comunes:

- Un chunk no mezcla dos secciones.
- Las secciones largas se parten por párrafos (y por frases si un párrafo no cabe).
- El título de la sección se antepone al texto, así el chunk se puede citar aunque
  se use solo el texto.
- El tamaño se mide con un estimador conservador (`caracteres / 3,6`). En la
  Fase 2 se recalibra con el tokenizador del embedding ganador y se vuelve a
  validar sin cambiar los textos.

## Uso

```bash
# Ver estadísticas sin escribir nada (útil mientras los markdown cambian)
uv run ragbench chunk build --dry-run

# Generar los chunks de los dos escenarios
uv run ragbench chunk build

# Generar solo uno
uv run ragbench chunk build --scenario boe

# Validar antes de congelar
uv run ragbench chunk validate
```

Salidas:

- `artifacts/chunks/boe.jsonl`
- `artifacts/chunks/debian.jsonl`
- `artifacts/chunks/manifest.json` (hash del markdown, hash de la config,
  estadísticas y avisos del parser)

## Esquema de cada chunk

```json
{
  "id": "boe-art38-p01",
  "scenario": "boe",
  "source": "data/Estatuto_Trabajadores_HTML.md",
  "section": "Artículo 38. Vacaciones anuales.",
  "section_path": ["Estatuto...", "Sección 5.ª Tiempo de trabajo", "Artículo 38..."],
  "article": "38",
  "text": "Artículo 38. Vacaciones anuales.\n\n1. El periodo de vacaciones...",
  "n_chars": 1420,
  "n_tokens_est": 395,
  "part": 1,
  "n_parts": 1,
  "start_line": 1016,
  "end_line": 1030
}
```

`start_line` y `end_line` permiten abrir el markdown y revisar el fragmento
exacto antes de asignarlo como oro en el golden set.

## Validación

`ragbench chunk validate` comprueba:

- esquema completo y tipos correctos;
- IDs únicos con formato estable `...-pNN`;
- partes consecutivas y `n_parts` coherente;
- tamaño dentro del máximo y estimación de tokens recalculable;
- fences de código cerrados;
- artículo presente cuando la sección empieza por «Artículo»;
- líneas de origen válidas.

Además avisa de chunks diminutos, textos duplicados y líneas de título que se
hayan colado en el cuerpo. Los avisos no bloquean; los errores sí.

## Congelación

1. Los markdown tienen que estar cerrados. Cualquier cambio posterior cambia
   líneas y puede cambiar IDs.
2. `uv run ragbench chunk build && uv run ragbench chunk validate`.
3. Revisar a mano una muestra de chunks (los que se usarán en el golden set).
4. Anotar en `CONFIG.md` la fecha, el hash de la config y el hash de cada
   markdown que aparece en `manifest.json`.
5. No volver a ejecutar `build` salvo que se acepte repetir todas las medidas.

## Pendiente del conversor de documentos (no tocar aquí)

Detectado al leer los markdown actuales:

- Los comandos y salidas de Debian están en líneas con backticks en vez de
  bloques cercados; un chunk puede quedar con código y prosa mezclados.
- Hay títulos con niveles irregulares (hasta 8 almohadillas) y algún título
  dentro de lo que debería ser un bloque de código.
- El troceador es tolerante con ambos casos, pero la calidad de las citas de
  sección mejorará cuando el conversor los unifique.
