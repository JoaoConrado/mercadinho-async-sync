import unittest
import asyncio
<<<<<<< HEAD
from unittest.mock import patch, AsyncMock
=======
from unittest.mock import patch
>>>>>>> a75c6c1689970f13d304862333a3ab4d1fc5a1b8
from src.db import db, login, add_carrinho, checkout
from src.payment_worker import process_payment

class TestMercadinhoAsyncSync(unittest.TestCase):
    def setUp(self):
        # Limpa/Reseta o mock do banco de dados antes de executar cada teste
        db["carrinho"] = []
        db["pedidos"] = {}

    def test_login_retorna_token_quando_sucesso(self):
        self.assertEqual(login("mestre", "123"), "token_jwt_123")

    def test_login_retorna_acesso_negado_quando_falha(self):
        self.assertEqual(login("hacker", "senha_ruim"), "Acesso Negado")
        self.assertEqual(login("mestre", "senha_ruim"), "Acesso Negado")

    def test_add_carrinho_atualiza_db(self):
        msg = add_carrinho("Café")
        self.assertEqual(msg, "Café adicionado!")
        self.assertIn("Café", db["carrinho"])

    def test_checkout_atualiza_status_do_pedido(self):
        add_carrinho("Café")
        order_id = checkout()
        self.assertTrue(order_id.startswith("PEDIDO-"))
        self.assertEqual(db["pedidos"][order_id]["status"], "processando_pagamento")
<<<<<<< HEAD

    @patch("src.payment_worker.save_db")
    @patch("src.payment_worker.asyncio.sleep", new_callable=AsyncMock)
    @patch('random.uniform')
    def test_process_payment_sucesso(self, mock_uniform, _mock_sleep, _mock_save):
        """Com latência ≤ 1,5 s, não há TimeoutError: primeira tentativa conclui e o pedido fica pago_com_sucesso."""
        mock_uniform.return_value = 1.0
        db["pedidos"]["PEDIDO-TESTE"] = {"itens": [], "status": "pendente"}
        
=======
    @patch('random.uniform')
    def test_process_payment_sucesso(self, mock_uniform):
        # Força o random.uniform a retornar uma latência baixa (1.0s <= 1.5s limite)
        mock_uniform.return_value = 1.0
        db["pedidos"]["PEDIDO-TESTE"] = {"itens": [], "status": "pendente"}
>>>>>>> a75c6c1689970f13d304862333a3ab4d1fc5a1b8
        sucesso = asyncio.run(process_payment("PEDIDO-TESTE"))
        
        self.assertTrue(sucesso)
        self.assertEqual(db["pedidos"]["PEDIDO-TESTE"]["status"], "pago_com_sucesso")
<<<<<<< HEAD
        self.assertEqual(mock_uniform.call_count, 1)

    @patch("src.payment_worker.save_db")
    @patch("src.payment_worker.asyncio.sleep", new_callable=AsyncMock)
    @patch('random.uniform')
    def test_process_payment_sucesso_apos_retentativas(self, mock_uniform, _mock_sleep, _mock_save):
        """Retry em ação: 1ª e 2ª tentativas dão timeout (> 1,5s). Na 3ª tentativa, sucesso."""
        mock_uniform.side_effect = [2.0, 2.0, 1.0]
        db["pedidos"]["PEDIDO-TESTE"] = {"itens": [], "status": "pendente"}
        
=======

    @patch('random.uniform')
    def test_process_payment_sucesso_apos_retentativas(self, mock_uniform):
        # Usamos side_effect para simular latências diferentes em cada chamada do loop:
        # 1ª tentativa: 2.0s (Falha - Timeout)
        # 2ª tentativa: 2.0s (Falha - Timeout)
        # 3ª tentativa: 1.0s (Sucesso)
        mock_uniform.side_effect = [2.0, 2.0, 1.0]
        db["pedidos"]["PEDIDO-TESTE"] = {"itens": [], "status": "pendente"}
>>>>>>> a75c6c1689970f13d304862333a3ab4d1fc5a1b8
        sucesso = asyncio.run(process_payment("PEDIDO-TESTE"))
        
        self.assertTrue(sucesso)
        self.assertEqual(db["pedidos"]["PEDIDO-TESTE"]["status"], "pago_com_sucesso")
        self.assertEqual(mock_uniform.call_count, 3)

<<<<<<< HEAD
    @patch("src.payment_worker.save_db")
    @patch("src.payment_worker.asyncio.sleep", new_callable=AsyncMock)
    @patch('random.uniform')
    def test_process_payment_falha_com_fallback(self, mock_uniform, _mock_sleep, _mock_save):
        """Fallback: todas as tentativas excedem o limite. Após 3 timeouts, o sistema define falha_pagamento."""
        mock_uniform.return_value = 2.0
        db["pedidos"]["PEDIDO-TESTE"] = {"itens": [], "status": "pendente"}
        
        sucesso = asyncio.run(process_payment("PEDIDO-TESTE"))
        
        self.assertFalse(sucesso)
        self.assertEqual(db["pedidos"]["PEDIDO-TESTE"]["status"], "falha_pagamento")
        self.assertEqual(mock_uniform.call_count, 3)
=======
    @patch('random.uniform')
    def test_process_payment_falha_com_fallback(self, mock_uniform):
        # Força o random.uniform a retornar latência alta constatemente forçando o Timeout (2.0s > 1.5s limite)
        mock_uniform.return_value = 2.0
        db["pedidos"]["PEDIDO-TESTE"] = {"itens": [], "status": "pendente"}
        sucesso = asyncio.run(process_payment("PEDIDO-TESTE"))
        
        # Deve retornar False esgotando as 3 tentativas e ativando fallback
        self.assertFalse(sucesso)
        self.assertEqual(db["pedidos"]["PEDIDO-TESTE"]["status"], "falha_pagamento")
>>>>>>> a75c6c1689970f13d304862333a3ab4d1fc5a1b8
