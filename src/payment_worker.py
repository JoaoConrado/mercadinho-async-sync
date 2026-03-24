import asyncio
import random
from src.db import db, save_db

async def process_payment(order_id: str):
    """Tenta processar um pagamento com até 3 retentativas."""
    for attempt in range(3):
        try:
            # Simulador de I/O de Rede com o Gateway de Cartão
            latency = random.uniform(0.5, 2.0)
            await asyncio.sleep(latency)
            
            # Pattern de Timeout
            if latency > 1.5:
                raise TimeoutError(f"Gateway lento (Latência: {latency:.2f}s)")
            
            db["pedidos"][order_id]["status"] = "pago_com_sucesso"
            save_db()
            print(f"[{order_id}] Pagamento aprovado na tentativa {attempt + 1}!")
            return True
        except TimeoutError as e:
            print(f"[{order_id}] Erro: {e}. Retentando...")
    
    # Pattern de Fallback
    db["pedidos"][order_id]["status"] = "falha_pagamento"
    save_db()
    print(f"[{order_id}] Falha crítica após 3 tentativas. Pedido cancelado (Fallback ativado).")
    return False

async def payment_worker(queue: asyncio.Queue):
    """Consome a fila de pagamentos em background continuamente."""
    while True:
        order_id = await queue.get()
        await process_payment(order_id)
        queue.task_done()