import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="SuperKart Forecast Portal", layout="wide")

st.title("🛒 SuperKart Revenue Forecasting Engine")
st.markdown("Operational Inventory Optimization Dashboard")

# Define target endpoints across internal Docker network bridge mappings
BACKEND_URL = "http://backend:5000/predict"

st.sidebar.header("Input Metrics Specifier")
product_mrp = st.sidebar.number_input("Product MRP ($)", min_value=1.0, max_value=500.0, value=120.0)
product_weight = st.sidebar.number_input("Product Weight", min_value=0.1, max_value=50.0, value=12.5)
allocated_area = st.sidebar.slider("Product Allocated Area Ratio", min_value=0.001, max_value=0.400, value=0.05)

store_type = st.sidebar.selectbox("Store Type Profile", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"])
store_size = st.sidebar.selectbox("Store Size Profile", ["Small", "Medium", "High"])

if st.button("Generate Quarterly Sales Forecast"):
    # Structure features into exactly the array formatting our preprocessed encoders expect
    payload = [{
        "Product_MRP": product_mrp,
        "Product_Weight": product_weight,
        "Product_Allocated_Area": allocated_area,
        "Store_Type": store_type,
        "Store_Size": store_size
    }]
    
    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            predicted_sales = result["predictions"][0]
            st.success(f"📈 Predicted Outlet Store Sales Total: **${predicted_sales:,.2f}**")
        else:
            st.error(f"Backend API Error: {response.text}")
    except Exception as e:
        st.error(f"Could not connect to backend prediction engine. Details: {str(e)}")
