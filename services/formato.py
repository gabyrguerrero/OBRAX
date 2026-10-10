"""Formato de números y moneda (estilo colombiano: 1.234,5)."""


def fmt(n: float, dec: int = 1) -> str:
    s = f"{n:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def dinero(n: float) -> str:
    return "$" + fmt(n, 0)
