import json
from datetime import datetime
from pathlib import Path

# Siempre junto a este fichero (nahia/resultados), da igual desde dónde se lance
CARPETA_RESULTADOS = Path(__file__).resolve().parent / "resultados"


def guardar_registro(nombre_fichero, **datos):
    CARPETA_RESULTADOS.mkdir(exist_ok=True)
    datos["fecha_hora"] = datetime.now().isoformat(timespec="seconds")
    ruta = CARPETA_RESULTADOS / nombre_fichero
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(json.dumps(datos, ensure_ascii=False) + "\n")
    return ruta


# Prueba con datos inventados (solo para ver que funciona)
if __name__ == "__main__":
    ruta = guardar_registro(
        "prueba.jsonl",
        modelo="modelo-de-prueba",
        version="0.0",
        cuantizacion="Q4",
        stack="ejemplo",
        escenario="BOE",
        pregunta_id="p01",
        pregunta="¿Qué dice el artículo 1?",
        respuesta="Respuesta de ejemplo.",
        ttft_s=0.5,
        tokens_por_s=30.0,
        latencia_total_s=2.0,
    )
    print("Guardado en:", ruta)