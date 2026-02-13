import os
from postgrest import SyncPostgrestClient
from dotenv import load_dotenv

load_dotenv()

def check_overhead():
    rest_url = f"{os.getenv('SUPABASE_URL')}/rest/v1"
    client = SyncPostgrestClient(
        rest_url,
        headers={
            "apikey": os.getenv("SUPABASE_KEY"),
            "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}"
        }
    )
    try:
        data = client.from_("master_overhead").select("*").execute().data
        for item in data:
            print(f"Group {item['group_number']}: Rate={item['overhead_rate']}, YieldLoss={item['yield_loss_percent']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_overhead()
