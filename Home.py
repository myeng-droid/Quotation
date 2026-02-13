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

# Shared CSS for Professional UI (Login & Dashboard)
def local_css():
    st.markdown("""
    <style>
    /* Main Background - Cool Blue Theme (Eye-friendly) */
    .stApp { 
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 50%, #E1F5FE 100%);
        background-attachment: fixed;
    }
    
    /* Main Container */
    .main .block-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        box-shadow: 0 4px 20px rgba(21, 101, 192, 0.1);
        margin-top: 1rem;
    }

    /* Input Fields */
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1.5px solid #90CAF9;
        background-color: #FAFAFA;
    }
    .stTextInput > div > div > input:focus {
        border-color: #1976D2;
        box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.15);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #1565C0 0%, #2196F3 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 25px;
        font-weight: bold;
        box-shadow: 0 3px 10px rgba(21, 101, 192, 0.35);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #0D47A1 0%, #1976D2 100%);
        box-shadow: 0 4px 15px rgba(21, 101, 192, 0.45);
        transform: translateY(-1px);
    }

    /* DataFrame */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(21, 101, 192, 0.08);
    }

    /* Title */
    h1 {
        color: #1565C0 !important;
    }
    
    /* Login Specific */
    .login-container {
        max-width: 800px;
        margin: 60px auto;
        padding: 0;
        background: transparent;
        box-shadow: none;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

def login():
    local_css() # Apply theme
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        /* Make main container transparent on login page to avoid the 'white box' */
        .main .block-container {
            background: transparent !important;
            box-shadow: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.5, 1, 0.5])
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #1565C0; font-size: 1.8em; margin-bottom: 25px;'>Cost Sheet Management System</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #424242; margin-top: 0;'>🔐 Sign In</h4>", unsafe_allow_html=True)
        
        username = st.text_input("Username", value="admin", key="user_login")
        password = st.text_input("Password", type="password", value="1234", key="pass_login")
        
        st.markdown("<div style='margin-top: 25px;'>", unsafe_allow_html=True)
        if st.button("Login", use_container_width=True, key="login_btn"):
            if username == "admin" and password == "1234":
                st.session_state['authentication_status'] = True
                st.rerun()
            else:
                st.error("Username/Password incorrect")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

def logout():
    st.session_state['authentication_status'] = None
    st.rerun()


# --- MAIN APP ---
if st.session_state['authentication_status'] is not True:
    login()
else:
    local_css() # Apply theme to dashboard
    
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
