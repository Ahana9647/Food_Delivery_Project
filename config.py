import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "food_delivery_orders.csv")
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_food_delivery_orders.csv")


OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
