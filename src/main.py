import asyncio
from src.db import db, login, add_carrinho, checkout
from src.payment_worker import payment_worker

async def main():
    print("--- 🛒 Iniciando Mercadinho 24h ---")
    
    # 1. Login Síncrono
    print("Login:", login("mestre", "123"))
    
    # 2. Add Carrinho Síncrono
    print("Carrinho:", add_carrinho("Maçã"))
    print("Carrinho:", add_carrinho("Pão Integral"))
    
    # 3. Checkout Síncrono
    print("Checkout:", checkout())
    print(f"Status DB atual: {db}")
    print("\n--- ⏳ Enviando para Fila de Pagamentos ---")
    
    # 4. Mensageria Assíncrona
    fila_pagamentos = asyncio.Queue()
    worker_task = asyncio.create_task(payment_worker(fila_pagamentos))
    
    await fila_pagamentos.put("Pedido #999")
    
    # Trava (await) para propósitos de demonstração, aguardando a fila terminar
    await fila_pagamentos.join()
    worker_task.cancel()
    
    print(f"\nStatus Final DB: {db}")

if __name__ == "__main__":
    asyncio.run(main())