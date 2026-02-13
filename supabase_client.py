"""
Supabase Client Module for Quotation App
Provides connection and helper functions for Supabase database operations.
"""

import os
from dotenv import load_dotenv
from postgrest import SyncPostgrestClient
import streamlit as st

# Load environment variables
load_dotenv()

# Supabase configuration
# Prioritize Streamlit Secrets, fallback to environment variables
SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")


def get_postgrest_client() -> SyncPostgrestClient:
    """Get a PostgREST client for Supabase database operations."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        error_msg = (
            "SUPABASE_URL and SUPABASE_KEY are missing. "
            "Local: Set in .env file. "
            "Streamlit Cloud: Set in App Settings -> Secrets."
        )
        raise ValueError(error_msg)
    
    rest_url = f"{SUPABASE_URL}/rest/v1"
    return SyncPostgrestClient(
        rest_url,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
    )


@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_customers():
    """Fetch all customers from Supabase."""
    client = get_postgrest_client()
    response = client.from_("master_customers").select("*").execute()
    return response.data


@st.cache_data(ttl=3600)
def fetch_currencies():
    """Fetch all currencies from Supabase."""
    client = get_postgrest_client()
    response = client.from_("master_currencies").select("*").execute()
    return response.data


@st.cache_data(ttl=3600)
def fetch_ports():
    """Fetch all ports from Supabase."""
    client = get_postgrest_client()
    response = client.from_("master_ports").select("*").execute()
    return response.data


@st.cache_data(ttl=3600)
def fetch_overhead():
    """Fetch overhead rates from Supabase."""
    client = get_postgrest_client()
    response = client.from_("master_overhead").select("*").execute()
    return response.data


@st.cache_data(ttl=3600)
def fetch_factory_expense():
    """Fetch factory expense rates from Supabase."""
    client = get_postgrest_client()
    response = client.from_("master_factory_expense").select("*").execute()
    return response.data




@st.cache_data(ttl=3600)
def fetch_shipping_rates():
    """Fetch tiered shipping rates from Supabase."""
    client = get_postgrest_client()
    response = client.from_("shipping_rates").select("*").order("min_qty").execute()
    return response.data


@st.cache_data(ttl=3600)
def fetch_rm_costs():
    """Fetch RM costs from Supabase."""
    client = get_postgrest_client()
    response = client.from_("master_rm_cost").select("*").order("update_date", desc=True).execute()
    return response.data


@st.cache_data(ttl=3600)
def fetch_calculator_specs():
    """Fetch calculator specifications from Supabase."""
    client = get_postgrest_client()
    response = client.from_("master_calculator").select("*").order("id").execute()
    return response.data


def get_overhead_by_group(group_number: int) -> float:
    """Get overhead rate for a specific group number."""
    overheads = fetch_overhead()
    for item in overheads:
        if item.get('group_number') == group_number:
            return item.get('overhead_rate', 0.0)
    return 0.0


def get_yield_loss_by_group(group_number: int) -> float:
    """Get yield loss percentage for a specific group number from master_overhead."""
    overheads = fetch_overhead()
    for item in overheads:
        if item.get('group_number') == group_number:
            return float(item.get('yield_loss_percent', 0.0))
    return 0.0


def save_quotation(data: dict) -> str:
    """
    Save the full quotation data to Supabase (6 tables).
    Uses Upsert for Header (on doc_no) to allow overwriting/retrying.
    """
    client = get_postgrest_client()
    
    # 1. Upsert Header (trx_general_infos)
    print("Saving/Updating Header...")
    general_info = data.get("general_info", {})
    # Use upsert with on_conflict if supported, or just upsert (PostgREST handles UNIQUE)
    res_hdr = client.from_("trx_general_infos").upsert(general_info, on_conflict="doc_no").execute()
    
    if not res_hdr.data:
        raise Exception("Failed to save header information")
        
    quotation_id = res_hdr.data[0]['id']
    print(f"Header ID: {quotation_id}")
    
    # 1.1 Clean up existing details (to avoid duplicates on upsert/retry)
    detail_tables = [
        "trx_export_expenses", "trx_interests", "trx_production_costs", 
        "trx_loadings", "trx_remarks"
    ]
    print("Cleaning up old details...")
    for table in detail_tables:
        client.from_(table).delete().eq("quotation_id", quotation_id).execute()

    # Helper to add quote_id and insert
    def insert_related(table, items, is_list=True):
        if not items:
            return
        
        # Prepare payload
        payload = items if is_list else [items]
        
        # Inject foreign key
        for item in payload:
            item['quotation_id'] = quotation_id
            
        print(f"Saving to {table}...")
        client.from_(table).insert(payload).execute()

    try:
        # 2. Insert Export Expenses
        insert_related("trx_export_expenses", data.get("export_expenses", {}), is_list=False)
        
        # 3. Insert Interests
        insert_related("trx_interests", data.get("interests", {}), is_list=False)
        
        # 4. Insert Product Costs
        insert_related("trx_production_costs", data.get("production_costs", []), is_list=True)
        
        # 5. Insert Loadings
        insert_related("trx_loadings", data.get("loadings", []), is_list=True)
        
        # 6. Insert Remarks
        insert_related("trx_remarks", data.get("remarks", []), is_list=True)
        
        return quotation_id
        
    except Exception as e:
        print(f"Error saving quotation details: {e}")
        raise e


def fetch_quotations():
    """Fetch all quotations header info for the dashboard."""
    client = get_postgrest_client()
    # Select all columns to ensure we get what exists. 
    # Note: 'status' and 'total_cost' are currently NOT in the header table schema, 
    # so they will be missing. Logic in Home.py should handle this.
    response = client.from_("trx_general_infos").select("*").order("created_at", desc=True).execute()
    return response.data

def delete_quotation(quotation_id: str):
    """Delete a quotation and all its related data (Cascade)."""
    client = get_postgrest_client()
    # Supabase cascade delete should handle the relations if set up, 
    # but our migration script said 'ON DELETE CASCADE', so we just delete header.
    client.from_("trx_general_infos").delete().eq("id", quotation_id).execute()
def get_next_doc_no_sequence(prefix: str) -> int:
    """
    Get the next sequence number for a given Document No. prefix (e.g. CS20260212-).
    """
    client = get_postgrest_client()
    # Find all documents starting with the prefix
    response = client.from_("trx_general_infos") \
        .select("doc_no") \
        .like("doc_no", f"{prefix}%") \
        .execute()
    
    if not response.data:
        return 1
    
    # Extract the sequence part and find the max
    sequences = []
    for item in response.data:
        try:
            # Assuming format prefixXXXX where prefix is like CS20260212-
            seq_str = item['doc_no'].replace(prefix, "")
            sequences.append(int(seq_str))
        except:
            continue
            
    if not sequences:
        return 1
        
    return max(sequences) + 1
