import unittest
from src.db import db, login, add_carrinho, checkout

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