import csv
import json
import sys
from pathlib import Path

# Las cuatro columnas del medio de la derecha son las que rellena una persona a mano.
COLUMNAS = [
    "escenario", "pregunta_id", "tipo", "modelo", "pregunta", "respuesta_esperada",
    "respuesta",
    "correccion_0_2", "fiel_si_no", "se_abstiene_si_no_na",
    "formato_idioma_si_no", "puntuado_por",
]


def crear_hoja_puntuacion(fichero_jsonl):
    """Crea la hoja de puntuación a mano: una fila por pregunta (repetición 1).

    Las repeticiones 2 y 3 (solo para medir coste) tienen la misma respuesta con
    temperatura 0, así que no hace falta puntuarlas.
    """
    entrada = Path(fichero_jsonl)
    salida = entrada.with_name(entrada.stem + "_puntuacion.csv")

    with open(entrada, encoding="utf-8") as f:
        registros = [json.loads(linea) for linea in f if linea.strip()]
    registros = [r for r in registros if r.get("repeticion", 1) == 1]

    with open(salida, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS, extrasaction="ignore")
        escritor.writeheader()
        for r in registros:
            escritor.writerow(r)

    return salida, len(registros)


if __name__ == "__main__":
    fichero = sys.argv[1] if len(sys.argv) > 1 else "resultados/prueba.jsonl"
    ruta, n = crear_hoja_puntuacion(fichero)
    print(f"Hoja creada en {ruta} con {n} respuestas")
