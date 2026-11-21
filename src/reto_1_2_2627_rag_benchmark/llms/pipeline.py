"""Ejecución local, trazabilidad y resumen del benchmark de LLMs."""

from __future__ import annotations

import csv
from contextlib import contextmanager
import gc
import importlib.metadata
import json
import math
import os
import platform
import re
import statistics
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from collections.abc import Iterator
from pathlib import Path
from typing import Any, TextIO

from ..embeddings.config import load_config as load_embedding_config
from ..embeddings.config import sha256_file, verify_frozen_file
from .config import SCENARIOS, LLMBenchmarkConfig, LLMModelConfig


SYSTEM_PROMPT = (
    "Responde en español usando exclusivamente la información de los fragmentos. "
    "Si los fragmentos no contienen la respuesta, responde exactamente: "
    "«No aparece en el documento». Cita el artículo o la sección que respalda "
    "la respuesta. No uses conocimiento externo y sé conciso."
)
PROMPT_VERSION = "ragbench-llm-v1"
RUN_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ScenarioInputs:
    scenario: str
    embedding_model: str
    chunks_path: Path
    questions_path: Path
    retrieval_path: Path
    questions: list[dict[str, Any]]
    chunk_by_id: dict[str, dict[str, Any]]
    retrieval_by_question: dict[str, dict[str, Any]]


def _load_json(path: Path) -> dict[str, Any]:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: JSON inválido: {exc}") from exc
    if not isinstance(result, dict):
        raise ValueError(f"{path}: se esperaba un objeto JSON")
    return result


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: JSON inválido: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: se esperaba un objeto JSON")
            rows.append(row)
    return rows


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


@contextmanager
def _mark_failed_on_error(
    manifest: dict[str, Any], manifest_path: Path
) -> Iterator[None]:
    try:
        yield
    except (OSError, RuntimeError, ValueError) as exc:
        manifest["status"] = "failed"
        manifest["failed_at"] = datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        )
        active_model = manifest.pop("active_model", None)
        if active_model:
            manifest["failed_model"] = active_model
        manifest["error"] = str(exc)
        _write_json(manifest_path, manifest)
        raise


def _append_jsonl(handle: TextIO, row: dict[str, Any]) -> None:
    handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    handle.flush()


def _model_slug(model_name: str) -> str:
    return model_name.replace("_", "-")


