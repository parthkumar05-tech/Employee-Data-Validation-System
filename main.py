from pathlib import Path
import sys
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from employee_validator import (
    REQUIRED_COLUMNS,
    normalize_columns,
    validate_employee_records,
)

INPUT_FILE = Path("employee_input.xlsx")
OUTPUT_FILE = Path("employee_validation_report.xlsx")


def format_worksheet(worksheet):
    """Apply readable formatting to a report worksheet."""
    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions

    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)

    for cell in worksheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    for column_cells in worksheet.columns:
        max_length = max(
            (len(str(cell.value)) if cell.value is not None else 0)
            for cell in column_cells
        )
        column_letter = get_column_letter(column_cells[0].column)
        worksheet.column_dimensions[column_letter].width = min(max(max_length + 3, 14), 40)


def create_report(employee_df, defects):
    defects_df = pd.DataFrame(
        defects,
        columns=["Row Number", "Employee_ID", "Defect"]
    )

    summary_rows = [
        ("Total employee records", len(employee_df)),
        ("Total defects", len(defects_df)),
        ("Records with defects", len(set(d["Row Number"] for d in defects))),
        ("Records without defects",
         len(employee_df) - len(set(d["Row Number"] for d in defects))),
    ]

    summary_df = pd.DataFrame(summary_rows, columns=["Metric", "Value"])

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        employee_df.to_excel(writer, sheet_name="Employee Data", index=False)
        defects_df.to_excel(writer, sheet_name="Defects", index=False)
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        for sheet in writer.book.worksheets:
            format_worksheet(sheet)

    return defects_df


def main():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        print("Run 'python3 create_sample_data.py' to create a sample input file.")
        sys.exit(1)

    try:
        employee_df = pd.read_excel(INPUT_FILE)
        employee_df = normalize_columns(employee_df)

        missing_columns = [
            col for col in REQUIRED_COLUMNS if col not in employee_df.columns
        ]
        if missing_columns:
            print("Your Excel file is missing these columns:", ", ".join(missing_columns))
            print("Required columns:", ", ".join(REQUIRED_COLUMNS))
            sys.exit(1)

        defects = validate_employee_records(employee_df)
        defects_df = create_report(employee_df, defects)

    except Exception as error:
        print(f"Could not process the Excel file: {error}")
        sys.exit(1)

    print("\n===== EMPLOYEE RECORDS =====")
    print(employee_df.to_string(index=False))

    print("\n===== VALIDATION RESULTS =====")
    if defects_df.empty:
        print("No defects found. All employee records are valid.")
    else:
        print(defects_df.to_string(index=False))

    print(f"\nExcel report generated successfully: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
