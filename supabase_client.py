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
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def get_postgrest_client() -> SyncPostgrestClient:
    """Get a PostgREST client for Supabase database operations."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    
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
def fetch_yield_loss():
    """Fetch yield loss percentages from Supabase."""
    client = get_postgrest_client()
    response = client.from_("master_yield_loss").select("*").execute()
    return response.data


def get_overhead_by_group(group_number: int) -> float:
    """Get overhead rate for a specific group number."""
    overheads = fetch_overhead()
    for item in overheads:
        if item.get('group_number') == group_number:
            return item.get('overhead_rate', 0.0)
    return 0.0


def get_yield_loss_by_group(group_number: int) -> float:
    """Get yield loss percentage for a specific group number."""
    yield_losses = fetch_yield_loss()
    for item in yield_losses:
        if item.get('group_number') == group_number:
            return item.get('yield_loss_percent', 0.0)
    return 0.0