def _check_ids(rows: list[dict[str, Any]], field: str, path: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = row.get(field)
        if not isinstance(value, str) or not value:
            raise ValueError(f"{path}: falta un {field} válido")
        if value in result:
            raise ValueError(f"{path}: {field} duplicado: {value}")
        result[value] = row
    return result


def load_scenario_inputs(
    config: LLMBenchmarkConfig, scenario: str
) -> ScenarioInputs:
    embedding_config = load_embedding_config(config.embedding_config_path)
    if scenario not in embedding_config.chunk_files:
        raise ValueError(f"el escenario {scenario} no está configurado en embeddings")

    chunks_path = embedding_config.chunk_files[scenario]
    questions_path = embedding_config.questions_dir / f"{scenario}.jsonl"
    verify_frozen_file(chunks_path, embedding_config.chunk_hashes[scenario])
    verify_frozen_file(questions_path, embedding_config.question_hashes[scenario])

    selection_path = embedding_config.output_dir / "selection.json"
    selection = _load_json(selection_path)
    selected = selection.get(scenario, {}).get("winner")
    if not isinstance(selected, str) or selected not in embedding_config.models:
        raise ValueError(
            f"{selection_path}: no hay un embedding ganador válido para {scenario}"
        )

    model_dir = embedding_config.output_dir / _model_slug(selected) / scenario
    retrieval_path = model_dir / "results.jsonl"
    if not retrieval_path.is_file():
        raise FileNotFoundError(
            f"faltan los resultados de retrieval para {selected}/{scenario}: "
            f"{retrieval_path}"
        )
    embedding_summary_path = model_dir / "summary.json"
    embedding_summary = _load_json(embedding_summary_path)
    if (
        embedding_summary.get("model") != selected
        or embedding_summary.get("scenario") != scenario
        or embedding_summary.get("model_id")
        != embedding_config.models[selected].model_id
        or embedding_summary.get("chunks_sha256")
        != embedding_config.chunk_hashes[scenario]
        or embedding_summary.get("questions_sha256")
        != embedding_config.question_hashes[scenario]
    ):
        raise ValueError(
            f"{embedding_summary_path}: el resumen no corresponde a las entradas "
            "congeladas y al embedding seleccionado"
        )

    chunks = _load_jsonl(chunks_path)
    questions = _load_jsonl(questions_path)
    retrieval_rows = _load_jsonl(retrieval_path)
    chunk_by_id = _check_ids(chunks, "id", chunks_path)
    question_by_id = _check_ids(questions, "id", questions_path)
    retrieval_by_question = _check_ids(
        retrieval_rows, "question_id", retrieval_path
    )

    if set(question_by_id) != set(retrieval_by_question):
        raise ValueError(
            f"{retrieval_path}: las preguntas no coinciden con {questions_path}"
        )
    for question_id, question in question_by_id.items():
        if question.get("scenario") != scenario:
            raise ValueError(f"{question_id}: escenario distinto de {scenario}")
        result = retrieval_by_question[question_id]
        if result.get("question") != question.get("question"):
            raise ValueError(f"{question_id}: texto de pregunta distinto en retrieval")
        if result.get("relevant_chunk_ids") != question.get("relevant_chunk_ids"):
            raise ValueError(f"{question_id}: evidencia de retrieval distinta al golden set")
        ranked_ids = result.get("ranked_chunk_ids")
        if not isinstance(ranked_ids, list) or len(ranked_ids) < config.top_k:
            raise ValueError(
                f"{retrieval_path}: {question_id} no tiene {config.top_k} resultados"
            )
        for chunk_id in ranked_ids[: config.top_k]:
            if chunk_id not in chunk_by_id:
                raise ValueError(
                    f"{retrieval_path}: {question_id} refiere a chunk inexistente "
                    f"{chunk_id}"
                )
        if not isinstance(question.get("expected_answer"), str):
            raise ValueError(f"{question_id}: falta expected_answer")

    return ScenarioInputs(
        scenario=scenario,
        embedding_model=selected,
        chunks_path=chunks_path,
        questions_path=questions_path,
        retrieval_path=retrieval_path,
        questions=questions,
        chunk_by_id=chunk_by_id,
        retrieval_by_question=retrieval_by_question,
    )


def _context_label(chunk: dict[str, Any]) -> str:
    article = chunk.get("article")
    section = chunk.get("section")
    if article:
        return f"Artículo {article}" + (f" — {section}" if section else "")
    if section:
        return str(section)
    section_path = chunk.get("section_path", [])
    return " > ".join(str(part) for part in section_path) or "Fragmento"


def _user_prompt(question: str, context_chunks: list[dict[str, Any]]) -> str:
    context = "\n\n".join(
        f"[{chunk['id']}] {_context_label(chunk)}\n{chunk['text']}"
        for chunk in context_chunks
    )
    return f"Pregunta:\n{question}\n\nFragmentos recuperados:\n{context}"


def render_prompt(
    tokenizer: Any,
    model: LLMModelConfig,
    question: str,
    context_chunks: list[dict[str, Any]],
) -> str:
    user_message = _user_prompt(question, context_chunks)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
    if model.prompt_format == "chat_template":
        if not getattr(tokenizer, "chat_template", None):
            raise ValueError(
                f"{model.model_id}: no tiene chat_template; configure un formato "
                "explícito en llms.toml"
            )
        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        if not isinstance(prompt, str):
            raise ValueError(f"{model.model_id}: el chat template no devolvió texto")
        return prompt

    if model.prompt_format == "granite_role_markers":
        vocabulary = tokenizer.get_vocab()
        markers = ("<|start_of_role|>", "<|end_of_role|>")
        if any(marker not in vocabulary for marker in markers):
            raise ValueError(f"{model.model_id}: faltan marcadores nativos de Granite")
        end_of_text = tokenizer.eos_token
        if not isinstance(end_of_text, str) or not end_of_text:
            raise ValueError(f"{model.model_id}: falta el token EOS de Granite")
        start, end = markers
        return (
            f"{start}system{end}{SYSTEM_PROMPT}{end_of_text}\n"
            f"{start}user{end}{user_message}{end_of_text}\n"
            f"{start}assistant{end}"
        )

    raise ValueError(f"{model.model_id}: formato de prompt no soportado")


def resolve_model_path(model_id: str) -> Path:
    local_path = Path(model_id).expanduser()
    if local_path.is_dir():
        return local_path.resolve()
    try:
        from huggingface_hub import try_to_load_from_cache

        config_path = try_to_load_from_cache(model_id, "config.json", repo_type="model")
    except (ImportError, OSError, ValueError) as exc:
        raise RuntimeError(
            f"no se pudo comprobar el caché local de {model_id}: {exc}"
        ) from exc
    if not isinstance(config_path, str) or not Path(config_path).is_file():
        raise FileNotFoundError(
            f"el modelo {model_id} no está completo en la caché local; "
            "el benchmark no descarga modelos"
        )
    return Path(config_path).parent.resolve()


def _prepare_prompts(
    config: LLMBenchmarkConfig,
    models: dict[str, LLMModelConfig],
    scenario_inputs: dict[str, ScenarioInputs],
) -> tuple[
    dict[str, Path],
    dict[str, int],
    dict[tuple[str, str, str], tuple[str, int]],
]:
    try:
        from transformers import AutoTokenizer
        from safetensors import safe_open
    except ImportError as exc:
        raise RuntimeError(
            "el preflight requiere Transformers y safetensors en el intérprete "
            "seleccionado"
        ) from exc

    model_paths: dict[str, Path] = {}
    model_parameters: dict[str, int] = {}
    prompts: dict[tuple[str, str, str], tuple[str, int]] = {}
    for name, model in models.items():
        path = resolve_model_path(model.model_id)
        model_paths[name] = path
        model_config_path = path / "config.json"
        if not model_config_path.is_file():
            raise FileNotFoundError(f"falta la configuración local del modelo: {path}")
        model_metadata = _load_json(model_config_path)
        actual_dtype = str(model_metadata.get("torch_dtype", "")).removeprefix("torch.")
        if actual_dtype != model.checkpoint_dtype:
            raise ValueError(
                f"{model.model_id}: checkpoint dtype {actual_dtype!r}, se esperaba "
                f"{model.checkpoint_dtype!r}"
            )
        if model_metadata.get("quantization_config"):
            raise ValueError(
                f"{model.model_id}: el checkpoint tiene cuantización configurada"
            )

        weight_files = sorted(path.glob("*.safetensors"))
        if not weight_files:
            raise FileNotFoundError(
                f"{model.model_id}: no hay pesos safetensors en {path}"
            )
        parameter_count = 0
        for weight_file in weight_files:
            with safe_open(weight_file, framework="pt", device="cpu") as weights:
                for key in weights.keys():
                    parameter_count += math.prod(weights.get_slice(key).get_shape())
        model_parameters[name] = parameter_count

        tokenizer = AutoTokenizer.from_pretrained(
            path, local_files_only=True, trust_remote_code=False
        )
        for scenario, inputs in scenario_inputs.items():
            for question in inputs.questions:
                question_id = question["id"]
                result = inputs.retrieval_by_question[question_id]
                context_chunks = [
                    inputs.chunk_by_id[chunk_id]
                    for chunk_id in result["ranked_chunk_ids"][: config.top_k]
                ]
                prompt = render_prompt(
                    tokenizer, model, question["question"], context_chunks
                )
                prompt_tokens = len(tokenizer.encode(prompt, add_special_tokens=False))
                if prompt_tokens + config.max_tokens > config.max_model_len:
                    raise ValueError(
                        f"{model.model_id}/{scenario}/{question_id}: prompt de "
                        f"{prompt_tokens} tokens + {config.max_tokens} de salida "
                        f"excede max_model_len={config.max_model_len}"
                    )
                prompts[(name, scenario, question_id)] = (prompt, prompt_tokens)
        del tokenizer
    return model_paths, model_parameters, prompts


def _cost_questions(
    questions: list[dict[str, Any]], count: int
) -> list[dict[str, Any]]:
    selected = []
    seen_types = set()
    for question in questions:
        question_type = question.get("type")
        if question_type not in seen_types:
            selected.append(question)
            seen_types.add(question_type)
        if len(selected) == count:
            return selected
    for question in questions:
        if question not in selected:
            selected.append(question)
        if len(selected) == count:
            return selected
    raise ValueError(f"se necesitan al menos {count} preguntas para medir coste")


def _memory_sample(
    torch: Any,
    model_name: str,
    phase: str,
    scenario: str | None,
    question_id: str | None,
) -> dict[str, Any]:
    device = torch.cuda.current_device()
    torch.cuda.synchronize(device)
    free_bytes, total_bytes = torch.cuda.mem_get_info(device)
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "model": model_name,
        "phase": phase,
        "scenario": scenario,
        "question_id": question_id,
        "device": torch.cuda.get_device_name(device),
        "device_total_bytes": int(total_bytes),
        "device_used_bytes": int(total_bytes - free_bytes),
        "allocated_bytes": int(torch.cuda.memory_allocated(device)),
        "reserved_bytes": int(torch.cuda.memory_reserved(device)),
        "peak_allocated_bytes": int(torch.cuda.max_memory_allocated(device)),
        "peak_reserved_bytes": int(torch.cuda.max_memory_reserved(device)),
    }


