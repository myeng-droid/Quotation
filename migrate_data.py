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
        client.from_(table_name).delete().neq("id", -1).execute()
    except Exception as e:
        if "PGRST205" in str(e):
            print(f"  [CRITICAL] Table '{table_name}' does not exist in Supabase! Please create it first.")
        else:
            print(f"  [WARNING] Could not clear {table_name}: {e}")


def migrate_customers():
    """Migrate customer data from Master Customer.xlsx to Supabase."""
    truncate_table("master_customers")
    print("[CUSTOMERS] Migrating customers...")
    
    # Try both root and Master folder
    file_path = "Master Customer.xlsx" if os.path.exists("Master Customer.xlsx") else "Master/Master Customer.xlsx"
    df = pd.read_excel(file_path)
    
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
    file_path = "MasterCurrency.xlsx" if os.path.exists("MasterCurrency.xlsx") else "Master/MasterCurrency.xlsx"
    df = pd.read_excel(file_path)
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
    """Migrate overhead data and yield loss from Master.xlsx to Supabase."""
    truncate_table("master_overhead")
    print("[OVERHEAD] Migrating overhead rates (including yield loss)...")
    try:
        # Load Overhead rates
        df_oh = pd.read_excel("Master.xlsx", sheet_name='Overhead', header=None)
        
        # Load Yield Loss percentages
        df_yield = pd.read_excel("Master.xlsx", sheet_name='Yield Loss %')
        df_yield.columns = ['group_number', 'yield_loss_percent']
        yield_map = {int(r['group_number']): float(r['yield_loss_percent']) 
                     for _, r in df_yield.dropna().iterrows()}

        data_rows = []
        # Based on inspection, data rows for Group 0-6 are at indices 3 to 9
        for idx in range(3, 10):
            try:
                group_val = df_oh.iloc[idx, 0] # Group is in col 0
                ovh_val = df_oh.iloc[idx, 1]   # Overhead is in col 1
                if pd.notna(group_val):
                    g_num = int(group_val)
                    data_rows.append({
                        'group_number': g_num, 
                        'overhead_rate': float(ovh_val) if pd.notna(ovh_val) else 0.0,
                        'yield_loss_percent': yield_map.get(g_num, 0.0)
                    })
            except Exception as e:
                print(f"  [SKIP] Row {idx}: {e}")
                continue
        
        if data_rows:
            get_client().from_("master_overhead").insert(data_rows).execute()
        print(f"[DONE] Overhead & Yield Loss: {len(data_rows)} uploaded")
    except Exception as e: print(f"[ERROR] Overhead Migration: {e}")


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




def migrate_shipping_rates():
    """Migrate shipping rates from Doc/shipping_rates_structure.csv to Supabase."""
    truncate_table("shipping_rates")
    print("[SHIPPING] Migrating shipping rates...")
    try:
        df = pd.read_csv("Doc/shipping_rates_structure.csv")
        # Columns: tier_id,min_qty,max_qty,price_per_container,unit,description_th
        records = []
        for _, row in df.iterrows():
            records.append({
                'min_qty': int(row['min_qty']),
                'max_qty': int(row['max_qty']),
                'price_per_container': float(row['price_per_container']),
                'unit': str(row['unit']),
                'description_th': str(row['description_th'])
            })
        
        if records:
            get_client().from_("shipping_rates").insert(records).execute()
        print(f"[DONE] Shipping Rates: {len(records)} uploaded")
    except Exception as e:
        print(f"[ERROR] Shipping Rates: {e}")


def migrate_rm_costs():
    """Migrate RM costs from Master/MasterRMCost.xlsx to Supabase."""
    truncate_table("master_rm_cost")
    print("[RM COST] Migrating RM costs...")
    try:
        df = pd.read_excel("Master/MasterRMCost.xlsx")
        # Columns: Product, Price, Update
        records = []
        for _, row in df.iterrows():
            if pd.isna(row['Product']) or pd.isna(row['Price']):
                continue
            update_date = pd.to_datetime(row['Update'])
            records.append({
                'product': str(row['Product']),
                'price': float(row['Price']),
                'update_date': update_date.strftime('%Y-%m-%d')
            })
        
        if records:
            # Upload in batches
            client = get_client()
            for i in range(0, len(records), 100):
                batch = records[i:i+100]
                client.from_("master_rm_cost").insert(batch).execute()
        print(f"[DONE] RM Costs: {len(records)} uploaded")
    except Exception as e:
        print(f"[ERROR] RM Costs: {e}")


def migrate_calculator():
    """Migrate Calculator specs from Master/Master Calculator.xlsx to Supabase."""
    truncate_table("master_calculator")
    print("[CALCULATOR] Migrating specs...")
    try:
        df = pd.read_excel("Master/Master Calculator.xlsx")
        # Columns: หัวข้อ, วิธีทำงาน, ตัวอย่าง
        records = []
        for _, row in df.iterrows():
            records.append({
                'topic': str(row.iloc[0]),
                'method': str(row.iloc[1]),
                'example': str(row.iloc[2]) if len(row) > 2 else ""
            })
        
        if records:
            get_client().from_("master_calculator").insert(records).execute()
        print(f"[DONE] Calculator Specs: {len(records)} uploaded")
    except Exception as e:
        print(f"[ERROR] Calculator Specs: {e}")


def main():
    print("=" * 50); print("Starting Master Data Migration to Supabase"); print("=" * 50)
    if not SUPABASE_URL or not SUPABASE_KEY: return
    migrate_customers()
    migrate_currencies()
    migrate_ports()
    migrate_overhead()
    migrate_factory_expense()
    # migrate_yield_loss() (DELETED - merged into overhead)
    migrate_shipping_rates()
    migrate_rm_costs()
    migrate_calculator()
    print("=" * 50); print("Migration Complete!"); print("=" * 50)

if __name__ == "__main__":
    main()
