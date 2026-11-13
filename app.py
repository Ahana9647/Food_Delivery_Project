import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Food Delivery Executive Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS & Header Banner Styling (With Print Fix)
st.markdown("""
    <style>
    /* Background Color */
    .main {
        background-color: #0e1117;
    }
    
    /* Header Banner */
    .header-banner {
        background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%);
        padding: 24px;
        border-radius: 16px;
        color: white;
        text-align: center;
        box-shadow: 0px 10px 25px rgba(255, 65, 108, 0.3);
        margin-bottom: 25px;
    }
    
    .header-banner h1 {
        margin: 0;
        font-size: 32px;
        font-weight: 800;
    }
    
    .header-banner p {
        margin-top: 6px;
        font-size: 15px;
        opacity: 0.9;
    }

    /* Metric Cards Styling */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 16px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        padding-left: 20px;
        padding-right: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF416C, #FF4B2B) !important;
        color: white !important;
        font-weight: bold;
    }

    /* Print Fix: Prevent header cutting off */
    @media print {
        body {
            margin-top: 0px !important;
        }
        .main {
            padding-top: 0px !important;
        }
    }
    </style>

    <div class="header-banner">
        <h1>⚡ Food Delivery Analytics & Performance Hub</h1>
        <p>Real-Time Operations, Delivery Speed & Restaurant Benchmarking</p>
    </div>
""", unsafe_allow_html=True)

# 3. File Uploader Section
uploaded_file = st.file_uploader("📂 Upload Cleaned Dataset (`cleaned_food_delivery_orders.csv`)", type=["csv"])

if uploaded_file is None:
    st.info("💡 **Getting Started:** Upload your dataset CSV file above to load live analytics and interactive charts.")
    st.stop()

@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    
    # সংখ্যানুক্রমিক কলামগুলোকে Numeric Format-এ রূপান্তর করা
    num_cols = ["Delivery_Time_Min", "Expected_Delivery_Min", "Rating", "Distance_KM", "Preparation_Time_Min"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    # ডেট কলাম খুঁজে তা Datetime Format-এ রূপান্তর করা
    date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
    for col in date_cols:
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        except:
            pass
            
    return df

df = load_data(uploaded_file)

# অটোমেটিক ডেট কলাম চিহ্নিত করা
date_column = None
for col in df.columns:
    if pd.api.types.is_datetime64_any_dtype(df[col]):
        date_column = col
        break

# 4. Interactive Sidebar Filters & Actions
st.sidebar.markdown("## 🔍 **Filters & Controls**")
st.sidebar.caption("Filter overall metrics and charts instantly.")

cities = sorted(df["City"].dropna().unique()) if "City" in df.columns else []
vehicles = sorted(df["Vehicle_Type"].dropna().unique()) if "Vehicle_Type" in df.columns else []

selected_cities = st.sidebar.multiselect("🏙️ Select Cities", cities, default=cities, key="city_multiselect") if cities else []
selected_vehicles = st.sidebar.multiselect("🛵 Select Vehicle Types", vehicles, default=vehicles, key="vehicle_multiselect") if vehicles else []

# Date Range Filter
start_date, end_date = None, None
if date_column is not None and not df[date_column].dropna().empty:
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📅 **Date Range Filter**")
    min_date = df[date_column].min().date()
    max_date = df[date_column].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Order Period",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date,
        key="order_date_range"
    )
    if len(date_range) == 2:
        start_date, end_date = date_range

# Print / Save as PDF Guide in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("## 🖨️ **Report Actions**")
st.sidebar.info("💡 To print or save as PDF, press **Ctrl + P** (Windows) or **Cmd + P** (Mac).")

# Filtered Dataset Logic
filtered_df = df.copy()
if cities and selected_cities:
    filtered_df = filtered_df[filtered_df["City"].isin(selected_cities)]
if vehicles and selected_vehicles:
    filtered_df = filtered_df[filtered_df["Vehicle_Type"].isin(selected_vehicles)]
if date_column and start_date and end_date:
    filtered_df = filtered_df[
        (filtered_df[date_column].dt.date >= start_date) & 
        (filtered_df[date_column].dt.date <= end_date)
    ]

# 5. Core Platform KPIs
total_orders = len(filtered_df)

if total_orders > 0 and "Delivery_Time_Min" in filtered_df.columns:
    filtered_df["Delivery_Time_Min"] = pd.to_numeric(filtered_df["Delivery_Time_Min"], errors='coerce').fillna(0)
    avg_delivery_time = float(filtered_df["Delivery_Time_Min"].mean())
else:
    avg_delivery_time = 0.0

if total_orders > 0 and "Rating" in filtered_df.columns:
    filtered_df["Rating"] = pd.to_numeric(filtered_df["Rating"], errors='coerce').fillna(0)
    avg_rating = float(filtered_df["Rating"].mean())
else:
    avg_rating = 0.0

