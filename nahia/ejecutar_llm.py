import json
import sys
import time

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, BaseStreamer

from prompt import construir_prompt
from registro import guardar_registro

MAX_TOKENS_SALIDA = 300


class Cronometro(BaseStreamer):
    """Apunta cuándo llega cada token, para medir TTFT y tokens/s."""

    def __init__(self):
        self.t_inicio = time.perf_counter()
        self.t_primer_token = None
        self.t_fin = None
        self.n_tokens = 0
        self._es_el_prompt = True

    def put(self, valor):
        if self._es_el_prompt:  # la primera llamada es el prompt, no un token generado
            self._es_el_prompt = False
            return
        if self.t_primer_token is None:
            self.t_primer_token = time.perf_counter()
        self.n_tokens += 1

    def end(self):
        self.t_fin = time.perf_counter()


def cargar_datos(escenario):
    chunks = json.load(open(f"../comun/chunks_{escenario}.json", encoding="utf-8"))
    golden = json.load(open(f"../comun/golden_set_{escenario}.json", encoding="utf-8"))
    return {c["id"]: c for c in chunks}, {q["id"]: q for q in golden}


def etiquetar(chunk):
    if "articulo" in chunk:
        etiqueta = chunk["articulo"]
    else:
        etiqueta = " > ".join(chunk["metadatos"].get("headings", []))
    return f"[{etiqueta}]\n{chunk['texto']}"


if __name__ == "__main__":
    nombre_modelo, escenario, pregunta_id = sys.argv[1], sys.argv[2], sys.argv[3]
    chunks, preguntas = cargar_datos(escenario)
    q = preguntas[pregunta_id]
    fragmentos = [etiquetar(chunks[i]) for i in q["chunks_correctos"]]
    prompt = construir_prompt(fragmentos, q["pregunta"])

    tokenizer = AutoTokenizer.from_pretrained(nombre_modelo)
    modelo = AutoModelForCausalLM.from_pretrained(nombre_modelo, dtype=torch.bfloat16).to("cuda")

    mensajes = [{"role": "user", "content": prompt}]
    texto = tokenizer.apply_chat_template(
        mensajes, tokenize=False, add_generation_prompt=True, enable_thinking=False
    )
    entradas = tokenizer(texto, return_tensors="pt").to("cuda")
    n_tokens_prompt = entradas["input_ids"].shape[1]

    torch.cuda.reset_peak_memory_stats()
    cronometro = Cronometro()
    with torch.no_grad():
        salida = modelo.generate(
            **entradas, max_new_tokens=MAX_TOKENS_SALIDA, do_sample=False, streamer=cronometro
        )
    respuesta = tokenizer.decode(salida[0][n_tokens_prompt:], skip_special_tokens=True).strip()

    ttft = cronometro.t_primer_token - cronometro.t_inicio
    latencia = cronometro.t_fin - cronometro.t_inicio
    gen = cronometro.t_fin - cronometro.t_primer_token
    tps = cronometro.n_tokens / gen if cronometro.n_tokens > 1 and gen > 0 else None
    vram_gb = torch.cuda.max_memory_allocated() / 1024**3

    ruta = guardar_registro(
        "prueba_llm.jsonl",
        modelo=nombre_modelo,
        version_modelo=getattr(modelo.config, "_commit_hash", None),
        cuantizacion="bf16",
        stack="transformers " + transformers.__version__,
        escenario=escenario,
        pregunta_id=pregunta_id,
        pregunta=q["pregunta"],
        respuesta=respuesta,
        respuesta_esperada=q["respuesta_esperada"],
        modo_fragmentos="correcto (golden set)",
        tokens_prompt=n_tokens_prompt,
        tokens_generados=cronometro.n_tokens,
        max_tokens_salida=MAX_TOKENS_SALIDA,
        temperatura=0,
        ttft_s=round(ttft, 3),
        tokens_por_s=round(tps, 1) if tps else None,
        latencia_total_s=round(latencia, 3),
        vram_pico_torch_gb=round(vram_gb, 2),
    )

    print("--- RESPUESTA ---")
    print(respuesta)
    print("--- ESPERADA ---")
    print(q["respuesta_esperada"])
    print(f"--- tokens prompt: {n_tokens_prompt} | generados: {cronometro.n_tokens}")
    print(f"--- TTFT: {ttft:.2f} s | tokens/s: {tps} | latencia: {latencia:.2f} s | VRAM torch: {vram_gb:.2f} GB")
    print("Guardado en:", ruta)