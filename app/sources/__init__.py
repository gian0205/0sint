"""Registry of OSINT source adapters.

To add a new source, implement `Source` in a new module and register it here.
"""
from __future__ import annotations

from .base import Source
from .cadunico import CadUnicoSource
from .links import ManualLinksSource
from .receita_federal import ReceitaFederalSource
from .situacao_cadastral import SituacaoCadastralSource
from .trt3 import TRT3Source
from .validator import ValidatorSource


REGISTRY: dict[str, Source] = {
    s.name: s
    for s in [
        ValidatorSource(),
        ManualLinksSource(),
        ReceitaFederalSource(),
        SituacaoCadastralSource(),
        CadUnicoSource(),
        TRT3Source(),
    ]
}


def get_sources(names: list[str] | None) -> list[Source]:
    if not names:
        return list(REGISTRY.values())
    return [REGISTRY[n] for n in names if n in REGISTRY]


__all__ = ["REGISTRY", "Source", "get_sources"]
