import streamlit as st
import pandas as pd

st.set_page_config(page_title="Reports", page_icon="📉", layout="wide")

st.markdown("# 📉 Reports Center")
st.info("🚧 This module is under construction.")

# Mockup UI
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### Report 1: Summary")
    st.metric("Total Quotations", "125")
    st.button("View Report 1")

with col2:
    st.markdown("### Report 2: Analytics")
    st.metric("Win Rate", "68%")
    st.button("View Report 2")

with col3:
    st.markdown("### Report 3: Export")
    st.write("Download full transaction history.")
    st.button("Download CSV")