def _generate_one(
    engine: Any, sampling_params: Any, prompt: str
) -> dict[str, Any]:
    started = time.perf_counter()
    output_rows = engine.generate([prompt], sampling_params, use_tqdm=False)
    elapsed = time.perf_counter() - started
    if len(output_rows) != 1 or not output_rows[0].outputs:
        raise RuntimeError("vLLM no devolvió una respuesta de generación")

    request = output_rows[0]
    completion = request.outputs[0]
    metrics = request.metrics
    first_token_latency = getattr(metrics, "first_token_latency", None)
    if not isinstance(first_token_latency, (int, float)) or first_token_latency <= 0:
        first_token_latency = None
    token_count = len(completion.token_ids)
    decode_time = None
    if metrics is not None:
        first_token_ts = getattr(metrics, "first_token_ts", None)
        last_token_ts = getattr(metrics, "last_token_ts", None)
        if (
            isinstance(first_token_ts, (int, float))
            and isinstance(last_token_ts, (int, float))
            and last_token_ts > first_token_ts
        ):
            decode_time = last_token_ts - first_token_ts
    tokens_per_second = (
        (token_count - 1) / decode_time
        if token_count > 1 and decode_time is not None and decode_time > 0
        else None
    )
    prompt_token_ids = getattr(request, "prompt_token_ids", None)

    return {
        "answer": completion.text,
        "finish_reason": completion.finish_reason,
        "stop_reason": completion.stop_reason,
        "prompt_tokens": len(prompt_token_ids) if prompt_token_ids is not None else None,
        "completion_tokens": token_count,
        "ttft_seconds": first_token_latency,
        "decode_seconds": decode_time,
        "tokens_per_second": tokens_per_second,
        "latency_seconds": elapsed,
    }


