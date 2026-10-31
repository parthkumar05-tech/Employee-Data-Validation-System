import streamlit as st
import pandas as pd
from io import BytesIO

from employee_validator import (
    validate_employee_records,
    normalize_columns
)

st.set_page_config(
    page_title="Employee Data Validator",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Employee Data Validation System")
st.write("Upload your employee Excel file to automatically detect data errors.")

st.divider()

uploaded_file = st.file_uploader(
    "Upload Employee Excel File",
    type=["xlsx"]
)

if uploaded_file is not None:

    try:
        df = pd.read_excel(uploaded_file)
        df = normalize_columns(df)

        st.success("Excel file uploaded successfully!")

        st.subheader("📁 Uploaded Employee Data")
        st.dataframe(df, use_container_width=True)

        if st.button("Validate Employee Records", type="primary"):

            defects = validate_employee_records(df)

            defects_df = pd.DataFrame(
                defects,
                columns=["Row Number", "Employee_ID", "Defect"]
            )

            defective_rows = set(
                defects_df["Row Number"].tolist()
            )

            valid_indices = [
                i for i in range(len(df))
                if i + 2 not in defective_rows
            ]

            valid_df = df.iloc[valid_indices].copy()

            invalid_indices = [
                i for i in range(len(df))
                if i + 2 in defective_rows
            ]

            invalid_df = df.iloc[invalid_indices].copy()

            total = len(df)
            invalid_count = len(invalid_df)
            valid_count = len(valid_df)

            st.session_state["valid"] = valid_df
            st.session_state["invalid"] = invalid_df
            st.session_state["defects"] = defects_df

            st.session_state["total"] = total
            st.session_state["valid_count"] = valid_count
            st.session_state["invalid_count"] = invalid_count

        if "valid" in st.session_state:

            st.divider()
            st.subheader("📈 Validation Summary")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Total Employees",
                st.session_state["total"]
            )

            col2.metric(
                "Valid Records",
                st.session_state["valid_count"]
            )

            col3.metric(
                "Defective Records",
                st.session_state["invalid_count"]
            )

            st.subheader("✅ Valid Employee Records")
            st.dataframe(
                st.session_state["valid"],
                use_container_width=True
            )

            st.subheader("❌ Defective Employee Records")
            st.dataframe(
                st.session_state["invalid"],
                use_container_width=True
            )

            st.subheader("🔍 Detected Defects")
            st.dataframe(
                st.session_state["defects"],
                use_container_width=True
            )

            # Generate Excel report
            output = BytesIO()

            with pd.ExcelWriter(
                output,
                engine="openpyxl"
            ) as writer:

                df.to_excel(
                    writer,
                    sheet_name="Employee Data",
                    index=False
                )

                st.session_state["defects"].to_excel(
                    writer,
                    sheet_name="Defects",
                    index=False
                )

                summary = pd.DataFrame({
                    "Metric": [
                        "Total Employees",
                        "Valid Records",
                        "Defective Records"
                    ],
                    "Count": [
                        st.session_state["total"],
                        st.session_state["valid_count"],
                        st.session_state["invalid_count"]
                    ]
                })

                summary.to_excel(
                    writer,
                    sheet_name="Summary",
                    index=False
                )

            st.download_button(
                label="📥 Download Excel Report",
                data=output.getvalue(),
                file_name="employee_validation_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Please upload an Excel file to begin validation.")