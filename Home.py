import streamlit as st
import pandas as pd
from supabase_client import fetch_quotations, delete_quotation
import time

# Page Config
st.set_page_config(
    page_title="Cost Sheet System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- AUTHENTICATION ---
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None

def login():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        .login-container {
            max_width: 400px;
            margin: 100px auto;
            padding: 2rem;
            border-radius: 10px;
            background-color: #f0f8ff;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stButton>button {
            width: 100%;
            background-color: #2196F3;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.markdown("<h2 style='text-align: center; color: #1565C0;'>🔐 Sign In</h2>", unsafe_allow_html=True)
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", type="password", value="1234")
        
        if st.button("Login"):
            if username == "admin" and password == "1234":
                st.session_state['authentication_status'] = True
                st.rerun()
            else:
                st.error("Username/Password incorrect")

def logout():
    st.session_state['authentication_status'] = None
    st.rerun()

# --- MAIN APP ---
if st.session_state['authentication_status'] is not True:
    login()
else:
    # Sidebar
    with st.sidebar:
        st.title("🤖 Quotation System")
        st.write(f"Welcome, **Admin**")
        st.markdown("---")
        if st.button("Logout"):
            logout()

    # Dashboard
    st.markdown("# 📊 Dashboard Listing")
    
    col_act1, col_act2 = st.columns([4, 1])
    with col_act2:
        if st.button("➕ New Cost Sheet", type="primary", use_container_width=True):
             st.switch_page("pages/1_Cost_Sheet_Editor.py")

    # Fetch Data
    try:
        data = fetch_quotations()
        if data:
            df = pd.DataFrame(data)
            
            # Ensure columns exist
            if 'status' not in df.columns:
                df['status'] = "Draft"
            if 'total_cost' not in df.columns:
                df['total_cost'] = 0.0
            
            # Formatter for easier reading
            st.dataframe(
                df,
                column_config={
                    "doc_date": st.column_config.DateColumn("Date"),
                    "doc_no": "Document No.",
                    "customer_importer": "Customer",
                    "total_cost": st.column_config.NumberColumn("Total Cost", format="%.2f"),
                    "status": st.column_config.SelectboxColumn(
                        "Status", options=["Draft", "Approved", "Sent"], required=True
                    )
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Action Section (Simple Delete)
            st.markdown("### Actions")
            del_doc = st.text_input("Enter Document No. to Delete:")
            if st.button("🗑️ Delete Quotation"):
                if del_doc:
                    # Find ID
                    found = df[df['doc_no'] == del_doc]
                    if not found.empty:
                        q_id = found.iloc[0]['id']
                        delete_quotation(q_id)
                        st.success(f"Deleted {del_doc}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Document not found.")
        else:
            st.info("No quotations found. Create your first one!")
            
    except Exception as e:
        st.error(f"Error fetching data: {e}")

    # CSS for styling
    st.markdown("""
    <style>
        .stApp {
            background-color: #Fdfdfd;
        }
        h1 {
            color: #1E88E5;
        }
        div[data-testid="stMetricValue"] {
            font-size: 24px;
        }
    </style>
    """, unsafe_allow_html=True)
