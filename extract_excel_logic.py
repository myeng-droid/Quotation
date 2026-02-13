import pandas as pd

def extract_logic():
    file_path = "Master/Master Calculator.xlsx"
    xls = pd.ExcelFile(file_path)
    print(f"All Sheets: {xls.sheet_names}")

if __name__ == "__main__":
    extract_logic()
