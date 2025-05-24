# export_utils.py
import base64
import uuid
import os
import pandas as pd
from weasyprint import HTML
from datetime import datetime

TEMP_DIR = "/tmp"

def generate_report(figures, titles, export_format="pdf", data_df=None, filters=None, report_mode="summary"):
    file_id = uuid.uuid4().hex
    export_path = os.path.join(TEMP_DIR, f"{file_id}.{export_format}")

    # Format metadata
    metadata = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>"
    if filters:
        metadata += "Filters: " + ", ".join([f"{k}: {v}" for k, v in filters.items()]) + "<br>"

    # Handle graph-based reports
    if export_format in ["pdf", "html"]:
        image_paths = []
        for fig, title in zip(figures, titles):
            if not fig or not fig.data:
                continue
            img_path = os.path.join(TEMP_DIR, f"{file_id}_{title}.png")
            fig.write_image(img_path)
            image_paths.append((title, img_path))

        html_content = "<html><head><style>img{width:600px;} h2{margin-top:40px;}</style></head><body>"
        html_content += f"<h1>Electricity Network Report</h1><p>{metadata}</p>"
        for title, path in image_paths:
            html_content += f"<h2>{title}</h2><img src='file://{path}'/>"
        html_content += "</body></html>"

        if export_format == "html":
            with open(export_path, "w") as f:
                f.write(html_content)
        else:
            HTML(string=html_content).write_pdf(export_path)

    # Handle CSV/Excel data export
    elif export_format in ["csv", "excel"] and data_df is not None:
        data_df = data_df.copy()
        # Add summary row
        summary_row = {col: data_df[col].sum() if pd.api.types.is_numeric_dtype(data_df[col]) else '' for col in data_df.columns}
        summary_row['name'] = 'TOTAL'
        data_df = pd.concat([data_df, pd.DataFrame([summary_row])], ignore_index=True)

        if export_format == "csv":
            data_df.to_csv(export_path, index=False)
        else:
            with pd.ExcelWriter(export_path, engine='xlsxwriter') as writer:
                data_df.to_excel(writer, index=False, sheet_name='Report')
                workbook = writer.book
                worksheet = writer.sheets['Report']
                bold = workbook.add_format({'bold': True, 'bg_color': '#d9d9d9'})
                worksheet.set_row(0, None, bold)  # Header style

    with open(export_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
        mime = {
            "pdf": "application/pdf",
            "html": "text/html",
            "csv": "text/csv",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }[export_format]
        href = f"data:{mime};base64,{encoded}"
        ext = "xlsx" if export_format == "excel" else export_format
        return href, f"report.{ext}"
