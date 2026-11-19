#!/usr/bin/env python3
"""
Benchmark de Modelos de Embedding Locales con vLLM para RAG.
Práctica: Benchmark de LLMs y Embeddings Locales (BOE y Debian Handbook).

Modelos evaluados:
1. BAAI/bge-m3 (~568M params, 1024 dim)
2. Qwen/Qwen3-Embedding-0.6B (~600M params, 1024 dim)
3. microsoft/harrier-oss-v1-0.6b (~600M params, 1024 dim)

Métricas reportadas:
- Recall@1, Recall@3, Recall@5
- MRR (Mean Reciprocal Rank)
- Tiempo de indexado (s)
- Tamaño del índice en disco (MB)
- VRAM pico real (GB)
"""

import os
import sys
import json
import time
import datetime
import threading
import argparse
import numpy as np
import torch
from vllm import LLM

MODELS_CONFIG = {
    "bge-m3": {
        "repo": "BAAI/bge-m3",
        "params": "568M",
        "dim": 1024,
        "runner": "pooling",
        "query_prefix": "",
        "doc_prefix": "",
        "notes": "Encoder multilingüe (XLM-RoBERTa), sin prefijo"
    },
    "qwen3-embedding": {
        "repo": "Qwen/Qwen3-Embedding-0.6B",
        "params": "600M",
        "dim": 1024,
        "runner": "pooling",
        "query_prefix": "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery: ",
        "doc_prefix": "",
        "notes": "Decoder multilingüe Qwen3, con instrucción en query"
    },
    "harrier-oss-v1": {
        "repo": "microsoft/harrier-oss-v1-0.6b",
        "params": "600M",
        "dim": 1024,
        "runner": "pooling",
        "query_prefix": "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery: ",
        "doc_prefix": "",
        "notes": "Decoder multilingüe Qwen3 (Microsoft), con instrucción en query"
    }
}

SCENARIOS = {
    "boe": {
        "name": "Estatuto de los Trabajadores (BOE)",
        "chunks_path": "data/chunks/boe_final.json",
        "golden_path": "golden-set/golden_boe.jsonl"
    },
    "debian": {
        "name": "Manual del Administrador de Debian (Debian)",
        "chunks_path": "data/chunks/debian_final.json",
        "golden_path": "golden-set/golden_debian.jsonl"
    }
}


class VRAMMonitor:
    def __init__(self, log_path: str, interval: float = 0.05):
        self.log_path = log_path
        self.interval = interval
        self.peak_bytes = 0
        self.total_bytes = 0
        self._running = False
        self._thread = None
        self._log_file = None

    def start(self):
        self._running = True
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        self._log_file = open(self.log_path, "w", buffering=1)
        self._log_file.write("timestamp,used_mb,used_gb,free_gb,total_gb\n")
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def _monitor_loop(self):
        while self._running:
            try:
                free, total = torch.cuda.mem_get_info(0)
                used = total - free
                if used > self.peak_bytes:
                    self.peak_bytes = used
                self.total_bytes = total
                ts = datetime.datetime.now().isoformat()
                used_mb = used / (1024 ** 2)
                used_gb = used / (1024 ** 3)
                free_gb = free / (1024 ** 3)
                total_gb = total / (1024 ** 3)
                if self._log_file and not self._log_file.closed:
                    self._log_file.write(f"{ts},{used_mb:.2f},{used_gb:.3f},{free_gb:.3f},{total_gb:.3f}\n")
            except Exception:
                pass
            time.sleep(self.interval)

    def stop(self) -> float:
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        if self._log_file and not self._log_file.closed:
            self._log_file.close()
        return self.peak_bytes / (1024 ** 3)


