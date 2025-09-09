import io
from openpyxl import Workbook
from openpyxl.styles import Font
from typing import List
from fastapi.responses import StreamingResponse
from app.schemas.requirement import TraceabilityMatrixRow


def export_traceability_matrix_to_excel(matrix_rows: List[TraceabilityMatrixRow], project_name: str) -> StreamingResponse:
    wb = Workbook()
    ws = wb.active
    if ws is None:
        ws = wb.create_sheet(title="Traceability Matrix")
    else:
        ws.title = "Traceability Matrix"

    # Header
    headers = ["Req ID", "Requirements Module",
               "Test Case ID(s)", "Status", "Comments"]
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = Font(bold=True)

    # Data rows
    for row_idx, row in enumerate(matrix_rows, start=2):
        ws.cell(row=row_idx, column=1, value=row.requirement_id)
        ws.cell(row=row_idx, column=2, value=row.requirement_description)
        ws.cell(row=row_idx, column=3, value=", ".join(row.test_case_ids))

        # If all test cases Pass → Pass, else Fail, or Pending
        if all(status == "Pass" for status in row.test_statuses):
            status_summary = "Pass"
        elif any(status == "Fail" for status in row.test_statuses):
            status_summary = "Fail"
        elif any(status == "Not Yet" for status in row.test_statuses):
            status_summary = "Not Yet"
        else:
            status_summary = "Pending"
            
        ws.cell(row=row_idx, column=4, value=status_summary)

        # Comments can be added manually
        ws.cell(row=row_idx, column=5, value="")

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    project_name_safe = project_name.replace(" ", "_")[:50]

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={project_name_safe}_traceability_matrix.xlsx"}
    )
