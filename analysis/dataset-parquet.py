from pyspark.sql import SparkSession
from faker import Faker
import random
from datetime import datetime, timedelta

# Inicializando PySpark
spark = SparkSession.builder \
    .appName("ECommerceSyntheticData") \
    .getOrCreate()

fake = Faker()

# Configurações
NUM_USERS = 50000
NUM_SELLERS = 1000
NUM_PRODUCTS = 20000
NUM_ORDERS = 500000
NUM_REVIEWS = 200000
NUM_SESSIONS = 100000
NUM_PAYMENTS = 400000

# Funções auxiliares
def rand_date(start_days_ago=1000, end_days_ago=0):
    return fake.date_time_between(start_date=f"-{start_days_ago}d", end_date=f"-{end_days_ago}d")

def create_users():
    return [
        (f"user_{i}", fake.name(), fake.email(), rand_date(1000), fake.state())
        for i in range(NUM_USERS)
    ]

def create_sellers():
    return [
        (f"seller_{i}", fake.company(), fake.city())
        for i in range(NUM_SELLERS)
    ]

def create_products(seller_ids):
    return [
        (
            f"product_{i}",
            fake.catch_phrase(),
            round(random.uniform(10, 1000), 2),
            random.choice(["Eletrônicos", "Moda", "Casa", "Esporte", "Beleza"]),
            random.choice(seller_ids)
        )
        for i in range(NUM_PRODUCTS)
    ]

def create_orders(user_ids):
    return [
        (
            f"order_{i}",
            random.choice(user_ids),
            rand_date(700),
            random.choice(["entregue", "cancelado", "em trânsito", "pendente"])
        )
        for i in range(NUM_ORDERS)
    ]

def create_order_items(order_ids, product_list):
    items = []
    for order_id in order_ids:
        for _ in range(random.randint(1, 5)):
            product = random.choice(product_list)
            items.append((order_id, product[0], random.randint(1, 3), product[2]))
    return items

def create_reviews(order_ids):
    return [
        (
            f"review_{i}",
            random.choice(order_ids),
            random.randint(1, 5),
            fake.sentence(),
            rand_date(700)
        )
        for i in range(NUM_REVIEWS)
    ]

def create_sessions(user_ids):
    return [
        (
            f"session_{i}",
            random.choice(user_ids),
            rand_date(365),
            random.randint(1, 90),
            random.choice(["mobile", "desktop", "tablet"])
        )
        for i in range(NUM_SESSIONS)
    ]

def create_payments(order_ids):
    return [
        (
            f"pay_{i}",
            random.choice(order_ids),
            rand_date(700),
            random.choice(["boleto", "cartão crédito", "cartão débito", "pix"]),
            round(random.uniform(10, 3000), 2)
        )
        for i in range(NUM_PAYMENTS)
    ]

# Criando os dados
users = create_users()
sellers = create_sellers()
products = create_products([s[0] for s in sellers])
orders = create_orders([u[0] for u in users])
order_items = create_order_items([o[0] for o in orders], products)
reviews = create_reviews([o[0] for o in orders])
sessions = create_sessions([u[0] for u in users])
payments = create_payments([o[0] for o in orders])

# Esquemas e criação dos DataFrames
users_df = spark.createDataFrame(users, ["user_id", "name", "email", "signup_date", "state"])
sellers_df = spark.createDataFrame(sellers, ["seller_id", "company_name", "location"])
products_df = spark.createDataFrame(products, ["product_id", "product_name", "price", "category", "seller_id"])
orders_df = spark.createDataFrame(orders, ["order_id", "user_id", "order_date", "status"])
order_items_df = spark.createDataFrame(order_items, ["order_id", "product_id", "quantity", "price"])
reviews_df = spark.createDataFrame(reviews, ["review_id", "order_id", "rating", "review_text", "review_date"])
sessions_df = spark.createDataFrame(sessions, ["session_id", "user_id", "start_time", "duration_minutes", "device"])
payments_df = spark.createDataFrame(payments, ["payment_id", "order_id", "payment_date", "payment_type", "amount"])

# Salvando como Parquet
users_df.write.mode("overwrite").parquet("data_parquet/users")
sellers_df.write.mode("overwrite").parquet("data_parquet/sellers")
products_df.write.mode("overwrite").parquet("data_parquet/products")
orders_df.write.mode("overwrite").parquet("data_parquet/orders")
order_items_df.write.mode("overwrite").parquet("data_parquet/order_items")
reviews_df.write.mode("overwrite").parquet("data_parquet/reviews")
sessions_df.write.mode("overwrite").parquet("data_parquet/sessions")
payments_df.write.mode("overwrite").parquet("data_parquet/payments")
