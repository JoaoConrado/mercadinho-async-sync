import json
import os

DB_FILE = "db.json"

# Carrega do arquivo JSON se existir, senão inicia vazio
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"carrinho": [], "pedidos": {}}

db = load_db()

# Função utilitária para salvar no disco
save_db = lambda: json.dump(db, open(DB_FILE, "w", encoding="utf-8"), indent=4)

# Funções Síncronas (One-liners)
login = lambda u, p: "token_jwt_123" if u == "mestre" and p == "123" else "Acesso Negado"
add_carrinho = lambda item: db["carrinho"].append(item) or save_db() or f"{item} adicionado!"
clear_carrinho = lambda: db.update({"carrinho": []}) or save_db() or "Carrinho limpo!"

def checkout():
    order_id = f"PEDIDO-{(len(db['pedidos']) + 1):03d}"
    db["pedidos"][order_id] = {"itens": db["carrinho"].copy(), "status": "processando_pagamento"}
    clear_carrinho()
    return order_id