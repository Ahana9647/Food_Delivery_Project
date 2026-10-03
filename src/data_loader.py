import os
import sys
import pandas as pd

# প্রজেক্টের মূল ফোল্ডারকে পাইথনের পাথ-এ যোগ করা যাতে config.py সহজে পাওয়া যায়
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import RAW_DATA_PATH

def load_raw_data():
    """
    Function to load the food_delivery_orders.csv file from the raw data path.
    """
    try:
        df = pd.read_csv(RAW_DATA_PATH)
        print(f"Data loaded successfully! Total rows: {df.shape[0]}, Total columns: {df.shape[1]}")
        return df
    except Exception as e:
        print(f"Error occurred while loading data: {e}")
        return None

if __name__ == "__main__":
    load_raw_data()