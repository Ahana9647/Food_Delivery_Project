import os
import sys
import pandas as pd


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import PROCESSED_DATA_PATH
from src.data_loader import load_raw_data

def clean_data():
    """
    Function to clean and process the raw food delivery dataset.
    """
    df = load_raw_data()
    if df is None:
        print("No data found to preprocess.")
        return None

    
    initial_rows = df.shape[0]
    df = df.drop_duplicates()
    print(f"Dropped duplicate rows: {initial_rows - df.shape[0]}")

    
    df = df.dropna()
    print(f"Total rows after handling missing values: {df.shape[0]}")

    
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"Cleaned data saved successfully at: {PROCESSED_DATA_PATH}")

    return df

if __name__ == "__main__":
    clean_data()