def _response_record(
    run_id: str,
    model: LLMModelConfig,
    parameter_count: int,
    model_revision: str | None,
    scenario: str,
    inputs: ScenarioInputs,
    question: dict[str, Any],
    prompt: str,
    prompt_tokens: int,
    generated: dict[str, Any],
    config: LLMBenchmarkConfig,
) -> dict[str, Any]:
    question_id = question["id"]
    result = inputs.retrieval_by_question[question_id]
    chunk_ids = result["ranked_chunk_ids"][: config.top_k]
    contexts = [
        {
            "chunk_id": chunk_id,
            "section": _context_label(inputs.chunk_by_id[chunk_id]),
            "text": inputs.chunk_by_id[chunk_id]["text"],
        }
        for chunk_id in chunk_ids
    ]
    return {
        "response_id": f"{run_id}:{model.name}:{scenario}:{question_id}",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": model.name,
        "model_id": model.model_id,
        "model_revision": model_revision,
        "size_category": model.size_category,
        "checkpoint_parameters": parameter_count,
        "checkpoint_parameters_billions": parameter_count / 1_000_000_000,
        "checkpoint_dtype": model.checkpoint_dtype,
        "quantization": model.quantization,
        "stack": "vLLM",
        "scenario": scenario,
        "embedding_model": inputs.embedding_model,
        "question_id": question_id,
        "question_type": question["type"],
        "question": question["question"],
        "expected_answer": question["expected_answer"],
        "relevant_chunk_ids": question["relevant_chunk_ids"],
        "retrieved_chunk_ids": chunk_ids,
        "contexts": contexts,
        "prompt_version": PROMPT_VERSION,
        "prompt": prompt,
        "prompt_tokens": prompt_tokens,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        **generated,
    }


def _score_template(response: dict[str, Any]) -> dict[str, Any]:
    return {
        "response_id": response["response_id"],
        "model": response["model"],
        "scenario": response["scenario"],
        "question_id": response["question_id"],
        "question_type": response["question_type"],
        "question": response["question"],
        "response": response["answer"],
        "correctness_score": None,
        "faithful": None,
        "abstention": None,
        "format_language": None,
        "notes": "",
    }


