from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class ProviderResult:
    raw: Dict[str, Any]
    normalized: Dict[str, Any]

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
