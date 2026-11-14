import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="Food Delivery Dashboard",
    page_icon="🍔",
    layout="wide"
)

# App Title
st.title("🍔 Food Delivery Project Dashboard")
st.markdown("---")
st.write("Welcome! This is your live food delivery data analysis and dashboard.")

# File Uploader Section
st.sidebar.header("Upload Dataset")
uploaded_file = st.sidebar.file_uploader("Upload your project's CSV file here", type=["csv"])

if uploaded_file is not None:
    # Read CSV
    df = pd.read_csv(uploaded_file)
    
    st.success("File uploaded successfully!")
    
    # Show Dataset Preview
    st.subheader("📊 Dataset Overview")
    st.dataframe(df.head())
    
    # Basic Stats
    st.subheader("📈 Quick Statistics")
    st.write(df.describe())
    
    # Simple Visualisation Example (if columns exist)
    if len(df.columns) > 1:
        st.subheader("📉 Data Visualisation")
        st.bar_chart(df.select_dtypes(include=[np.number]).iloc[:, :2])
else:
    st.info("👈 Please upload your food delivery CSV file from the left sidebar.")
    
    # Dummy data notice for testing
    st.markdown("### Sample Dashboard Preview:")
    sample_data = pd.DataFrame({
        'Delivery_Time_Min': [25, 40, 30, 45, 20, 35],
        'Order_Cost': [15.5, 22.0, 18.0, 30.5, 12.0, 25.0]
    })
    st.dataframe(sample_data)