def _cost_record(
    run_id: str,
    model: LLMModelConfig,
    parameter_count: int,
    model_revision: str | None,
    scenario: str,
    question: dict[str, Any],
    response_id: str | None,
    prompt: str,
    prompt_tokens: int,
    generated: dict[str, Any],
    kind: str,
    repetition: int | None,
    memory: dict[str, Any],
) -> dict[str, Any]:
    return {
        "measurement_id": (
            f"{run_id}:{model.name}:{scenario}:{question['id']}:{kind}:"
            f"{repetition if repetition is not None else 0}"
        ),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kind": kind,
        "repetition": repetition,
        "response_id": response_id,
        "model": model.name,
        "model_id": model.model_id,
        "model_revision": model_revision,
        "size_category": model.size_category,
        "checkpoint_parameters": parameter_count,
        "checkpoint_parameters_billions": parameter_count / 1_000_000_000,
        "checkpoint_dtype": model.checkpoint_dtype,
        "quantization": model.quantization,
        "stack": "vLLM",
        "scenario": scenario,
        "question_id": question["id"],
        "question_type": question["type"],
        "prompt": prompt,
        "prompt_tokens": prompt_tokens,
        **generated,
        "vram_peak_allocated_gb": memory["peak_allocated_bytes"] / (1024**3),
        "vram_peak_reserved_gb": memory["peak_reserved_bytes"] / (1024**3),
        "device_used_gb": memory["device_used_bytes"] / (1024**3),
    }


def _median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def _write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field) for field in fields} for row in rows)


