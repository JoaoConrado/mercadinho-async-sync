"""
Demonstração acadêmica: Timeout, Retry e Fallback
==================================================

Implementação de referência: ``src/payment_worker.process_payment``....

* **Timeout** — A latência simulada do gateway vem de ``random.uniform(0.5, 2.0)``.
  Se for **maior que 1,5 s**, o código levanta ``TimeoutError`` (gateway lento).

* **Retry** — O laço ``for attempt in range(3)`` tenta de novo após cada timeout,
  até **3 tentativas** no total.

* **Fallback** — Se as 3 tentativas falharem, o pedido não fica indefinido: o status
  passa a **``falha_pagamento``** e o fluxo encerra de forma controlada.

Os testes abaixo usam ``unittest.mock`` para fixar latências e ``AsyncMock`` em
``asyncio.sleep`` para não esperar tempo real — adequado para CI e para rodar a
demonstração na aula em segundos.
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from src.db import db
from src.payment_worker import process_payment


class TestResilienciaGatewayPagamento(unittest.TestCase):
    """Cenários que evidenciam timeout, retentativas e fallback."""

    def setUp(self):
        db["carrinho"] = []
        db["pedidos"] = {}

    @patch("src.payment_worker.save_db")
    @patch("src.payment_worker.asyncio.sleep", new_callable=AsyncMock)
    @patch("random.uniform")
    def test_timeout_nao_dispara_com_latencia_abaixo_do_limite(
        self, mock_uniform, _mock_sleep, _mock_save
    ):
        """
        Com latência **≤ 1,5 s**, não há ``TimeoutError``: primeira tentativa
        conclui e o pedido fica ``pago_com_sucesso``.
        """
        mock_uniform.return_value = 1.0
        db["pedidos"]["PEDIDO-DEMO"] = {"itens": ["Item"], "status": "processando_pagamento"}

        ok = asyncio.run(process_payment("PEDIDO-DEMO"))

        self.assertTrue(ok)
        self.assertEqual(db["pedidos"]["PEDIDO-DEMO"]["status"], "pago_com_sucesso")
        self.assertEqual(mock_uniform.call_count, 1)

    @patch("src.payment_worker.save_db")
    @patch("src.payment_worker.asyncio.sleep", new_callable=AsyncMock)
    @patch("random.uniform")
    def test_retry_duas_falhas_timeout_terceira_tentativa_sucesso(
        self, mock_uniform, _mock_sleep, _mock_save
    ):
        """
        **Retry em ação:** 1ª e 2ª tentativas simulam latência 2,0 s (> 1,5 s) → timeout.
        Na **3ª tentativa** a latência é 1,0 s → sucesso. Espera-se **3 chamadas**
        a ``random.uniform`` e status final ``pago_com_sucesso``.
        """
        mock_uniform.side_effect = [2.0, 2.0, 1.0]
        db["pedidos"]["PEDIDO-DEMO"] = {"itens": [], "status": "processando_pagamento"}

        ok = asyncio.run(process_payment("PEDIDO-DEMO"))

        self.assertTrue(ok)
        self.assertEqual(db["pedidos"]["PEDIDO-DEMO"]["status"], "pago_com_sucesso")
        self.assertEqual(mock_uniform.call_count, 3)

    @patch("src.payment_worker.save_db")
    @patch("src.payment_worker.asyncio.sleep", new_callable=AsyncMock)
    @patch("random.uniform")
    def test_fallback_apos_tres_timeouts_consecutivos(
        self, mock_uniform, _mock_sleep, _mock_save
    ):
        """
        **Fallback:** todas as tentativas excedem o limite (2,0 s). Após **3 timeouts**,
        o sistema define ``falha_pagamento``, retorna ``False`` e não lança exceção
        não tratada — comportamento gracioso.
        """
        mock_uniform.return_value = 2.0
        db["pedidos"]["PEDIDO-DEMO"] = {"itens": [], "status": "processando_pagamento"}

        ok = asyncio.run(process_payment("PEDIDO-DEMO"))

        self.assertFalse(ok)
        self.assertEqual(db["pedidos"]["PEDIDO-DEMO"]["status"], "falha_pagamento")
        self.assertEqual(mock_uniform.call_count, 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
