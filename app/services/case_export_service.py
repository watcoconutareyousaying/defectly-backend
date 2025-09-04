from openpyxl import Workbook
from openpyxl.styles import Font
from typing import Dict, List

FIELD_ORDER = [
    "test_case_id",
    "module",
    "description",
    "precondition",
    "test_steps",
    "test_data",
    "expected_result",
    "actual_result",
    "status",
    "remarks",
]


def _write_dict_to_sheet(ws, data: Dict[str, any], field_order: List[str]):
    ws.cell(row=1, column=1, value="Field")
    ws.cell(row=1, column=2, value="Value")
    bold_font = Font(bold=True)
    ws["A1"].font = bold_font
    ws["B1"].font = bold_font
    row = 2
    for field in field_order:
        ws.cell(row=row, column=1, value=field.replace("_", " ").capitalize())
        ws.cell(row=row, column=2, value=data.get(field, ""))
        row += 1


def export_test_case_to_excel(tc_data: Dict[str, any]):
    wb = Workbook()
    ws = wb.active
    ws.title = "TestCase"
    _write_dict_to_sheet(ws, tc_data, FIELD_ORDER)
    return wb
