import pandas as pd

employees = [
    {"Employee_ID": "E101", "Name": "Rahul", "Email": "rahul@example.com", "Salary": 45000},
    {"Employee_ID": "E102", "Name": "Priya", "Email": "priya@example.com", "Salary": 52000},
    {"Employee_ID": "E103", "Name": "", "Email": "amit@example.com", "Salary": 30000},
    {"Employee_ID": "E103", "Name": "Amit Kumar", "Email": "amit.kumar@example.com", "Salary": 60000},
    {"Employee_ID": "E104", "Name": "Amit", "Email": "amitexample.com", "Salary": -5000},
]

df = pd.DataFrame(employees)
df.to_excel("employee_input.xlsx", index=False)

print("Sample employee_input.xlsx created successfully.")
print(df.to_string(index=False))
