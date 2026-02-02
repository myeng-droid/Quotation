import pandas as pd
import os

file_path = "Master/Master Customer.xlsx"
if os.path.exists(file_path):
    try:
        # Read the first few rows to see columns and data
        df = pd.read_excel(file_path, nrows=5)
        print("Columns in Master Customer.xlsx:")
        print(df.columns.tolist())
        print("\nFirst 5 rows:")
        print(df.to_string())
        
        # Check for specific columns requested by user
        required = ["CUSTOMER_CODE", "CUSTOMER_NAME"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            print(f"\nWarning: Missing columns: {missing}")
        else:
            print(f"\nSuccess: Found required columns: {required}")
            
    except Exception as e:
        print(f"Error reading Excel: {e}")
else:
    print(f"File not found: {file_path}")
