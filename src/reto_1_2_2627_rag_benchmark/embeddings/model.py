"""Adaptadores Hugging Face para los modelos locales del benchmark."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


class LocalEmbeddingModel:
    def __init__(self, config, device: str) -> None:
        try:
            import torch
            from transformers import AutoModel, AutoProcessor, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError(
                "Faltan dependencias de embeddings. Instala el extra "
                "'uv sync --extra embeddings'."
            ) from exc

        self.torch = torch
        self.config = config
        self.device = torch.device(
            ("cuda" if torch.cuda.is_available() else "cpu")
            if device == "auto"
            else device
        )
        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError(f"se solicitó {self.device}, pero CUDA no está disponible")

        common = {
            "local_files_only": True,
            "trust_remote_code": False,
        }
        try:
            if config.input_mode == "chat_template":
                self.processor = AutoProcessor.from_pretrained(config.model_id, **common)
                self.tokenizer = None
            else:
                self.tokenizer = AutoTokenizer.from_pretrained(config.model_id, **common)
                self.processor = None
            self.model = AutoModel.from_pretrained(
                config.model_id, dtype="auto", **common
            ).to(self.device)
        except (OSError, ValueError) as exc:
            raise RuntimeError(
                f"no se pudo cargar el modelo local '{config.model_id}' "
                f"(solo caché local; no se intentó descargar): {exc}"
            ) from exc
        self.model.eval()
        self.model_path = self._model_directory()
        self.model_revision = (
            self.model_path.name
            if self.model_path is not None and len(self.model_path.name) == 40
            else None
        )
        self.pooling = self._pooling_mode()
        self.max_length = self._max_length()
        self.model_dtype = str(next(self.model.parameters()).dtype).removeprefix(
            "torch."
        )
        self.torch_version = torch.__version__
        self.memory_trace: list[dict] = []

    def _model_directory(self) -> Path | None:
        path = Path(self.config.model_id).expanduser()
        if path.is_dir():
            return path
        try:
            from huggingface_hub import try_to_load_from_cache

            config_path = try_to_load_from_cache(
                self.config.model_id, "config.json", repo_type="model"
            )
        except (ImportError, OSError, ValueError):
            return None
        return Path(config_path).parent if isinstance(config_path, str) else None

    def _pooling_mode(self) -> str:
        if self.config.pooling != "auto":
            return self.config.pooling
        directory = self._model_directory()
        if directory is None:
            raise RuntimeError(
                f"{self.config.name}: pooling='auto' necesita metadatos locales "
                "1_Pooling/config.json o una configuración explícita"
            )
        pooling_path = directory / "1_Pooling/config.json"
        if pooling_path.is_file():
            settings = json.loads(pooling_path.read_text(encoding="utf-8"))
            choices = [
                mode
                for mode, key in (
                    ("cls", "pooling_mode_cls_token"),
                    ("mean", "pooling_mode_mean_tokens"),
                )
                if settings.get(key, False)
            ]
            if len(choices) == 1:
                return choices[0]
            raise RuntimeError(
                f"{self.config.name}: pooling no soportado o ambiguo en {pooling_path}"
            )
        model_config = self.model.config
        if getattr(model_config, "pooling", None) == "avg":
            return "mean"
        raise RuntimeError(
            f"{self.config.name}: no se detectó una estrategia de pooling conocida"
        )

    def _max_length(self) -> int:
        if self.config.max_length:
            return self.config.max_length
        if self.tokenizer is not None:
            limit = self.tokenizer.model_max_length
            if isinstance(limit, int) and limit < 1_000_000:
                return limit
        return int(
            getattr(
                getattr(self.model.config, "text_config", self.model.config),
                "max_position_embeddings",
                8192,
            )
        )

    def _prepare_batch(self, texts: list[str], task_prefix: str) -> dict[str, Any]:
        if self.config.input_mode == "chat_template":
            conversations = [
                [
                    {"role": "system", "content": task_prefix},
                    {"role": "user", "content": [{"type": "text", "text": text}]},
                ]
                for text in texts
            ]
            batch = self.processor.apply_chat_template(
                conversations,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
                processor_kwargs={"padding": True, "truncation": False},
            )
        else:
            batch = self.tokenizer(
                [f"{task_prefix}{text}" for text in texts],
                padding=True,
                truncation=False,
                return_tensors="pt",
            )
        if batch["input_ids"].shape[1] > self.max_length:
            raise ValueError(
                f"{self.config.name}: entrada de {batch['input_ids'].shape[1]} tokens "
                f"excede max_length={self.max_length}; no se truncará silenciosamente"
            )
        return {
            key: value.to(self.device)
            for key, value in batch.items()
            if hasattr(value, "to")
        }

    def encode(
        self, texts: list[str], task_prefix: str, batch_size: int, phase: str
    ) -> Any:
        torch = self.torch
        result = []
        with torch.inference_mode():
            for batch_index, start in enumerate(range(0, len(texts), batch_size), 1):
                batch = self._prepare_batch(
                    texts[start : start + batch_size], task_prefix
                )
                hidden = self.model(**batch).last_hidden_state
                mask = batch["attention_mask"].unsqueeze(-1).to(hidden.dtype)
                if self.pooling == "cls":
                    pooled = hidden[:, 0]
                else:
                    pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
                pooled = torch.nn.functional.normalize(pooled.float(), p=2, dim=1)
                result.append(pooled.cpu())
                self._sample_memory(phase, batch_index)
        return torch.cat(result, dim=0).numpy()

    def start_memory_measurement(self) -> None:
        self.memory_trace = []
        if self.device.type == "cuda":
            self.torch.cuda.reset_peak_memory_stats(self.device)
            self._sample_memory("model_loaded", 0)

    def _sample_memory(self, phase: str, batch_index: int) -> None:
        if self.device.type != "cuda":
            return
        self.memory_trace.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                "phase": phase,
                "batch": batch_index,
                "allocated_bytes": self.torch.cuda.memory_allocated(self.device),
                "reserved_bytes": self.torch.cuda.memory_reserved(self.device),
            }
        )

    def peak_memory_gb(self) -> float | None:
        if self.device.type != "cuda":
            return None
        return self.torch.cuda.max_memory_allocated(self.device) / (1024**3)

    def peak_reserved_memory_gb(self) -> float | None:
        if self.device.type != "cuda":
            return None
        return self.torch.cuda.max_memory_reserved(self.device) / (1024**3)
