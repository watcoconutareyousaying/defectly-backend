from openpyxl import Workbook
from openpyxl.styles import Font
from typing import List, Dict
from app.models.case import Case

# Define the header and the corresponding keys in your case_data
EXPORT_COLUMNS = [
    ("Test Case ID", "case_id"),
    ("Module", "module"),
    ("Title", "title"),  # <- you can map description/title as needed
    ("Description", "description"),
    ("Test Steps", "steps"),
    ("Test Data", "data"),
    ("Expected Result", "expected_result"),
    ("Priority", "priority"),   # make sure your schema supports this
    ("Status", "status"),
    ("Remarks", "remarks"),
]


def export_cases_to_excel(cases: List[Case]):
    wb = Workbook()
    if wb.active is None:
        ws = wb.create_sheet(title="TestCases")
    else:
        ws = wb.active
        ws.title = "TestCases"

    # Write header row
    for col_idx, (header, _) in enumerate(EXPORT_COLUMNS, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = Font(bold=True)

    # Write case rows
    for row_idx, case in enumerate(cases, start=2):
        data: Dict = case.case_data or {}
        for col_idx, (_, field_key) in enumerate(EXPORT_COLUMNS, start=1):
            ws.cell(row=row_idx, column=col_idx, value=data.get(field_key, ""))

    return wb
