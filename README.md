# Mercadinho 24h - Async & Sync

Este projeto implementa um emulador de e-commerce fictício de alta escalabilidade, operando 24h. O objetivo é puramente focado em arquitetura Python puro, demonstrando a interação e orquestração entre rotinas síncronas e assíncronas utilizando dados mocados em memória.

## 📂 Estrutura de Pastas

* `src/`: Contém todo o código-fonte principal da aplicação.
  * `db.py`: Concentra o banco de dados mocado (`dict`) e todas as operações síncronas resolvidas via `lambda`.
  * `payment_worker.py`: Contém a regra de negócio do Gateway de Pagamento assíncrono, aplicando resiliência (Timeout, Retry de 3 tentativas e Fallback).
  * `main.py`: O ponto de entrada que une as pontas. Simula o fluxo de um usuário realizando compras até a aprovação via Fila (`asyncio.Queue`).
* `tests/`: Contém todos os testes automatizados unitários usando o framework nativo `unittest`.

## 🧠 Por que da escolha Síncrona vs Assíncrona?

A escalabilidade de um sistema depende de como o *Event Loop* é gerenciado.

**1. Processos Síncronos (Instantâneos)**
O *Login*, *Adição de itens ao Carrinho* e o *Gatilho de Checkout* não envolvem gargalos de I/O de rede com terceiros. Eles apenas modificam dados primitivos na memória. Por retornarem na casa dos microssegundos, o uso de abordagens síncronas minimalistas (via funções `lambda`) é muito mais performático e direto.

**2. Processos Assíncronos (Gargalos / Rede)**
O *Pagamento* simula a chamada para um Gateway de Cartão de Crédito externo. As redes são imprevisíveis (podem levar 1 a 2 segundos). Se essa chamada fosse síncrona, todo o "servidor" (o Event Loop principal) ficaria paralisado impedindo que *outros* usuários fizessem login enquanto a transação de *um único* usuário não finalizasse. 
Utilizando o padrão de Fila (`asyncio.Queue`) e *Task Background Workers*, assim que o pedido é gerado no checkout, ele é enfileirado para pagamento; a interface é imediatamente liberada, garantindo disponibilidade 24h sob alta carga de acessos paralelos.

## 🛡️ Resiliência
O Worker Assíncrono está blindado. Há um tempo limite simulado (`Timeout`) que levanta uma exceção se a latência demorar muito. Quando a exceção ocorre, um laço de `Retry` tenta reenviar a transação até 3 vezes. Em último caso, ele não quebra o sistema; em vez disso, atualiza o status de forma graciosa ativando o `Fallback` (`falha_pagamento`).

## 🚀 Como Executar

**Pré-requisitos (Apenas para a Interface Web):**
```bash
pip install -r requirements.txt
```

**Para rodar a Interface Web (FastAPI):**
```bash
uvicorn src.api:app --reload
```
*Acesse `http://localhost:8000` em seu navegador.*

**Para rodar a simulação do Mercadinho:**
```bash
python -m src.main
```

**Para rodar os testes automatizados:**
```bash
python -m unittest discover -s tests -v
```