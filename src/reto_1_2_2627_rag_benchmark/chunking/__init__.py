"""Troceado del corpus para el benchmark RAG."""

from .chunker import chunk_document
from .config import ScenarioConfig, Settings, load_settings

__all__ = ["chunk_document", "load_settings", "ScenarioConfig", "Settings"]
