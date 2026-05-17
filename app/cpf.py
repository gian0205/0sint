"""CPF utilities: normalization, validation, formatting."""
from __future__ import annotations

import random
import re


_DIGITS_RE = re.compile(r"\D+")


def normalize(cpf: str) -> str:
    return _DIGITS_RE.sub("", cpf or "")


def format_cpf(cpf: str) -> str:
    c = normalize(cpf)
    if len(c) != 11:
        return cpf
    return f"{c[0:3]}.{c[3:6]}.{c[6:9]}-{c[9:11]}"


def mask(cpf: str) -> str:
    c = normalize(cpf)
    if len(c) != 11:
        return cpf
    return f"***.{c[3:6]}.{c[6:9]}-**"


def _check_digit(digits: str, weights: range) -> int:
    total = sum(int(d) * w for d, w in zip(digits, weights))
    rem = total % 11
    return 0 if rem < 2 else 11 - rem


def is_valid(cpf: str) -> bool:
    c = normalize(cpf)
    if len(c) != 11 or c == c[0] * 11:
        return False
    d1 = _check_digit(c[:9], range(10, 1, -1))
    d2 = _check_digit(c[:10], range(11, 1, -1))
    return c[9] == str(d1) and c[10] == str(d2)


def generate(region_digit: int | None = None) -> str:
    """Generate a syntactically valid CPF for testing.

    Optional `region_digit` (0-9) forces the 9th digit (fiscal region selector).
    Returned value is formatted (xxx.xxx.xxx-xx).
    """
    base = [random.randint(0, 9) for _ in range(8)]
    base.append(region_digit if region_digit is not None else random.randint(0, 9))
    base_str = "".join(str(d) for d in base)
    d1 = _check_digit(base_str, range(10, 1, -1))
    d2 = _check_digit(base_str + str(d1), range(11, 1, -1))
    return format_cpf(base_str + str(d1) + str(d2))


def region(cpf: str) -> str | None:
    """Return the fiscal region (FR/UF group) based on the 9th digit."""
    c = normalize(cpf)
    if len(c) != 11:
        return None
    regions = {
        "1": "DF, GO, MS, MT, TO",
        "2": "AC, AM, AP, PA, RO, RR",
        "3": "CE, MA, PI",
        "4": "AL, PB, PE, RN",
        "5": "BA, SE",
        "6": "MG",
        "7": "ES, RJ",
        "8": "SP",
        "9": "PR, SC",
        "0": "RS",
    }
    return regions.get(c[8])
