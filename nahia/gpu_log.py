import csv
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

CARPETA_RESULTADOS = Path(__file__).resolve().parent / "resultados"


class RegistradorGPU:
    """Registra nvidia-smi en un CSV cada segundo, en un hilo, durante un bloque `with`.

    Es el mismo formato que usa este fichero como script, pero lo lanza el
    benchmark solo, así nunca se olvida el registro de GPU.
    """

    def __init__(self, ruta, intervalo_s=1.0):
        import threading

        self.ruta = Path(ruta)
        self.intervalo_s = intervalo_s
        self.pico_mb = 0
        self._parar = threading.Event()
        self._hilo = threading.Thread(target=self._bucle, daemon=True)

    def _bucle(self):
        self.ruta.parent.mkdir(exist_ok=True)
        with open(self.ruta, "w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            escritor.writerow(["fecha_hora", "gpu", "memoria_usada_mb", "memoria_total_mb"])
            while not self._parar.is_set():
                ahora = datetime.now().isoformat(timespec="seconds")
                for indice, usada, total in memoria_gpu_mb():
                    escritor.writerow([ahora, indice, usada, total])
                    self.pico_mb = max(self.pico_mb, usada)
                f.flush()
                self._parar.wait(self.intervalo_s)

    def __enter__(self):
        self._hilo.start()
        return self

    def __exit__(self, *exc):
        self._parar.set()
        self._hilo.join()


def memoria_gpu_mb():
    salida = subprocess.check_output(["nvidia-smi"], text=True)
    # Busca el patrón "102MiB / 20096MiB". El primero es la memoria de la instancia MIG.
    encontrado = re.search(r"(\d+)MiB\s*/\s*(\d+)MiB", salida)
    if encontrado is None:
        raise RuntimeError("No encuentro la memoria en la salida de nvidia-smi")
    usada, total = int(encontrado.group(1)), int(encontrado.group(2))
    return [(0, usada, total)]


if __name__ == "__main__":
    nombre = sys.argv[1] if len(sys.argv) > 1 else "gpu_prueba"
    CARPETA_RESULTADOS.mkdir(exist_ok=True)
    ruta = CARPETA_RESULTADOS / f"{nombre}.csv"
    picos = {}

    print(f"Registrando la GPU en {ruta} (para parar: Ctrl+C)")
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["fecha_hora", "gpu", "memoria_usada_mb", "memoria_total_mb"])
        try:
            while True:
                ahora = datetime.now().isoformat(timespec="seconds")
                for indice, usada, total in memoria_gpu_mb():
                    escritor.writerow([ahora, indice, usada, total])
                    picos[indice] = max(picos.get(indice, 0), usada)
                f.flush()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nParado.")
            for indice, pico in picos.items():
                print(f"GPU {indice}: pico de {pico} MiB ({pico / 1024:.1f} GiB)")