"""Benchmark RAG del corpus BOE para la carpeta Multilingual.

Indexa unicamente BOE.md y guarda los resultados en resultados_boe/.
"""

from benchmark_common import main

if __name__ == "__main__":
    main("boe")
