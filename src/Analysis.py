import os
import sys
import numpy as np
import pandas as pd

# Add the project root directory to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import PROCESSED_DATA_PATH, OUTPUT_DIR

def analyze_data():
    """
    Function to perform advanced data analysis on the cleaned food delivery dataset.
    """
    if not os.path.exists(PROCESSED_DATA_PATH):
        print("Processed data file not found! Please run preprocessing first.")
        return None

    # Load the processed/cleaned dataset
    df = pd.read_csv(PROCESSED_DATA_PATH)
    delivered_df = df[df["Order_Status"] == "Delivered"]

    print("--- Advanced Data Analysis Report ---\n")

    # Metrics calculation
    total_orders = len(df)
    total_revenue = delivered_df["Order_Value"].sum()
    delivered_orders = (df["Order_Status"] == "Delivered").sum()
    cancelled_orders = (df["Order_Status"] == "Cancelled").sum()
    delivery_success_rate = delivered_orders / total_orders * 100
    cancellation_rate = cancelled_orders / total_orders * 100
    aov_delivered = delivered_df["Order_Value"].mean()
    
    avg_delivery_time_delivered = delivered_df["Delivery_Time_Min"].mean()
    avg_expected_time = df["Expected_Delivery_Min"].mean()
    on_time_rate = delivered_df["On_Time"].dropna().mean() * 100 if "On_Time" in delivered_df.columns else 0
    avg_prep_time_delivered = delivered_df["Preparation_Time_Min"].mean()
    avg_rating_delivered = delivered_df["Rating"].mean()
    
    total_unique_customers = df["Customer_ID"].nunique() if "Customer_ID" in df.columns else 0
    
    if "Customer_ID" in delivered_df.columns:
        orders_per_customer = delivered_df["Customer_ID"].value_counts()
        repeat_customers = (orders_per_customer > 1).sum()
        total_customers = len(orders_per_customer)
        repeat_customer_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
    else:
        repeat_customer_rate = 0

    avg_distance_delivered = delivered_df["Distance_KM"].mean() if "Distance_KM" in delivered_df.columns else 0
    avg_delivery_fee = delivered_df["Delivery_Fee"].mean() if "Delivery_Fee" in delivered_df.columns else 0

    # Print summary to console
    print(f"Total Orders: {total_orders}")
    print(f"Total Revenue (Delivered only): {total_revenue:.2f}")
    print(f"Delivered Orders: {delivered_orders}")
    print(f"Cancelled Orders: {cancelled_orders}")
    print(f"Delivery Success Rate: {delivery_success_rate:.2f}%")
    print(f"Cancellation Rate: {cancellation_rate:.2f}%")
    print(f"AOV (Delivered only): {aov_delivered:.2f}")
    print(f"Average Delivery Time (Delivered only): {avg_delivery_time_delivered:.2f} minutes")
    print(f"On-Time Rate (Delivered only): {on_time_rate:.2f}%")
    print(f"Average Rating (Delivered only): {avg_rating_delivered:.2f}")
    print(f"Repeat Customer Rate: {repeat_customer_rate:.2f}%")

    # Restaurant Ranking
    summary_lines = []
    summary_lines.append(f"Total Orders: {total_orders}")
    summary_lines.append(f"Total Revenue (Delivered only): {total_revenue:.2f}")
    summary_lines.append(f"Delivery Success Rate: {delivery_success_rate:.2f}%")
    summary_lines.append(f"On-Time Rate: {on_time_rate:.2f}%")
    summary_lines.append(f"Average Rating: {avg_rating_delivered:.2f}")
    summary_lines.append(f"Repeat Customer Rate: {repeat_customer_rate:.2f}%\n")

    if "Restaurant" in df.columns:
        MIN_ORDERS = 100    
        rest_all = df.groupby("Restaurant").agg(
            Total_Orders=("Order_ID", "count"),
            Delivered_Orders=("Order_Status", lambda s: (s == "Delivered").sum()),
        )
        rest_all["Success_Rate_%"] = rest_all["Delivered_Orders"] / rest_all["Total_Orders"] * 100
        
        rest_del = delivered_df.groupby("Restaurant").agg(
            Revenue=("Order_Value", "sum"),
            Avg_Rating=("Rating", "mean"),
            On_Time_Rate_Pct=("On_Time", "mean") if "On_Time" in delivered_df.columns else ("Order_ID", "count"),
            Avg_Delivery_Time=("Delivery_Time_Min", "mean"),
        )
        if "On_Time" in delivered_df.columns:
            rest_del["On_Time_Rate_%"] = rest_del.pop("On_Time_Rate_Pct") * 100
        
        restaurants = rest_all.join(rest_del)
        restaurants = restaurants[restaurants["Total_Orders"] >= MIN_ORDERS]
        
        def norm(s):
            return (s - s.min()) / (s.max() - s.min()) if s.max() != s.min() else s
        
        if not restaurants.empty:
            restaurants["Performance_Score"] = (
                norm(restaurants["Success_Rate_%"]) + 
                norm(restaurants["On_Time_Rate_%"]) + 
                norm(restaurants["Avg_Rating"]) + 
                (1 - norm(restaurants["Avg_Delivery_Time"]))
            ) / 4 * 100
            restaurants = restaurants.sort_values("Performance_Score", ascending=False).round(2)
            cols = ["Total_Orders", "Revenue", "Success_Rate_%", "On_Time_Rate_%", "Avg_Rating", "Avg_Delivery_Time", "Performance_Score"]
            restaurants.insert(0, "Rank", range(1, len(restaurants) + 1))
            
            print("\nRestaurant Performance Ranking (Top Best):")
            print(restaurants[["Rank"] + cols].head(10).to_string())
            
            summary_lines.append("Restaurant Performance Ranking:\n")
            summary_lines.append(restaurants[["Rank"] + cols].to_string())

    # Save summary to text file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    summary_path = os.path.join(OUTPUT_DIR, "analysis_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))
        
    print(f"\nAnalysis summary saved successfully at: {summary_path}")
    return df

if __name__ == "__main__":
    analyze_data()