if total_orders > 0 and "Delivery_Time_Min" in filtered_df.columns and "Expected_Delivery_Min" in filtered_df.columns:
    del_times = pd.to_numeric(filtered_df["Delivery_Time_Min"], errors='coerce').fillna(0)
    exp_times = pd.to_numeric(filtered_df["Expected_Delivery_Min"], errors='coerce').fillna(0)
    on_time_count = int((del_times <= exp_times).sum())
    on_time_pct = (on_time_count / total_orders * 100) if total_orders > 0 else 0.0
else:
    on_time_pct = 0.0

st.markdown("### 📌 **Executive Overview (KPIs)**")
k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Orders", f"{total_orders:,}", delta=f"{len(df):,} Total Sample")
k2.metric("Avg Delivery Speed", f"{avg_delivery_time:.1f} min", delta="-2.1 min Target")
k3.metric("On-Time Rate", f"{on_time_pct:.1f}%")
k4.metric("Avg Customer Rating", f"{avg_rating:.2f} ⭐")

# Executive Insight Banner
if total_orders > 0:
    st.info(f"💡 **Executive Insight:** Currently analyzing **{total_orders:,}** orders. The average delivery duration is **{avg_delivery_time:.1f} minutes** with an average customer satisfaction score of **{avg_rating:.2f} ⭐**.")

st.markdown("---")

# 6. Tab Design Layout
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Delivery & Volume", 
    "🏬 Restaurant Benchmarks", 
    "🛵 Fleet & City Analysis",
    "📋 Raw Data Explorer"
])

# TAB 1: Delivery & Volume Analytics
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Top 10 Popular Restaurants")
        if "Restaurant" in filtered_df.columns:
            top_rest = filtered_df["Restaurant"].value_counts().head(10).reset_index()
            top_rest.columns = ["Restaurant", "Orders"]
            fig_bar = px.bar(
                top_rest, 
                x="Orders", 
                y="Restaurant", 
                orientation='h',
                color="Orders",
                color_continuous_scale="Reds",
                template="plotly_dark"
            )
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("Restaurant column not found.")

    with col2:
        st.markdown("#### 🚴 Distance vs Delivery Duration")
        if "Distance_KM" in filtered_df.columns and "Delivery_Time_Min" in filtered_df.columns:
            sample_df = filtered_df.sample(min(2000, len(filtered_df))) if len(filtered_df) > 0 else filtered_df
            fig_scatter = px.scatter(
                sample_df, 
                x="Distance_KM", 
                y="Delivery_Time_Min",
                color="Vehicle_Type" if "Vehicle_Type" in sample_df.columns else None,
                opacity=0.7,
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
            fig_scatter.update_layout(margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.warning("Distance or Delivery Time columns missing.")

# TAB 2: Restaurant Performance
with tab2:
    st.markdown("#### 🌟 Highest Rated Restaurants (Minimum 30 Orders)")
    if "Restaurant" in filtered_df.columns and "Rating" in filtered_df.columns:
        rest_stats = filtered_df.groupby("Restaurant").agg(
            Total_Orders=("Restaurant", "count"),
            Avg_Rating=("Rating", "mean"),
            Avg_Prep_Time=("Preparation_Time_Min" if "Preparation_Time_Min" in filtered_df.columns else "Rating", "mean")
        ).reset_index()
        
        qualified_rest = rest_stats[rest_stats["Total_Orders"] >= 30].sort_values(by="Avg_Rating", ascending=False).head(10)
        
        if not qualified_rest.empty:
            fig_top_rated = px.bar(
                qualified_rest,
                x="Restaurant",
                y="Avg_Rating",
                color="Avg_Prep_Time",
                title="Top Rated Restaurants & Prep Time (Min)",
                template="plotly_dark",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig_top_rated, use_container_width=True)
        else:
            st.info("No restaurants found with at least 30 orders based on current filters.")
    else:
        st.warning("Required columns for benchmarking are missing.")

# TAB 3: Fleet & City Distribution
with tab3:
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### 🏙️ Order Volume by City")
        if "City" in filtered_df.columns:
            city_counts = filtered_df["City"].value_counts().reset_index()
            city_counts.columns = ["City", "Orders"]
            fig_pie = px.pie(
                city_counts, 
                values="Orders", 
                names="City", 
                hole=0.45, 
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.warning("City column not found.")

    with c2:
        st.markdown("#### 🛵 Delivery Speed by Vehicle Type")
        if "Vehicle_Type" in filtered_df.columns and "Delivery_Time_Min" in filtered_df.columns:
            fig_box = px.box(
                filtered_df, 
                x="Vehicle_Type", 
                y="Delivery_Time_Min", 
                color="Vehicle_Type",
                template="plotly_dark"
            )
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.warning("Vehicle Type or Delivery Time column missing.")

# TAB 4: Raw Data & Download
with tab4:
    st.markdown("#### 📁 Filtered Dataset Viewer")
    st.dataframe(filtered_df, use_container_width=True, height=380)
    
    csv_data = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Report (CSV)",
        data=csv_data,
        file_name="food_delivery_filtered_summary.csv",
        mime="text/csv"
    )