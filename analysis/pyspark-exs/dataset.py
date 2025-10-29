import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import timedelta

fake = Faker()

# Parâmetros
NUM_USERS = 50000
NUM_SELLERS = 1000
NUM_PRODUCTS = 20000
NUM_ORDERS = 500000
NUM_REVIEWS = 200000
NUM_SESSIONS = 100000
NUM_PAYMENTS = 400000

# Usuários
users = pd.DataFrame({
    "user_id": [f"user_{i}" for i in range(NUM_USERS)],
    "name": [fake.name() for _ in range(NUM_USERS)],
    "email": [fake.email() for _ in range(NUM_USERS)],
    "signup_date": [fake.date_between(start_date="-3y", end_date="today") for _ in range(NUM_USERS)],
    "state": [fake.state() for _ in range(NUM_USERS)]
})

# Vendedores
sellers = pd.DataFrame({
    "seller_id": [f"seller_{i}" for i in range(NUM_SELLERS)],
    "company_name": [fake.company() for _ in range(NUM_SELLERS)],
    "location": [fake.city() for _ in range(NUM_SELLERS)]
})

# Produtos
products = pd.DataFrame({
    "product_id": [f"product_{i}" for i in range(NUM_PRODUCTS)],
    "product_name": [fake.catch_phrase() for _ in range(NUM_PRODUCTS)],
    "price": [round(random.uniform(10, 1000), 2) for _ in range(NUM_PRODUCTS)],
    "category": [random.choice(["Eletrônicos", "Moda", "Casa", "Esporte", "Beleza"]) for _ in range(NUM_PRODUCTS)],
    "seller_id": [random.choice(sellers["seller_id"]) for _ in range(NUM_PRODUCTS)]
})

# Pedidos
orders = pd.DataFrame({
    "order_id": [f"order_{i}" for i in range(NUM_ORDERS)],
    "user_id": [random.choice(users["user_id"]) for _ in range(NUM_ORDERS)],
    "order_date": [fake.date_time_between(start_date="-2y", end_date="now") for _ in range(NUM_ORDERS)],
    "status": [random.choice(["entregue", "cancelado", "em trânsito", "pendente"]) for _ in range(NUM_ORDERS)]
})

# Itens dos pedidos
order_items = []
for order in orders["order_id"]:
    for _ in range(random.randint(1, 5)):
        product = products.sample(1).iloc[0]
        order_items.append({
            "order_id": order,
            "product_id": product["product_id"],
            "quantity": random.randint(1, 3),
            "price": product["price"]
        })
order_items = pd.DataFrame(order_items)

# Avaliações
reviews = pd.DataFrame({
    "review_id": [f"review_{i}" for i in range(NUM_REVIEWS)],
    "order_id": [random.choice(orders["order_id"]) for _ in range(NUM_REVIEWS)],
    "rating": [random.randint(1, 5) for _ in range(NUM_REVIEWS)],
    "review_text": [fake.sentence() for _ in range(NUM_REVIEWS)],
    "review_date": [fake.date_time_between(start_date="-2y", end_date="now") for _ in range(NUM_REVIEWS)]
})

# Sessões
sessions = pd.DataFrame({
    "session_id": [f"session_{i}" for i in range(NUM_SESSIONS)],
    "user_id": [random.choice(users["user_id"]) for _ in range(NUM_SESSIONS)],
    "start_time": [fake.date_time_between(start_date="-1y", end_date="now") for _ in range(NUM_SESSIONS)],
    "duration_minutes": [random.randint(1, 90) for _ in range(NUM_SESSIONS)],
    "device": [random.choice(["mobile", "desktop", "tablet"]) for _ in range(NUM_SESSIONS)]
})

# Pagamentos
payments = pd.DataFrame({
    "payment_id": [f"pay_{i}" for i in range(NUM_PAYMENTS)],
    "order_id": [random.choice(orders["order_id"]) for _ in range(NUM_PAYMENTS)],
    "payment_date": [fake.date_time_between(start_date="-2y", end_date="now") for _ in range(NUM_PAYMENTS)],
    "payment_type": [random.choice(["boleto", "cartão crédito", "cartão débito", "pix"]) for _ in range(NUM_PAYMENTS)],
    "amount": [round(random.uniform(10, 3000), 2) for _ in range(NUM_PAYMENTS)]
})

# Salvando em CSV
users.to_csv("users.csv", index=False)
sellers.to_csv("sellers.csv", index=False)
products.to_csv("products.csv", index=False)
orders.to_csv("orders.csv", index=False)
order_items.to_csv("order_items.csv", index=False)
reviews.to_csv("reviews.csv", index=False)
sessions.to_csv("sessions.csv", index=False)
payments.to_csv("payments.csv", index=False)
