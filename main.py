import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime

# Page Configuration
st.set_page_config(
    page_title="Food Delivery Analytics & Performance Hub",
    page_icon="🍔",
    layout="wide"
)

# Custom Header Styling
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #d35400 0%, #e67e22 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    <div class="main-header">
        <h1>🍔 Food Delivery Analytics & Performance Hub</h1>
        <p>Real-Time Operations, Delivery Speed & Restaurant Benchmarking</p>
    </div>
""", unsafe_allow_html=True)

# ----------------- DATA LOADING -----------------
@st.cache_data
def load_project_data():
    data_dir = "data"
    df = None
    if os.path.exists(data_dir):
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        if csv_files:
            try:
                df = pd.read_csv(os.path.join(data_dir, csv_files[0]))
            except Exception:
                pass
                
    if df is None:
        # Fallback comprehensive sample dataset matching the project structure
        np.random.seed(42)
        n = 500
        cities = ['Bangalore', 'Chennai', 'Delhi', 'Kolkata', 'Mumbai']
        vehicles = ['Bike', 'EV', 'Scooter', 'Bicycle']
        restaurants = ['ABC Kitchen', 'Spice Hub', 'Urban Tadka', 'Flavours of Bengal', 'Mumbai Masala', 'Delhi Darbar', 'Desi Rasoi', 'Royal Dine', 'Green Chilli', 'Bengal Bites']
        
        df = pd.DataFrame({
            'Order_ID': [f"FD10{i}" for i in range(1000, 1000 + n)],
            'Order_Date': pd.date_range(start='2026-01-01', periods=n, freq='D'),
            'Order_Time': pd.to_datetime('2026-01-01 12:00:00') + pd.to_timedelta(np.random.randint(0, 86400, n), unit='s'),
            'Restaurant': np.random.choice(restaurants, n),
            'Customer_ID': [f"C{np.random.randint(3000, 3200)}" for _ in range(n)],
            'City': np.random.choice(cities, n),
            'Vehicle_Type': np.random.choice(vehicles, n),
            'Distance_KM': np.round(np.random.uniform(1.0, 15.0, n), 1),
            'Preparation_Time_Min': np.random.randint(10, 30, n),
            'Delivery_Time_Min': np.random.randint(20, 75, n),
            'Order_Cost': np.round(np.random.uniform(200, 1200, n), 2),
            'Rating': np.round(np.random.uniform(3.5, 5.0, n), 1)
        })
    return df

raw_df = load_project_data()

# ----------------- SIDEBAR FILTERS & CONTROLS -----------------
st.sidebar.markdown("## 🔍 Filters & Controls")
st.sidebar.markdown("Filter overall metrics and charts instantly.")

# File Uploader option in sidebar
st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("Upload Cleaned Dataset (.csv)", type=["csv"])
if uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file)
        st.sidebar.success("Custom dataset loaded successfully!")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# City Filter
if 'City' in raw_df.columns:
    all_cities = raw_df['City'].unique().tolist()
    selected_cities = st.sidebar.multiselect("Select Cities", all_cities, default=all_cities)
    if selected_cities:
        df = raw_df[raw_df['City'].isin(selected_cities)]
    else:
        df = raw_df.copy()
else:
    df = raw_df.copy()

# Vehicle Type Filter
if 'Vehicle_Type' in df.columns:
    all_vehicles = df['Vehicle_Type'].unique().tolist()
    selected_vehicles = st.sidebar.multiselect("Select Vehicle Types", all_vehicles, default=all_vehicles)
    if selected_vehicles:
        df = df[df['Vehicle_Type'].isin(selected_vehicles)]

# Date Range Filter
st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Date Range Filter")
if 'Order_Date' in df.columns:
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], errors='coerce')
    min_date = df['Order_Date'].min().date() if not df['Order_Date'].isnull().all() else datetime.date(2026, 1, 1)
    max_date = df['Order_Date'].max().date() if not df['Order_Date'].isnull().all() else datetime.date(2026, 12, 31)
    
    date_range = st.sidebar.date_input("Select Order Period", value=(min_date, max_date))

# ----------------- EXECUTIVE OVERVIEW (KPIs) -----------------
st.markdown("### 📌 Executive Overview (KPIs)")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_orders = len(df)
avg_speed = df['Delivery_Time_Min'].mean() if 'Delivery_Time_Min' in df.columns else 0.0
avg_rating = df['Rating'].mean() if 'Rating' in df.columns else 4.2
on_time_rate = (len(df[df['Delivery_Time_Min'] <= 40]) / total_orders * 100) if total_orders > 0 and 'Delivery_Time_Min' in df.columns else 70.0

with kpi1:
    st.metric("Total Orders", f"{total_orders:,}", "Total Sample Active")
with kpi2:
    st.metric("Avg Delivery Speed", f"{avg_speed:.1f} min", "-2.1 min Target")
with kpi3:
    st.metric("On-Time Rate", f"{on_time_rate:.1f}%")
with kpi4:
    st.metric("Avg Customer Rating", f"{avg_rating:.2f} ⭐")

st.markdown(f"💡 *Executive Insight: Currently analyzing {total_orders:,} orders. The average delivery duration is {avg_speed:.1f} minutes with an overall customer satisfaction score of {avg_rating:.2f} ⭐.*")
st.markdown("---")

# ----------------- DASHBOARD TABS -----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Delivery & Volume", 
    "🏆 Restaurant Benchmarks", 
    "🚴 Fleet & City Analysis", 
    "📋 Raw Data Explorer"
])

# --- TAB 1: Delivery & Volume ---
with tab1:
    st.subheader("Top 10 Popular Restaurants")
    col_a, col_b = st.columns(2)
    
    with col_a:
        if 'Restaurant' in df.columns:
            top_rest = df['Restaurant'].value_counts().head(10)
            st.bar_chart(top_rest)
        else:
            st.info("Restaurant column not found.")
            
    with col_b:
        st.subheader("Distance vs Delivery Duration")
        if 'Distance_KM' in df.columns and 'Delivery_Time_Min' in df.columns:
            chart_data = df[['Distance_KM', 'Delivery_Time_Min']].dropna()
            st.scatter_chart(chart_data)
        else:
            st.info("Required columns for scatter chart not available.")

# --- TAB 2: Restaurant Benchmarks ---
with tab2:
    st.subheader("Highest Rated Restaurants")
    if 'Restaurant' in df.columns and 'Rating' in df.columns:
        rated_rest = df.groupby('Restaurant')['Rating'].mean().sort_values(ascending=False).head(10)
        st.bar_chart(rated_rest)
    else:
        st.info("Rating data not available.")

# --- TAB 3: Fleet & City Analysis ---
with tab3:
    col_c, col_d = st.columns(2)
    
    with col_c:
        st.subheader("Order Volume by City")
        if 'City' in df.columns:
            city_counts = df['City'].value_counts()
            st.bar_chart(city_counts)
            
    with col_d:
        st.subheader("Delivery Speed by Vehicle Type")
        if 'Vehicle_Type' in df.columns and 'Delivery_Time_Min' in df.columns:
            vehicle_speed = df.groupby('Vehicle_Type')['Delivery_Time_Min'].mean()
            st.bar_chart(vehicle_speed)

# --- TAB 4: Raw Data Explorer ---
with tab4:
    st.subheader("Filtered Dataset Viewer")
    st.dataframe(df, use_container_width=True)
    
    # Download button for filtered data
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Report (CSV)",
        data=csv_data,
        file_name="filtered_food_delivery_report.csv",
        mime="text/csv"
    )
