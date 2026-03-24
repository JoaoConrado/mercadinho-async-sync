# mercadinho-async-py

Emulador fictício de um e-commerce 24h focado em alta escalabilidade, separando rotinas síncronas de assíncronas utilizando apenas Python puro (sem dependências externas).

## 1. Stack Tecnológica e Padrões
* **Linguagem:** Python Puro (Built-in libraries: `asyncio`, `time`, `random`).
* **Estilo de Código:** Minimalista, com preferência por one-liners e lambdas em processos síncronos simples.
* **Mensageria Fictícia:** Fila em memória usando `asyncio.Queue`.
* **Banco de Dados:** Estruturas em memória (`dict` e `list`).

## 2. Comportamento Síncrono vs Assíncrono

| Ação | Tipo de Fluxo | Resolução | Retorno Simulado |
| :--- | :--- | :--- | :--- |
| **Login** | Síncrono (RPC) | Função `lambda` | Token JWT imediato. |
| **Add Carrinho** | Síncrono (RPC) | Função `lambda` | Atualização do dicionário em tempo real. |
| **Checkout** | Síncrono (RPC) | Função `lambda` | Gera ID do pedido e congela o carrinho. |
| **Pagamento** | **Assíncrono** | `asyncio.Queue` | Enfileira a tarefa no event loop e libera a tela. |
| **Worker** | **Assíncrono** | `asyncio.Task` | Roda em background simulando o Gateway de Cartão. |

## 3. Resiliência do Sistema (Worker de Pagamento)
O processamento da fila de pagamentos implementa os seguintes padrões de segurança em código:
* **Timeout:** Simulado com `random.uniform()`. Se a latência gerada passar do limite estipulado (ex: 1.5s), a transação levanta um erro.
* **Retry:** Laço de repetição (`for`) configurado para 3 tentativas caso ocorra o erro de timeout.
* **Fallback:** Se o laço esgotar as tentativas sem sucesso, o sistema assume a contingência alterando o status do pedido para `falha_pagamento` e encerra o processamento.

## 4. Estrutura de Dados e Mock (One-liners)

```python
# Estado global do Banco de Dados
db = {
    "carrinho": [], 
    "status_pedido": "pendente"
}

# Funções Síncronas
login = lambda u, p: "token_jwt_123" if u == "mestre" else "Acesso Negado"
add_carrinho = lambda item: db["carrinho"].append(item) or f"{item} adicionado!"
checkout = lambda: db.update({"status_pedido": "processando_pagamento"}) or "Pedido #999 gerado."