def _cost_summary(
    cost_rows: list[dict[str, Any]],
    memory_rows: list[dict[str, Any]],
    repeats: int,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    model_metadata: dict[tuple[str, str], dict[str, Any]] = {}
    for row in cost_rows:
        if row.get("kind") == "measurement":
            key = (row["model"], row["scenario"], row["question_id"])
            grouped.setdefault(key, []).append(row)
            model_metadata.setdefault((row["model"], row["scenario"]), row)

    question_metrics: dict[tuple[str, str], list[dict[str, float | None]]] = {}
    for (model, scenario, question_id), rows in grouped.items():
        if len(rows) != repeats or {row.get("repetition") for row in rows} != set(
            range(1, repeats + 1)
        ):
            raise ValueError(
                f"{model}/{scenario}/{question_id}: se esperaban {repeats} "
                "repeticiones medidas"
            )
        question_metrics.setdefault((model, scenario), []).append(
            {
                metric: _median(
                    [
                        float(row[metric])
                        for row in rows
                        if isinstance(row.get(metric), (int, float))
                        and math.isfinite(float(row[metric]))
                    ]
                )
                for metric in (
                    "ttft_seconds",
                    "tokens_per_second",
                    "latency_seconds",
                )
            }
        )

    memory_by_model: dict[str, list[dict[str, Any]]] = {}
    for row in memory_rows:
        memory_by_model.setdefault(row["model"], []).append(row)

    summaries = []
    for (model, scenario), values in sorted(question_metrics.items()):
        model_memory = memory_by_model.get(model, [])
        metadata = model_metadata[(model, scenario)]
        summaries.append(
            {
                "model": model,
                "model_id": metadata["model_id"],
                "size_category": metadata["size_category"],
                "checkpoint_parameters_billions": metadata[
                    "checkpoint_parameters_billions"
                ],
                "checkpoint_dtype": metadata["checkpoint_dtype"],
                "quantization": metadata["quantization"],
                "scenario": scenario,
                "stack": "vLLM",
                "ttft_seconds": _median(
                    [float(row["ttft_seconds"]) for row in values if row["ttft_seconds"] is not None]
                ),
                "tokens_per_second": _median(
                    [float(row["tokens_per_second"]) for row in values if row["tokens_per_second"] is not None]
                ),
                "latency_seconds": _median(
                    [float(row["latency_seconds"]) for row in values if row["latency_seconds"] is not None]
                ),
                "vram_peak_gb": max(
                    (
                        float(row["peak_reserved_bytes"]) / (1024**3)
                        for row in model_memory
                    ),
                    default=None,
                ),
                "vram_peak_allocated_gb": max(
                    (
                        float(row["peak_allocated_bytes"]) / (1024**3)
                        for row in model_memory
                    ),
                    default=None,
                ),
                "device_used_peak_gb": max(
                    (
                        float(row["device_used_bytes"]) / (1024**3)
                        for row in model_memory
                    ),
                    default=None,
                ),
                "cost_questions": len(values),
                "repetitions": repeats,
            }
        )
    return summaries


def _new_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")


def run_benchmark(
    config: LLMBenchmarkConfig,
    selected_models: list[str] | None = None,
    selected_scenarios: list[str] | None = None,
    dry_run: bool = False,
) -> Path | None:
    model_names = selected_models or list(config.models)
    unknown_models = sorted(set(model_names) - set(config.models))
    if unknown_models:
        raise ValueError(f"modelos desconocidos: {', '.join(unknown_models)}")
    scenarios = selected_scenarios or list(config.scenarios)
    unknown_scenarios = sorted(set(scenarios) - set(SCENARIOS))
    if unknown_scenarios:
        raise ValueError(f"escenarios no habilitados: {', '.join(unknown_scenarios)}")
    if not model_names or not scenarios:
        raise ValueError("se debe seleccionar al menos un modelo y un escenario")

    inputs = {scenario: load_scenario_inputs(config, scenario) for scenario in scenarios}
    models = {name: config.models[name] for name in model_names}
    model_paths, model_parameters, prompts = _prepare_prompts(config, models, inputs)
    for scenario, scenario_input in inputs.items():
        _cost_questions(scenario_input.questions, config.cost_question_count)

    if dry_run:
        for name, model in models.items():
            print(
                f"{name}: {model.model_id} "
                f"({model_parameters[name] / 1_000_000_000:.3f}B parameters) "
                f"-> {model_paths[name]}"
            )
        for scenario, scenario_input in inputs.items():
            print(
                f"{scenario}: {len(scenario_input.questions)} preguntas, "
                f"embedding={scenario_input.embedding_model}, top-k={config.top_k}"
            )
        print(
            f"Prompts verificados: {len(prompts)}; "
            f"máximo de salida: {config.max_tokens} tokens"
        )
        return None

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["VLLM_ENABLE_V1_MULTIPROCESSING"] = "0"
    try:
        import torch
        import vllm
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
    except ImportError as exc:
        raise RuntimeError(
            "el benchmark requiere vLLM, PyTorch y Transformers en el intérprete "
            "seleccionado; usa vllm-env/bin/python"
        ) from exc
    if not torch.cuda.is_available():
        raise RuntimeError("el benchmark de LLMs requiere una GPU CUDA disponible")

    run_id = _new_run_id()
    run_dir = config.output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    embedding_config = load_embedding_config(config.embedding_config_path)
    selection_path = embedding_config.output_dir / "selection.json"
    manifest: dict[str, Any] = {
        "schema_version": RUN_SCHEMA_VERSION,
        "run_id": run_id,
        "status": "running",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "config_path": str(config.config_path),
        "config_sha256": sha256_file(config.config_path),
        "prompt_version": PROMPT_VERSION,
        "scenarios": scenarios,
        "models": {},
        "top_k": config.top_k,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "max_model_len": config.max_model_len,
        "gpu_memory_utilization": config.gpu_memory_utilization,
        "enforce_eager": config.enforce_eager,
        "seed": config.seed,
        "prefix_caching": False,
        "cost_question_count": config.cost_question_count,
        "cost_repeats": config.cost_repeats,
        "stack": "vLLM",
        "vllm_version": vllm.__version__,
        "torch_version": torch.__version__,
        "transformers_version": importlib.metadata.version("transformers"),
        "python_version": platform.python_version(),
        "gpu": torch.cuda.get_device_name(torch.cuda.current_device()),
        "gpu_total_memory_gb": torch.cuda.get_device_properties(
            torch.cuda.current_device()
        ).total_memory
        / (1024**3),
        "embedding_selection_path": str(selection_path),
        "embedding_selection_sha256": sha256_file(selection_path),
        "inputs": {
            scenario: {
                "embedding_model": scenario_input.embedding_model,
                "chunks_path": str(scenario_input.chunks_path),
                "chunks_sha256": sha256_file(scenario_input.chunks_path),
                "questions_path": str(scenario_input.questions_path),
                "questions_sha256": sha256_file(scenario_input.questions_path),
                "retrieval_path": str(scenario_input.retrieval_path),
                "retrieval_sha256": sha256_file(scenario_input.retrieval_path),
            }
            for scenario, scenario_input in inputs.items()
        },
        "completed_models": [],
    }
    manifest_path = run_dir / "manifest.json"
    _write_json(manifest_path, manifest)

    responses_path = run_dir / "responses.jsonl"
    scores_path = run_dir / "scores.jsonl"
    costs_path = run_dir / "cost_runs.jsonl"
    memory_path = run_dir / "memory.jsonl"
    cost_rows: list[dict[str, Any]] = []
    memory_rows: list[dict[str, Any]] = []
    cost_fields = (
        "model",
        "model_id",
        "size_category",
        "checkpoint_parameters_billions",
        "checkpoint_dtype",
        "quantization",
        "scenario",
        "stack",
        "ttft_seconds",
        "tokens_per_second",
        "latency_seconds",
        "vram_peak_gb",
        "vram_peak_allocated_gb",
        "device_used_peak_gb",
        "cost_questions",
        "repetitions",
    )

    with (
        _mark_failed_on_error(manifest, manifest_path),
        responses_path.open("w", encoding="utf-8") as responses_handle,
        scores_path.open("w", encoding="utf-8") as scores_handle,
        costs_path.open("w", encoding="utf-8") as costs_handle,
        memory_path.open("w", encoding="utf-8") as memory_handle,
    ):
        for model_name, model in models.items():
            model_path = model_paths[model_name]
            revision = (
                model_path.name
                if re.fullmatch(r"[0-9a-f]{40}", model_path.name)
                else None
            )
            manifest["models"][model_name] = {
                "model_id": model.model_id,
                "model_path": str(model_path),
                "model_revision": revision,
                "size_category": model.size_category,
                "checkpoint_parameters": model_parameters[model_name],
                "checkpoint_parameters_billions": (
                    model_parameters[model_name] / 1_000_000_000
                ),
                "checkpoint_dtype": model.checkpoint_dtype,
                "quantization": model.quantization,
                "prompt_format": model.prompt_format,
            }
            manifest["active_model"] = model_name
            _write_json(manifest_path, manifest)
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats(torch.cuda.current_device())
            tokenizer = AutoTokenizer.from_pretrained(
                model_path, local_files_only=True, trust_remote_code=False
            )
            engine = LLM(
                model=str(model_path),
                dtype="auto",
                trust_remote_code=False,
                max_model_len=config.max_model_len,
                gpu_memory_utilization=config.gpu_memory_utilization,
                enforce_eager=config.enforce_eager,
                tensor_parallel_size=1,
                enable_prefix_caching=False,
                disable_log_stats=False,
                seed=config.seed,
            )
            sampling_params = SamplingParams(
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                seed=config.seed,
            )
            memory = _memory_sample(torch, model_name, "model_loaded", None, None)
            memory_rows.append(memory)
            _append_jsonl(memory_handle, memory)

            first_scenario = scenarios[0]
            warmup_question = inputs[first_scenario].questions[0]
            warmup_prompt, warmup_prompt_tokens = prompts[
                (model_name, first_scenario, warmup_question["id"])
            ]
            warmup_generated = _generate_one(engine, sampling_params, warmup_prompt)
            memory = _memory_sample(
                torch, model_name, "warmup", first_scenario, warmup_question["id"]
            )
            memory_rows.append(memory)
            _append_jsonl(memory_handle, memory)
            warmup = _cost_record(
                run_id,
                model,
                model_parameters[model_name],
                revision,
                first_scenario,
                warmup_question,
                None,
                warmup_prompt,
                warmup_prompt_tokens,
                warmup_generated,
                "warmup",
                None,
                memory,
            )
            cost_rows.append(warmup)
            _append_jsonl(costs_handle, warmup)

            for scenario in scenarios:
                scenario_input = inputs[scenario]
                response_by_question: dict[str, dict[str, Any]] = {}
                for question in scenario_input.questions:
                    prompt, prompt_tokens = prompts[
                        (model_name, scenario, question["id"])
                    ]
                    generated = _generate_one(engine, sampling_params, prompt)
                    response = _response_record(
                        run_id,
                        model,
                        model_parameters[model_name],
                        revision,
                        scenario,
                        scenario_input,
                        question,
                        prompt,
                        prompt_tokens,
                        generated,
                        config,
                    )
                    response_by_question[question["id"]] = response
                    _append_jsonl(responses_handle, response)
                    _append_jsonl(scores_handle, _score_template(response))
                    memory = _memory_sample(
                        torch, model_name, "quality", scenario, question["id"]
                    )
                    memory_rows.append(memory)
                    _append_jsonl(memory_handle, memory)

                for question in _cost_questions(
                    scenario_input.questions, config.cost_question_count
                ):
                    prompt, prompt_tokens = prompts[
                        (model_name, scenario, question["id"])
                    ]
                    response = response_by_question[question["id"]]
                    for repetition in range(1, config.cost_repeats + 1):
                        generated = _generate_one(engine, sampling_params, prompt)
                        memory = _memory_sample(
                            torch,
                            model_name,
                            "cost",
                            scenario,
                            question["id"],
                        )
                        memory_rows.append(memory)
                        _append_jsonl(memory_handle, memory)
                        cost_row = _cost_record(
                            run_id,
                            model,
                            model_parameters[model_name],
                            revision,
                            scenario,
                            question,
                            response["response_id"],
                            prompt,
                            prompt_tokens,
                            generated,
                            "measurement",
                            repetition,
                            memory,
                        )
                        cost_rows.append(cost_row)
                        _append_jsonl(costs_handle, cost_row)

            del engine
            del tokenizer
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
            manifest["completed_models"].append(model_name)
            manifest.pop("active_model", None)
            _write_json(manifest_path, manifest)
            gc.collect()

    with _mark_failed_on_error(manifest, manifest_path):
        cost_summary = _cost_summary(cost_rows, memory_rows, config.cost_repeats)
        _write_csv(run_dir / "cost_summary.csv", cost_fields, cost_summary)
        manifest["status"] = "completed"
        manifest["completed_at"] = datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        )
        _write_json(manifest_path, manifest)
    return run_dir


