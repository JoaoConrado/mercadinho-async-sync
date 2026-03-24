#!/usr/bin/env python3
"""
Script de demonstração para aula / banca: executa testes automatizados que
evidenciam **timeout**, **retry (até 3 tentativas)** e **fallback** no worker
de pagamento.

Uso (na raiz do repositório):

    python scripts/demo_resiliencia.py

Ou, equivalente:

    python -m unittest tests.test_resiliencia -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main() -> int:
    root = _project_root()
    sys.path.insert(0, str(root))

    banner = """
╔══════════════════════════════════════════════════════════════════╗
║  Mercadinho 24h — Demonstração: Timeout · Retry · Fallback      ║
╠══════════════════════════════════════════════════════════════════╣
║  Regra no código (payment_worker.process_payment):              ║
║    • Latência simulada > 1,5 s  → TimeoutError (timeout)          ║
║    • Até 3 tentativas no laço   → retry                           ║
║    • Após 3 falhas              → status falha_pagamento         ║
║      (fallback gracioso)                                        ║
╚══════════════════════════════════════════════════════════════════╝
"""
    print(banner, flush=True)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName("tests.test_resiliencia")

    runner = unittest.TextTestRunner(verbosity=2, buffer=False)
    result = runner.run(suite)

    print(flush=True)
    if result.wasSuccessful():
        print("Resultado: todos os cenários de resiliência passaram ✓", flush=True)
        print(
            "Inclua este output (ou o comando unittest) no relatório da disciplina.",
            flush=True,
        )
        return 0

    print(
        "Resultado: um ou mais testes falharam — revise o worker ou os mocks.",
        flush=True,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
