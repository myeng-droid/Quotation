import pandas as pd
import os

file_path = "Master/MasterCurrency.xlsx"
if os.path.exists(file_path):
    try:
        df = pd.read_excel(file_path, nrows=5)
        print("Columns in MasterCurrency.xlsx:")
        print(df.columns.tolist())
        print("\nFirst 5 rows:")
        print(df.to_string())
    except Exception as e:
        print(f"Error reading Excel: {e}")
else:
    print(f"File not found: {file_path}")
