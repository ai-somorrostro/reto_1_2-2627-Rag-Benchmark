"""Estimación de tokens sin depender del tokenizador de cada modelo.

El objetivo de la Fase 1 no es contar tokens exactos, sino garantizar que
ningún chunk supere el límite de los embeddings que se probarán después. Por
eso se usa un estimador conservador y configurable (caracteres por token).
En la Fase 2, al fijar el embedding, se puede recalibrar el valor y volver a
validar el corpus sin tocar los textos.
"""

from __future__ import annotations

import math


def estimate_tokens(text: str, chars_per_token: float = 3.6) -> int:
    """Devuelve una estimación del número de tokens de ``text``.

    Es lineal en caracteres, lo que permite trocear por presupuesto de
    caracteres y saber de antemano que el chunk renderizado no se pasa.
    """
    if chars_per_token <= 0:
        raise ValueError("chars_per_token debe ser mayor que 0")
    text = text.strip()
    if not text:
        return 0
    return max(1, math.ceil(len(text) / chars_per_token))


def char_budget(tokens: int, chars_per_token: float) -> int:
    """Convierte un presupuesto de tokens en un presupuesto de caracteres."""
    if tokens < 0:
        raise ValueError("el presupuesto de tokens no puede ser negativo")
    return int(tokens * chars_per_token)
