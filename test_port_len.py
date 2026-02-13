"""
Test Script: Try to insert ports with truncated Country Code
"""
import os
import sys
import pandas as pd
from dotenv import load_dotenv
from postgrest import SyncPostgrestClient

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_client() -> SyncPostgrestClient:
    rest_url = f"{SUPABASE_URL}/rest/v1"
    return SyncPostgrestClient(rest_url, headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})

def test_insert_truncated():
    client = get_client()
    # Try one record with Country Code truncated to 10
    record = {
        "main_port_name": "Test Port",
        "country_code": "ABCDEFGHIJ" # 10 chars
    }
    try:
        client.from_("master_ports").insert([record]).execute()
        print("Success with 10 chars!")
    except Exception as e:
        print(f"Failed even with 10 chars: {e}")

    # Try one record with 11 chars
    record_11 = {
        "main_port_name": "Test Port 11",
        "country_code": "ABCDEFGHIJK" # 11 chars
    }
    try:
        client.from_("master_ports").insert([record_11]).execute()
        print("Success with 11 chars!")
    except Exception as e:
        print(f"Failed with 11 chars: {e}")

if __name__ == "__main__":
    test_insert_truncated()
