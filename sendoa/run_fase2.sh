#!/usr/bin/env bash
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$RAIZ/.venv/bin/python"
SALIDA="$RAIZ/sendoa/resultados_oficiales"
UMBRAL_MIB="${UMBRAL_MIB:-1500}"

mkdir -p "$SALIDA"
LOG="$SALIDA/run_fase2_$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1

echo "== run_fase2 =="
date -Iseconds
echo "Log: $LOG"
echo

uso_mig_mib() {
  nvidia-smi 2>/dev/null | grep -m1 -oE '[0-9]+MiB / [0-9]+MiB' \
    | awk '{print $1}' | tr -d 'MiB'
}

comprobar_gpu() {
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "ERROR: nvidia-smi no disponible." >&2
    exit 1
  fi
  local uso
  uso="$(uso_mig_mib || true)"
  if [[ -z "${uso:-}" ]]; then
    echo "ERROR: no puedo leer la memoria de la instancia MIG." >&2
    exit 1
  fi
  echo "Memoria MIG en uso: ${uso} MiB (umbral ${UMBRAL_MIB} MiB)"
  if (( uso > UMBRAL_MIB )); then
    echo "ERROR: la instancia MIG parece ocupada (${uso} MiB). Abortando." >&2
    exit 1
  fi
}

for f in comun/chunks_boe.json comun/chunks_debian.json \
         comun/golden_set_boe.json comun/golden_set_debian.json \
         sendoa/config_bge_m3.json sendoa/config_qwen3.json \
         sendoa/config_gemma.json; do
  [[ -f "$RAIZ/$f" ]] || { echo "ERROR: falta $f" >&2; exit 1; }
done
[[ -x "$PY" ]] || { echo "ERROR: no existe $PY" >&2; exit 1; }

comprobar_gpu
echo
echo "Se van a lanzar 6 ejecuciones oficiales (3 embeddings x 2 escenarios)."
echo "Salida: $SALIDA"
read -r -p "¿Tienes turno exclusivo y la GPU libre? Escribe 'si': " resp
[[ "$resp" == "si" ]] || { echo "Cancelado."; exit 1; }

modelos=(
  "BAAI/bge-m3|sendoa/config_bge_m3.json"
  "Qwen/Qwen3-Embedding-0.6B|sendoa/config_qwen3.json"
  "google/embeddinggemma-300m|sendoa/config_gemma.json"
)
escenarios=(boe debian)

for par in "${modelos[@]}"; do
  modelo="${par%%|*}"
  config="${par##*|}"
  for esc in "${escenarios[@]}"; do
    comprobar_gpu
    echo
    echo ">>> $modelo | $esc | $(date -Iseconds)"
    "$PY" "$RAIZ/sendoa/eval_retrieval.py" \
      --modelo "$modelo" \
      --escenario "$esc" \
      --chunks "$RAIZ/comun/chunks_${esc}.json" \
      --golden "$RAIZ/comun/golden_set_${esc}.json" \
      --config "$RAIZ/$config" \
      --salida "$SALIDA" \
      --turno-exclusivo
  done
done

echo
echo ">>> Generando Tabla A oficial"
"$PY" "$RAIZ/sendoa/tabla_a.py" \
  --resultados "$SALIDA" \
  --salida "$RAIZ/sendoa/tablas" \
  --solo-oficiales

echo "Fin: $(date -Iseconds)"