def summarize_scores(run_dir: Path) -> tuple[Path, Path]:
    run_dir = run_dir.resolve()
    manifest = _load_json(run_dir / "manifest.json")
    if manifest.get("status") != "completed":
        raise ValueError(f"{run_dir}: la ejecución no está completa")
    responses = _load_jsonl(run_dir / "responses.jsonl")
    scores = _load_jsonl(run_dir / "scores.jsonl")
    response_by_id = _check_ids(responses, "response_id", run_dir / "responses.jsonl")
    score_by_id = _check_ids(scores, "response_id", run_dir / "scores.jsonl")
    if set(response_by_id) != set(score_by_id):
        raise ValueError("scores.jsonl debe tener exactamente una nota por respuesta")

    grouped: dict[tuple[str, str], list[tuple[dict[str, Any], dict[str, Any]]]] = {}
    for response_id, response in response_by_id.items():
        score = score_by_id[response_id]
        if (
            score.get("model") != response.get("model")
            or score.get("scenario") != response.get("scenario")
            or score.get("question_id") != response.get("question_id")
        ):
            raise ValueError(f"{response_id}: los datos de score no corresponden")
        correctness = score.get("correctness_score")
        if type(correctness) is not int or correctness not in (0, 1, 2):
            raise ValueError(f"{response_id}: correctness_score debe ser 0, 1 o 2")
        for field in ("faithful", "abstention", "format_language"):
            if type(score.get(field)) is not bool:
                raise ValueError(f"{response_id}: {field} debe ser true o false")
        key = (response["model"], response["scenario"])
        grouped.setdefault(key, []).append((response, score))

    rows = []
    for (model, scenario), pairs in sorted(grouped.items()):
        unanswerable = [
            score
            for response, score in pairs
            if response["question_type"] == "no_answer"
        ]
        answerable = [
            score
            for response, score in pairs
            if response["question_type"] != "no_answer"
        ]
        if len(unanswerable) != 3:
            raise ValueError(
                f"{model}/{scenario}: se esperaban 3 preguntas sin respuesta; "
                f"hay {len(unanswerable)}"
            )
        rows.append(
            {
                "model": model,
                "model_id": pairs[0][0]["model_id"],
                "size_category": pairs[0][0]["size_category"],
                "checkpoint_parameters_billions": pairs[0][0][
                    "checkpoint_parameters_billions"
                ],
                "checkpoint_dtype": pairs[0][0]["checkpoint_dtype"],
                "quantization": pairs[0][0]["quantization"],
                "scenario": scenario,
                "responses": len(pairs),
                "correctness_mean_0_2": statistics.mean(
                    score["correctness_score"] for _, score in pairs
                ),
                "faithful_percent": 100
                * sum(score["faithful"] for _, score in pairs)
                / len(pairs),
                "correct_abstentions_of_3": sum(
                    score["abstention"] for score in unanswerable
                ),
                "false_abstentions": sum(
                    score["abstention"] for score in answerable
                ),
                "format_language_percent": 100
                * sum(score["format_language"] for _, score in pairs)
                / len(pairs),
            }
        )

    quality_fields = (
        "model",
        "model_id",
        "size_category",
        "checkpoint_parameters_billions",
        "checkpoint_dtype",
        "quantization",
        "scenario",
        "responses",
        "correctness_mean_0_2",
        "faithful_percent",
        "correct_abstentions_of_3",
        "false_abstentions",
        "format_language_percent",
    )
    quality_path = run_dir / "quality_summary.csv"
    _write_csv(quality_path, quality_fields, rows)

    cost_path = run_dir / "cost_summary.csv"
    cost_rows = _load_csv(cost_path) if cost_path.is_file() else []
    cost_by_key = {(row["model"], row["scenario"]): row for row in cost_rows}
    combined_fields = quality_fields + (
        "stack",
        "ttft_seconds",
        "tokens_per_second",
        "latency_seconds",
        "vram_peak_gb",
        "vram_peak_allocated_gb",
        "device_used_peak_gb",
    )
    combined = []
    for row in rows:
        cost = cost_by_key.get((row["model"], row["scenario"]), {})
        combined.append({**row, **cost})
    combined_path = run_dir / "summary.csv"
    _write_csv(combined_path, combined_fields, combined)
    return quality_path, combined_path


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))
