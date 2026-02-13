import pandas as pd

def read_excel_logic():
    file_path = "Master/Master Calculator.xlsx"
    try:
        # Load the spreadsheet
        xls = pd.ExcelFile(file_path)
        print(f"Sheets: {xls.sheet_names}")
        
        # Usually, the main logic is in the first sheet or one named 'Spec'
        df = pd.read_excel(file_path, sheet_name=0)
        
        # Display first few rows to understand structure
        print("\n--- First 10 rows ---")
        print(df.head(10))
        
        # Search for Interest related keywords
        interest_rows = df[df.apply(lambda row: row.astype(str).str.contains('Interest', case=False).any(), axis=1)]
        print("\n--- Interest Related Rows ---")
        print(interest_rows)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read_excel_logic()
