import unittest
import pandas as pd

from employee_validator import validate_employee_records


class TestEmployeeValidation(unittest.TestCase):

    def make_df(self, records):
        return pd.DataFrame(records)

    def test_valid_employee(self):
        df = self.make_df([{
            "Employee_ID": "E101",
            "Name": "Rahul",
            "Email": "rahul@example.com",
            "Salary": 45000
        }])
        self.assertEqual(validate_employee_records(df), [])

    def test_missing_name(self):
        df = self.make_df([{
            "Employee_ID": "E101",
            "Name": "",
            "Email": "rahul@example.com",
            "Salary": 45000
        }])
        defects = validate_employee_records(df)
        self.assertIn("Missing Employee Name", [d["Defect"] for d in defects])

    def test_negative_salary(self):
        df = self.make_df([{
            "Employee_ID": "E101",
            "Name": "Amit",
            "Email": "amit@example.com",
            "Salary": -5000
        }])
        defects = validate_employee_records(df)
        self.assertIn("Negative Salary", [d["Defect"] for d in defects])

    def test_invalid_email(self):
        df = self.make_df([{
            "Employee_ID": "E101",
            "Name": "Amit",
            "Email": "amitexample.com",
            "Salary": 45000
        }])
        defects = validate_employee_records(df)
        self.assertIn("Invalid Email", [d["Defect"] for d in defects])

    def test_duplicate_employee_ids_flag_both_rows(self):
        df = self.make_df([
            {"Employee_ID": "E103", "Name": "Amit", "Email": "amit@example.com", "Salary": 30000},
            {"Employee_ID": "E103", "Name": "Amit Kumar", "Email": "amit.k@example.com", "Salary": 60000},
        ])
        defects = validate_employee_records(df)
        duplicate_defects = [d for d in defects if d["Defect"] == "Duplicate Employee ID"]
        self.assertEqual(len(duplicate_defects), 2)

    def test_missing_employee_id(self):
        df = self.make_df([{
            "Employee_ID": "",
            "Name": "Rahul",
            "Email": "rahul@example.com",
            "Salary": 45000
        }])
        defects = validate_employee_records(df)
        self.assertIn("Missing Employee ID", [d["Defect"] for d in defects])

    def test_invalid_salary(self):
        df = self.make_df([{
            "Employee_ID": "E101",
            "Name": "Rahul",
            "Email": "rahul@example.com",
            "Salary": "not-a-number"
        }])
        defects = validate_employee_records(df)
        self.assertIn("Invalid Salary", [d["Defect"] for d in defects])

    def test_missing_salary(self):
        df = self.make_df([{
            "Employee_ID": "E101",
            "Name": "Rahul",
            "Email": "rahul@example.com",
            "Salary": None
        }])
        defects = validate_employee_records(df)
        self.assertIn("Missing Salary", [d["Defect"] for d in defects])

    def test_missing_required_column_raises_error(self):
        df = self.make_df([{
            "Employee_ID": "E101",
            "Name": "Rahul",
            "Email": "rahul@example.com"
        }])
        with self.assertRaises(ValueError):
            validate_employee_records(df)


if __name__ == "__main__":
    unittest.main(verbosity=2)
