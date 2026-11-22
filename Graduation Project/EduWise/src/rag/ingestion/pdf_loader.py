# Extract text from PDFs (PyMuPDF)
# مسؤول عن استخراج النصوص من ملفات 
# PDF وتحويلها إلى قائمة من النصوص، بحيث كل عنصر يمثل صفحة مستقلة


from pathlib import Path
import fitz # مكتبة PyMuPDF المسؤولة عن قراءة ملفات PDF واستخراج النصوص

def load_pdf_pages(pdf_path: str | Path) -> list[str]:
    path = Path(pdf_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"PDF not found at: {path}")

    doc = fitz.open(path)
    try:
        raw_pages = [page.get_text("text") for page in doc]
    finally:
        doc.close()
    return raw_pages