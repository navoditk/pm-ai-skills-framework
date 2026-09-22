from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ProviderResult:
    raw: dict[str, Any]
    normalized: dict[str, Any]

class EvaluationProvider(ABC):
    @abstractmethod
    def validate(self, skill_path: str) -> ProviderResult:
        ...

    @abstractmethod
    def similarity(self, skill_path: str, catalog_path: str) -> ProviderResult:
        ...

    @abstractmethod
    def evaluate(self, skill_path: str, profile: str) -> ProviderResult:
        ...
