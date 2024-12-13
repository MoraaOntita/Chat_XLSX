import os
import pandas as pd

def split_sheet_into_tables(sheet_data):
    """
    Splits a single Excel sheet's data into multiple tables based on blank rows.
    """
    tables = []  # List to hold detected tables
    current_table = []  # Temporary storage for rows in the current table

    for _, row in sheet_data.iterrows():
        # Check if the row is completely blank
        if row.isnull().all():
            # If we reach a blank row and the current table has data, save it
            if current_table:
                tables.append(pd.DataFrame(current_table))
                current_table = []  # Reset for the next table
        else:
            # Add non-blank row to the current table
            current_table.append(row)

    # Add the last table if the sheet doesn't end with a blank row
    if current_table:
        tables.append(pd.DataFrame(current_table))

    return tables

def extract_and_save_tables_from_excel(excel_file, output_folder):
    """
    Extracts tables from each sheet in an Excel file and saves them as separate CSV files.

    Args:
        excel_file (str): Path to the input Excel file.
        output_folder (str): Folder where the extracted tables will be saved.
    """
    # Load the Excel file
    xls = pd.ExcelFile(excel_file)
    os.makedirs(output_folder, exist_ok=True)  # Ensure output folder exists

    # Iterate through all sheets
    for sheet_name in xls.sheet_names:
        print(f"Processing sheet: {sheet_name}")
        # Load the sheet (no header assumed initially)
        sheet_data = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)

        # Split sheet into tables
        tables = split_sheet_into_tables(sheet_data)

        # Save each table as a separate CSV
        for idx, table in enumerate(tables):
            # Clean table: drop all-NaN columns, reset index
            table_cleaned = table.dropna(how="all", axis=1).reset_index(drop=True)

            # Auto-fix column headers if necessary
            table_cleaned.columns = [f"Column_{i}" for i in range(len(table_cleaned.columns))]

            # Save the table as a CSV file
            output_csv = os.path.join(output_folder, f"{sheet_name}_table_{idx+1}.csv")
            table_cleaned.to_csv(output_csv, index=False)
            print(f"Saved table {idx+1} from sheet '{sheet_name}' to {output_csv}")
