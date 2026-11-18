import json
from pathlib import Path
from transformers import AutoTokenizer

ruta = Path(__file__).resolve().parent.parent / "comun" / "chunks_debian.json"
textos = [c["texto"] for c in json.load(open(ruta, encoding="utf-8"))]

for nombre in ["intfloat/multilingual-e5-small", "BAAI/bge-m3"]:
    tok = AutoTokenizer.from_pretrained(nombre)
    n = [len(x) for x in tok(textos, add_special_tokens=True, truncation=False)["input_ids"]]
    print(nombre, "| max:", max(n), "| >256:", sum(x > 256 for x in n),
          "| >512:", sum(x > 512 for x in n), "| >1024:", sum(x > 1024 for x in n))