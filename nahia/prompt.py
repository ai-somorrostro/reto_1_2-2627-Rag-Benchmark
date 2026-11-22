PROMPT = """Eres un asistente que responde preguntas usando SOLO los fragmentos que te doy.

Reglas:
1. Responde solo con la información de los fragmentos. No inventes nada.
2. Si la respuesta no está en los fragmentos, responde exactamente: No aparece en el documento.
3. Cita siempre el artículo o la sección de donde sacas la respuesta.
4. Responde en español.

Fragmentos:
{fragmentos}

Pregunta: {pregunta}

Respuesta:"""


def construir_prompt(fragmentos, pregunta):
    texto = "\n\n".join(fragmentos)
    return PROMPT.format(fragmentos=texto, pregunta=pregunta)


# Prueba con datos inventados (solo para ver que funciona)
if __name__ == "__main__":
    fragmentos_prueba = [
        "Artículo 1. Ejemplo de fragmento número uno.",
        "Artículo 2. Ejemplo de fragmento número dos.",
    ]
    print(construir_prompt(fragmentos_prueba, "¿Qué dice el artículo 1?"))
