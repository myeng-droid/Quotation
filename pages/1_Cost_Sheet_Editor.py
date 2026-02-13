import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import time
import yfinance as yf
from supabase_client import (
    fetch_customers, fetch_currencies, fetch_ports, fetch_overhead, 
    fetch_factory_expense, fetch_shipping_rates, fetch_rm_costs, fetch_calculator_specs,
    get_overhead_by_group, get_yield_loss_by_group, get_next_doc_no_sequence
)


# --- AUTH CHECK ---

# --- PAGE CONFIG ---
st.set_page_config(page_title="Cost Sheet System", layout="wide", page_icon="📝")

# --- AUTH CHECK ---
if st.session_state.get('authentication_status') is not True:
    st.error("Please login from the Home page.")
    st.stop()


# Custom CSS for Professional UI
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
    
    .section-header { 
        background: linear-gradient(90deg, #1565C0 0%, #1976D2 50%, #2196F3 100%);
        color: white; 
        padding: 14px 22px; 
        border-radius: 10px; 
        margin-top: 25px; 
        margin-bottom: 18px;
        font-weight: bold;
        font-size: 1.05em;
        box-shadow: 0 3px 12px rgba(21, 101, 192, 0.35);
    }
    
    .sub-section {
        background: linear-gradient(135deg, #E3F2FD 0%, #E1F5FE 100%);
        padding: 16px;
        border-radius: 10px;
        border-left: 5px solid #1976D2;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(21, 101, 192, 0.08);
    }
    
    .total-card {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        padding: 22px;
        border-radius: 14px;
        border: 2px solid #4CAF50;
        text-align: center;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2);
    }
    
    .warning-text {
        color: #C62828;
        font-weight: bold;
        background: linear-gradient(90deg, #FFEBEE 0%, #FFCDD2 100%);
        padding: 12px 15px;
        border-radius: 8px;
        border-left: 5px solid #EF5350;
        margin-bottom: 15px;
        box-shadow: 0 2px 6px rgba(198, 40, 40, 0.1);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        border-radius: 6px;
        border: 1.5px solid #90CAF9;
        background-color: #FAFAFA;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
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
    
    /* Data Editor */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(21, 101, 192, 0.08);
    }
    
    /* Title */
    h1 {
        color: #1565C0 !important;
    }
    
    /* Remark Section */
    .remark-section {
        background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FFA000;
        margin-top: 20px;
    }
    
    /* Loading Table Section */
    .loading-section {
        background: linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #8E24AA;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MASTER DATA MOCKUP (Replace with real logic as needed) ---
@st.cache_data
def load_customer_data():
    """Load customer data from Supabase"""
    try:
        data = fetch_customers()
        if data:
            df = pd.DataFrame(data)
            # Map Supabase columns back to the app's internal names
            # Supabase: customer_code, customer_name, payment_term_customer_name
            # App: CUSTOMER_CODE, CUSTOMER_NAME, Term
            df = df.rename(columns={
                'customer_code': 'CUSTOMER_CODE',
                'customer_name': 'CUSTOMER_NAME',
                'payment_term_customer_name': 'Term'
            })
            
            # Sort by CUSTOMER_NAME
            df = df.sort_values('CUSTOMER_NAME')
            # Create display format [CODE] NAME
            df['Display'] = df.apply(lambda x: f"[{x['CUSTOMER_CODE']}] {x['CUSTOMER_NAME']}", axis=1)
            
            if 'Term' not in df.columns:
                df['Term'] = "N/A"
            
            return df[['CUSTOMER_CODE', 'CUSTOMER_NAME', 'Display', 'Term']]
        
        # Fallback to local file if Supabase is empty
        file_path = "Master/Master Customer.xlsx"
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            df = df.rename(columns={'PAYMENTTERMCUSTOMERNAME': 'Term'})
            df = df.sort_values('CUSTOMER_NAME')
            df['Display'] = df.apply(lambda x: f"[{x['CUSTOMER_CODE']}] {x['CUSTOMER_NAME']}", axis=1)
            return df[['CUSTOMER_CODE', 'CUSTOMER_NAME', 'Display', 'Term']]
            
        return pd.DataFrame(columns=['CUSTOMER_CODE', 'CUSTOMER_NAME', 'Display', 'Term'])
    except Exception as e:
        st.error(f"Error loading customer data from Supabase: {e}")
        return pd.DataFrame(columns=['CUSTOMER_CODE', 'CUSTOMER_NAME', 'Display', 'Term'])

@st.cache_data
def load_currency_data():
    """Load currency data from Supabase"""
    try:
        data = fetch_currencies()
        if data:
            # Supabase column name is 'code'
            return sorted([item['code'] for item in data if item.get('code')])
        
        # Fallback to local file
        file_path = "Master/MasterCurrency.xlsx"
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            code_col = 'รหัส (Code)'
            if code_col in df.columns:
                return sorted(df[code_col].dropna().unique().tolist())
        return ["USD", "THB", "EUR", "JPY"]
    except Exception as e:
        st.error(f"Error loading currency data from Supabase: {e}")
        return ["USD", "THB", "EUR", "JPY"]

@st.cache_data
def load_port_data():
    """Load port data from Supabase"""
    try:
        data = fetch_ports()
        if data:
            df = pd.DataFrame(data)
            # Map Supabase columns: main_port_name, country_code
            # App: Main Port Name, Country Code
            df = df.rename(columns={
                'main_port_name': 'Main Port Name',
                'country_code': 'Country Code'
            })
            
            # Sort by Main Port Name
            df = df.sort_values('Main Port Name')
            # Create display format [Country Code] Main Port Name
            df['Display'] = df.apply(lambda x: f"[{x['Country Code']}] {x['Main Port Name']}", axis=1)
            return df[['Country Code', 'Main Port Name', 'Display']]
        
        # Fallback to local file
        file_path = "Master/Master Port.csv"
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, encoding='utf-8-sig', low_memory=False)
            df = df.dropna(subset=['Main Port Name'])
            df = df.sort_values('Main Port Name')
            df['Display'] = df.apply(lambda x: f"[{x['Country Code']}] {x['Main Port Name']}", axis=1)
            return df[['Country Code', 'Main Port Name', 'Display']]
        return pd.DataFrame(columns=['Country Code', 'Main Port Name', 'Display'])
    except Exception as e:
        st.error(f"Error loading port data from Supabase: {e}")
        return pd.DataFrame(columns=['Country Code', 'Main Port Name', 'Display'])

# Load customer data
CUSTOMER_DF = load_customer_data()
CUSTOMER_LIST = CUSTOMER_DF['Display'].tolist()
CUSTOMER_MAP = dict(zip(CUSTOMER_DF['Display'], CUSTOMER_DF['CUSTOMER_CODE']))
CUSTOMER_TERMS_MAP = dict(zip(CUSTOMER_DF['Display'], CUSTOMER_DF['Term']))

CURRENCY_LIST = load_currency_data()

# Load port data
PORT_DF = load_port_data()
PORT_DISPLAY_LIST = PORT_DF['Display'].tolist()
PORT_MAP = dict(zip(PORT_DF['Display'], PORT_DF['Main Port Name']))

CUSTOMERS = CUSTOMER_LIST # For backward compatibility in other parts if needed

PAYMENT_LIST = ["T/T AFTER FAX", "T/T 30 DAYS", "L/C AT SIGHT", "CASH"]
DESTINATIONS = ["Bangkok", "Laem Chabang", "Singapore", "Hong Kong", "Tokyo", "Shanghai"]
RM_ITEMS = [f"HM {i}" for i in range(1, 21)]
SHIPMENT_MONTHS = ["Nov.25", "Dec.25", "Jan.26", "Feb.26"]

# Load data from Supabase
try:
    OH_DATA = {item['group_number']: float(item['overhead_rate']) for item in fetch_overhead()}
    if not OH_DATA:
        OH_DATA = {0: 0.10, 1: 0.34, 2: 0.51, 3: 0.57, 4: 0.64, 5: 0.97, 6: 1.59}
except Exception as e:
    st.error(f"Error loading Overhead from Supabase: {e}")
    OH_DATA = {0: 0.10, 1: 0.34, 2: 0.51, 3: 0.57, 4: 0.64, 5: 0.97, 6: 1.59}

try:
    factory_data = fetch_factory_expense()
    FACTORY_EXPENSE_DEFAULT = float(factory_data[0]['expense_rate']) if factory_data else 0.42
except Exception as e:
    st.error(f"Error loading Factory Expense from Supabase: {e}")
    FACTORY_EXPENSE_DEFAULT = 0.42

# Load Tiered Shipping Rates
try:
    SHIPPING_RATES = fetch_shipping_rates()
except Exception as e:
    st.error(f"Error loading Shipping Rates from Supabase: {e}")
    SHIPPING_RATES = []

# Load RM costs
try:
    RM_COSTS_DATA = fetch_rm_costs()
    RM_COSTS_DF = pd.DataFrame(RM_COSTS_DATA) if RM_COSTS_DATA else pd.DataFrame()
    # Unique product list for dropdown
    RM_LIST = sorted(list(set([item['product'] for item in RM_COSTS_DATA]))) if RM_COSTS_DATA else []
except Exception as e:
    st.error(f"Error loading RM Costs from Supabase: {e}")
    RM_LIST = []
    RM_COSTS_DATA = []

def get_rm_base_price(product, shipment_date_str):
    """Match RM price by product and closest update date."""
    if not RM_COSTS_DATA: return 0.0
    try:
        target_date = pd.to_datetime(shipment_date_str, format='%b.%y', errors='coerce')
        if pd.isna(target_date): return 0.0
        
        matches = [r for r in RM_COSTS_DATA if r['product'] == product]
        if not matches: return 0.0
        
        # Sort by date descending
        matches.sort(key=lambda x: x['update_date'], reverse=True)
        # Find the latest price that is on or before the target shipment date
        for r in matches:
            if pd.to_datetime(r['update_date']) <= target_date:
                return float(r['price'])
        # Fallback to the oldest if none match
        return float(matches[-1]['price'])
    except:
        return 0.0

def get_shipping_rate(qty):
    """Find the applicable rate for the given quantity from tiers."""
    for tier in SHIPPING_RATES:
        if tier['min_qty'] <= qty <= tier['max_qty']:
            return float(tier['price_per_container'])
    # If no tier found, use a default fallback or the last tier
    if SHIPPING_RATES:
        return float(SHIPPING_RATES[-1]['price_per_container'])
    return 1400.0 # Standard fallback

def generate_default_doc_no():
    """Generates CSYYYYMMDD-XXXX based on current count in DB."""
    today_str = datetime.now().strftime('%Y%m%d')
    prefix = f"CS{today_str}-"
    try:
        next_seq = get_next_doc_no_sequence(prefix)
        return f"{prefix}{next_seq:04d}"
    except Exception as e:
        print(f"Error generating doc_no: {e}")
        return f"{prefix}0001"

# --- UI START ---
st.title("📝 Cost Sheet Management System")

# --- 1. ข้อมูลทั่วไป ---
st.markdown('<div class="section-header">1. ข้อมูลทั่วไป (General Information)</div>', unsafe_allow_html=True)

# Row 1: Document & Trader & Team
# Row 1: Document & Trader & Team
c1_1, c1_2, c1_3, c1_4 = st.columns(4)
with c1_1:
    doc_no = st.text_input("Document No.", value=generate_default_doc_no())
    trader_name = st.text_input("ชื่อ Trader")
with c1_2:
    doc_date = st.date_input("Document Date (Conclude)", value=date.today())
    team = st.selectbox("Team", ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"])
with c1_3:
    cust1_display = st.selectbox("Customer1 (Importer)", CUSTOMER_LIST)
    cust1 = CUSTOMER_MAP.get(cust1_display, "")
    incoterm = st.selectbox("Incoterm", ["FOB", "CFR", "CIF", "EXW", "DDP"])
with c1_4:
    cust2_display = st.selectbox("Customer 2 (End Customer)", [""] + CUSTOMER_LIST)
    cust2 = CUSTOMER_MAP.get(cust2_display, "")

c5, c6 = st.columns(2)
with c5:
    ship_from = st.date_input("Shipment Date from", value=doc_date)
with c6:
    ship_to = st.date_input("Shipment Date to", value=date(2026, 5, 30))

st.markdown("##### Exchange Rate Details")
r1, r2, r3, r4, r5 = st.columns([1.5, 1.5, 1.5, 1.5, 1.5]) 
with r1:
    currency = st.selectbox("Currency", CURRENCY_LIST)

# Helper to fetch rate
def get_yahoo_rate(pair="THB=X"):
    try:
        ticker = yf.Ticker(pair)
        hist = ticker.history(period="1d")
        if not hist.empty:
            return hist["Close"].iloc[-1]
    except Exception as e:
        st.error(f"Error fetching rate: {e}")
    return None

with r2:
    if st.button("Get Spot Rate (Yahoo)"):
        # Map currency to ticker (Approximation)
        ticker_map = {"USD": "THB=X", "EUR": "EURTHB=X", "JPY": "JPYTHB=X"} 
        target_ticker = ticker_map.get(currency, "THB=X")
        fetched_rate = get_yahoo_rate(target_ticker)
        if fetched_rate:
            st.session_state['spot_val'] = fetched_rate
            st.success(f"Fetched: {fetched_rate:.4f}")
            
    # Use session state for spot rate
    if 'spot_val' not in st.session_state:
        st.session_state['spot_val'] = 34.00
    
    spot_rate = st.number_input("Spot Rate", value=st.session_state['spot_val'], format="%.4f")

with r3:
    discount_rate = st.number_input("(-) Discount Rate", value=0.00, format="%.4f")
with r4:
    premium_rate = st.number_input("(+) Premium Rate", value=0.50, format="%.4f")
with r5:
    # Auto-calc
    default_ex = spot_rate - discount_rate + premium_rate
    ex_rate = st.number_input("Exchange Rate", value=default_ex, format="%.4f")

# Destination Section (4 destinations)
st.markdown("##### Destination")
dest_col1, dest_col2, dest_col3, dest_col4 = st.columns(4)
with dest_col1:
    dest1_display = st.selectbox("Destination 1", [""] + PORT_DISPLAY_LIST, key="dest1_sel")
    destination1 = PORT_MAP.get(dest1_display, "")
with dest_col2:
    dest2_display = st.selectbox("Destination 2", [""] + PORT_DISPLAY_LIST, key="dest2_sel")
    destination2 = PORT_MAP.get(dest2_display, "")
with dest_col3:
    dest3_display = st.selectbox("Destination 3", [""] + PORT_DISPLAY_LIST, key="dest3_sel")
    destination3 = PORT_MAP.get(dest3_display, "")
with dest_col4:
    dest4_display = st.selectbox("Destination 4", [""] + PORT_DISPLAY_LIST, key="dest4_sel")
    destination4 = PORT_MAP.get(dest4_display, "")

# --- 2. Export Expense & Freight ---
st.markdown('<div class="section-header">2. ค่าใช้จ่ายส่งออก (Export Expense & Freight)</div>', unsafe_allow_html=True)
st.markdown('<div class="warning-text">⚠️ Export Expense** ค่าใช้จ่าย Export Expense เป็นค่าใช้จ่ายตามมาตรฐาน สามารถปรับได้ตามเกิดขึ้นจริง</div>', unsafe_allow_html=True)

# Insurance Section
st.write("**Insurance**")
ins_type = st.radio("เงื่อนไขประกัน", [
    "Non Africa: FOB/CFR (125% x Selling Price x 0.000098)", 
    "Non Africa: CIF (110% x Selling Price x 0.00049)",
    "Africa: FOB/CFR (125% x Selling Price x 0.000446)",
    "Africa: CIF (110% x Selling Price x 0.00223)"
], horizontal=True)

# Placeholder for calculated insurance display
ins_display = st.empty()
st.write("---")

# Container & Invoice Info
col_size, col_cnt, col_inv, col_ton = st.columns([1.5, 1, 1, 1])
with col_size:
    container_size = st.selectbox("ขนาดตู้ Container", ['20"', '40"', '20" High Cube'])
with col_cnt:
    container_qty = st.number_input("จำนวนตู้ส่งออก (Container)", min_value=1, value=1)
with col_inv:
    invoice_qty = st.number_input("จำนวน Invoice", min_value=1, value=1)
with col_ton:
    ton_per_container = st.number_input("จำนวน Ton/ตู้", min_value=0.0, value=25.0, format="%.2f")

# Group 1: Freight
st.markdown('<div class="sub-section"><b>1. Freight (ค่าระวางเรือ)</b></div>', unsafe_allow_html=True)
v_freight = st.number_input("Freight (ค่าระวางเรือระหว่างประเทศ)", value=0.0)

# Group 2: Export Expense
st.markdown('<div class="sub-section"><b>2. Export Expense (ค่าใช้จ่ายส่งออกตามกลุ่ม)</b></div>', unsafe_allow_html=True)
e_col1, e_col2 = st.columns(2)

with e_col1:
    st.write("**Shipping & Transport**")
    # Tiered Shipping Rate Calculation
    applicable_rate = get_shipping_rate(container_qty)
    v_shipping = st.number_input(f"ค่า Shipping ({applicable_rate:,.0f} บาท/ตู้)", value=float(container_qty * applicable_rate))
    v_truck = st.number_input("ค่าขนย้าย-ส่งออก: หัวลาก/ผ่านท่า (8,300 บ./ตู้)", value=float(container_qty * 8300))
    
    st.write("**Survey & Inspection**")
    v_survey_check = st.number_input("ค่าตรวจสอบ + รมยา (1,050 บาท/ตู้)", value=float(container_qty * 1050))
    v_survey_vehicle = st.number_input("ค่าพาหนะไปรมยา (1,350 บาท/Inv)", value=float(invoice_qty * 1350))
    


with e_col2:
    st.write("**Port Charges (ค่าระวางส่งออก)**")
    v_thc = st.number_input("THC ค่าดำเนินการในท่าเรือต้นทาง (2,800 บาท/ตู้)", value=float(container_qty * 2800))
    v_seal = st.number_input("Seal ค่าอุปกรณ์ล๊อคประตูตู้ (300 บาท/ตู้)", value=float(container_qty * 300))
    v_bl_fee = st.number_input("B/L Fee ค่าเอกสาร B/L (2,000 บาท/Inv)", value=float(invoice_qty * 2000))
    v_handling = st.number_input("Handling Charges ค่าดำเนินการ (1,000 บาท/Inv)", value=float(invoice_qty * 1000))

# Documents Section
st.markdown('<div class="sub-section"><b>3. ค่าเอกสารส่งออก (Export Documents)</b></div>', unsafe_allow_html=True)
doc_col1, doc_col2 = st.columns(2)
with doc_col1:
    v_doc_prep = st.number_input("ค่าจัดทำเอกสาร (5,500 บ./Inv)", value=float(invoice_qty * 5500))
    v_doc_agri = st.number_input("ค่าพาหนะจนท.เกษตร (1,000 บาท/Inv)", value=float(invoice_qty * 1000))
    v_doc_phyto = st.number_input("ค่าป่วยการใบรับรองปลอดศัตรูพืช (200 บาท/Inv)", value=float(invoice_qty * 200))
    v_doc_health = st.number_input("HEALTH CERTIFICATE (300 บาท/Inv)", value=float(invoice_qty * 300))
    v_doc_origin = st.number_input("ค่าใบรับรองแหล่งกำเนิดสินค้า (208 บาท/Inv)", value=float(invoice_qty * 208))
with doc_col2:
    v_doc_ms24 = st.number_input("ค่าแบบพิมพ์/ค่าธรรมเนียม มส.24 (120 บาท/Inv)", value=float(invoice_qty * 120))
    v_doc_chamber = st.number_input("ค่าใบรับรองเอกสารสภาหอการค้า (230 บาท/Inv)", value=float(invoice_qty * 230))
    v_doc_dft = st.number_input("ค่าใบรับรองกรมการค้าต่างประเทศ (30 บาท/Inv)", value=float(invoice_qty * 30))

# Other Expenses - 10 lines table
st.markdown('<div class="sub-section"><b>4. ค่าใช้จ่ายอื่นๆ</b></div>', unsafe_allow_html=True)
if 'other_expenses_data' not in st.session_state:
    other_exp_init = []
    for i in range(10):
        other_exp_init.append({
            "ลำดับ": i + 1,
            "รายการค่าใช้จ่าย": "",
            "จำนวนเงิน (USD/Ton)": 0.0
        })
    st.session_state.other_expenses_data = pd.DataFrame(other_exp_init)

other_exp_cfg = {
    "ลำดับ": st.column_config.NumberColumn(disabled=True, width="small"),
    "รายการค่าใช้จ่าย": st.column_config.TextColumn(width="large"),
    "จำนวนเงิน (USD/Ton)": st.column_config.NumberColumn(format="%.2f", width="medium")
}

other_expenses_df = st.data_editor(
    st.session_state.other_expenses_data,
    column_config=other_exp_cfg,
    num_rows="fixed",
    use_container_width=True,
    hide_index=True,
    key="other_expenses_editor"
)

# Calculate total other expenses
other_expense_value = other_expenses_df["จำนวนเงิน (USD/Ton)"].sum()

# Calculate totals
port_charges_total = v_thc + v_seal + v_bl_fee + v_handling
survey_total = v_survey_check + v_survey_vehicle
docs_total = v_doc_agri + v_doc_phyto + v_doc_health + v_doc_origin + v_doc_ms24 + v_doc_chamber + v_doc_dft

# --- 3. Interest & Storage ---
st.markdown('<div class="section-header">3. ดอกเบี้ยและคลังสินค้า (Interest & WH Storage)</div>', unsafe_allow_html=True)
i_col1, i_col2 = st.columns(2)

with i_col1:
    st.write("**AR Interest**")
    # Auto fill payment term
    # AR Interest calculation usually needs a customer lookup
    ar_customer_display = st.selectbox("เลือก Customer (จากลิสต์)", CUSTOMER_LIST, key="ar_cust")
    ar_customer_code = CUSTOMER_MAP.get(ar_customer_display, "")
    p_term_auto = CUSTOMER_TERMS_MAP.get(ar_customer_display, "N/A")
    st.info(f"Payment Term (Auto): {p_term_auto}")
    
    p_term_ship = st.selectbox("Payment Term For Shipment", PAYMENT_LIST)
    ar_rate = st.number_input("AR Interest Rate (%) (STD.2.4%)", value=0.0, key="ar_r")
    ar_days = st.number_input("AR Interest Day (วัน)", value=0, key="ar_d")

with i_col2:
    st.write("**RM Interest & WH Storage**")
    rm_rate = st.number_input("RM Interest Rate (%) (STD.2.5%)", value=0.0, key="rm_r")
    rm_days = st.number_input("RM Interest Day (วัน)", value=0, key="rm_d")
    
    st.write("---")
    wh_days = st.number_input("WH Storage Day (วัน) (30 บาท/เดือน/Ton)", value=30)
    # Calculation for WH Storage: 30 THB / Ton / Month (Assume 30 days = 1 month)
    # Will calculate in final step based on total quantity

# --- 4. Details & Production Cost ---
st.markdown('<div class="section-header">4. รายละเอียดสินค้าและต้นทุนผลิต (Production Cost)</div>', unsafe_allow_html=True)
st.info("กรุณากรอกข้อมูลสินค้า (สามารถเพิ่มรายการได้สูงสุด 15 รายการ)")

# Yield Loss % - default value (ไม่แสดงใน UI)
yield_loss_pct = 0.0

# Initialize Data v3 - ตามคอลัมน์จาก Master.xlsx sheet "ข้อมูลที่แสดงในหัวข้อที่ 4"
# คอลัมน์ที่ต้องกรอก: Item, Product Name, Product RM, ราคา RM, PACKAGING, Group (0-6), Overhead (auto), Quantity, Factory Expense (auto), Commision, A&P, Agreement, Selling Price
# คอลัมน์คำนวณ (แสดงในสรุป): Yield loss, Yield loss %, Freight, Export Expense, Total Cost, MarginCost, AR Interest, RM Interest, WH Storage, MarginCost After

# Show loaded values from Master.xlsx
st.info(f"📊 ค่าจาก Master.xlsx: Factory Expense = {FACTORY_EXPENSE_DEFAULT:.2f} | Overhead Groups: {list(OH_DATA.keys())}")

if 'cost_data_v3' not in st.session_state:
    # 15 Rows init, matching Master Input columns
    init_data = []
    for i in range(15):
        init_data.append({
            "Item": i+1,
            "Product Name": f"Product {i+1}" if i==0 else "",
            "Product RM": "",
            "Group": 0,
            "PACKAGING": 0.0,
            "Brand": "",
            "Pack Size": "",
            "Quantity": 0.0,
            "Commision": 0.0,
            "A&P": 0.0,
            "Agreement": 0.0,
            "Other Cost": 0.0,
            "Selling Price": 0.0
        })
    st.session_state.cost_data_v3 = pd.DataFrame(init_data)

# Config for Editor - Matching Master Input editable fields
column_cfg = {
    "Item": st.column_config.NumberColumn(disabled=True, width="small"),
    "Product Name": st.column_config.TextColumn(width="medium"),
    "Product RM": st.column_config.SelectboxColumn(options=RM_LIST, width="medium"),
    "Group": st.column_config.SelectboxColumn(options=[0,1,2,3,4,5,6], width="small", help="Overhead Group (0-6)"),
    "PACKAGING": st.column_config.NumberColumn(format="%.4f", width="small"),
    "Brand": st.column_config.TextColumn(width="small"),
    "Pack Size": st.column_config.TextColumn(width="small"),
    "Quantity": st.column_config.NumberColumn(format="%.2f", width="small"),
    "Commision": st.column_config.NumberColumn(format="%.4f", width="small"),
    "A&P": st.column_config.NumberColumn(format="%.4f", width="small"),
    "Agreement": st.column_config.NumberColumn(format="%.4f", width="small"),
    "Other Cost": st.column_config.NumberColumn(format="%.4f", width="small"),
    "Selling Price": st.column_config.NumberColumn(format="%.4f", width="small")
}

# Apply auto-lookup: Update Overhead based on Group selection
for idx in range(len(st.session_state.cost_data_v3)):
    group_val = st.session_state.cost_data_v3.loc[idx, "Group"]
    st.session_state.cost_data_v3.loc[idx, "Overhead"] = OH_DATA.get(group_val, 0.0)
    st.session_state.cost_data_v3.loc[idx, "Factory Expense"] = FACTORY_EXPENSE_DEFAULT

# Ensure stable order for Section 4
st.session_state.cost_data_v3 = st.session_state.cost_data_v3.sort_values("Item")

edited_df = st.data_editor(
    st.session_state.cost_data_v3,
    column_config=column_cfg,
    num_rows="fixed", 
    use_container_width=True,
    hide_index=True, 
    key="cost_editor_v3"
)

# Keep session state in sync
st.session_state.cost_data_v3 = edited_df

# After editing, update Overhead based on new Group values
for idx in edited_df.index:
    group_val = edited_df.loc[idx, "Group"]
    edited_df.loc[idx, "Overhead"] = OH_DATA.get(group_val, 0.0)
    edited_df.loc[idx, "Factory Expense"] = FACTORY_EXPENSE_DEFAULT



# --- CALCULATIONS BASED ON MASTER CALCULATOR ---
total_qty_all = edited_df["Quantity"].sum()
results = []

# Insurance Calculation Logic (Automated)
# Moved here because it depends on edited_df (Products Table)
ins_multipliers = {
    "Non Africa: FOB/CFR (125% x Selling Price x 0.000098)": 1.25 * 0.000098,
    "Non Africa: CIF (110% x Selling Price x 0.00049)": 1.10 * 0.00049,
    "Africa: FOB/CFR (125% x Selling Price x 0.000446)": 1.25 * 0.000446,
    "Africa: CIF (110% x Selling Price x 0.00223)": 1.10 * 0.00223
}

multiplier = ins_multipliers.get(ins_type, 0.0)
total_selling_thb = (edited_df["Selling Price"] * edited_df["Quantity"]).sum() * ex_rate
v_insurance = total_selling_thb * multiplier

# Update the display in Section 2 (using placeholder defined earlier)
ins_display.info(f"**ค่าเบี้ยประกันส่งออก (Insurance) คำนวณอัตโนมัติ:** {v_insurance:,.2f} บาท")

# Total Export Expenses Combined (THB)
total_export_exp_combined = (v_freight + v_shipping + v_truck + survey_total + v_insurance + 
                              docs_total + v_doc_prep + port_charges_total + other_expense_value)

# Fetch Overhead table for Yield Loss and rate
overhead_table = fetch_overhead()
oh_yield_map = {item['group_number']: (float(item['overhead_rate']), float(item['yield_loss_percent'])) for item in overhead_table}

for index, row in edited_df.iterrows():
    qty = row.get("Quantity", 0.0)
    prod_rm = row.get("Product RM", "")
    
    # Filter empty rows
    if qty <= 0 and not row.get("Product Name") and not prod_rm:
        continue

    # 1. RM Price Lookup & Conversion
    # Formula: ((Auto look up price)*1000)/Exchange Rate
    base_price = get_rm_base_price(prod_rm, doc_date.strftime('%b.%y'))
    rm_price = (base_price * 1000 / ex_rate) if ex_rate > 0 else (base_price * 1000)
    
    # 2. Yield Loss Lookup
    g_num = row.get("Group", 0)
    oh_rate, y_loss_pct = oh_yield_map.get(g_num, (0.0, 0.0))
    # Note: In Master Calculator example, Group 3 has y_loss_pct = 0.95 and Yield loss = Price / 0.95
    yield_loss_cost = (rm_price / y_loss_pct) if y_loss_pct > 0 else rm_price
    
    # 3. BP = (Yield loss - RM Price) / 3
    bp_val = (yield_loss_cost - rm_price) / 3
    
    # 4. RM Net Yield = Yield loss - BP
    rm_net_yield = yield_loss_cost - bp_val
    
    # 5. PACKAGING, Overhead, Factory Expense (already converted in Master Calculator? no, usually per unit)
    # The image/Excel suggests these are also unit costs.
    # Overhead: Auto lookup and convert: (Rate * 1000) / Exchange Rate
    overhead_val = (oh_rate * 1000 / ex_rate) if ex_rate > 0 else (oh_rate * 1000)
    # Factory Expense: Auto from master and convert: (Rate * 1000) / Exchange Rate
    factory_exp_val = (FACTORY_EXPENSE_DEFAULT * 1000 / ex_rate) if ex_rate > 0 else (FACTORY_EXPENSE_DEFAULT * 1000)
    
    # 6. Export Expense (Unit)
    # Formula: ((Export Expense + Documents + ...)/Exchange Rate)/Quantity
    unit_export_exp = 0.0
    if total_qty_all > 0 and ex_rate > 0:
        unit_export_exp = (total_export_exp_combined / total_qty_all) / ex_rate
    
    # Other components
    c_pkg = row.get("PACKAGING", 0.0)
    c_comm = row.get("Commision", 0.0)
    c_ap = row.get("A&P", 0.0)
    c_agree = row.get("Agreement", 0.0)
    c_other = row.get("Other Cost", 0.0)
    selling = row.get("Selling Price", 0.0)

    # 7. Total Cost
    # RM Net Yield+ PACKAGING+ Overhead+ Factory Expense+ Freight+ Export Expense+Commission+ A&P+Agreemen+ Other Cost
    total_cost = (rm_net_yield + c_pkg + overhead_val + factory_exp_val + 
                  unit_export_exp + c_comm + c_ap + c_agree + c_other)
    
    # 8. MarginCost
    margin_cost = selling - total_cost
    
    # 9. Interests (Per Unit) - Based on Master Calculator.xlsx formulas
    # Formula: ((Selling Price * Rate %) / 365) * Days
    unit_ar_int = (selling * (ar_rate / 100) / 365) * ar_days if ar_days > 0 else 0.0
    unit_rm_int = (selling * (rm_rate / 100) / 365) * rm_days if rm_days > 0 else 0.0
    
    # 10. WH Storage (Total for the container/lot)
    # Formula in Master Calculator: (WH Storage Day * Quantity * (30/30)) / Exchange Rate
    # Note: (30/30) appears to be 1 Baht per Ton per Day.
    total_wh_storage = (wh_days * qty * 1.0) / ex_rate if (qty > 0 and ex_rate > 0) else 0.0
    
    # 11. Margin After (Per Unit) - Following Excel formula exactly: 
    # Formula: MarginCost - AR Interest - RM Interest - WH Storage
    # Note: Excel subtracts the TOTAL storage from the UNIT margin.
    margin_after_unit = margin_cost - unit_ar_int - unit_rm_int - total_wh_storage
    
    # Also calculate totals for the summary table
    total_ar_int = unit_ar_int * qty
    total_rm_int = unit_rm_int * qty
    margin_after_total = margin_after_unit * qty

    results.append({
        "Item": row["Item"],
        "Product Name": row["Product Name"],
        "Product RM": prod_rm,
        "RM Price": round(rm_price, 4),
        "Group (0-6)": g_num,
        "Yield loss %": y_loss_pct,
        "Yield loss": round(yield_loss_cost, 4),
        "BP": round(bp_val, 4),
        "RM Net Yield": round(rm_net_yield, 4),
        "PACKAGING": c_pkg,
        "Brand": row["Brand"],
        "Pack Size": row["Pack Size"],
        "Overhead": round(overhead_val, 4),
        "Quantity": qty,
        "Factory Expense": round(factory_exp_val, 4),
        "Export Expense": round(unit_export_exp, 4),
        "Commision": c_comm,
        "A&P": c_ap,
        "Agreement": c_agree,
        "Other Cost": c_other,
        "Total Cost": round(total_cost, 4),
        "Selling Price": selling,
        "MarginCost (Unit)": round(margin_cost, 4),
        "AR Interest (Unit)": round(unit_ar_int, 4),
        "RM Interest (Unit)": round(unit_rm_int, 4),
        "WH Storage (Total)": round(total_wh_storage, 4),
        "Margin After (Unit)": round(margin_after_unit, 4)
    })


summary_df = pd.DataFrame(results)

if not summary_df.empty:
    st.write("---")
    st.subheader("สรุปต้นทุนและกำไร (Cost & Margin Summary)")
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # Grand Totals
    grand_total_cost = (summary_df["Total Cost"] * edited_df.loc[summary_df.index, "Quantity"]).sum()
    grand_total_curr = grand_total_cost / ex_rate if ex_rate > 0 else 0
    
    st.markdown(f"""
    <div class="total-card">
        <h3>Grand Total Cost: {grand_total_curr:,.2f} {currency}</h3>
    </div>
    """, unsafe_allow_html=True)

# --- Remark Section (20 lines) - Moved to end ---
st.markdown('<div class="remark-section"><b>📝 Remark</b></div>', unsafe_allow_html=True)
if 'remark_data' not in st.session_state:
    st.session_state.remark_data = pd.DataFrame({
        "No.": list(range(1, 21)),
        "Remark": [""] * 20
    })

remark_cfg = {
    "No.": st.column_config.NumberColumn(disabled=True, width="small"),
    "Remark": st.column_config.TextColumn(width="large")
}

remark_df = st.data_editor(
    st.session_state.remark_data,
    column_config=remark_cfg,
    num_rows="fixed",
    use_container_width=True,
    hide_index=True,
    key="remark_editor"
)

# --- Loading Table (จัดโหลด) 15 rows x 7 columns - Moved to end ---
st.markdown('<div class="loading-section"><b>📦 จัดโหลด (Loading)</b></div>', unsafe_allow_html=True)
if 'loading_data' not in st.session_state:
    loading_init = []
    for i in range(15):
        loading_init.append({
            "No.": i + 1,
            "รายการสินค้า": "",
            "จำนวน (ลัง/กล่อง)": 0,
            "น้ำหนัก/หน่วย (KG)": 0.0,
            "น้ำหนักรวม (KG)": 0.0,
            "ตู้ที่": "",
            "หมายเหตุ": ""
        })
    st.session_state.loading_data = pd.DataFrame(loading_init)

loading_cfg = {
    "No.": st.column_config.NumberColumn(disabled=True, width="small"),
    "รายการสินค้า": st.column_config.TextColumn(width="medium"),
    "จำนวน (ลัง/กล่อง)": st.column_config.NumberColumn(format="%d", width="small"),
    "น้ำหนัก/หน่วย (KG)": st.column_config.NumberColumn(format="%.2f", width="small"),
    "น้ำหนักรวม (KG)": st.column_config.NumberColumn(format="%.2f", width="small"),
    "ตู้ที่": st.column_config.TextColumn(width="small"),
    "หมายเหตุ": st.column_config.TextColumn(width="medium")
}

# Ensure stable order for Loading Table
st.session_state.loading_data = st.session_state.loading_data.sort_values("No.")

loading_df = st.data_editor(
    st.session_state.loading_data,
    column_config=loading_cfg,
    num_rows="fixed",
    use_container_width=True,
    hide_index=True,
    key="loading_editor"
)

# Keep session state in sync
st.session_state.loading_data = loading_df

# --- Save Section ---
st.markdown("---")
st.header("💾 บันทึกข้อมูล (Save Data)")

if st.button("Save to Database", type="primary"):
    try:
        from supabase_client import save_quotation
        
        # 1. Prepare Header Data (trx_general_infos)
        # Note: Ensure all variables (doc_no, cust1, etc.) are available from earlier in the script
        general_info = {
            "doc_no": doc_no,
            "doc_date": str(doc_date),
            "trader_name": trader_name,
            "team": team,
            "customer_importer": cust1,
            "customer_end_user": cust2,
            "incoterm": incoterm,

            "ship_date_from": str(ship_from),
            "ship_date_to": str(ship_to),
            "currency": currency,
            "spot_rate": spot_rate,
            "discount_rate": discount_rate,
            "premium_rate": premium_rate,
            "exchange_rate": ex_rate,
            "dest_1": destination1,
            "dest_2": destination2,
            "dest_3": destination3,
            "dest_4": destination4
        }
        
        # 2. Prepare Export Expense Data (trx_export_expenses)
        export_expenses = {
            "container_size": container_size,
            "container_qty": int(container_qty),
            "invoice_qty": int(invoice_qty),
            "ton_per_container": ton_per_container,
            "freight_cost": v_freight,
            "shipping_cost": v_shipping,
            "truck_cost": v_truck,
            "survey_check_cost": v_survey_check,
            "survey_vehicle_cost": v_survey_vehicle,
            "insurance_cost": v_insurance,
            "thc_cost": v_thc,
            "seal_cost": v_seal,
            "bl_fee": v_bl_fee,
            "handling_fee": v_handling,
            "doc_prep_fee": v_doc_prep,
            "doc_agri_fee": v_doc_agri,
            "doc_phyto_fee": v_doc_phyto,
            "doc_health_fee": v_doc_health,
            "doc_origin_fee": v_doc_origin,
            "doc_ms24_fee": v_doc_ms24,
            "doc_chamber_fee": v_doc_chamber,
            "doc_dft_fee": v_doc_dft
        }
        
        # 3. Prepare Interest Data (trx_interests)
        interests = {
            "payment_term_auto": p_term_auto,
            "payment_term_ship": p_term_ship,
            "ar_rate": ar_rate,
            "ar_days": int(ar_days),
            "rm_rate": rm_rate,
            "rm_days": int(rm_days),
            "wh_days": int(wh_days)
        }
        
        # 4. Prepare Production Costs (trx_production_costs) mapped from results
        production_costs = []
        for r in results:
            item = {
                "item_order": r["Item"],
                "product_name": r["Product Name"],
                "product_rm": r["Product RM"],
                "rm_price_snapshot": r["RM Price"],
                "yield_loss_pct": r["Yield loss %"],
                "yield_loss_val": r["Yield loss"],
                "bp_val": r["BP"],
                "rm_net_yield": r["RM Net Yield"],
                "packaging": r["PACKAGING"],
                "brand": r["Brand"],
                "pack_size": r["Pack Size"],
                "overhead_group": r["Group (0-6)"],
                "overhead_val": r["Overhead"],
                "quantity": r["Quantity"],
                "factory_expense": r["Factory Expense"],
                "freight_val": 0.0, # Not explicitly in results dict, handled in export expense usually, or calculated
                "export_expense": r["Export Expense"],
                "commission": r["Commision"],
                "ap_expense": r["A&P"],
                "agreement": r["Agreement"],
                "other_cost": r["Other Cost"],
                "total_cost": r["Total Cost"],
                "selling_price": r["Selling Price"],
                "margin_cost": r["MarginCost (Unit)"],
                "ar_interest": r["AR Interest (Unit)"],
                "rm_interest": r["RM Interest (Unit)"],
                "wh_storage": r["WH Storage (Total)"],
                "margin_after": r["Margin After (Unit)"],
                "status": "Draft"
            }
            production_costs.append(item)
            
        # 5. Prepare Loadings
        loadings = []
        for idx, row in loading_df.iterrows():
            if row["รายการสินค้า"]: # Only add if product name exists
                loadings.append({
                    "order_no": row["No."],
                    "product_name": row["รายการสินค้า"],
                    "qty_cartons": int(row["จำนวน (ลัง/กล่อง)"]),
                    "weight_per_unit": float(row["น้ำหนัก/หน่วย (KG)"]),
                    "total_weight": float(row["น้ำหนักรวม (KG)"]),
                    "container_no": row["ตู้ที่"],
                    "remark": row["หมายเหตุ"]
                })
                
        # 6. Prepare Remarks
        remarks = []
        for idx, row in remark_df.iterrows():
            if row["Remark"]:
                remarks.append({
                    "order_no": row["No."],
                    "remark_text": row["Remark"]
                })

        # Bundle everything
        full_data = {
            "general_info": general_info,
            "export_expenses": export_expenses,
            "interests": interests,
            "production_costs": production_costs,
            "loadings": loadings,
            "remarks": remarks
        }
        
        # Call API
        quotation_id = save_quotation(full_data)
        st.success(f"✅ Saved successfully! Quotation ID: {quotation_id}")
        st.balloons()
        
    except Exception as e:
        st.error(f"❌ Error saving data: {str(e)}")

st.write("---")
if st.button("💾 บันทึกเอกสาร Cost Sheet", use_container_width=True):
    st.success(f"บันทึกข้อมูล {doc_no} เรียบร้อยแล้ว")