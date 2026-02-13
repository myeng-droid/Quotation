import pandas as pd

def extract_exact():
    file_path = "Master/Master Calculator.xlsx"
    df = pd.read_excel(file_path, sheet_name='Spec Calculator', header=None)
    for i, row in df.iterrows():
        row_str = " | ".join(map(str, row.values))
        if "MarginCost" in row_str or "Total Cost" in row_str:
            print(f"Row {i}: {row_str}")

if __name__ == "__main__":
    extract_exact()
