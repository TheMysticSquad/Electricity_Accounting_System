# export_utils.py
import base64
import uuid
import os
from weasyprint import HTML

TEMP_DIR = "/tmp"

def generate_report(figures, titles, export_format="pdf"):
    file_id = uuid.uuid4().hex
    image_paths = []

    for fig, title in zip(figures, titles):
        if not fig or not fig.data:
            continue
        img_path = os.path.join(TEMP_DIR, f"{file_id}_{title}.png")
        fig.write_image(img_path)
        image_paths.append((title, img_path))

    html_content = "<html><head><style>img{width:600px;} h2{margin-top:40px;}</style></head><body>"
    html_content += "<h1>Electricity Network Report</h1>"
    for title, path in image_paths:
        html_content += f"<h2>{title}</h2><img src='file://{path}'/>"
    html_content += "</body></html>"

    export_path = os.path.join(TEMP_DIR, f"{file_id}.{export_format}")
    if export_format == "html":
        with open(export_path, "w") as f:
            f.write(html_content)
    else:
        HTML(string=html_content).write_pdf(export_path)

    with open(export_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
        mime = "application/pdf" if export_format == "pdf" else "text/html"
        href = f"data:{mime};base64,{encoded}"
        return href, f"report.{export_format}"
