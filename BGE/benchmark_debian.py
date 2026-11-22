"""Benchmark RAG del corpus Debian para la carpeta BGE.

Indexa unicamente debian.md y guarda los resultados en resultados_debian/.
"""

from benchmark_common import main

if __name__ == "__main__":
    main("debian")
