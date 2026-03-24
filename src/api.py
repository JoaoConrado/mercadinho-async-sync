import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.db import db, login, add_carrinho, checkout, clear_carrinho
from src.payment_worker import payment_worker

# Fila global da aplicação Web
fila_pagamentos = asyncio.Queue()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Inicia o Worker de Pagamento em background
    worker_task = asyncio.create_task(payment_worker(fila_pagamentos))
    yield
    # Shutdown: Cancela a tarefa graciosa ao desligar o servidor
    worker_task.cancel()

app = FastAPI(
    title="Mercadinho 24h API",
    description="API de emulação de e-commerce demonstrando a orquestração entre rotinas **Síncronas** (Instantâneas) e **Assíncronas** (Background Workers e Filas).",
    version="1.0.0",
    lifespan=lifespan
)

# Rota que serve a nossa interface (Tela do Cliente)
@app.get("/", response_class=FileResponse, include_in_schema=False)
async def get_index():
    return "src/static/index.html"

class LoginData(BaseModel):
    username: str = "mestre"
    password: str = "123"

@app.post("/login", summary="Realizar Login", tags=["Autenticação"], description="Valida o usuário de forma **síncrona** e retorna um token JWT fictício.")
def api_login(data: LoginData):
    # Ação Síncrona
    token = login(data.username, data.password)
    return {"token": token}

class ItemData(BaseModel):
    item: str = "Maçã 🍎"

@app.post("/cart", summary="Adicionar Item ao Carrinho", tags=["Carrinho"], description="Adiciona um item ao carrinho de compras no banco de dados em memória de forma **síncrona**.")
def api_add_cart(data: ItemData):
    # Ação Síncrona
    msg = add_carrinho(data.item)
    return {"message": msg, "carrinho": db["carrinho"]}

@app.post("/cart/clear", summary="Limpar Carrinho", tags=["Carrinho"])
def api_clear_cart():
    # Ação Síncrona
    msg = clear_carrinho()
    return {"message": msg, "carrinho": db["carrinho"]}

class CheckoutMode(BaseModel):
    mode: str = "random"

@app.post("/checkout", summary="Finalizar Pedido (Checkout)", tags=["Checkout"], description="Gera o pedido de forma **síncrona** e o envia para a fila de pagamento **assíncrona** (Background Worker). Retorna a resposta antes do pagamento terminar.")
async def api_checkout(data: CheckoutMode = CheckoutMode()):
    # Ação Síncrona inicial (congelar carrinho)
    order_id = checkout()
    # Passagem Assíncrona para background (libera a tela imediatamente)
    await fila_pagamentos.put({"order_id": order_id, "mode": data.mode})
    return {"message": f"{order_id} gerado com sucesso.", "status": db["pedidos"][order_id]["status"]}

@app.get("/status", summary="Consultar Status do Sistema", tags=["Monitoramento"], description="Retorna o estado atual do banco de dados fictício (Carrinho e Status do Pedido).")
def api_status():
    # Retorna o estado atual do BD Mockado para atualizar a tela
    return {"db": db}