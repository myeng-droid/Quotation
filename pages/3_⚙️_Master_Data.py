import streamlit as st
import pandas as pd

st.set_page_config(page_title="Master Data", page_icon="⚙️", layout="wide")

st.markdown("# ⚙️ Master Data Management")
st.info("🚧 This module is under construction.")

tabs = st.tabs(["Customers", "Ports", "Overhead", "Products"])

with tabs[0]:
    st.write("Manage Customers Table")
    # Placeholder grid
    df = pd.DataFrame({"ID": ["C001", "C002"], "Name": ["Customer A", "Customer B"]})
    st.data_editor(df, num_rows="dynamic")

with tabs[1]:
    st.write("Manage Ports")

with tabs[2]:
    st.write("Manage Overhead Rates")
