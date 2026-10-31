import re
import pandas as pd

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

REQUIRED_COLUMNS = ["Employee_ID", "Name", "Email", "Salary"]


def normalize_columns(df):
    """Standardize Excel headers, e.g. 'Employee ID' -> 'Employee_ID'."""
    result = df.copy()
    result.columns = (
        result.columns.astype(str)
        .str.strip()
        .str.replace(r"\s+", "_", regex=True)
    )
    return result


def _is_missing(value):
    """Safely detect blank, None, or NaN values."""
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def validate_employee_records(df):
    """
    Validate all employee rows.
    Returns a list of defect dictionaries. Row Number is the Excel row number.
    """
    data = normalize_columns(df)

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in data.columns]
    if missing_columns:
        raise ValueError(
            "Missing required column(s): " + ", ".join(missing_columns)
        )

    defects = []

    # Normalize IDs for duplicate checking, while preserving original values.
    normalized_ids = data["Employee_ID"].apply(
        lambda value: "" if _is_missing(value) else str(value).strip().upper()
    )
    duplicate_mask = (
        normalized_ids.ne("") & normalized_ids.duplicated(keep=False)
    )

    for index, row in data.iterrows():
        employee_id = row["Employee_ID"]
        excel_row = int(index) + 2  # Header is Excel row 1.

        def add_defect(message):
            defects.append({
                "Row Number": excel_row,
                "Employee_ID": employee_id,
                "Defect": message
            })

        # Employee ID checks
        if _is_missing(employee_id) or str(employee_id).strip() == "":
            add_defect("Missing Employee ID")
        elif bool(duplicate_mask.loc[index]):
            add_defect("Duplicate Employee ID")

        # Name checks
        name = row["Name"]
        if _is_missing(name) or str(name).strip() == "":
            add_defect("Missing Employee Name")

        # Email checks
        email = row["Email"]
        if (
            _is_missing(email)
            or not EMAIL_PATTERN.fullmatch(str(email).strip())
        ):
            add_defect("Invalid Email")

        # Salary checks
        salary = row["Salary"]
        if _is_missing(salary) or str(salary).strip() == "":
            add_defect("Missing Salary")
        else:
            numeric_salary = pd.to_numeric(salary, errors="coerce")
            if pd.isna(numeric_salary):
                add_defect("Invalid Salary")
            elif numeric_salary < 0:
                add_defect("Negative Salary")

    return defects
