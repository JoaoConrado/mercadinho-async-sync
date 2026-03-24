import unittest
import asyncio
from unittest.mock import patch
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

    @patch('random.uniform')
    def test_process_payment_sucesso(self, mock_uniform):
        # Força o random.uniform a retornar uma latência baixa (1.0s <= 1.5s limite)
        mock_uniform.return_value = 1.0
        db["pedidos"]["PEDIDO-TESTE"] = {"itens": [], "status": "pendente"}
        sucesso = asyncio.run(process_payment("PEDIDO-TESTE"))
        
        self.assertTrue(sucesso)
        self.assertEqual(db["pedidos"]["PEDIDO-TESTE"]["status"], "pago_com_sucesso")

    @patch('random.uniform')
    def test_process_payment_sucesso_apos_retentativas(self, mock_uniform):
        # Usamos side_effect para simular latências diferentes em cada chamada do loop:
        # 1ª tentativa: 2.0s (Falha - Timeout)
        # 2ª tentativa: 2.0s (Falha - Timeout)
        # 3ª tentativa: 1.0s (Sucesso)
        mock_uniform.side_effect = [2.0, 2.0, 1.0]
        db["pedidos"]["PEDIDO-TESTE"] = {"itens": [], "status": "pendente"}
        sucesso = asyncio.run(process_payment("PEDIDO-TESTE"))
        
        self.assertTrue(sucesso)
        self.assertEqual(db["pedidos"]["PEDIDO-TESTE"]["status"], "pago_com_sucesso")
        self.assertEqual(mock_uniform.call_count, 3)

    @patch('random.uniform')
    def test_process_payment_falha_com_fallback(self, mock_uniform):
        # Força o random.uniform a retornar latência alta constatemente forçando o Timeout (2.0s > 1.5s limite)
        mock_uniform.return_value = 2.0
        db["pedidos"]["PEDIDO-TESTE"] = {"itens": [], "status": "pendente"}
        sucesso = asyncio.run(process_payment("PEDIDO-TESTE"))
        
        # Deve retornar False esgotando as 3 tentativas e ativando fallback
        self.assertFalse(sucesso)
        self.assertEqual(db["pedidos"]["PEDIDO-TESTE"]["status"], "falha_pagamento")