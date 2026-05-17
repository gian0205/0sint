"""Audit logging for LGPD/forensic accountability.

Every CPF lookup is recorded with operator, purpose, case_id, timestamp,
and masked CPF. Raw CPF is never written to the audit log.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .cpf import mask
from .models import LookupRequest


_LOGGER_NAME = "0sint.audit"


def _build_logger() -> logging.Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    log_path = Path("audit.log")
    handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=10, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def record_lookup(
    req: LookupRequest, operator: str, sources_consulted: list[str], *, cached: bool
) -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": "cpf_lookup",
        "cpf_masked": mask(req.cpf),
        "purpose": req.purpose.value,
        "operator": operator,
        "case_id": req.case_id,
        "sources": sources_consulted,
        "cached": cached,
    }
    _build_logger().info(json.dumps(entry, ensure_ascii=False))
