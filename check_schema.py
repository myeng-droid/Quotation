import os
from postgrest import SyncPostgrestClient
from dotenv import load_dotenv

load_dotenv()

def check_table(table_name):
    rest_url = f"{os.getenv('SUPABASE_URL')}/rest/v1"
    client = SyncPostgrestClient(
        rest_url,
        headers={
            "apikey": os.getenv("SUPABASE_KEY"),
            "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}"
        }
    )
    try:
        # Try a simple select
        client.from_(table_name).select("*").limit(1).execute()
        print(f"[OK] Table '{table_name}' exists.")
    except Exception as e:
        print(f"[ERROR] Table '{table_name}': {e}")

if __name__ == "__main__":
    check_table("master_rm_cost")
    check_table("master_calculator")
    check_table("master_input")
