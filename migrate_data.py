"""
Migration Script: Upload Master Data to Supabase (FINAL VERSION)
Run this script once to migrate all master data from local Excel/CSV files to Supabase.
This version truncates tables before migration to ensure a clean state.
"""

import os
import sys
import math
import pandas as pd
from dotenv import load_dotenv
from postgrest import SyncPostgrestClient

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def get_client() -> SyncPostgrestClient:
    """Get PostgREST client."""
    rest_url = f"{SUPABASE_URL}/rest/v1"
    return SyncPostgrestClient(
        rest_url,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
    )


def clean_value(value):
    """Clean a value for JSON serialization."""
    if value is None:
        return None
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
    return value


def clean_record(record, valid_keys=None):
    """Clean a record by removing None/NaN values and filtering keys."""
    cleaned = {}
    for k, v in record.items():
        if valid_keys and k not in valid_keys:
            continue
        clean_v = clean_value(v)
        if clean_v is not None:
            cleaned[k] = clean_v
    return cleaned


def truncate_table(table_name):
    """Delete all records from a table using a DELETE without WHERE."""
    print(f"[TRUNCATE] Clearing table {table_name}...")
    client = get_client()
    try:
        # PostgREST doesn't support TRUNCATE directly easily, so we use DELETE
        # Need to ensure RLS allows delete or use service_role key if available
        # Here we try to delete all records
        client.from_(table_name).delete().neq("id", -1).execute()
    except Exception as e:
        print(f"  [WARNING] Could not clear {table_name}: {e}")


def migrate_customers():
    """Migrate customer data from Master Customer.xlsx to Supabase."""
    truncate_table("master_customers")
    print("[CUSTOMERS] Migrating customers...")
    
    df = pd.read_excel("Master/Master Customer.xlsx")
    
    column_mapping = {
        'COMPANY_CODE': 'company_code',
        'CUSTOMER_CODE': 'customer_code',
        'CUSTOMER_NAME': 'customer_name',
        'CUSTOMER_ADDRESS1': 'customer_address',
        'COUNTRY': 'country',
        'PAYMENTTERMCUSTOMER': 'payment_term_customer',
        'PAYMENTTERMCUSTOMERNAME': 'payment_term_customer_name',
        'HOLDSHIPMENT': 'hold_shipment',
        'PAYMENTTERMCUSTCOMP': 'payment_term_custcomp',
        'PAYMENTTERMCUSTCOMPNAME': 'payment_term_custcomp_name',
        'CREDITLIMITCUSTCOMP': 'credit_limit_custcomp',
        'BL_DATE': 'bl_date',
        'DOCUMENT_NO': 'document_no',
        'ORG_CODE': 'org_code',
        'REMARK': 'remark'
    }
    
    df = df.rename(columns=column_mapping)
    if 'bl_date' in df.columns:
        df['bl_date'] = pd.to_datetime(df['bl_date'], errors='coerce')
        df['bl_date'] = df['bl_date'].dt.strftime('%Y-%m-%d')
        df['bl_date'] = df['bl_date'].replace('NaT', None)
    
    records = df.to_dict('records')
    batch_size = 100
    client = get_client()
    valid_keys = set(column_mapping.values())
    
    uploaded = 0
    errors = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        clean_batch = [clean_record(r, valid_keys) for r in batch if clean_record(r, valid_keys).get('customer_code')]
        if clean_batch:
            try:
                client.from_("master_customers").insert(clean_batch).execute()
                uploaded += len(clean_batch)
                print(f"  [OK] Uploaded batch {i//batch_size + 1}")
            except Exception as e:
                errors += 1
                print(f"  [ERROR] Batch {i//batch_size + 1}: {e}")
    print(f"[DONE] Customers: {uploaded} uploaded")


def migrate_currencies():
    """Migrate currency data from MasterCurrency.xlsx to Supabase."""
    truncate_table("master_currencies")
    print("[CURRENCIES] Migrating currencies...")
    df = pd.read_excel("Master/MasterCurrency.xlsx")
    df.columns = ['sequence_no', 'code', 'currency_name', 'symbol', 'is_base_currency']
    df['is_base_currency'] = df['is_base_currency'].notna()
    records = [clean_record(r) for r in df.to_dict('records') if clean_record(r).get('code')]
    if records:
        get_client().from_("master_currencies").insert(records).execute()
    print(f"[DONE] Currencies: {len(records)} uploaded")