def load_chunks(chunks_path: str):
    with open(chunks_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def load_golden_set(golden_path: str):
    items = []
    with open(golden_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def run_benchmark(model_key: str, scenario_key: str):
    cfg = MODELS_CONFIG[model_key]
    scen = SCENARIOS[scenario_key]
    model_name = cfg["repo"]
    
    print(f"\n=======================================================")
    print(f"BENCHMARK: {model_key} ({model_name}) | Escenario: {scen['name']}")
    print(f"=======================================================")

    log_vram_path = f"results/embeddings/logs/vram_{model_key}_{scenario_key}.log"
    vram_mon = VRAMMonitor(log_vram_path)
    vram_mon.start()

    try:
        # Inicializar vLLM
        print(f"[*] Cargando modelo {model_name} en vLLM...")
        t0_load = time.perf_counter()
        llm = LLM(
            model=model_name,
            runner=cfg["runner"],
            max_model_len=8192,
            gpu_memory_utilization=0.15,
            enforce_eager=True,
            disable_log_stats=True
        )
        t_load = time.perf_counter() - t0_load
        print(f"[+] Modelo cargado en {t_load:.2f} s")

        # Calentamiento (Warmup)
        print("[*] Calentando motor vLLM...")
        _ = llm.embed(["Calentamiento del modelo de embeddings antes de indexar."], use_tqdm=False)

        # Cargar corpus
        chunks = load_chunks(scen["chunks_path"])
        chunk_ids = [c["id"] for c in chunks]
        chunk_texts = [cfg["doc_prefix"] + c["texto"] for c in chunks]
        print(f"[*] Total fragmentos a indexar: {len(chunks)}")

        # Indexado con medición de tiempo
        print("[*] Indexando fragmentos...")
        t0_index = time.perf_counter()
        doc_outputs = llm.embed(chunk_texts, use_tqdm=True)
        t_index = time.perf_counter() - t0_index
        print(f"[+] Indexado completado en {t_index:.3f} s ({len(chunks)/t_index:.1f} chunks/s)")

        # Convertir a matriz numpy y normalizar L2 para similitud coseno
        doc_embeddings = np.array([out.outputs.embedding for out in doc_outputs], dtype=np.float32)
        # Normalización L2
        norms = np.linalg.norm(doc_embeddings, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1e-12, norms)
        doc_embeddings_norm = doc_embeddings / norms

        # Guardar índice en disco para medir tamaño en MB
        index_dir = "results/embeddings/indices"
        os.makedirs(index_dir, exist_ok=True)
        index_file = os.path.join(index_dir, f"{model_key}_{scenario_key}_index.npy")
        np.save(index_file, doc_embeddings_norm)
        index_size_mb = os.path.getsize(index_file) / (1024 ** 2)
        print(f"[+] Índice guardado en {index_file} ({index_size_mb:.2f} MB)")

        # Cargar golden set
        golden_items = load_golden_set(scen["golden_path"])
        evaluable_items = [item for item in golden_items if item.get("chunks") and len(item["chunks"]) > 0]
        unanswerable_items = [item for item in golden_items if not item.get("chunks") or len(item["chunks"]) == 0]

        print(f"[*] Evaluando retrieval sobre {len(golden_items)} preguntas ({len(evaluable_items)} con respuesta)...")

        queries = []
        for item in golden_items:
            q_text = cfg["query_prefix"] + item["pregunta"]
            queries.append(q_text)

        t0_retrieval = time.perf_counter()
        query_outputs = llm.embed(queries, use_tqdm=False)
        t_retrieval = time.perf_counter() - t0_retrieval

        query_embeddings = np.array([out.outputs.embedding for out in query_outputs], dtype=np.float32)
        q_norms = np.linalg.norm(query_embeddings, axis=1, keepdims=True)
        q_norms = np.where(q_norms == 0, 1e-12, q_norms)
        query_embeddings_norm = query_embeddings / q_norms

        # Calcular ranking de similitud coseno
        # sim_matrix: [num_queries, num_docs]
        sim_matrix = np.dot(query_embeddings_norm, doc_embeddings_norm.T)

        results_by_question = []
        
        hit_1_count = 0
        hit_3_count = 0
        hit_5_count = 0

        all_1_count = 0
        all_3_count = 0
        all_5_count = 0

        macro_recalls_1 = []
        macro_recalls_3 = []
        macro_recalls_5 = []

        reciprocal_ranks = []

        for idx, item in enumerate(golden_items):
            q_id = item["id"]
            q_tipo = item["tipo"]
            gold_chunks = item.get("chunks", [])
            
            sims = sim_matrix[idx]
            ranked_indices = np.argsort(-sims)
            
            top5_ranks = []
            for rank_pos in range(min(5, len(ranked_indices))):
                doc_idx = ranked_indices[rank_pos]
                cid = chunk_ids[doc_idx]
                score = float(sims[doc_idx])
                is_hit = cid in gold_chunks
                top5_ranks.append({
                    "rank": rank_pos + 1,
                    "chunk_id": cid,
                    "similarity": round(score, 4),
                    "is_gold": is_hit
                })

            q_result = {
                "id": q_id,
                "tipo": q_tipo,
                "pregunta": item["pregunta"],
                "respuesta_esperada": item.get("respuesta", ""),
                "gold_chunks": gold_chunks,
                "top5": top5_ranks
            }

            if gold_chunks:
                # Top k chunk ids
                top1_cids = {chunk_ids[i] for i in ranked_indices[:1]}
                top3_cids = {chunk_ids[i] for i in ranked_indices[:3]}
                top5_cids = {chunk_ids[i] for i in ranked_indices[:5]}

                # Hit (al menos 1)
                h1 = any(gc in top1_cids for gc in gold_chunks)
                h3 = any(gc in top3_cids for gc in gold_chunks)
                h5 = any(gc in top5_cids for gc in gold_chunks)

                # All (todos los chunks)
                a1 = all(gc in top1_cids for gc in gold_chunks)
                a3 = all(gc in top3_cids for gc in gold_chunks)
                a5 = all(gc in top5_cids for gc in gold_chunks)

                # Macro / proporcional
                m1 = sum(1 for gc in gold_chunks if gc in top1_cids) / len(gold_chunks)
                m3 = sum(1 for gc in gold_chunks if gc in top3_cids) / len(gold_chunks)
                m5 = sum(1 for gc in gold_chunks if gc in top5_cids) / len(gold_chunks)

                # MRR: primer acierto
                rr = 0.0
                for r_pos, doc_idx in enumerate(ranked_indices):
                    if chunk_ids[doc_idx] in gold_chunks:
                        rr = 1.0 / (r_pos + 1)
                        break

                if h1: hit_1_count += 1
                if h3: hit_3_count += 1
                if h5: hit_5_count += 1

                if a1: all_1_count += 1
                if a3: all_3_count += 1
                if a5: all_5_count += 1

                macro_recalls_1.append(m1)
                macro_recalls_3.append(m3)
                macro_recalls_5.append(m5)

                reciprocal_ranks.append(rr)

                q_result["hit@1"] = h1
                q_result["hit@3"] = h3
                q_result["hit@5"] = h5
                q_result["all@1"] = a1
                q_result["all@3"] = a3
                q_result["all@5"] = a5
                q_result["proportional@5"] = round(m5, 4)
                q_result["reciprocal_rank"] = round(rr, 4)
            else:
                q_result["hit@1"] = None
                q_result["hit@3"] = None
                q_result["hit@5"] = None
                q_result["all@5"] = None
                q_result["reciprocal_rank"] = None

            results_by_question.append(q_result)

        n_eval = len(evaluable_items)
        recall_1_hit = hit_1_count / n_eval
        recall_3_hit = hit_3_count / n_eval
        recall_5_hit = hit_5_count / n_eval

        recall_1_all = all_1_count / n_eval
        recall_3_all = all_3_count / n_eval
        recall_5_all = all_5_count / n_eval

        macro_recall_1 = sum(macro_recalls_1) / n_eval
        macro_recall_3 = sum(macro_recalls_3) / n_eval
        macro_recall_5 = sum(macro_recalls_5) / n_eval

        mrr = sum(reciprocal_ranks) / n_eval

    finally:
        peak_vram_gb = vram_mon.stop()

    summary = {
        "model_key": model_key,
        "model_repo": model_name,
        "parameters": cfg["params"],
        "dimension": cfg["dim"],
        "scenario_key": scenario_key,
        "scenario_name": scen["name"],
        "total_chunks": len(chunks),
        "total_questions": len(golden_items),
        "evaluable_questions": n_eval,
        "unanswerable_questions": len(unanswerable_items),
        "stack": "vLLM",
        "vllm_version": "0.34.0",
        "torch_version": torch.__version__,
        "cuda_device": torch.cuda.get_device_name(0),
        "timestamp_iso": datetime.datetime.now().isoformat(),
        # Métricas estándar (Hit: al menos un chunk relevante en top-k)
        "recall_at_1_hit": round(recall_1_hit, 4),
        "recall_at_3_hit": round(recall_3_hit, 4),
        "recall_at_5_hit": round(recall_5_hit, 4),
        # Métricas estrictas (All: todos los chunks requeridos en top-k)
        "recall_at_1_all": round(recall_1_all, 4),
        "recall_at_3_all": round(recall_3_all, 4),
        "recall_at_5_all": round(recall_5_all, 4),
        # Métricas macro/proporcionales
        "recall_at_1_macro": round(macro_recall_1, 4),
        "recall_at_3_macro": round(macro_recall_3, 4),
        "recall_at_5_macro": round(macro_recall_5, 4),
        "mrr": round(mrr, 4),
        # Métricas de coste
        "index_time_sec": round(t_index, 3),
        "index_speed_chunks_per_sec": round(len(chunks) / t_index, 2),
        "index_size_mb": round(index_size_mb, 2),
        "vram_peak_gb": round(peak_vram_gb, 3),
        "query_retrieval_time_sec": round(t_retrieval, 4)
    }

    out_data = {
        "summary": summary,
        "questions": results_by_question
    }

    out_file = f"results/embeddings/data/{model_key}_{scenario_key}.json"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)

    print(f"\n--- RESUMEN ({model_key} - {scenario_key}) ---")
    print(f"Recall@1 (Hit/All): {recall_1_hit:.4f} / {recall_1_all:.4f}")
    print(f"Recall@3 (Hit/All): {recall_3_hit:.4f} / {recall_3_all:.4f}")
    print(f"Recall@5 (Hit/All): {recall_5_hit:.4f} / {recall_5_all:.4f}")
    print(f"MRR:               {mrr:.4f}")
    print(f"Tiempo indexado:   {t_index:.2f} s")
    print(f"Tamaño índice:     {index_size_mb:.2f} MB")
    print(f"VRAM pico:         {peak_vram_gb:.3f} GB")
    print(f"Guardado en:       {out_file}")
    return summary


def main():
    parser = argparse.ArgumentParser(description="Benchmark de embeddings con vLLM")
    parser.add_argument("--model", choices=list(MODELS_CONFIG.keys()) + ["all"], default="all")
    parser.add_argument("--scenario", choices=list(SCENARIOS.keys()) + ["all"], default="all")
    args = parser.parse_args()

    models = list(MODELS_CONFIG.keys()) if args.model == "all" else [args.model]
    scenarios = list(SCENARIOS.keys()) if args.scenario == "all" else [args.scenario]

    summaries = []
    for s in scenarios:
        for m in models:
            s_res = run_benchmark(m, s)
            summaries.append(s_res)

    print("\nTODOS LOS BENCHMARKS FINALIZADOS CON ÉXITO.")


if __name__ == "__main__":
    main()
