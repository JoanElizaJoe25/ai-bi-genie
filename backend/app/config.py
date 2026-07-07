"""
Configuration settings for AI-BI Genie backend.
Loads environment variables and defines constants.
"""

import os
from dotenv import load_dotenv

# Load .env file if it exists (for local development)
load_dotenv()

# GCP Settings
GCP_PROJECT = os.getenv("GCP_PROJECT", "sada-seed-2025-sandbox")
BQ_DATASET = os.getenv("BQ_DATASET", "intern_a_ecommerce")
LOCATION = os.getenv("LOCATION", "us-central1")

# Gemini Model
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-001")

# Guard Settings
MAX_BYTES_BILLED = int(os.getenv("MAX_BYTES_BILLED", 100 * 1024 * 1024))
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", 20))
MAX_CONVERSATION_TURNS = int(os.getenv("MAX_CONVERSATION_TURNS", 6))

# BigQuery Schema - This is what Gemini uses to generate SQL
BQ_SCHEMA = f"""
Dataset: `{GCP_PROJECT}.{BQ_DATASET}`

Tables and columns:

1. `{GCP_PROJECT}.{BQ_DATASET}.orders`
   - order_id (STRING) - Primary Key
   - customer_id (STRING) - Foreign Key to customers
   - order_status (STRING) - Values: delivered, shipped, canceled, invoiced, processing, unavailable, created, approved
   - order_purchase_timestamp (TIMESTAMP)
   - order_approved_at (TIMESTAMP)
   - order_delivered_carrier_date (TIMESTAMP)
   - order_delivered_customer_date (TIMESTAMP)
   - order_estimated_delivery_date (TIMESTAMP)

2. `{GCP_PROJECT}.{BQ_DATASET}.order_items`
   - order_id (STRING) - Foreign Key to orders
   - order_item_id (INTEGER) - Item sequence number within an order
   - product_id (STRING) - Foreign Key to products
   - seller_id (STRING) - Foreign Key to sellers
   - shipping_limit_date (TIMESTAMP)
   - price (FLOAT) - Product price in BRL (Brazilian Real)
   - freight_value (FLOAT) - Shipping cost in BRL

3. `{GCP_PROJECT}.{BQ_DATASET}.products`
   - product_id (STRING) - Primary Key
   - product_category_name (STRING) - Category in Portuguese
   - product_name_lenght (INTEGER) - Note: typo in original data
   - product_description_lenght (INTEGER) - Note: same typo
   - product_photos_qty (INTEGER)
   - product_weight_g (INTEGER) - Weight in grams
   - product_length_cm (INTEGER)
   - product_height_cm (INTEGER)
   - product_width_cm (INTEGER)

4. `{GCP_PROJECT}.{BQ_DATASET}.customers`
   - customer_id (STRING) - Primary Key
   - customer_unique_id (STRING)
   - customer_zip_code_prefix (INTEGER)
   - customer_city (STRING)
   - customer_state (STRING) - Brazilian state abbreviation

5. `{GCP_PROJECT}.{BQ_DATASET}.order_payments`
   - order_id (STRING) - Foreign Key to orders
   - payment_sequential (INTEGER)
   - payment_type (STRING) - Values: credit_card, boleto, voucher, debit_card
   - payment_installments (INTEGER)
   - payment_value (FLOAT) - Payment amount in BRL

6. `{GCP_PROJECT}.{BQ_DATASET}.sellers`
   - seller_id (STRING) - Primary Key
   - seller_zip_code_prefix (INTEGER)
   - seller_city (STRING)
   - seller_state (STRING)

7. `{GCP_PROJECT}.{BQ_DATASET}.order_reviews`
   - review_id (STRING) - Primary Key
   - order_id (STRING) - Foreign Key to orders
   - review_score (INTEGER) - Rating from 1 to 5
   - review_comment_title (STRING)
   - review_comment_message (STRING)
   - review_creation_date (TIMESTAMP)
   - review_answer_timestamp (TIMESTAMP)

8. `{GCP_PROJECT}.{BQ_DATASET}.geolocation`
   - geolocation_zip_code_prefix (INTEGER)
   - geolocation_lat (FLOAT)
   - geolocation_lng (FLOAT)
   - geolocation_city (STRING)
   - geolocation_state (STRING)

9. `{GCP_PROJECT}.{BQ_DATASET}.product_category_name_translation`
   - string_field_0 (STRING) - Portuguese category name
   - string_field_1 (STRING) - English category name

Key Relationships:
- orders.customer_id -> customers.customer_id
- order_items.order_id -> orders.order_id
- order_items.product_id -> products.product_id
- order_items.seller_id -> sellers.seller_id
- order_payments.order_id -> orders.order_id
- order_reviews.order_id -> orders.order_id
- products.product_category_name -> product_category_name_translation.string_field_0
"""
