import os
import sys
import pandas as pd

# Add the project root directory to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import PROCESSED_DATA_PATH, OUTPUT_DIR

def analyze_data():
    """
    Function to perform data analysis on the cleaned food delivery dataset.
    """
    if not os.path.exists(PROCESSED_DATA_PATH):
        print("Processed data file not found! Please run preprocessing first.")
        return None

    # Load the processed dataset
    df = pd.read_csv(PROCESSED_DATA_PATH)
    print("--- Data Analysis Report ---")
    
    # 1. Total order count
    print(f"Total Orders: {df.shape[0]}")

    # 2. City-wise order count
    city_counts = None
    if 'City' in df.columns:
        city_counts = df['City'].value_counts()
        print("\nOrders by City:")
        print(city_counts)

    # 3. Delivery mode statistics
    if 'Delivery_Mode' in df.columns:
        mode_counts = df['Delivery_Mode'].value_counts()
        print("\nOrders by Delivery Mode:")
        print(mode_counts)

    # 4. Save analysis summary to a text file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    summary_path = os.path.join(OUTPUT_DIR, "analysis_summary.txt")
    
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"Total Orders: {df.shape[0]}\n\n")
        f.write("Orders by City:\n")
        f.write(str(city_counts) if 'City' in df.columns else "City column not found")
        
    print(f"\nAnalysis summary saved successfully at: {summary_path}")
    return df

if __name__ == "__main__":
    analyze_data()