def migrate_ports():
    """Migrate port data from Master Port.csv to Supabase."""
    truncate_table("master_ports")
    print("[PORTS] Migrating ports...")
    df = pd.read_csv("Master/Master Port.csv", encoding='utf-8', low_memory=False)
    column_mapping = {
        'World Port Index Number': 'port_index_number',
        'Region Name': 'region_name',
        'Main Port Name': 'main_port_name',
        'Alternate Port Name': 'alternate_port_name',
        'UN/LOCODE': 'un_locode',
        'Country Code': 'country_code',
        'Latitude': 'latitude',
        'Longitude': 'longitude',
        'Harbor Size': 'harbor_size',
        'Harbor Type': 'harbor_type'
    }
    df = df[list(column_mapping.keys())].rename(columns=column_mapping)
    df['port_index_number'] = pd.to_numeric(df['port_index_number'], errors='coerce').fillna(0).astype(int)
    records = df.to_dict('records')
    batch_size = 500
    client = get_client()
    uploaded = 0
    for i in range(0, len(records), batch_size):
        batch = [clean_record(r) for r in records[i:i+batch_size] if clean_record(r).get('main_port_name')]
        if batch:
            try:
                client.from_("master_ports").insert(batch).execute()
                uploaded += len(batch)
                print(f"  [OK] Uploaded batch {i//batch_size + 1}")
            except Exception as e:
                print(f"  [ERROR] Batch {i//batch_size + 1}: {e}")
    print(f"[DONE] Ports: {uploaded} uploaded")


def migrate_overhead():
    """Migrate overhead data from Master.xlsx to Supabase."""
    truncate_table("master_overhead")
    print("[OVERHEAD] Migrating overhead rates...")
    try:
        df = pd.read_excel("Master.xlsx", sheet_name='Overhead', header=None)
        data_rows = []
        # Based on inspection, data rows for Group 0-6 are at indices 3 to 9
        for idx in range(3, 10):
            try:
                group_val = df.iloc[idx, 0] # Group is in col 0
                ovh_val = df.iloc[idx, 1]   # Overhead is in col 1
                if pd.notna(group_val):
                    data_rows.append({
                        'group_number': int(group_val), 
                        'overhead_rate': float(ovh_val) if pd.notna(ovh_val) else 0.0
                    })
            except Exception as e:
                print(f"  [SKIP] Row {idx}: {e}")
                continue
        if data_rows:
            get_client().from_("master_overhead").insert(data_rows).execute()
        print(f"[DONE] Overhead: {len(data_rows)} uploaded")
    except Exception as e: print(f"[ERROR] Overhead: {e}")


def migrate_factory_expense():
    """Migrate factory expense data from Master.xlsx to Supabase."""
    truncate_table("master_factory_expense")
    print("[FACTORY] Migrating factory expenses...")
    try:
        df = pd.read_excel("Master.xlsx", sheet_name='Factory Expense')
        rate = float(df.iloc[0, 0])
        get_client().from_("master_factory_expense").insert([{'expense_rate': rate, 'description': 'Factory Expense 2025'}]).execute()
        print(f"[DONE] Factory: 1 record uploaded ({rate})")
    except Exception as e: print(f"[ERROR] Factory: {e}")


def migrate_yield_loss():
    """Migrate yield loss percentage data from Master.xlsx to Supabase."""
    truncate_table("master_yield_loss")
    print("[YIELD] Migrating yield loss...")
    try:
        df = pd.read_excel("Master.xlsx", sheet_name='Yield Loss %')
        df.columns = ['group_number', 'yield_loss_percent']
        records = [{'group_number': int(r['group_number']), 'yield_loss_percent': float(r['yield_loss_percent'])} 
                   for _, r in df.dropna().iterrows()]
        if records:
            get_client().from_("master_yield_loss").insert(records).execute()
        print(f"[DONE] Yield Loss: {len(records)} uploaded")
    except Exception as e: print(f"[ERROR] Yield Loss: {e}")


def main():
    print("=" * 50); print("Starting Master Data Migration to Supabase"); print("=" * 50)
    if not SUPABASE_URL or not SUPABASE_KEY: return
    migrate_customers()
    migrate_currencies()
    migrate_ports()
    migrate_overhead()
    migrate_factory_expense()
    migrate_yield_loss()
    print("=" * 50); print("Migration Complete!"); print("=" * 50)

if __name__ == "__main__":
    main()
